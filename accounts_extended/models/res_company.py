from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import ValidationError




class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    tax_entity1 = fields.Many2one('res.company', string="Tax Entity1")
    share1 = fields.Integer('Share %')
    tax_entity2 = fields.Many2one('res.company', string="Tax Entity2")
    share2 = fields.Integer('Share %')
    crr_reminder_users = fields.Many2many('res.users', string="CRR & CUR Reminder Users",
                                          help="Users who will receive monthly CRR & CUR reminders")
    po_threshold_amount = fields.Float('PO Thresshold Amount')
    tax_entity_ids = fields.One2many(
        "res.company.tax.entity",
        "company_id",
        string="Tax Entities",
    )

class ResCompanyTaxEntity(models.Model):
    _name = "res.company.tax.entity"
    _description = "Tax Entity Master"

    company_id = fields.Many2one("res.company",string="Company",required=True,ondelete="cascade")
    budget_id = fields.Many2one("crossovered.budget",string="Company",required=True,ondelete="cascade")
    entity_id = fields.Many2one("res.company",string="Entity",required=True)
    share = fields.Float(string="Share (%)",required=True)
    sequence = fields.Integer(string="Sequence",default=1)
    loan_account_id = fields.Many2one("account.account",string="Loan Account")

    @api.constrains("share", "company_id")
    def _check_share_sum(self):
        for rec in self:
            if rec.company_id:
                total_share = sum(rec.company_id.tax_entity_ids.mapped("share"))
                # if total_share != 100 :
                #     raise ValidationError(
                #         f"Total Tax Entity share for {rec.company_id.display_name} "
                #         f"cannot exceed or lesser than 100%. Current total: {total_share}%"
                #     )
