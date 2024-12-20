from odoo import models, fields, api


class PerformanceReview(models.Model):
    _name = 'performance.review'
    _description = 'Performance Review'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    name = fields.Char(string="Name", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    state = fields.Selection([
        ('preparation', 'Preparation'),
        ('preparation_clarification', 'Preparation - In Clarification'),
        ('half_year_pending', 'Half Year Goals Pending'),
        ('half_year_clarification', 'Half Year Goals Clarification'),
        ('full_year_pending', 'Full Year Goals Pending'),
        ('full_year_clarification', 'Full Year Goals Clarification'),
        ('review_completed', 'Review Completed'),
    ], default='preparation', string="State", tracking=True)

    # Fields for Initiate Performance Review
    create_review_current_year = fields.Boolean(string="Create Review Current Year")
    create_review_previous_year = fields.Boolean(string="Create Review Previous Year")

    # Fields for Preparation
    goal_sets_kras = fields.One2many('performance.review.kra', 'review_id', string="Goal Sets/KRAs")
    goal_review_comments = fields.One2many('performance.review.comment', 'review_id', string="Goal Review Comments")
    supporting_document = fields.Binary(string="Supporting Document")
    action_needed = fields.Text(string="Action Needed")

    # Fields for Full Year Manager Review
    emp_number = fields.Char(string="Employee Number")
    organisation = fields.Char(string="Organisation")
    department = fields.Char(string="Department")
    designation = fields.Char(string="Designation")
    status = fields.Char(string="Status")
    pending_from_date = fields.Date(string="Pending From Date")
    pending_days = fields.Integer(string="Pending Number of Days")
    total_weightage = fields.Float(string="Total Weightage")
    weightage_avg_achieved = fields.Float(string="Weightage Average Achieved")
    fy_final_rating = fields.Float(string="Final Rating (Out of 5)")
    mgr_recommended_rating = fields.Float(string="Manager Recommended Rating")

    # Fields for Review Completed
    final_rating = fields.Float(string="Final Rating")


class PerformanceReviewKRA(models.Model):
    _name = 'performance.review.kra'
    _description = 'Performance Review KRA'

    review_id = fields.Many2one('performance.review', string="Review")
    category = fields.Char(string="Category")
    kra = fields.Char(string="KRA")
    goal_description = fields.Text(string="Goal Description")
    goal = fields.Text(string="Goal")


class PerformanceReviewComment(models.Model):
    _name = 'performance.review.comment'
    _description = 'Performance Review Comment'

    review_id = fields.Many2one('performance.review', string="Review")
    commented_by = fields.Many2one('res.users', string="Commented By")
    comments = fields.Text(string="Comments")
    commented_date = fields.Datetime(string="Commented Date", default=fields.Datetime.now)
    need_response_from = fields.Many2one('hr.employee', string="Need Response From")
