from odoo import models, fields, api, _
from odoo.exceptions import *


class SelfRating(models.Model):
    _name = 'self.rating'
    _description = 'Self Rating'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee',string='Employee Name', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    date_of_joining = fields.Date(string='Date of Joining', tracking=True)
    designation = fields.Char(string="Designation")
    reporting_to_id = fields.Many2one('hr.employee',string='Reporting to', required=True, tracking=True)
    location = fields.Char('Location', tracking=True)
    appraisal_date = fields.Date(string='Appraisal Date', tracking=True)
    reviewer_id = fields.Many2one('hr.employee',string='Reviewer', required=True, tracking=True)
    quarterly_review = fields.Boolean(string="Quarterly Performance Review", default=False)
    half_yearly_review = fields.Boolean(string="Half Yearly Performance Review", default=False)
    annual_review = fields.Boolean(string="Annual Performance Review/Appraisal", default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string="Status", default='draft', tracking=True)
    kra_ids = fields.One2many('self.rating.kra', 'rating_id', string="KRA Details")
    assessment_kra_ids = fields.One2many(
        'self.rating.assessment.kra', 'rating_id', string="Assessment KRA Details"
    )
    appraiser_overall_rating = fields.Float(string="Appraiser’s Overall Rating")
    appraiser_remarks = fields.Text(string="Appraiser’s Remarks")
    employee_signature = fields.Many2one('hr.employee', string="Employee’s Signature")
    reporting_manager_signature = fields.Many2one('hr.employee', string="Reporting Manager’s Signature")
    reviewer_signature = fields.Many2one('hr.employee', string="Reviewer’s Signature")
    development_plan_ids = fields.One2many(
        'self.rating.development.plan', 'rating_id', string="Employee Development Plan"
    )
    employee_signature_dev = fields.Many2one('hr.employee', string="Employee’s Signature")
    reporting_manager_signature_dev = fields.Many2one('hr.employee', string="Reporting Manager’s Signature")

    def action_submit(self):
        for record in self:
            record.write({'state': 'in_progress'})

    def action_mark_completed(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_set_to_drat(self):
        for record in self:
            record.write({'state': 'draft'})


class SelfRatingKRA(models.Model):
    _name = 'self.rating.kra'
    _description = 'KRA Details'

    rating_id = fields.Many2one('self.rating', string="Self Rating Reference", ondelete='cascade')
    name = fields.Char(string="KRA", required=True)
    weightage = fields.Float(string="Weightage (%)")
    employee_response = fields.Text(string="Employee's Response")
    appraiser_remarks = fields.Text(string="Appraiser's Remarks")


class SelfRatingAssessmentKRA(models.Model):
    _name = 'self.rating.assessment.kra'
    _description = 'Assessment KRA Details'

    rating_id = fields.Many2one('self.rating', string="Self Rating Reference", ondelete='cascade')
    name = fields.Char(string="KRA", required=True)
    weightage = fields.Float(string="Weightage (%)")
    employee_rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent'),
    ], string="Employee's Rating", default='3')
    appraiser_rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent'),
    ], string="Appraiser's Rating")

class SelfRatingDevelopmentPlan(models.Model):
    _name = 'self.rating.development.plan'
    _description = 'Employee Development Plan'

    rating_id = fields.Many2one('self.rating', string="Self Rating Reference", ondelete='cascade')
    action = fields.Char(string="Action", required=True)
    timeline = fields.Char(string="Time Line", required=True)
    by_whom = fields.Many2one('hr.employee', string="By Whom", required=True)
    remarks = fields.Text(string="Remarks")