from odoo import models, fields, api


class KraMaster(models.Model):
    _name = "kra.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KRA Master"

    name=fields.Char(string="Name")
    details_ids = fields.One2many('kra.details', 'kra_id', string="KRA Details")


class KraDetails(models.Model):
    _name = "kra.details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KRA Details"

    kra_id = fields.Many2one('kra.master', string="KRA Master", ondelete='cascade')

    category = fields.Char(string="Category", required=True)
    business_unit = fields.Text(string="Business Unit")
    kra_type = fields.Char(string="KRA")
    goal_description = fields.Char(string="Goal Description")
    weightage = fields.Float(string="Weightage")
