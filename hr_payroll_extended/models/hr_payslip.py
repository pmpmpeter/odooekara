from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def generate_payslip(self):
        return self.env.ref('hr_payroll_extended.report_action_custom_payslip').report_action(self)
