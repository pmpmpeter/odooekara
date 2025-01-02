from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning

class AccountPayment(models.Model):
    _inherit = "account.payment"

    utr_number = fields.Char('UTR Number', copy=False)
    is_fund_requsiting = fields.Boolean(string='Fund Requisition', copy=False)
    is_contra_payment = fields.Boolean(string='Contra Payment', copy=False)

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

    def action_post(self):
        for pay in self:
            if pay.payment_method_line_id.name == 'Cheque' and not pay.is_cheque_cleared:
                raise UserError(_("Alert !! Kindly Clear the cheque and Update the utr number."))
            if not pay.utr_number and pay.payment_type == 'outbound':
                raise UserError(_("Alert !! Kindly update the UTR Number."))
            if pay.amount <=0:
                raise UserError(_("Alert !! Amount should be greated than Zero"))
            if pay.move_id and pay.payment_type == 'outbound':
                for line in pay.move_id.line_ids:
                    if line.account_id == pay.outstanding_account_id:
                        line.name +=('-'+pay.utr_number)
        res = super(AccountPayment, self).action_post()
        return res
