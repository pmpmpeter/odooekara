# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command, tools
from odoo.exceptions import *

class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    stage = fields.Selection(
        selection=[
            ('second_interview', 'Second Interview'),
            ('shortlist', 'Shortlist'),
            ('first_level', 'First Level Interview'),
            ('hold', 'Hold')
        ],
        string='Stage',
    )

class Job_Applicant(models.Model):
    _inherit = "hr.applicant"

    sourcing_type = fields.Selection(
        [('internal_sourcing', 'Internal Sourcing'), ('external_sourcing', 'External Sourcing')],
        string="Sourcing Type", default='external_sourcing', required=True, copy=False,
        help="This field specifies the source of the candidate's CV")

    referred_by = fields.Many2one(
        'res.users',
        string='Referred By', copy=False,
        help="The employee who referred this candidate."
    )

    grade_job_level_id = fields.Many2one('hr.job.levels', string='Job Levels', copy=False)
    verification_date = fields.Date(string="Verification Due Date", copy=False)

    is_pre_emp_form_clicked = fields.Boolean(string="Pre-Employment Form Clicked", default=False,copy=False)

    monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)", store=True, copy=False)
    statutory_bonus_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable (per month)", default='no', required=True, copy=False
    )
    stat_bonus_amount = fields.Float(string="Statutory Bonus Amount", store=True, copy=False, readonly=True)
    provident_fund_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable (per month)", default='no', required=True, copy=False
    )
    provident_fund = fields.Float(string="Provident Fund", store=True, copy=False, readonly=True)
    esi_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable (per month)", default='no', required=True, copy=False
    )
    esi_amount = fields.Float(string="ESI Amount", store=True, copy=False, readonly=True)
    variable_pay_percentage = fields.Float(string="Percentage of Variable Pay", store=True, copy=False)
    variable_pay_amount = fields.Float(string="Variable Pay Amounts", store=True, readonly=True, copy=False)
    annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive", store=True, copy=False)
    annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay", store=True, copy=False)
    monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive", store=True, copy=False)
    medical_insurance = fields.Float(string="Medical Insurance", store=True, copy=False)
    group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance", store=True, copy=False)
    solis_health_benefit_beacon_plan = fields.Float(string="Solis Health Benefit Beacon Plan", store=True, copy=False)
    indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month", store=True, copy=False, readonly=True)
    #there is calculation for this take home salary
    grade_id = fields.Many2one('hr.job.levels', string="Grade", copy=False)  # Create a custom model for grades if needed
    location_id = fields.Many2one('res.country.state', string="Location", copy=False)  # Using states as an example for locations
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

    # Add additional fields as needed for Name, Designation, and Date of Joining
    # designation = fields.Char(string="Designation")
    # date_of_joining = fields.Date(string="Date of Joining")

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

    # To fix the value as 0.0
    @api.constrains('statutory_bonus_applicable')
    def _check_statutory_bonus(self):
        for record in self:
            if record.statutory_bonus_applicable == 'no':
                record.stat_bonus_amount = 0.0

    @api.constrains('provident_fund_applicable')
    def _check_provident_fund(self):
        for record in self:
            if record.provident_fund_applicable == 'no':
                record.provident_fund = 0.0

    @api.constrains('esi_applicable')
    def _check_esi(self):
        for record in self:
            if record.esi_applicable == 'no':
                record.esi_amount = 0.0

    @api.onchange('monthly_fixed_salary', 'provident_fund_applicable')
    def _onchange_provident_fund(self):
        for record in self:
            if record.provident_fund_applicable == 'yes':
                if record.monthly_fixed_salary < 15000:
                    record.provident_fund = record.monthly_fixed_salary * 0.12
                elif record.monthly_fixed_salary >= 15000:
                    record.provident_fund = 15000 * 0.12

    @api.onchange('monthly_fixed_salary', 'esi_applicable')
    def _onchange_esi_amount(self):
        for record in self:
            if record.esi_applicable == 'yes':
                if record.monthly_fixed_salary <= 21000:
                    record.esi_amount = record.monthly_fixed_salary * 0.0325
                else:
                    record.esi_amount = 0.0

    @api.onchange('monthly_fixed_salary', 'variable_pay_percentage', 'provident_fund')
    def _onchange_variable_pay_amount(self):
        for record in self:
            if record.variable_pay_percentage > 0:
                monthly_salary = record.monthly_fixed_salary or 0.0
                provident_fund_annual = (record.provident_fund or 0.0) * 12
                variable_percentage = record.variable_pay_percentage / 100
                record.variable_pay_amount = round((monthly_salary * 12 + provident_fund_annual) * variable_percentage,0)

    def action_create_pre_form(self):
        if not self.referred_by:
            raise ValidationError("The 'Referee' field is required to create a Pre-Employment Check Form.")

        template = self.env.ref('hr_extended.reference_check_form_template')
        for rec in self:
            if rec.referred_by.email:
                template.send_mail(rec.id, force_send=True)

        vals = {
            'applicant_id': self.id,
            'candidate_name': self.partner_name,
            'candidate_email':self.email_from,
            'referee_id': self.referred_by.id,
            'referee_phone':self.referred_by.partner_id.phone,
            'referee_email' : self.referred_by.partner_id.email,
            'recruiter_id' : self.user_id.id
        }
        pre_form = self.env['preemp.check'].create(vals)
        self.write({'is_pre_emp_form_clicked': True})
        return pre_form

    def action_send_first_invitiation(self):
        vals = {
            'applicant_id': self.id,
            'user_id': self.user_id.id,
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

    def action_open_related_candidate(self):
        self.ensure_one()
        candidate = self.env['preemp.check'].search([('applicant_id','=',self.id),('candidate_name', '=', self.partner_name),
                                                     ('candidate_email', '=',self.email_from)], limit=1)

        if candidate:
            return {
                'name': _('Referral Candidate'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'preemp.check',
                'view_id': self.env.ref('hr_extended.view_pre_employment_reference_check_form').id,
                'res_id': candidate.id,
                'target': 'current',
            }

    def action_approve(self):
        """move to 'Shortlisted' stage"""
        for record in self:
            shortlist_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'shortlist')], limit=1)
            if shortlist_stage:
                record.stage_id = shortlist_stage.id
            else:
                raise UserError("Shortlist stage not found! Please create one in Recruitment stages.")    

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
