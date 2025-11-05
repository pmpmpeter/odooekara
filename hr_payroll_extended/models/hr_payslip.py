from odoo import models, fields, api, _
from datetime import datetime, date
import calendar

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def generate_payslip(self):
        return self.env.ref('hr_payroll_extended.report_action_custom_payslip').report_action(self)

    def compute_ytd_value(self,emp):
            self.ensure_one()
            fiscal_year = self.env['account.fiscal.year'].sudo().search([
                ('company_id', '=', self.company_id.id),
                ('date_from', '<=', self.date_from),
                ('date_to', '>=', self.date_from)
            ], limit=1)
            if not fiscal_year:
                return 0
            fiscal_start = fiscal_year.date_from
            date_to = self.date_to
            payslips = self.env['hr.payslip'].sudo().search([
                ('employee_id', '=', emp.id),
                ('date_from', '>=', fiscal_start),
                ('date_to','<=',date_to)
            ])
            income_total = 0
            earnings_ytd = 0
            recoveries = 0
            for pay in payslips:
                if pay:
                    for income_totals in pay.line_ids:
                        if income_totals.salary_rule_id.code == 'INC-T':
                            income_total += income_totals.total
                        if income_totals.salary_rule_id.code == 'Other_earnings_through_payroll':
                            earnings_ytd += income_totals.total
                        if income_totals.salary_rule_id.code == 'Other_recoveries':
                            recoveries += income_totals.total
            months = {(p.date_from.year, p.date_from.month) for p in payslips}
            date = self.date_from
            year = date.year
            month = date.month
            days_in_month = calendar.monthrange(year, month)[1]
            return {
                'month_total': int(len(months)),
                'income_total': income_total,
                'ytd_april':earnings_ytd,
                'recoveries':recoveries,
                'days_in_month':days_in_month,
            }

class HRSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appears_on_batch_report = fields.Boolean(string='Appears on Batch JV')

