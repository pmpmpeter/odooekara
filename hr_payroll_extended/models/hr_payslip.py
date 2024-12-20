from odoo import models, fields, api, _


class HrPayroll(models.Model):
    """inherited the model to add some fields"""
    _inherit = 'hr.payslip'