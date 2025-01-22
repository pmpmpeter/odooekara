from odoo import fields, models, api
import math


class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_da_per_annum = fields.Float(string='Basic & DA', copy=False)
    basic_da_per_month = fields.Float(string='Basic & DA', copy=False)
    hra_per_annum = fields.Float(string='House Rent Allowance', copy=False)
    hra_per_month = fields.Float(string='House Rent Allowance', copy=False)
    special_allowance_per_annum = fields.Float(string='Special Allowance', copy=False)
    special_allowance_per_month = fields.Float(string='Special Allowance', copy=False)
    sub_total_a_per_annum = fields.Float(string='Sub-total Part A', copy=False)
    sub_total_a_per_month = fields.Float(string='Sub-total Part A', copy=False)
    statutory_bonus_per_annum = fields.Float(string='Statutory Bonus', copy=False)
    statutory_bonus_per_month = fields.Float(string='Statutory Bonus', copy=False)
    pf_employer_per_annum = fields.Float(string="Provident Fund (Employer's Contribution)", copy=False)
    pf_employer_per_month = fields.Float(string="Provident Fund (Employer's Contribution)", copy=False)
    esic_employer_per_annum = fields.Float(string='ESIC (Employer Contribution)', copy=False)
    esic_employer_per_month = fields.Float(string='ESIC (Employer Contribution)', copy=False)
    sub_total_b_per_annum = fields.Float(string='Sub-total Part B', copy=False)
    sub_total_b_per_month = fields.Float(string='Sub-total Part B', copy=False)
    variable_pay_per_annum = fields.Float(string='Variable Pay', copy=False)
    variable_pay_per_month = fields.Float(string='Variable Pay', copy=False)
    sub_total_c_per_annum = fields.Float(string='Sub-total Part C', copy=False)
    sub_total_c_per_month = fields.Float(string='Sub-total Part C', copy=False)
    total_salary_per_annum = fields.Float(string='Total Salary', copy=False)
    total_salary_per_month = fields.Float(string='Total Salary', copy=False)
    medical_insurances = fields.Float(string='Medical Insurance', copy=False)
    group_personal_acc_insurance = fields.Float(string='Group Personal Accident Insurance', copy=False)
    sub_total_d = fields.Float(string='Sub-total Part D', copy=False)
    total_ctc_annum = fields.Float(string='Total Cost to Company', copy=False)
    total_ctc_month = fields.Float(string='Total Cost to Company', copy=False)
    monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)", copy=False)
    stat_bonus_amount = fields.Float(string="Statutory Bonus Amount", store=True, copy=False)
    provident_fund = fields.Float(string="Provident Fund", store=True, copy=False)
    esi_amount = fields.Float(string="ESI Amount", store=True, copy=False)
    variable_pay_percentage = fields.Float(string="Percentage of Variable Pay", store=True, copy=False)
    annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive", store=True,
                                                      copy=False)
    store_performance_incentive_annum = fields.Float(string="Store Performance Incentive", store=True,
                                                     copy=False)
    store_performance_incentive_month = fields.Float(string="Store Performance Incentive", store=True,
                                                     copy=False)
    annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay", store=True, copy=False)
    performance_linked_pay_annum = fields.Float(string="Performance Linked Pay", store=True, copy=False)
    performance_linked_pay_month = fields.Float(string="Performance Linked Pay", store=True, copy=False)
    monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive", store=True, copy=False)
    monthly_performance_incentive_annum = fields.Float(string="Monthly Performance Incentive", store=True,
                                                       copy=False)
    monthly_performance_incentive_month = fields.Float(string="Monthly Performance Incentive", store=True,
                                                       copy=False)
    medical_insurance = fields.Float(string="Medical Insurance", store=True, copy=False)
    group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance", store=True, copy=False)
    solis_health_benefit_beacon_plan = fields.Float(string="Solis Health Benefit Beacon Plan", store=True, copy=False)
    indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month", store=True, copy=False)
    statutory_bonus_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable", default='no',
        copy=False
    )
    provident_fund_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable", default='no',
        copy=False
    )
    esi_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable", default='no', copy=False
    )
    location = fields.Selection([
        ('corporate', 'Corporate'),
        ('bangalore', 'Bangalore'),
        ('ttc', 'TTC'),
        ('ttk', 'TTK'),
        ('cbm', 'CBM'),
        ('lilac1', 'Lilac 1'),
        ('lilac2', 'Lilac 2'),
        ('tta', 'TTA'),
        ('tvm_obt', 'TVM/OBT'),
    ], default='corporate', string="Location", tracking=True, required=True)
    location_id = fields.Many2one('location.master', string="Location",tracking=True)
    grade = fields.Selection([
        ('spl_grade', 'Spl Grade'),
        ('grade_a', 'Grade A'),
        ('grade_b', 'Grade B'),
        ('grade_c', 'Grade C'),
        ('grade_d', 'Grade D'),
        ('grade_e', 'Grade E'),
        ('grade_f', 'Grade F'),
        ('grade_g', 'Grade G'),
    ], default='spl_grade', string="Grade", tracking=True, required=True)

    @api.onchange('location_id', 'monthly_fixed_salary', 'statutory_bonus_applicable', 'provident_fund_applicable',
                  'esi_applicable', 'grade',
                  'variable_pay_percentage', 'annual_store_performance_incentive', 'annual_performance_linked_pay',
                  'monthly_performance_incentive',
                  'medical_insurance', 'group_personal_accident_insurance')
    def _onchange_calculate_salary_breakup(self):
        for record in self:
            # Fetch the salary structure based on location and grade
            salary_structure = self.env['salary.master'].search([
                ('location_id', '=', record.location_id.id),
                ('grade', '=', record.grade)
            ], limit=1)

            if salary_structure:
                record.basic_da_per_annum = salary_structure.annual_salary
                record.basic_da_per_month = salary_structure.monthly_salary
                record.hra_per_annum = 0
                record.hra_per_month = 0
                record.statutory_bonus_per_annum = 0
                record.statutory_bonus_per_month = 0
                record.special_allowance_per_annum = 0
                record.special_allowance_per_month = 0
                record.sub_total_a_per_annum = record.basic_da_per_annum
                record.sub_total_a_per_month = round(record.sub_total_a_per_annum / 12, 0)

                # New logic for statutory bonus when location is TTA and grade is D
                if record.location_id.name == 'TTA' and record.grade == 'grade_d':
                    record.statutory_bonus_per_annum = min(16800, (
                            record.monthly_fixed_salary * 12) - record.basic_da_per_annum)
                    record.statutory_bonus_per_month = round(record.statutory_bonus_per_annum / 12, 0)
                else:
                    if record.statutory_bonus_applicable == 'yes':
                        if (record.basic_da_per_annum / 12) <= 21000:
                            record.statutory_bonus_per_annum = min(record.basic_da_per_annum, 84000) * 0.20
                        else:
                            record.statutory_bonus_per_annum = 0

                        # Calculate Statutory Bonus (Per Month)
                        record.statutory_bonus_per_month = round(record.statutory_bonus_per_annum / 12)

                # Continue with the rest of the calculations
                if record.provident_fund_applicable == 'yes':
                    if record.monthly_fixed_salary < 15000:
                        record.pf_employer_per_month = (record.monthly_fixed_salary * 0.12)
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12)
                else:
                    record.pf_employer_per_month = 0

                record.pf_employer_per_annum = round(record.pf_employer_per_month * 12)
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_month = math.ceil(record.monthly_fixed_salary * 0.0325)
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_month = 0

                record.esic_employer_per_annum = record.esic_employer_per_month * 12
                record.sub_total_b_per_annum = record.statutory_bonus_per_annum + record.pf_employer_per_annum + record.esic_employer_per_annum
                record.sub_total_b_per_month = record.statutory_bonus_per_month + record.pf_employer_per_month + record.esic_employer_per_month
                record.store_performance_incentive_annum = record.annual_store_performance_incentive
                record.store_performance_incentive_month = round(record.store_performance_incentive_annum / 12, 0)
                record.performance_linked_pay_annum = record.annual_performance_linked_pay
                record.performance_linked_pay_month = round(record.performance_linked_pay_annum / 12, 0)
                record.monthly_performance_incentive_annum = record.monthly_performance_incentive
                record.monthly_performance_incentive_month = round(record.monthly_performance_incentive_annum / 12, 0)
                record.variable_pay_per_annum = (record.monthly_fixed_salary * 12 + record.pf_employer_per_annum) * (
                        record.variable_pay_percentage / 100)
                record.variable_pay_per_month = round(record.variable_pay_per_annum / 12, 0)
                record.sub_total_c_per_annum = record.store_performance_incentive_annum + record.performance_linked_pay_annum + record.monthly_performance_incentive_annum + record.variable_pay_per_annum
                record.sub_total_c_per_month = round(record.sub_total_c_per_annum / 12, 0)
                record.total_salary_per_annum = record.sub_total_c_per_annum + record.sub_total_b_per_annum + record.sub_total_a_per_annum
                record.total_salary_per_month = round(record.total_salary_per_annum / 12, 0)
                record.medical_insurances = record.medical_insurance
                record.group_personal_acc_insurance = record.group_personal_accident_insurance
                record.sub_total_d = record.medical_insurances + record.group_personal_acc_insurance
                record.total_ctc_annum = record.total_salary_per_annum + record.sub_total_d
                record.total_ctc_month = round(record.total_ctc_annum / 12, 0)
                record.indicative_take_home_salary = record.sub_total_a_per_month + record.statutory_bonus_per_month - record.pf_employer_per_month - round(
                    record.esic_employer_per_month / 0.0325 * 0.75 / 100)

            elif (record.location_id.name not in ['tta', 'tvm_obt']) or (record.monthly_fixed_salary >= 54000):
                # Calculate Basic & DA (Per Annum)
                record.basic_da_per_annum = round((record.monthly_fixed_salary * 12 * 0.4) / 12000, 0) * 12000
                record.hra_per_annum = record.basic_da_per_annum * 0.40

                # Calculate (Per Month)
                record.basic_da_per_month = round(record.basic_da_per_annum / 12, 0)
                record.hra_per_month = round(record.hra_per_annum / 12, 0)

                # Calculate Statutory Bonus (Per Annum) if applicable
                if record.location_id.name == 'TTA' and record.grade == 'grade_d':
                    record.statutory_bonus_per_annum = min(16800, (
                            record.monthly_fixed_salary * 12) - record.basic_da_per_annum)
                    record.statutory_bonus_per_month = round(record.statutory_bonus_per_annum / 12, 0)
                elif record.statutory_bonus_applicable == 'yes':
                    if (record.basic_da_per_annum / 12) <= 21000:
                        record.statutory_bonus_per_annum = min(record.basic_da_per_annum, 84000) * 0.20
                    else:
                        record.statutory_bonus_per_annum = 0

                    # Calculate Statutory Bonus (Per Month)
                    record.statutory_bonus_per_month = round(record.statutory_bonus_per_annum / 12)

                # Calculate Special Allowance (Per Annum)
                record.special_allowance_per_annum = (record.monthly_fixed_salary * 12) - (
                        record.basic_da_per_annum + record.hra_per_annum + record.statutory_bonus_per_annum
                )
                record.sub_total_a_per_annum = record.basic_da_per_annum + record.hra_per_annum + record.special_allowance_per_annum

                # Calculate Special Allowance (Per Month)
                record.special_allowance_per_month = round(record.special_allowance_per_annum / 12, 0)
                record.sub_total_a_per_month = round(record.sub_total_a_per_annum / 12, 0)
                # Calculate Provident Fund (Employer's Contribution Per Month)
                if record.provident_fund_applicable == 'yes':
                    if record.monthly_fixed_salary < 15000:
                        record.pf_employer_per_month = (record.monthly_fixed_salary * 0.12)
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12)
                else:
                    record.pf_employer_per_month = 0

                record.pf_employer_per_annum = record.pf_employer_per_annum * 12
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_month = math.ceil(record.monthly_fixed_salary * 0.0325)
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_month = 0

                record.esic_employer_per_annum = record.esic_employer_per_month * 12
                record.sub_total_b_per_annum = record.statutory_bonus_per_annum + record.pf_employer_per_annum + record.esic_employer_per_annum
                record.sub_total_b_per_month = record.statutory_bonus_per_month + record.pf_employer_per_month + record.esic_employer_per_month
                record.store_performance_incentive_annum = record.annual_store_performance_incentive
                record.store_performance_incentive_month = round(record.store_performance_incentive_annum / 12, 0)
                record.performance_linked_pay_annum = record.annual_performance_linked_pay
                record.performance_linked_pay_month = round(record.performance_linked_pay_annum / 12, 0)
                record.monthly_performance_incentive_annum = record.monthly_performance_incentive
                record.monthly_performance_incentive_month = round(record.monthly_performance_incentive_annum / 12, 0)
                record.variable_pay_per_annum = (record.monthly_fixed_salary * 12 + record.pf_employer_per_annum) * (
                        record.variable_pay_percentage / 100)
                record.variable_pay_per_month = round(record.variable_pay_per_annum / 12, 0)
                record.sub_total_c_per_annum = record.store_performance_incentive_annum + record.performance_linked_pay_annum + record.monthly_performance_incentive_annum + record.variable_pay_per_annum
                record.sub_total_c_per_month = round(record.sub_total_c_per_annum / 12, 0)
                record.total_salary_per_annum = record.sub_total_c_per_annum + record.sub_total_b_per_annum + record.sub_total_a_per_annum
                record.total_salary_per_month = round(record.total_salary_per_annum / 12, 0)
                record.medical_insurances = record.medical_insurance
                record.group_personal_acc_insurance = record.group_personal_accident_insurance
                record.sub_total_d = record.medical_insurances + record.group_personal_acc_insurance
                record.total_ctc_annum = record.total_salary_per_annum + record.sub_total_d
                record.total_ctc_month = round(record.total_ctc_annum / 12, 0)
                record.indicative_take_home_salary = record.sub_total_a_per_month + record.statutory_bonus_per_month - record.pf_employer_per_month - round(
                    record.esic_employer_per_month / 0.0325 * 0.75 / 100)
            else:
                record.basic_da_per_annum = 0
                record.basic_da_per_month = 0
                record.hra_per_annum = 0
                record.hra_per_month = 0
                record.statutory_bonus_per_annum = 0
                record.statutory_bonus_per_month = 0
                record.special_allowance_per_annum = 0
                record.special_allowance_per_month = 0
                record.sub_total_a_per_annum = 0
                record.sub_total_a_per_month = 0
                if record.provident_fund_applicable == 'yes':
                    if record.monthly_fixed_salary < 15000:
                        record.pf_employer_per_month = (record.monthly_fixed_salary * 0.12) * 12
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12, 0)
                else:
                    record.pf_employer_per_month = 0

                record.pf_employer_per_annum = record.pf_employer_per_month * 12
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_month = math.ceil(record.monthly_fixed_salary * 0.0325)
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_month = 0
                record.esic_employer_per_annum = record.esic_employer_per_month * 12
                record.sub_total_b_per_annum = record.pf_employer_per_annum + record.esic_employer_per_annum
                record.sub_total_b_per_month = record.statutory_bonus_per_month + record.pf_employer_per_month + record.esic_employer_per_month
                record.store_performance_incentive_annum = record.annual_store_performance_incentive
                record.store_performance_incentive_month = round(record.store_performance_incentive_annum / 12, 0)
                record.performance_linked_pay_annum = record.annual_performance_linked_pay
                record.performance_linked_pay_month = round(record.performance_linked_pay_annum / 12, 0)
                record.monthly_performance_incentive_annum = record.monthly_performance_incentive
                record.monthly_performance_incentive_month = round(record.monthly_performance_incentive_annum / 12, 0)
                record.variable_pay_per_annum = (record.monthly_fixed_salary * 12 + record.pf_employer_per_annum) * (
                        record.variable_pay_percentage / 100)
                record.variable_pay_per_month = round(record.variable_pay_per_annum / 12, 0)
                record.sub_total_c_per_annum = record.store_performance_incentive_annum + record.performance_linked_pay_annum + record.monthly_performance_incentive_annum + record.variable_pay_per_annum
                record.sub_total_c_per_month = round(record.sub_total_c_per_annum / 12, 0)
                record.total_salary_per_annum = record.sub_total_c_per_annum + record.sub_total_b_per_annum + record.sub_total_a_per_annum
                record.total_salary_per_month = round(record.total_salary_per_annum / 12, 0)
                record.medical_insurances = record.medical_insurance
                record.group_personal_acc_insurance = record.group_personal_accident_insurance
                record.sub_total_d = record.medical_insurances + record.group_personal_acc_insurance
                record.total_ctc_annum = record.total_salary_per_annum + record.sub_total_d
                record.total_ctc_month = round(record.total_ctc_annum / 12, 0)
                record.indicative_take_home_salary = record.sub_total_a_per_month + record.statutory_bonus_per_month - record.pf_employer_per_month - round(
                    record.esic_employer_per_month / 0.0325 * 0.75 / 100)

    basic_da = fields.Float(string="Basic & DA (PA)", store=True, copy=False, )
    house_rent_allowance = fields.Float(string="House Rent Allowance (PA)", store=True, copy=False)
    special_allowance = fields.Float(string="Special Allowance (PA)", store=True, copy=False)

    # monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)", store=True,
    #                                     copy=False,)
    # stat_bonus_amount = fields.Float(string="Statutory Bonus Amount", store=True, copy=False)
    # provident_fund = fields.Float(string="Provident Fund", store=True, copy=False)
    # esi_amount = fields.Float(string="ESI Amount", store=True, copy=False)
    # variable_pay_percentage = fields.Float(string="Percentage of Variable Pay  (per annum)", store=True, copy=False)
    variable_pay_amount = fields.Float(string="Variable Pay Amounts", store=True, copy=False)
    # annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive", store=True,
    #                                                   copy=False)
    # annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay", store=True, copy=False)
    # monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive", store=True, copy=False)
    # medical_insurance = fields.Float(string="Medical Insurance", store=True, copy=False)
    # group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance", store=True, copy=False)
    # solis_health_benefit_beacon_plan = fields.Float(string="Solis Health Benefit Beacon Plan", store=True, copy=False)
    # indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month", store=True, copy=False)
    #
    # statutory_bonus_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable (per month)", default='no',
    #     copy=False
    # )
    # provident_fund_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable (per month)", default='no',
    #     copy=False
    # )
    # esi_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable (per month)", default='no', copy=False
    # )
    # fixed_pay = fields.Float(string="Fixed Pay", store=False, copy=False)
    #fixed_pay newly added but not know
    # def action_open_contract_list(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.action_hr_contract')
    #     action.update({'domain': [('employee_id', '=', self.employee_id.id)],
    #                   'views':  [[False, 'list'], [False, 'kanban'], [False, 'activity'], [False, 'form']],
    #                    'context': {'default_employee_id': self.employee_id.id}})
    #     return action
