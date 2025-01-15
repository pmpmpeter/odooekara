# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command, tools
from odoo.exceptions import *
from odoo.exceptions import UserError, ValidationError


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    stage = fields.Selection(
        selection=[
            ('new', 'New'),
            ('initial', 'Initial Qualification'),
            ('first_level', 'First Level Interview'),
            ('second_interview', 'Second Interview'),
            ('shortlist', 'Shortlist'),
            ('offer_accepted', 'Offer Accepted'),
            ('hold', 'Hold')
        ],
        string='Stage',
    )


class HrJobKra(models.Model):
    _inherit = "hr.job"

    kra_master = fields.Many2one('kra.master', string='KRA', copy=False,
                                 help="Select the Key Result Area (KRA) Master associated with this applicant.")


class Job_Applicant(models.Model):
    _inherit = "hr.applicant"

    # sourcing_type = fields.Selection(
    #     [('internal_sourcing', 'Internal Sourcing'), ('external_sourcing', 'External Sourcing')],
    #     string="Sourcing Type", default='external_sourcing', required=True, copy=False,
    #     help="This field specifies the source of the candidate's CV")
    #
    # referred_by = fields.Many2one(
    #     'res.users',
    #     string='Referred By', copy=False,
    #     help="The employee who referred this candidate."
    # )
    document_sent = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Document Sent", default='no', copy=False, readonly=True)
    offer_letter_approved = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Offer Letter Approval", default='no', copy=False, readonly=True)
    offer_letter_sent = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Offer Letter Sent", default='no', copy=False, readonly=True)
    grade_job_level_id = fields.Many2one('hr.job.levels', string='Job Levels', copy=False)
    verification_date = fields.Date(string="Verification Due Date", copy=False)

    # is_pre_emp_form_clicked = fields.Boolean(string="Pre-Employment Form Clicked", default=False, copy=False)

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
        [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable", default='no', required=True,
        copy=False
    )
    provident_fund_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable", default='no', required=True,
        copy=False
    )
    esi_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable", default='no', required=True, copy=False
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

    last_stage_id = fields.Many2one('hr.recruitment.stage', string='Last Stage', copy=False)
    stage_status = fields.Selection(
        related='stage_id.stage',
        string='Stage Status',
        store=True,
        readonly=False,  # Allows updates if required
    )
    first_invitation_letter_ids = fields.Many2many('applicant.invitation.letter',
                                                   compute='_compute_first_invitation_letter',
                                                   string='Invitation Letters', copy=False)
    first_invitation_letter_count = fields.Integer("Invitation Letter Count",
                                                   compute='_compute_first_invitation_letter', default=0, copy=False)
    interview_assessment_letter_ids = fields.Many2many('interview.assessment',
                                                       compute='_compute_interview_assessment_letter',
                                                       string='Assessment Letters', copy=False)
    interview_assessment_letter_count = fields.Integer("Assessment Letter Count",
                                                       compute='_compute_interview_assessment_letter', default=0,
                                                       copy=False)

    @api.onchange('location', 'monthly_fixed_salary', 'statutory_bonus_applicable', 'provident_fund_applicable',
                  'esi_applicable', 'grade',
                  'variable_pay_percentage', 'annual_store_performance_incentive', 'annual_performance_linked_pay',
                  'monthly_performance_incentive',
                  'medical_insurance', 'group_personal_accident_insurance')
    def _onchange_calculate_salary_breakup(self):
        for record in self:
            # Fetch the salary structure based on location and grade
            salary_structure = self.env['salary.structure'].search([
                ('location', '=', record.location),
                ('grade', '=', record.grade)
            ], limit=1)

            if salary_structure:
                record.basic_da_per_annum = salary_structure.annual_salary
                record.basic_da_per_month = salary_structure.monthly_salary
                record.hra_per_annum = 0
                record.hra_per_annum = 0
                record.hra_per_month = 0
                record.statutory_bonus_per_annum = 0
                record.statutory_bonus_per_month = 0
                record.special_allowance_per_annum = 0
                record.special_allowance_per_month = 0
                record.statutory_bonus_per_annum = 0
                record.statutory_bonus_per_month = 0
                record.sub_total_a_per_annum = record.basic_da_per_annum
                record.sub_total_a_per_month = round(record.sub_total_a_per_annum / 12, 0)
                if record.provident_fund_applicable == 'yes':
                    if record.monthly_fixed_salary < 15000:
                        record.pf_employer_per_annum = (record.monthly_fixed_salary * 0.12) * 12
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12, 0)
                else:
                    record.pf_employer_per_annum = 0

                record.pf_employer_per_month = round(record.pf_employer_per_annum / 12, 0)
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_annum = (record.monthly_fixed_salary * 0.0325) * 12
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_annum = 0

                record.esic_employer_per_month = round(record.esic_employer_per_annum / 12, 0)
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

            elif (record.location not in ['tta', 'tvm_obt']) or (record.monthly_fixed_salary >= 54000):
                # Calculate Basic & DA (Per Annum)
                record.basic_da_per_annum = round((record.monthly_fixed_salary * 12 * 0.4) / 12000, 0) * 12000
                record.hra_per_annum = record.basic_da_per_annum * 0.40

                # Calculate (Per Month)
                record.basic_da_per_month = round(record.basic_da_per_annum / 12, 0)
                record.hra_per_month = round(record.hra_per_annum / 12, 0)

                # Calculate Statutory Bonus (Per Annum) if applicable
                if record.statutory_bonus_applicable == 'yes':
                    if (record.basic_da_per_annum / 12) <= 21000:
                        record.statutory_bonus_per_annum = min(record.basic_da_per_annum, 84000) * 0.20
                    else:
                        record.statutory_bonus_per_annum = 0

                    # Calculate Statutory Bonus (Per Month)
                    record.statutory_bonus_per_month = round(record.statutory_bonus_per_annum / 12, 0)

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
                        record.pf_employer_per_annum = (record.monthly_fixed_salary * 0.12) * 12
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12, 0)
                else:
                    record.pf_employer_per_annum = 0

                record.pf_employer_per_month = round(record.pf_employer_per_annum / 12, 0)
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_annum = (record.monthly_fixed_salary * 0.0325) * 12
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_annum = 0

                record.esic_employer_per_month = round(record.esic_employer_per_annum / 12, 0)
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
                record.statutory_bonus_per_annum = 0
                record.statutory_bonus_per_month = 0
                record.sub_total_a_per_annum = 0
                record.sub_total_a_per_month = 0
                if record.provident_fund_applicable == 'yes':
                    if record.monthly_fixed_salary < 15000:
                        record.pf_employer_per_annum = (record.monthly_fixed_salary * 0.12) * 12
                    else:
                        record.pf_employer_per_month = round(15000 * 0.12, 0)
                else:
                    record.pf_employer_per_annum = 0

                record.pf_employer_per_month = round(record.pf_employer_per_annum / 12, 0)
                if record.esi_applicable == 'yes':
                    if record.monthly_fixed_salary <= 21000:
                        record.esic_employer_per_annum = (record.monthly_fixed_salary * 0.0325) * 12
                    else:
                        record.esic_employer_per_month = 0
                else:
                    record.esic_employer_per_annum = 0
                record.esic_employer_per_month = round(record.esic_employer_per_annum / 12, 0)
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

    def _compute_interview_assessment_letter(self):
        for record in self:
            domain = [('applicant_id', '=', record.id)]
            interview_assessment_letter_ids = self.env['interview.assessment'].sudo().search(domain)
            record.interview_assessment_letter_ids = interview_assessment_letter_ids
            record.interview_assessment_letter_count = len(interview_assessment_letter_ids)

    def action_open_interview_assessment_letter(self):
        action = self.env.ref('hr_extended.action_interview_assessment')
        result = action.sudo().read()[0]
        result.pop('id', None)
        result['context'] = {}
        if len(self.interview_assessment_letter_ids.ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, self.interview_assessment_letter_ids.ids)) + "])]"
        elif len(self.interview_assessment_letter_ids.ids) == 1:
            res = self.env.ref('hr_extended.view_interview_assessment_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.interview_assessment_letter_ids.ids and self.interview_assessment_letter_ids.ids[
                0] or False
        return result

    def _compute_first_invitation_letter(self):
        for record in self:
            domain = [('applicant_id', '=', record.id)]
            first_invitation_letter_ids = self.env['applicant.invitation.letter'].sudo().search(domain)
            record.first_invitation_letter_ids = first_invitation_letter_ids
            record.first_invitation_letter_count = len(first_invitation_letter_ids)

    def action_open_invitation_letter(self):
        action = self.env.ref('hr_extended.applicant_invitation_letter_action')
        result = action.sudo().read()[0]
        result.pop('id', None)
        result['context'] = {}
        if len(self.first_invitation_letter_ids.ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, self.first_invitation_letter_ids.ids)) + "])]"
        elif len(self.first_invitation_letter_ids.ids) == 1:
            res = self.env.ref('hr_extended.applicant_invitation_letter_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.first_invitation_letter_ids.ids and self.first_invitation_letter_ids.ids[0] or False
        return result

    def get_next_stage_name_applicant(self):
        self.ensure_one()
        stage_mapping = {
            'new': 'initial',
            'initial': 'first_level',
            'first_level': 'second_interview',
            'second_interview': 'shortlist',
        }
        next_stage_key = stage_mapping.get(self.stage_id.stage)
        next_stage = self.env['hr.recruitment.stage'].search([('stage', '=', next_stage_key)], limit=1)
        return next_stage.name if next_stage else "No Next Stage Defined"

    def action_send_first_invitiation(self):
        if not self.partner_name:
            raise UserError(_("Please fill the name of the Applicant"))
        if not self.email_from:
            raise UserError(_("Please fill the Email of the Applicant"))
        if not self.user_id:
            raise UserError(_("Please fill the Recruiter for the Applicant"))
        next_stage = self.get_next_stage_name_applicant()
        letter_heading = 'Invitation Letter - ' + str(next_stage)

        existing_letter = self.env['applicant.invitation.letter'].search([
            ('applicant_id', '=', self.id),
            ('state', 'in', ['draft', 'sent'])
        ], limit=1)

        if existing_letter:
            raise ValidationError(_("A invitation letter already exists for this applicant."))

        vals = {
            'applicant_id': self.id,
            'user_id': self.user_id.id,
            'letter_heading': letter_heading,
            # 'stage_id':self.stage_id.name
        }
        first_invitation_id = self.env['applicant.invitation.letter'].create(vals)
        # self.write({'stage_id': 1})
        ctx = self.env.context.copy()
        # ctx.update({'default_move_type': 'out_receipt'})
        return {
            'name': _('Invitation Letter'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'applicant.invitation.letter',
            'view_id': self.env.ref('hr_extended.applicant_invitation_letter_form_view').id,
            'context': ctx,
            'res_id': first_invitation_id.id,
        }

    # def action_open_related_candidate(self):
    #     self.ensure_one()
    #     candidate = self.env['preemp.check'].search(
    #         [('applicant_id', '=', self.id), ('candidate_name', '=', self.partner_name),
    #          ('candidate_email', '=', self.email_from)], limit=1)
    #
    #     if candidate:
    #         return {
    #             'name': _('Referral Candidate'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'preemp.check',
    #             'view_id': self.env.ref('hr_extended.view_pre_employment_reference_check_form').id,
    #             'res_id': candidate.id,
    #             'target': 'current',
    #         }

    def get_document_update_interview_subject(self):
        """Fetch the active subject from document.update.interview.status."""
        document_update = self.env['document.update.interview.status'].search([('active', '=', True)], limit=1)
        return document_update.name

    def action_send_document_update_mail(self):
        for applicant in self.filtered(lambda s: not s.stage_id.stage):
            raise UserError(_("Alert !! Configure %s stage properly.") % (applicant.stage_id.display_name))
        for applicant in self.filtered(lambda s: s.stage_id.stage not in ['shortlist']):
            raise UserError(
                _("Alert !! You cannot send document update at %s stage") % (applicant.stage_id.display_name))
        for applicant in self.filtered(lambda s: s.stage_id.stage in ['shortlist']):
            if not applicant.get_document_update_interview_subject():
                raise UserError(_("Kindly update the document subject email."))
            template = self.env.ref('hr_extended.document_update_interview_status_mail')
            if not template:
                raise UserError(_("Alert !! Offer Letter template not found."))
            if not applicant.email_from:
                raise UserError(_("Alert !! Update applicant email address."))
            if applicant.email_from and template:
                template.send_mail(applicant.id, force_send=True)
                applicant.write({'document_sent': 'yes'})

    def action_approve_offer_letter(self):
        for record in self:
            record.offer_letter_approved = "yes"

    def action_send_offer_letter_mail(self):
        for applicant in self.filtered(lambda s: not s.stage_id.stage):
            raise UserError(_("Alert !! Configure %s stage properly.") % (applicant.stage_id.display_name))
        for applicant in self.filtered(lambda s: s.stage_id.stage not in ['shortlist']):
            raise UserError(
                _("Alert !! You cannot send document update at %s stage") % (applicant.stage_id.display_name))
        for applicant in self.filtered(lambda s: s.stage_id.stage in ['shortlist']):
            template = self.env.ref('hr_extended.offer_letter_mail')
            if not template:
                raise UserError(_("Alert !! Offer Letter template not found."))
            if not applicant.email_from:
                raise UserError(_("Alert !! Update applicant email address."))
            if applicant.email_from and template:
                template.send_mail(applicant.id, force_send=True)
                applicant.write({'offer_letter_sent': 'yes'})

            # compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
            # if not compose_form:
            #     raise UserError(_("Email composition form not found."))
            # ctx = {
            #     'default_model': 'hr.applicant',
            #     'default_res_ids': applicant.ids,
            #     'default_template_id': template.id,
            #     'default_composition_mode': 'comment',
            #     'force_email': True,
            # }
            # # applicant.write({'offer_letter_sent': 'yes'})
            # return {
            #     'name': _('Compose Offer Letter Email'),
            #     'type': 'ir.actions.act_window',
            #     'view_mode': 'form',
            #     'res_model': 'mail.compose.message',
            #     'views': [(compose_form.id, 'form')],
            #     'view_id': compose_form.id,
            #     'target': 'new',
            #     'context': ctx,
            # }

    def action_first_stage_new(self):
        """move to 'New' stage"""
        for record in self:
            new_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'new')], limit=1)
            if new_stage:
                record.stage_id = new_stage.id
            else:
                raise UserError("New stage not found! Please create one in Recruitment stages.")

    def action_approve(self):
        """move to 'Shortlisted' stage"""
        for record in self:
            if hasattr(self, 'x_has_request_approval'):
                self.x_has_request_approval = False
            shortlist_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'shortlist')], limit=1)
            if shortlist_stage:
                record.stage_id = shortlist_stage.id
            else:
                raise UserError("Shortlist stage not found! Please create one in Recruitment stages.")

    def action_offer_accepted(self):
        """move to 'Offer Accepted' stage"""
        for record in self:
            offer_accepted_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'offer_accepted')], limit=1)
            if offer_accepted_stage:
                record.stage_id = offer_accepted_stage.id
            else:
                raise UserError("Offer Accepted stage not found! Please create map in Recruitment stages.")

    def action_hold(self):
        """Mark as on hold"""
        for record in self:
            hold_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'hold')], limit=1)
            record.last_stage_id = record.stage_id.id
            if hold_stage:
                record.stage_id = hold_stage.id
            else:
                raise UserError("Hold stage not found! Please create one in Recruitment stages.")

    def action_reopen(self):
        """Reopen the application from hold status"""
        for record in self:
            record.stage_id = record.last_stage_id.id

    def _create_kra_for_employee(self, employee, job_position):
        """
        Create a KRA record for the newly created employee based on the job position.
        """
        kra_model = self.env['employee.kra']
        kra_values = {
            'employee_id': employee.id,
            'emp_job_id': job_position.id,  # Explicitly set job_id
            'kra_master': job_position.kra_master.id,
        }
        kra_record = kra_model.sudo().create(kra_values)
        return kra_record

    def _create_jonining_documents_for_employee(self, employee, job_position):
        for record in self:
            joining_doc_employee = self.env['joining.documents']
            domain1 = [('active', '=', True)]
            joining_docs = self.env['employee.join.doc.config'].sudo().search(domain1)
            if joining_docs:
                for doc in joining_docs:
                    vals = {
                        'join_doc_id': doc.id,
                        'name': doc.name,
                        'document_type': doc.document_type,
                        'subject': doc.subject,
                        'employee_id': employee.id,
                        'reference_file': doc.file,
                        'reference_filename': doc.file_name,
                        'job_position_id': employee.job_id.id,
                        'department_id': employee.department_id.id,
                        'company_id': doc.company_id.id,
                        'joining_date': self.availability,
                        'contact_id': doc.contact_id.id if doc.contact_id else False,
                    }
                    joining_record = joining_doc_employee.sudo().create(vals)
                    print(joining_record, joining_record.join_doc_id, joining_record.join_doc_id.name, joining_record.sequence)
                    # raise ValidationError(888)

                    # preemp_check_vals = {
                    #     'applicant_id': self.id,
                    #     'candidate_name': self.partner_name,
                    #     'candidate_email': self.email_from,
                    # }
                    # self.env['preemp.check'].sudo().create(preemp_check_vals)


    def create_employee_from_applicant(self):
        if not self.grade_job_level_id:
            raise ValidationError("Please set the Job Level before creating an employee.")
        if not self.job_id:
            raise ValidationError("Please set the Job Position before creating an employee.")
        if not self.department_id:
            raise ValidationError("Please set the Department before creating an employee.")
        action = super(Job_Applicant, self).create_employee_from_applicant()

        employee_id = action.get('res_id')
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if employee and self.job_id:
                employee.write({
                    'job_level_id': self.grade_job_level_id.id,  # Set job level on employee
                })
                self._create_kra_for_employee(employee, self.job_id)
                self._create_jonining_documents_for_employee(employee, self.job_id)
                self._attach_documents_to_employee(employee)
        return action

    def _attach_documents_to_employee(self, employee):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.applicant'),
            ('res_id', '=', self.id)
        ])
        for attachment in attachments:
            attachment.copy({
                'res_model': 'hr.employee',
                'res_id': employee.id
            })

    def action_create_interview_assessment(self):
        if not self.interviewer_ids:
            raise ValidationError("The 'Interviewer' field is required to create an Interview Assessment Form.")

        for interviewer in self.interviewer_ids:
            if not interviewer.email:
                raise ValidationError(
                    f"Interviewer {interviewer.name} does not have an email address. Please provide a valid email.")

        vals = {
            'name': self.partner_name,
            'position_interviewed_for': self.job_id.name,
            'position_offered': self.job_id.id,
            'applicant_id': self.id,
            'expected_date_of_joining': self.availability,
        }

        interview_assessment_id = self.env['interview.assessment'].create(vals)

        return {
            'name': _('Interview Assessment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'interview.assessment',
            'view_id': self.env.ref('hr_extended.view_interview_assessment_form').id,
            'res_id': interview_assessment_id.id,
        }


    # monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)", store=True,
    #                                     copy=False)
    # statutory_bonus_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable (per month)", default='no', required=True,
    #     copy=False
    # )
    # stat_bonus_amount = fields.Float(string="Statutory Bonus Amount", store=True, copy=False)
    # provident_fund_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable (per month)", default='no', required=True,
    #     copy=False
    # )
    # provident_fund = fields.Float(string="Provident Fund", store=True, copy=False, readonly=True)
    # esi_applicable = fields.Selection(
    #     [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable (per month)", default='no', required=True, copy=False
    # )
    # esi_amount = fields.Float(string="ESI Amount", store=True, copy=False, readonly=True)
    # variable_pay_percentage = fields.Float(string="Percentage of Variable Pay (per annum)", store=True, copy=False)
    variable_pay_amount = fields.Float(string="Variable Pay Amounts", store=True, readonly=True, copy=False)
    # annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive", store=True,
    #                                                   copy=False)
    # annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay", store=True, copy=False)
    # monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive", store=True, copy=False)
    # medical_insurance = fields.Float(string="Medical Insurance", store=True, copy=False)
    # group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance", store=True, copy=False)
    # solis_health_benefit_beacon_plan = fields.Float(string="Solis Health Benefit Beacon Plan", store=True, copy=False)
    # indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month", store=True, copy=False)
    basic_da = fields.Float(string="Basic & DA (PA)", store=True, copy=False)
    house_rent_allowance = fields.Float(string="House Rent Allowance (PA)", store=True, copy=False)
    special_allowance = fields.Float(string="Special Allowance (PA)", store=True, copy=False)
    # there is calculation for this take home salary
    grade_id = fields.Many2one('hr.job.levels', string="Grade",
                               copy=False)  # Create a custom model for grades if needed
    location_id = fields.Many2one('res.country.state', string="Location",
                                  copy=False)  # Using states as an example for locations

# # To fix the value as 0.0
# @api.constrains('statutory_bonus_applicable')
# def _check_statutory_bonus(self):
#     for record in self:
#         if record.statutory_bonus_applicable == 'no':
#             record.stat_bonus_amount = 0.0
#
# @api.constrains('provident_fund_applicable')
# def _check_provident_fund(self):
#     for record in self:
#         if record.provident_fund_applicable == 'no':
#             record.provident_fund = 0.0
#
# @api.constrains('esi_applicable')
# def _check_esi(self):
#     for record in self:
#         if record.esi_applicable == 'no':
#             record.esi_amount = 0.0
#
# @api.onchange('monthly_fixed_salary', 'provident_fund_applicable')
# def _onchange_provident_fund(self):
#     for record in self:
#         if record.provident_fund_applicable == 'yes':
#             if record.monthly_fixed_salary < 15000:
#                 record.provident_fund = record.monthly_fixed_salary * 0.12
#             elif record.monthly_fixed_salary >= 15000:
#                 record.provident_fund = 15000 * 0.12
#
# @api.onchange('monthly_fixed_salary', 'esi_applicable')
# def _onchange_esi_amount(self):
#     for record in self:
#         if record.esi_applicable == 'yes':
#             if record.monthly_fixed_salary <= 21000:
#                 record.esi_amount = record.monthly_fixed_salary * 0.0325
#             else:
#                 record.esi_amount = 0.0
#
# @api.onchange('monthly_fixed_salary', 'variable_pay_percentage', 'provident_fund')
# def _onchange_variable_pay_amount(self):
#     for record in self:
#         if record.variable_pay_percentage > 0:
#             monthly_salary = record.monthly_fixed_salary or 0.0
#             provident_fund_annual = (record.provident_fund or 0.0) * 12
#             variable_percentage = record.variable_pay_percentage / 100
#             record.variable_pay_amount = round((monthly_salary * 12 + provident_fund_annual) * variable_percentage,
#                                                0)

# def action_create_pre_form(self):
#     if not self.referred_by:
#         raise ValidationError("The 'Referee' field is required to create a Pre-Employment Check Form.")
#     if not self.email_from:
#         raise ValidationError("The Candidate Email fields is required to create a Pre-Employment Check Form.")
#
#     template = self.env.ref('hr_extended.reference_check_form_template')
#     for rec in self:
#         if rec.referred_by.email:
#             template.send_mail(rec.id, force_send=True)
#
#     vals = {
#         'applicant_id': self.id,
#         'candidate_name': self.partner_name,
#         'candidate_email': self.email_from,
#         'referee_id': self.referred_by.id,
#         'referee_phone': self.referred_by.partner_id.phone,
#         'referee_email': self.referred_by.partner_id.email,
#         'recruiter_id': self.user_id.id,
#     }
#     pre_form = self.env['preemp.check'].create(vals)
#     self.write({'is_pre_emp_form_clicked': True})
#     return pre_form
