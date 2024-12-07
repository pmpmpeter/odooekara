# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command, tools
from odoo.exceptions import *

class PreEmpCheck(models.Model):
    _name = 'preemp.check'
    _description = 'Pre Employment Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "candidate_name"

    # applicant_id = fields.Many2one('hr.applicant', string='Applicant', ondelete='cascade')
    applicant_id = fields.Integer(string='Applicant',readonly=True)
    candidate_name = fields.Char(string="Candidate Name",copy=False)
    candidate_email = fields.Char(string="Candidate Email ID", readonly=True)
    date = fields.Date(string="Date",copy=False,default=fields.Date.context_today)
    location = fields.Char(string="Location",copy=False)
    referee_id = fields.Many2one('res.users',string="Name of Referee",copy=False)
    recruiter_id = fields.Many2one('res.users',string="Recruiting Manager",copy=False)
    referee_phone = fields.Char(string="Phone Number",copy=False)
    referee_email = fields.Char(string="Email ID",copy=False)
    referee_title = fields.Char(string="Title of Referee",copy=False)
    referee_relationship = fields.Char(string="Relationship to Candidate",copy=False)
    technical_skills_comments = fields.Text(string="Technical Skills and Expertise",copy=False)
    job_duties_comments = fields.Text(string="Job Duties Handled during the Tenure",copy=False)
    professional_skills_comments = fields.Text(string="Professional Interactive Skills",copy=False)

    integrity_resources = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Integrity or Effectiveness in Handling Organization’s Resources?",copy=False
    )
    integrity_interactions = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Integrity or Effectiveness in Professional Interactions?",copy=False
    )
    responsibility_productivity = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Ability to Accept Responsibility or Maintain Productivity?",copy=False
    )
    maturity_composure = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Maturity, Composure, or Professional Conduct Under Job Stresses?",copy=False
    )
    adaptability = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string="Ability to Adapt to New or Changing Work Situations?",copy=False
    )

    additional_comments = fields.Text(string="If Yes to Any, Please Comment",copy=False)
    other_comments = fields.Text(string="Other Comments or Recommendation",copy=False)

    state = fields.Selection([
        ('to_submit', 'To Submit'),
        ('done', 'Done')
    ], string='Status', default='to_submit', required=True, tracking=True, copy=False)

    def action_done(self):
        for rec in self:
            rec.state='done'

    def action_send_form_pdf_mail(self):
        template = self.env.ref('hr_extended.reference_check_pdf_form_template')
        for rec in self:
            if rec.recruiter_id.email:
                template.send_mail(rec.id, force_send=True)
