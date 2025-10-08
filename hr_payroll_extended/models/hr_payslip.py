from odoo import models, fields, api, _
from datetime import datetime, date

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def generate_payslip(self):
        return self.env.ref('hr_payroll_extended.report_action_custom_payslip').report_action(self)

    def compute_ytd_value(self,emp):
            self.ensure_one()
            fiscal_year = self.env['account.fiscal.year'].search([
                ('company_id', '=', self.company_id.id),
                ('date_from', '<=', self.date_from),
                ('date_to', '>=', self.date_from)
            ], limit=1)
            if not fiscal_year:
                return 0
            fiscal_start = fiscal_year.date_from
            date_to = self.date_to
            payslips = self.env['hr.payslip'].search([
                ('employee_id', '=', emp.id),
                ('date_from', '>=', fiscal_start),
                ('date_to','<=',date_to)
            ])

            months = {(p.date_from.year, p.date_from.month) for p in payslips}
            return int(len(months))

