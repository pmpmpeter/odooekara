
import base64

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class HRPayslipInherit(models.Model):
    _inherit = "hr.payslip"

    @api.model
    def create_batch_jv(self):
            entry_id = []
            for rec in self:
                ent = rec.move_id.id
                print(ent,'ppppppppp')
                entry_id.append(ent)
            print(entry_id,'kkkkkkk')
            batch = self.env['account.batch.jv'].create({
                'journal_id': self[0].journal_id.id,
                'journal_ids':[(4, eid) for eid in entry_id]
            })

            return {
                "type": "ir.actions.act_window",
                "res_model": "account.batch.jv",
                "views": [[False, "form"]],
                "res_id": batch.id,
            }