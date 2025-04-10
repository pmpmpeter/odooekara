from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning


class AccountPayment(models.Model):
    _inherit = "account.payment"

    utr_number = fields.Char('UTR Number', copy=False)
    old_utr_number = fields.Char('OLD UTR Number', copy=False)
    is_fund_requsiting = fields.Boolean(string='Fund Requisition', copy=False)
    is_contra_payment = fields.Boolean(string='Contra Payment', copy=False)
    is_credit_payment = fields.Boolean(string='Credit Payment', copy=False)
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    reason_approved = fields.Text(string='Approval comments', copy=False)
    partner_cl_balance = fields.Float(compute='_get_partner_cl_balance', string='Partner Balance')
    closing_balance = fields.Float(compute='_get_closing_balance', string='Closing Balance')
    type = fields.Selection([
        ("capex", "Capex"),
        ("opex", "Opex")], default='opex', string="Capex/Opex")
    payment_purchase_id = fields.Many2one('purchase.order',copy=False, string='Purchase Order')

    def _get_closing_balance(self):
        closing_balance = 0
        query = """
            select sum(balance) as balance FROM account_move_line aml 
            join account_move am on am.id=aml.move_id 
            where am.state='posted' and aml.account_id=%s
            """
        params = tuple(self.journal_id.default_account_id.ids)
        data_get8 = self.env.cr.execute(query, params)
        lines8 = self.env.cr.dictfetchall()
        if (lines8[0].get('balance') != None):
            closing_balance = lines8[0].get('balance') or 0
        for record in self:
            # pdb.set_trace()
            record.closing_balance = closing_balance

    def _get_partner_cl_balance(self):
        partner_cl_balance = 0
        if self.partner_id:
            query = """
                select sum(balance) as balance FROM account_move_line aml 
                join account_move am on am.id=aml.move_id 
                join account_account ac on ac.id=aml.account_id 
                where am.state='posted' and aml.partner_id=%s and ac.account_type in ('asset_receivable', 'liability_payable')
                """
            params = tuple(self.partner_id.ids)
            data_get8 = self.env.cr.execute(query, params)
            lines8 = self.env.cr.dictfetchall()
            if (lines8[0].get('balance') != None):
                partner_cl_balance = lines8[0].get('balance') or 0
            for record in self:
                record.partner_cl_balance = partner_cl_balance
        else:
            self.partner_cl_balance = 0

    def action_update_utr_number(self):
        for rec in self:
            if rec.state == 'posted' and rec.utr_number:
                if rec.move_id:
                    for line in rec.move_id.line_ids:
                        if line.account_id == rec.outstanding_account_id:
                            if rec.old_utr_number:
                                line.name = line.name.replace(rec.old_utr_number, rec.utr_number)
                            else:
                                line.name += ('-' + rec.utr_number)
                    rec.old_utr_number = rec.utr_number

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
                    [('model_id', '=', 'account.payment'), ('state', '=', 'confirm')], limit=1)
                if rec:
                    record.approval_state = 'To Submit for Approval'
                else:
                    record.approval_state = 'Not Applicable'

    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            if 'is_internal_transfer' in self.env.context:
                if self.env.context['is_internal_transfer']:
                    payment.is_internal_transfer = True
            else:
                payment.is_internal_transfer = payment.partner_id \
                                               and payment.partner_id == payment.journal_id.company_id.partner_id \
                                               and payment.destination_journal_id

    @api.onchange('type')
    def onchange_type(self):
        for rec in self:
            # print('rrrrrr',rec.type,rec.move_id._origin.id)
            move = self.env['account.move'].sudo().search([('id', '=', rec.move_id._origin.id)])
            move.expense_type = rec.type

    def action_post(self):
        for pay in self:
            if pay.state != 'approved' and pay.payment_type == 'outbound':
                raise ValidationError('You cannot confirm payments that are not Approved.')
            # if pay.payment_method_line_id.name == 'Cheque' and not pay.is_cheque_cleared and pay.payment_type == 'outbound':
            #     raise UserError(_("Alert !! Kindly Clear the cheque"))
            # if not pay.utr_number and (pay.payment_type == 'outbound' or pay.is_fund_requsiting):
            #     raise UserError(_("Alert !! Kindly update the UTR Number."))
            if pay.amount <= 0:
                raise UserError(_("Alert !! Amount should be greated than Zero"))
            if pay.move_id and pay.utr_number:
                for line in pay.move_id.line_ids:
                    if line.account_id == pay.outstanding_account_id:
                        line.name += ('-' + pay.utr_number)
                pay.old_utr_number = pay.utr_number
            user_email = pay.expense_sheet_id.user_id.email if pay.expense_sheet_id.user_id else ''
            employee_email = pay.expense_sheet_id.employee_id.work_email if pay.expense_sheet_id.employee_id else ''
            template = self.env.ref('account.mail_template_data_payment_receipt')
            template.write({'email_to': ', '.join(filter(None, [user_email, employee_email]))})
            template.send_mail(pay.id, force_send=True)
        res = super(AccountPayment, self).action_post()
        return res

    def action_approve_payment(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def action_reject_payment(self):
        for rec in self:
            rec.write({'state': 'cancel'})

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    def action_print_bank_advice_payment_pdf(self):
        return self.env.ref('account_batch_payment.action_print_batch_payment').report_action(self)
