from odoo import api, fields, models, _, tools
from datetime import datetime

class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    tax_entity1 = fields.Many2one('res.company', string="Tax Entity1")
    share1 = fields.Integer('Share %')
    tax_entity2 = fields.Many2one('res.company', string="Tax Entity2")
    share2 = fields.Integer('Share %')
    crr_reminder_users = fields.Many2many('res.users', string="CRR & CUR Reminder Users",
                                          help="Users who will receive monthly CRR & CUR reminders")
    po_threshold_amount = fields.Float('PO Thresshold Amount')