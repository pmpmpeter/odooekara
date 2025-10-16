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
            # april_payslips = payslips.filtered(
            #     lambda p: p.date_from.month == 4 or p.date_to.month == 4
            # )
            # earnings_ytd = 0
            # if self.date_from.month != 4:
            #     for pay in april_payslips:
            #         if pay:
            #             for ear_ytd in pay.line_ids:
            #                 if ear_ytd.salary_rule_id.code == 'Other_earnings_through_payroll':
            #                     earnings_ytd += ear_ytd.total
            #     print(earnings_ytd, 'wwwwwwwwwww')
            months = {(p.date_from.year, p.date_from.month) for p in payslips}
            return {
                'month_total': int(len(months)),
                'income_total': income_total,
                'ytd_april':earnings_ytd,
                'recoveries':recoveries
            }

