from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_da = fields.Float(string="Basic & DA (PA)", store=True, copy=False, )
    house_rent_allowance = fields.Float(string="House Rent Allowance (PA)", store=True, copy=False)
    special_allowance = fields.Float(string="Special Allowance (PA)", store=True, copy=False)

    monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)", store=True,
                                        copy=False,)
    stat_bonus_amount = fields.Float(string="Statutory Bonus Amount", store=True, copy=False)
    provident_fund = fields.Float(string="Provident Fund", store=True, copy=False)
    esi_amount = fields.Float(string="ESI Amount", store=True, copy=False)
    variable_pay_percentage = fields.Float(string="Percentage of Variable Pay  (per annum)", store=True, copy=False)
    variable_pay_amount = fields.Float(string="Variable Pay Amounts", store=True, copy=False)
    annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive", store=True,
                                                      copy=False)
    annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay", store=True, copy=False)
    monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive", store=True, copy=False)
    medical_insurance = fields.Float(string="Medical Insurance", store=True, copy=False)
    group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance", store=True, copy=False)
    solis_health_benefit_beacon_plan = fields.Float(string="Solis Health Benefit Beacon Plan", store=True, copy=False)
    indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month", store=True, copy=False)

    statutory_bonus_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable (per month)", default='no', required=True,
        copy=False
    )
    provident_fund_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable (per month)", default='no', required=True,
        copy=False
    )
    esi_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable (per month)", default='no', required=True, copy=False
    )
    fixed_pay = fields.Float(string="Fixed Pay", store=False, copy=False)
    #fixed_pay newly added but not know
    # def action_open_contract_list(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.action_hr_contract')
    #     action.update({'domain': [('employee_id', '=', self.employee_id.id)],
    #                   'views':  [[False, 'list'], [False, 'kanban'], [False, 'activity'], [False, 'form']],
    #                    'context': {'default_employee_id': self.employee_id.id}})
    #     return action
