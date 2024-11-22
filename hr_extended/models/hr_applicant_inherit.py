# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import *


class Job_Applicant(models.Model):
    _inherit = "hr.applicant"

    sourcing_type = fields.Selection(
        [('internal_sourcing', 'Internal Sourcing'), ('external_sourcing', 'External Sourcing')], string="Sourcing Type", default='external_sourcing', required=True, copy=False,
        help="This field specifies the source of the candidate's CV")

    referred_by = fields.Many2one(
        'res.users',
        string='Referred By',
        help="The employee who referred this candidate."
    )

    is_pre_emp_form_clicked = fields.Boolean(string="Pre-Employment Form Clicked", default=False)

    monthly_fixed_salary = fields.Float(string="Monthly Fixed Salary (excl PF & all incentive pay)")
    statutory_bonus_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Statutory Bonus Applicable", default='no', required=True, copy=False
    )
    provident_fund_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Provident Fund Applicable", default='no',required=True, copy=False
    )
    esi_applicable = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="ESI Applicable", default='no',required=True, copy=False
    )
    variable_pay_percentage = fields.Float(string="Percentage of Variable Pay")
    annual_store_performance_incentive = fields.Float(string="Annual Store Performance Incentive")
    annual_performance_linked_pay = fields.Float(string="Annual Performance Linked Pay")
    monthly_performance_incentive = fields.Float(string="Monthly Performance Incentive")
    medical_insurance = fields.Float(string="Medical Insurance")
    group_personal_accident_insurance = fields.Float(string="Group Personal Accident Insurance")
    indicative_take_home_salary = fields.Float(string="Indicative Take Home Salary Per Month")
    grade_id = fields.Many2one('hr.job.levels', string="Grade")  # Create a custom model for grades if needed
    location_id = fields.Many2one('res.country.state', string="Location")  # Using states as an example for locations

    # Add additional fields as needed for Name, Designation, and Date of Joining
    # designation = fields.Char(string="Designation")
    # date_of_joining = fields.Date(string="Date of Joining")

    def action_create_pre_form(self):
        if not self.referred_by:
            raise ValidationError("The 'Referee' field is required to create a Pre-Employment Check Form.")

        pre_form = self.env['preemp.check'].create({
            'candidate_name': self.partner_name,
            'referee_id': self.referred_by.id,
            'referee_phone':self.referred_by.partner_id.phone,
            'referee_email' : self.referred_by.partner_id.email,
            })

        self.is_pre_emp_form_clicked=True

        return pre_form

    def action_open_related_candidate(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Referral Candidate',
            'view_mode': 'tree,form',
            'res_model': 'preemp.check',
            'domain': [('candidate_name', '=', self.partner_name)],
            'target': 'current',
        }