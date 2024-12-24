# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    utr_number = fields.Char('UTR Number', copy=False)

    def action_post(self):
        for pay in self:
            if not pay.utr_number and pay.payment_type == 'outbound':
                raise UserError(_("Alert !! Kindly update the UTR Number."))
            if pay.amount <=0:
                raise UserError(_("Alert !! Amount should be greated than Zero"))
            if pay.move_id:
                for line in pay.move_id.line_ids:
                    if line.account_id == pay.outstanding_account_id:
                        line.name +=('-'+pay.utr_number)
        res = super(AccountPayment, self).action_post()
        return res
