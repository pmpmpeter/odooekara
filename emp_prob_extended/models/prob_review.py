from odoo import models, fields, api, _
import base64
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import *


class ProbationReviewForm(models.Model):
    _name = 'prob.review.form'
    _description = 'Probation Review Form'
    _inherit = 'mail.thread'

    name = fields.Char(string='Employee Name', required=True, tracking=True)
    job_title = fields.Many2one('hr.job', string='Job Title', tracking=True)
    grade = fields.Char(string='Grade', tracking=True)
    department = fields.Many2one('hr.department', string='Department / Section', tracking=True)
    date_of_joining = fields.Date(string='Date of Joining', tracking=True)
    reporting_manager = fields.Many2one('hr.employee', string='Reporting Manager',
                                        tracking=True)
    reporting_manager_designation = fields.Char(string='Manager Designation', tracking=True)
    three_month_review_due = fields.Date(string='Due Date', tracking=True)
    three_month_review_completed = fields.Date(string='Completed On', tracking=True)
    six_month_review_due = fields.Date(string='Due Date', tracking=True)
    six_month_review_completed = fields.Date(string='Completed On', tracking=True)

    REVIEW_RATING_SELECTION = [
        ('improvement_required', 'Improvement required'),
        ('satisfactory', 'Satisfactory'),
        ('good', 'Good'),
        ('excellent', 'Excellent')
    ]

    quality_of_work = fields.Selection(REVIEW_RATING_SELECTION, string='Quality and accuracy of work',
                                       default='satisfactory', required=True, tracking=True)
    efficiency = fields.Selection(REVIEW_RATING_SELECTION, string='Efficiency', default='satisfactory', required=True,
                                  tracking=True)
    attendance = fields.Selection(REVIEW_RATING_SELECTION, string='Attendance', default='satisfactory', required=True,
                                  tracking=True)
    time_keeping = fields.Selection(REVIEW_RATING_SELECTION, string='Time Keeping', default='satisfactory',
                                    required=True,
                                    tracking=True)
    work_relationships = fields.Selection(REVIEW_RATING_SELECTION,
                                          string='Work relationships',
                                          default='satisfactory', required=True, tracking=True)
    competency_in_role = fields.Selection(REVIEW_RATING_SELECTION, string='Competency in the role',
                                          default='satisfactory', required=True, tracking=True)

    performance_improvement_details = fields.Text(
        string='Areas of Performance, Conduct or Attendance Requiring Improvement')
    concerns_addressed_summary = fields.Text(string='How Concerns Will Be Addressed')
    performance_progress_summary = fields.Text(string='Employee Performance and Progress Summary')

    objectives_met = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], required=True, string='Have the objectives identified for the period of the probation been met?', default='yes')

    training_needs_met = fields.Selection([
        ('yes', 'YES'),
        ('no', 'NO')
    ], required=True, string='Have the training / development needs identified for this period of the probation been addressed?',
        default='yes')

    objectives_met_reason = fields.Text(string="Reason for not meeting objectives",
                                        help="Provide details if objectives have not been met")
    objectives_review_date = fields.Date(string='Objectives Review Date', help="Date of review for objectives")
    training_needs_met_reason = fields.Text(string="Reason for not addressing training needs",
                                            help="Provide details if training needs have not been addressed")
    training_review_date = fields.Date(string='Training Review Date', help="Date of review for training needs")
    employee_signature_id = fields.Many2one('hr.employee', string="Employee's Signature")
    manager_signature_id = fields.Many2one('hr.employee', string="Manager's Signature")
    date_part_1 = fields.Date(string="Date")
