from odoo import api, fields, models, _, Command, tools
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from bisect import bisect_left
from collections import defaultdict
from math import *
import datetime
import re
import pdb
from datetime import date, timedelta, datetime
from num2words import num2words
from odoo.osv import expression
from odoo.tools import format_amount, format_date, formatLang, groupby
from odoo.tools.float_utils import float_is_zero
from markupsafe import Markup


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    purchase_type = fields.Many2one('purchase.orders.type','Purchase Type')
    budget_id = fields.Many2one('crossovered.budget.lines','Budget Code', copy=False)
    budget_balance_warning = fields.Html(
        compute='_compute_budget_balance_warning',
    )

    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)

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
                rec = self.env['multi.approval.type'].sudo().search(
                    [('model_id', '=', 'purchase.order'), ('state', '=', 'confirm')], limit=1)
                if rec:
                    record.approval_state = 'To Submit for Approval'
                else:
                    record.approval_state = 'Not Applicable'

    @api.depends('budget_id','company_id', 'partner_id', 'amount_total', 'currency_id', 'order_line.product_qty', 'order_line.price_unit','amount_untaxed')
    def _compute_budget_balance_warning(self):
        msg=''
        for order in self.filtered(lambda s: s.budget_id):
            order.with_company(order.company_id)
            order.budget_balance_warning = ''
            po_date = order.date_order or fields.Date.today()
            # domain1 = [('date_from', '<=', po_date), ('date_to', '>=', po_date),('id', '=', order.budget_id.id)]
            domain1 = [('id', '=', order.budget_id.id)]
            budget_allocated_id = self.env['crossovered.budget.lines'].sudo().search(domain1, limit=1)
            if budget_allocated_id:
                allocated_amount= budget_allocated_id.planned_amount
                spent_amount = budget_allocated_id.practical_amount
                available_amount = allocated_amount - spent_amount
                allocated_amount_formatted = formatLang(self.env, allocated_amount, currency_obj=order.company_id.currency_id)
                available_amount_formatted = formatLang(self.env, available_amount, currency_obj=order.company_id.currency_id)
                if order.amount_total > available_amount:
                    msg = Markup(
                              "<span style='color: red;'>Alert !! Budget is exceeding for %s."
                              "Allocated budget is %s and Available balance is %s.</span>"
                          ) % (order.budget_id.display_name, allocated_amount_formatted, available_amount_formatted)
                else:
                    msg = Markup(
                              "For %s Allocated budget is %s and Available balance is %s."
                          ) % (order.budget_id.display_name, allocated_amount_formatted, available_amount_formatted)
            else:
                msg = Markup("Alert !! No active budget found.</span>")
        self.budget_balance_warning = msg

    def exceed_budget_balance_warning(self):
        msg = ''
        for order in self.filtered(lambda s: s.budget_id):
            order.with_company(order.company_id)
            order.budget_balance_warning = ''
            po_date = order.date_order or fields.Date.today()
            # domain1 = [('date_from', '<=', po_date), ('date_to', '>=', po_date), ('id', '=', order.budget_id.id)]
            domain1 = [('id', '=', order.budget_id.id)]
            budget_allocated_id = self.env['crossovered.budget.lines'].sudo().search(domain1, limit=1)
            if budget_allocated_id:
                allocated_amount = budget_allocated_id.planned_amount
                spent_amount = budget_allocated_id.practical_amount
                available_amount = allocated_amount - spent_amount
                allocated_amount_formatted = formatLang(self.env, allocated_amount,
                                                        currency_obj=order.company_id.currency_id)
                available_amount_formatted = formatLang(self.env, available_amount,
                                                        currency_obj=order.company_id.currency_id)
                if order.amount_total > available_amount:
                    msg = "Alert !! Budget is exceeding for %s. Allocated budget is %s and Available balance is %s." % (
                    order.budget_id.display_name, allocated_amount_formatted, available_amount_formatted)
                    raise UserError(_(msg))

    def button_confirm(self):
        for order in self.filtered(lambda c: c.state in ['draft', 'sent', 'to approve']):
            if not order.budget_id:
                raise UserError(_("Alert !! Please select the budget."))
            if order.budget_id.crossovered_budget_id.state not in ['done']:
                raise UserError(_("Alert !! The Budget is not approved."))
            if not order.order_line:
                raise UserError(_("Alert !! Please select Products."))
            if not order.purchase_type:
                raise UserError(_("Alert !! Please select the Purchase Type for %s to confirm.")%(order.display_name))
            total_amount = order.amount_total

            other_pos = self.sudo().search([
                ('state', 'not in', ['done', 'cancel','purchase']),
                ('id','!=',order.id)
            ])
            total_other_po = []
            for other_po in other_pos:
                if sorted(other_po.order_line.mapped('product_id').ids) == sorted(order.order_line.mapped('product_id').ids):
                    # total_amount += (other_po.amount_total)
                    total_other_po.append(other_po)

            # Fetch configuration settings
            level_1 = float(order.company_id.po_value_1)
            quotes_1 = int(order.company_id.quotes_required_1)
            level_2 = float(order.company_id.po_value_2)
            quotes_2 = int(order.company_id.quotes_required_2)
            level_3 = float(order.company_id.po_value_3)
            quotes_3 = int(order.company_id.quotes_required_3)
            # Compare and validate levels
            if total_amount <= level_1 and len(total_other_po)+1 < quotes_1:
                raise UserError(_("PO Value exceeds Level 1. Minimum %s quotes required.") % quotes_1)
            elif total_amount > level_1 and total_amount <= level_2 and len(total_other_po)+1 < quotes_2:
                raise UserError(_("PO Value exceeds Level 2. Minimum %s quotes required.") % quotes_2)
            elif total_amount > level_2 and len(total_other_po)+1 < quotes_3:
                raise UserError(_("PO Value exceeds Level 3. Minimum %s quotes required.") % quotes_3)
            for line in order.order_line:
                # Check if the price is zero or less
                if line.price_unit <= 0:
                    raise ValidationError(_(
                        "The price of the product '%s'"
                        "cannot be zero or less. Please correct it before confirming."
                    ) % (line.product_id.display_name))
            order.exceed_budget_balance_warning()
            order.write({'state':'sent'})
        return super(PurchaseOrderInherit, self).button_confirm()

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id)._get_fiscal_position(partner)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Create PO line
            # order_line_values = line._prepare_purchase_order_line(
            #     name=name, product_qty=product_qty, price_unit=price_unit,
            #     taxes_ids=taxes_ids)
            # order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines
