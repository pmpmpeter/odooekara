# -*- coding: utf-8 -*-
from collections import defaultdict
from contextlib import ExitStack, contextmanager
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from hashlib import sha256
from json import dumps
import logging
from markupsafe import Markup
from psycopg2 import OperationalError
import re
from textwrap import shorten
from unittest.mock import patch
import base64
from io import BytesIO
from odoo.tools.misc import xlsxwriter
from num2words import num2words
from odoo import api, fields, models, _, Command
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.addons.account.tools import format_structured_reference_iso
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    groupby,
    index_exists,
    is_html_empty,
)

_logger = logging.getLogger(__name__)
import pdb

MAX_HASH_VERSION = 3

PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]

TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'entry',
    'in_invoice': 'in_refund',
    'in_refund': 'entry',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}

EMPTY = object()

BILL_APPR = ['in_invoice', 'in_receipt', 'in_refund']


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('to approve', 'To Approve'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )
    expense_sequence = fields.Char(string='Task ID')
    expense_type = fields.Selection([
        ("capex", "Capex"),
        ("opex", "Opex")], default='opex', string="Capex/Opex")
    expense_invoice_no = fields.Char(string="Tax/Proforma Invoice No")
    expense_invoice_type_id = fields.Many2one('invoice.type', string="Type of Invoice")
    expense_user_id = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    is_payment_approval = fields.Boolean(string="Is Payment Approval", default=False)
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    partner_tcs_warning = fields.Text(
        compute='_compute_partner_tcs_warning',
        groups="account.group_account_invoice,account.group_account_readonly",
    )
    partner_tds_warning = fields.Text(
        compute='_compute_partner_tds_warning',
        groups="account.group_account_invoice,account.group_account_readonly",
    )
    budget_id = fields.Many2one('crossovered.budget.lines', 'Budget Code', copy=False, required=0)

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            if m.invoice_filter_type_domain:
                journal_type = [m.invoice_filter_type_domain]
            else:
                journal_type = ['cash', 'bank', 'general']
            # pdb.set_trace()
            company = m.company_id or self.env.company
            m.suitable_journal_ids = self.env['account.journal'].search([
                *self.env['account.journal']._check_company_domain(company),
                ('type', 'in', journal_type),
            ])

    @api.depends('company_id', 'partner_id', 'amount_total', 'currency_id', 'invoice_line_ids.quantity',
                 'invoice_line_ids.price_unit', 'amount_untaxed_signed')
    def _compute_partner_tcs_warning(self):
        msg = ''
        for move in self.filtered(lambda move: move.partner_id.commercial_partner_id.tcs_applicable):
            move.with_company(move.company_id)
            move.partner_tcs_warning = ''
            invoice_date = move.invoice_date or move.date or fields.Date.today()
            domain1 = [('date_from', '<=', invoice_date), ('date_to', '>=', invoice_date)]
            fiscal_year = self.env['account.fiscal.year'].sudo().search(domain1, limit=1)
            fiscal_year_start_date = fiscal_year_end_date = invoice_date
            basic_amount = 0
            if fiscal_year:
                fiscal_year_start_date = fiscal_year.date_from
                fiscal_year_end_date = fiscal_year.date_to
            if move.partner_id and move.amount_untaxed_signed > 0:
                query1 = """
                        SELECT sum(am.amount_untaxed_signed) as amount_untaxed_signed
                        FROM account_move am
                        where am.move_type in ('out_invoice', 'out_refund', 'out_receipt') and am.partner_id=%s
                        and am.date<=%s and am.date>=%s and am.state='posted';
                        """
                query_params1 = (
                    move.partner_id.commercial_partner_id.id, str(fiscal_year_end_date), str(fiscal_year_start_date))
                data_get1 = self.env.cr.execute(query1, query_params1)
                lines1 = self.env.cr.dictfetchall()
                if lines1[0].get('amount_untaxed_signed') and lines1[0].get('amount_untaxed_signed') != None:
                    basic_amount = lines1[0].get('amount_untaxed_signed')
            show_warning = move.state == 'draft' and move.move_type in ['out_invoice', 'out_receipt']
            if move.move_type in ['out_invoice', 'out_receipt']:
                basic_amount += move.tax_totals['amount_untaxed']
            elif move.move_type in ['out_refund']:
                basic_amount -= move.tax_totals['amount_untaxed']
            tcs_limit = self.partner_id.commercial_partner_id.tcs_applicable or self.company_id.tcs_limit
            tcs_limit_amount = self.partner_id.commercial_partner_id.tcs_limit_amount_partner or self.company_id.tcs_limit_amount
            if show_warning and tcs_limit and basic_amount > float(tcs_limit_amount):
                basic_amount_formatted = formatLang(self.env, basic_amount, currency_obj=move.company_id.currency_id)
                tcs_limit_amount_formatted = formatLang(self.env, float(tcs_limit_amount),
                                                        currency_obj=move.company_id.currency_id)
                msg = "Cummulative Sales for - %s in %s is %s which is exceeding TCS limit of %s." % (
                    move.partner_id.name, fiscal_year.display_name, basic_amount_formatted, tcs_limit_amount_formatted)
        self.partner_tcs_warning = msg

    @api.depends('company_id', 'partner_id', 'amount_total', 'currency_id', 'invoice_line_ids.quantity',
                 'invoice_line_ids.price_unit', 'amount_untaxed_signed')
    def _compute_partner_tds_warning(self):
        msg = ''
        for move in self.filtered(lambda move: move.partner_id.commercial_partner_id.tds_applicable):
            move.with_company(move.company_id)
            move.partner_tds_warning = ''
            invoice_date = move.invoice_date or move.date or fields.Date.today()
            domain1 = [('date_from', '<=', invoice_date), ('date_to', '>=', invoice_date)]
            fiscal_year = self.env['account.fiscal.year'].sudo().search(domain1, limit=1)
            fiscal_year_start_date = fiscal_year_end_date = invoice_date
            basic_amount = 0
            if fiscal_year:
                fiscal_year_start_date = fiscal_year.date_from
                fiscal_year_end_date = fiscal_year.date_to
            if move.partner_id and move.amount_untaxed_signed < 0:
                query1 = """
                           SELECT sum(am.amount_untaxed_signed) as amount_untaxed_signed
                           FROM account_move am
                           where am.move_type in ('in_invoice', 'in_refund', 'in_receipt') and am.partner_id=%s
                           and am.date<=%s and am.date>=%s and am.state='posted';
                           """
                query_params1 = (
                    move.partner_id.commercial_partner_id.id, str(fiscal_year_end_date), str(fiscal_year_start_date))
                data_get1 = self.env.cr.execute(query1, query_params1)
                lines1 = self.env.cr.dictfetchall()
                if lines1[0].get('amount_untaxed_signed') and lines1[0].get('amount_untaxed_signed') != None:
                    basic_amount = -lines1[0].get('amount_untaxed_signed')
            show_warning = move.state == 'draft' and move.move_type in ['in_invoice', 'in_receipt']
            if move.move_type in ['in_invoice', 'in_receipt']:
                basic_amount += move.tax_totals['amount_untaxed']
            elif move.move_type in ['in_refund']:
                basic_amount -= move.tax_totals['amount_untaxed']
            tds_limit = self.partner_id.commercial_partner_id.tds_applicable or self.company_id.tds_limit
            tds_limit_amount = self.partner_id.commercial_partner_id.tds_limit_amount_partner or self.company_id.tds_limit_amount
            tds_tax_id = self.partner_id.commercial_partner_id.tds_tax_id or self.company_id.tds_tax_id
            if show_warning and tds_limit and basic_amount > float(tds_limit_amount):
                basic_amount_formatted = formatLang(self.env, basic_amount, currency_obj=move.company_id.currency_id)
                tds_limit_amount_formatted = formatLang(self.env, float(tds_limit_amount),
                                                        currency_obj=move.company_id.currency_id)
                msg = "Cummulative Purchases for - %s in %s is %s which is exceeding TDS limit of %s. Kindly deduct %s." % (
                    move.partner_id.name, fiscal_year.display_name, basic_amount_formatted, tds_limit_amount_formatted,
                    tds_tax_id.display_name)
        self.partner_tds_warning = msg

    @api.depends('approval_document.type_id.state', 'approval_document.line_ids.state')
    def compute_approval_state(self):
        for record in self:
            if record.approval_document:
                line_states = record.approval_document.line_ids.mapped('state')
                if all(state == 'Draft' for state in line_states):
                    record.approval_state = 'Waiting For Approval'
                elif 'Waiting for Approval' in line_states:
                    waiting_lines = record.approval_document.line_ids.filtered(
                        lambda l: l.state == 'Waiting for Approval')
                    if waiting_lines:
                        record.approval_state = f"Waiting for {', '.join(waiting_lines.mapped('name'))} Approval"
                elif all(state == 'Approved' for state in line_states):
                    record.approval_state = 'Approved'
                elif 'Refused' in line_states:
                    record.approval_state = 'Rejected'
                elif 'Cancel' in line_states:
                    record.approval_state = 'Cancelled'
            else:
                entry_rec = self.env['multi.approval.type'].sudo().search(
                    [('model_id', '=', 'account.move'), ('state', '=', 'confirm'),
                     ('description', '=', 'Journal Entries')], limit=1)
                rec = self.env['multi.approval.type'].sudo().search(
                    [('model_id', '=', 'account.move'), ('state', '=', 'confirm')], limit=1)
                if record.move_type == 'entry':
                    if entry_rec:
                        record.approval_state = 'To Submit for Approval'
                    else:
                        record.approval_state = 'Not Applicable'
                elif record.move_type == 'out_invoice':
                    if rec:
                        record.approval_state = 'To Submit for Approval'
                    else:
                        record.approval_state = 'Not Applicable'
                elif record.move_type == 'in_invoice':
                    if rec:
                        record.approval_state = 'To Submit for Approval'

    def button_draft(self):
        super().button_draft()
        for record in self:
            rec = self.env['multi.approval.type'].sudo().search(
                [('model_id', '=', 'account.move'), ('state', '=', 'confirm')], limit=1)
            if rec:
                record.approval_state = 'To Submit for Approval'
                record.x_has_request_approval = False

    def button_cancel(self):
        # Shortcut to move from posted to cancelled directly. Useful for E-invoices that must not be changed
        # when sent to the government.
        moves_to_reset_draft = self.filtered(lambda x: x.state == 'posted')
        if moves_to_reset_draft:
            moves_to_reset_draft.button_draft()

        # Check if any journal entry is neither in 'draft' nor 'approve' state
        if any(move.state not in ['draft', 'to approve'] for move in self):
            raise UserError(_("Only draft or to approved journal entries can be cancelled."))

        # Write state change to 'cancel'
        model_name = 'account.move'
        res_id = self.id
        origin_ref = f"{model_name},{res_id}"
        existing_approvals = self.env['multi.approval'].search([("origin_ref", "=", origin_ref)])
        existing_approvals.write({'state': 'Cancel'})
        self.write({
            'auto_post': 'no',
            'approval_state': 'Not Applicable',
            'x_has_request_approval': False,
            'state': 'cancel'
        })

    def action_post(self):
        for rec in self:
            purchase_order = self.line_ids.purchase_line_id.order_id
            if purchase_order:
                purchase_order.budget_id.reserved_amount -= rec.amount_untaxed
        res = super(AccountMoveInherit, self).action_post()
        for rec in self:
            if rec.move_type == 'in_invoice' and rec.partner_id.tds_applicable:
                wiz_tds = self.env['l10n_in.withhold.wizard'].with_context({
                    'active_ids': rec.ids,  # Pass the active record ID
                    'active_model': self._name  # Pass the current model name
                }).create({})
                wiz_line_tds = self.env['l10n_in.withhold.wizard.line'].create({
                    'withhold_id': wiz_tds.id,
                    'tax_id': rec.partner_id.tds_tax_id.id,
                    'base': rec.amount_untaxed,
                })
                wiz_tds.action_create_and_post_withhold()
        return res
