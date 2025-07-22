from odoo import _, api, fields, models , Command
from odoo.exceptions import UserError
from datetime import date, timedelta
import pdb

class AccountPaymentInvoices(models.Model):
    _name = 'account.payment.invoice.line'
    _description = "Account Payment Invoices"

    invoice_id = fields.Many2one('account.move.line', string='Invoice')
    date = fields.Date(string='Date', related='invoice_id.date', store=True)
    payment_id = fields.Many2one('account.payment', string='Payment')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    reconcile_amount = fields.Monetary(string='Reconcile Amount')
    amount_total = fields.Monetary(string="Amount Total", related='invoice_id.move_id.amount_total')
    residual = fields.Monetary(string="Residual Amount", related='invoice_id.amount_residual_currency')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_invoice_ids = fields.One2many('account.payment.invoice.line', 'payment_id', string="Customer Invoices")

    @api.onchange('payment_type', 'partner_type', 'partner_id', 'currency_id')
    def _onchange_to_get_vendor_invoices(self):
        if self.payment_type in ['outbound'] and self.partner_type and self.partner_id and self.currency_id:

            self.payment_invoice_ids = [(6, 0, [])]
            domain1= [
                ('partner_id', 'child_of', self.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['entry', 'in_invoice', 'in_refund']),
                ('account_id.account_type', 'in', ['liability_payable']),
                ('amount_residual', '!=', 0),('credit', '!=', 0),('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id)]
            invoice_recs = self.env['account.move.line'].sudo().search(domain1)
            invoice_recs = invoice_recs.sorted(lambda l: l.move_id.invoice_date)
            payment_invoice_values = []
            for invoice_rec in invoice_recs:
                payment_invoice_values.append([0, 0, {'invoice_id': invoice_rec.id}])
            self.payment_invoice_ids = payment_invoice_values
            # for line in invoice_recs:
            #     if line.id == 35443:
            #         pdb.set_trace()
            # payment_invoice_values = []
            # for invoice_rec in invoice_recs:
            #     move_type = invoice_rec.move_id.move_type
            #     if move_type != 'entry':
            #         total = invoice_rec.move_id.amount_total
            #     else:
            #         total = invoice_rec.debit if invoice_rec.debit > 0 else invoice_rec.credit

            #     payment_invoice_values.append([0, 0, {
            #         # 'invoice_id': invoice_rec.id,
            #         'amount_total': total,
            #     }])
            # self.payment_invoice_ids = invoice_recs
        if self.payment_type in ['inbound'] and self.partner_type and self.partner_id and self.currency_id:
            self.payment_invoice_ids = [(6, 0, [])]
            domain1= [
                ('partner_id', 'child_of', self.partner_id.id),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ['entry', 'out_invoice', 'out_refund']),
                ('account_id.account_type', 'in', ['asset_receivable']),
                ('amount_residual', '!=', 0),('debit', '!=', 0),('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id)]
            invoice_recs = self.env['account.move.line'].sudo().search(domain1)
            invoice_recs = invoice_recs.sorted(lambda l: l.move_id.invoice_date)
            # pdb.set_trace()
            # payment_invoice_values = []
            # for invoice_rec in invoice_recs:
            #     move_type = invoice_rec.move_id.move_type
            #     if move_type != 'entry':
            #         total = invoice_rec.move_id.amount_total
            #     else:
            #         total = invoice_rec.debit if invoice_rec.debit > 0 else invoice_rec.credit

            #     payment_invoice_values.append([0, 0, {
            #         'invoice_id': invoice_rec.id,
            #         'amount_total': total,
            #     }])
            # self.payment_invoice_ids = invoice_recs
            payment_invoice_values = []
            for invoice_rec in invoice_recs:
                payment_invoice_values.append([0, 0, {'invoice_id': invoice_rec.id}])
            self.payment_invoice_ids = payment_invoice_values

    @api.onchange('payment_invoice_ids')
    def reconcile_amount_onchange(self):
        for rec in self:
            total = 0
            for pay in rec.payment_invoice_ids:
                total += pay.reconcile_amount
            if rec.amount < total:
                raise UserError(
                    _("Alert!! You are trying to allocate an amount that exceeds the payment amount."))

    @api.onchange('amount')
    def amount_onchange(self):
        for rec in self:
            if rec.payment_invoice_ids:
                for line in rec.payment_invoice_ids:
                    line.reconcile_amount = 0.0
                if rec.amount > 0:
                    for line in rec.payment_invoice_ids:
                        total_reconcile = sum(abs(line.reconcile_amount) for line in rec.payment_invoice_ids)
                        if total_reconcile < rec.amount:
                            available_amount = rec.amount - total_reconcile
                            if abs(line.residual) < available_amount:
                                    line.reconcile_amount = abs(line.residual)
                            else:
                                line.reconcile_amount = available_amount
                else:
                    for line in rec.payment_invoice_ids:
                        line.reconcile_amount = 0

    def action_post(self):
        super(AccountPayment, self).action_post()
        for payment in self:
            if payment.payment_invoice_ids:
                total_reconcile_amount = sum(payment.payment_invoice_ids.mapped('reconcile_amount'))
                # total_payment_available = sum(payment.other_charges_lines.mapped('other_charge')) + payment.amount
                total_payment_amount_main = payment.amount
                # total_reconcile_line_amount = sum(payment.other_charges_lines.mapped('other_charge'))
                total_reconcile_line_amount = 0
                total_payment_available = total_payment_amount_main + total_reconcile_line_amount
                # pdb.set_trace()
                if total_payment_available != total_reconcile_amount:
                    raise UserError(
                        _("The sum of the reconcile amount of listed invoices is not equal to payment amount."))
                if not payment.payment_invoice_ids.filtered(lambda line: line.reconcile_amount > 0):
                    raise UserError(
                            _("Kindly update the amount to reconcile for each transactions."))

            if payment.payment_invoice_ids.filtered(lambda line: line.reconcile_amount <= 0):
                payment.payment_invoice_ids.filtered(lambda line: line.reconcile_amount <= 0).sudo().unlink()

            # for line_id in payment.payment_invoice_ids.filtered(lambda line: line.reconcile_amount > 0 and line.amount_total >= line.reconcile_amount):
            #     # if not line_id.reconcile_amount:
            #     #     continue
            #     # pdb.set_trace()
            #         # pdb.set_trace()
            #     lines = payment.move_id.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
            #     lines += line_id.invoice_id.filtered(
            #             lambda line: line.account_id == lines[0].account_id and not line.reconciled)
            #         # pdb.set_trace()
            #     lines.with_context(amount=line_id.reconcile_amount).reconcile()
            #     print("Case1111111111111111111111111111111", lines)
            for line_id in payment.payment_invoice_ids.filtered(lambda line: line.reconcile_amount > 0):
                if not line_id.reconcile_amount:
                    continue
                if line_id.amount_total <= line_id.reconcile_amount:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                        # pdb.set_trace()
                        lines += line_id.invoice_id.move_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                        lines += line_id.invoice_id.move_id.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                else:
                    self.ensure_one()
                    # pdb.set_trace()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                        if lines:
                            if line_id.invoice_id.move_id.filtered(lambda line: line.move_type != 'entry'):
                                lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                                lines += line_id.invoice_id.move_id.line_ids.filtered(
                                    lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                                lines.with_context(amount=-line_id.reconcile_amount).reconcile()
                            if line_id.invoice_id.move_id.filtered(lambda line: line.move_type == 'entry'):
                                lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                                for m in range(len(lines)):
                                    my_list = []
                                    if not line_id.id in my_list:
                                        sasi1111= line_id.filtered(
                                            lambda l: l.reconcile_amount > 0)
                                        direct_je_line = sasi1111.invoice_id.move_id.line_ids.filtered(
                                            lambda line: line.account_id.id == line_id.invoice_id.account_id.id and not line.reconciled)
                                        if len(direct_je_line) <=1:
                                            lines += direct_je_line
                                            lines.with_context(amount=-line_id.reconcile_amount).reconcile()
                                        elif len(direct_je_line) >1:
                                            my_list2 = []
                                            for i in range(len(direct_je_line)):
                                                if line_id.id not in my_list2:
                                                    lines += line_id.invoice_id
                                                    lines.with_context(amount=-line_id.reconcile_amount).reconcile()
                                                my_list2.append(line_id.id)
                                    my_list.append(line_id.id)
                    elif payment.payment_type == 'outbound':
                        if line_id.invoice_id.move_id.filtered(lambda line: line.move_type != 'entry'):
                            lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                            if lines:
                                lines += line_id.invoice_id.move_id.line_ids.filtered(
                                    lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                                lines.with_context(amount=line_id.reconcile_amount).reconcile()
                        elif line_id.invoice_id.move_id.filtered(lambda line: line.move_type == 'entry'):
                            lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0 and line.account_id.account_type in ['asset_receivable','liability_payable'])
                            for m in range(len(lines)):
                                my_list = []
                                if not line_id.id in my_list:
                                    sasi1111= line_id.filtered(
                                            lambda l: l.reconcile_amount > 0)
                                    direct_je_line = sasi1111.invoice_id.move_id.line_ids.filtered(
                                        lambda line: line.account_id.id == line_id.invoice_id.account_id.id and not line.reconciled)
                                    if len(direct_je_line) <=1:
                                        lines += direct_je_line
                                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
                                    elif len(direct_je_line) >1:
                                        my_list2 = []
                                        for i in range(len(direct_je_line)):
                                            if line_id.id not in my_list2:
                                                lines += line_id.invoice_id
                                                lines.with_context(amount=line_id.reconcile_amount).reconcile()
                                            my_list2.append(line_id.id)
                                my_list.append(line_id.id)
            # stop
