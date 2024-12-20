from odoo import api, fields, models, _, tools

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_code = fields.Char('Code', related='company_id.company_code')
    tcs_limit = fields.Boolean('Enable TCS Limit', related='company_id.tcs_limit', readonly=False)
    tcs_limit_amount = fields.Float(
        'Maximum TCS Amount', related='company_id.tcs_limit_amount',
        help="By adding maximum limit amount will let users know about the TCS limit", readonly=False)
    tds_limit = fields.Boolean('Enable TDS Limit', related='company_id.tds_limit', readonly=False)
    tds_limit_amount = fields.Float(
        'Maximum TDS Amount', related='company_id.tds_limit_amount',
        help="By adding maximum limit amount will let users know about the TDS limit", readonly=False)
    tds_tax_id = fields.Many2one('account.tax', string="TDS Tax", required=False, related='company_id.tds_tax_id', readonly=False)