from odoo import models, fields, api, _
from odoo.exceptions import *
from odoo.exceptions import ValidationError, UserError


class SelfRating(models.Model):
    _name = 'self.rating'
    _description = 'Self Rating'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee',string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True, related='employee_id.department_id')
    date_of_joining = fields.Date(string='Date of Joining', tracking=True, related='employee_id.joining_date')
    designation = fields.Char(string="Designation")
    reporting_to_id = fields.Many2one('hr.employee',string='Reporting to', tracking=True, related='employee_id.parent_id',)
    location = fields.Char('Location', tracking=True)
    appraisal_date = fields.Date(string='Appraisal Date', tracking=True)
    reviewer_id = fields.Many2one('hr.employee',string='Reviewer', tracking=True)
    state = fields.Selection([
        ('request_appraisal', 'Request Appraisal'),
        ('preparation', 'Preparation'),
        ('preparation_clarification', 'Preparation - In Clarification'),
        ('half_year_pending', 'Half Year Goals Pending'),
        ('half_year_clarification', 'Half Year Goals Clarification'),
        ('full_year_pending', 'Full Year Goals Pending'),
        ('full_year_clarification', 'Full Year Goals Clarification'),
        ('review_completed', 'Review Completed'),
    ], default='request_appraisal', string="State", tracking=True)
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
    goal_sets_kras = fields.One2many('performance.review.kra', 'rating_id', string="Goal Sets/KRAs")
    goal_review_comments = fields.One2many('performance.review.comment', 'rating_id', string="Goal Review Comments")
    manager_rating_ids = fields.One2many('manager.rating', 'rating_id', string="Manager Ratings")
    # director_rating_ids = fields.One2many('director.rating', 'rating_id', string="Director Ratings")
    supporting_document = fields.Binary(string="Supporting Document")
    action_needed = fields.Text(string="Action Needed")

    emp_number = fields.Char(string="Employee Number")
    organisation = fields.Char(string="Organisation")
    department = fields.Char(string="Department")
    status = fields.Char(string="Status")
    pending_from_date = fields.Date(string="Pending From Date")
    pending_days = fields.Integer(string="Pending Number of Days")
    total_weightage = fields.Float(string="Total Weightage")
    weightage_avg_achieved = fields.Float(string="Weightage Average Achieved")
    fy_final_rating = fields.Float(string="Final Rating (Out of 5)")
    mgr_recommended_rating = fields.Float(string="Manager Recommended Rating")

    # Fields for Review Completed
    final_rating = fields.Float(string="Final Rating")

    review_line_ids = fields.One2many('performance.review.line', 'review_id', string='Review Details')
    total_score_employee = fields.Float(string='Total', compute='_compute_totals', store=True)
    total_employee_weighted_score = fields.Float(string='Total Employee Weighted Score', compute='_compute_totals',
                                                 store=True)
    total_score_manager = fields.Float(string='Total', compute='_compute_totals', store=True)
    total_manager_weighted_score = fields.Float(string='Total Manager Weighted Score', compute='_compute_totals',
                                                store=True)
    employee_final_score = fields.Float(string='Employee Final Score', compute='_compute_totals', store=True)
    manager_final_score = fields.Float(string='Manager Final Score', compute='_compute_totals', store=True)
    is_employee = fields.Boolean(string="Is Employee", compute="_compute_is_employee", store=False)

    recommended_increment = fields.Float(string="Recommended Increment (%)", help="Recommended Increment percentage")
    recommended_pbvp_payout = fields.Float(string="Recommended PBVP Payout (%)",
                                           help="To be released on a pro-rata basis")
    pbvp_payout = fields.Float(string="PBVP Payout (%)",
                                           help="To be released on a pro-rata basis")
    eligible_for_promotion = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Eligible for Promotion?")
    new_job_level = fields.Char(string="Job Level")
    new_designation = fields.Char(string="New Designation (if applicable)")
    remark = fields.Char(string="Remark")
    refuse_reason = fields.Text(string="Refuse Reason")
    director_remark = fields.Text(string="Director Remark")
    is_performance_record = fields.Boolean(string="Is Performance Record", compute="_compute_is_performance_record", store=True)

    @api.depends('state')
    def _compute_is_performance_record(self):
        """
        Automatically sets 'is_performance_record' to True if the state is not 'request_appraisal'.
        """
        for record in self:
            record.is_performance_record = record.state != 'request_appraisal'

    @api.depends('employee_id')
    def _compute_is_employee(self):
        current_user = self.env.user
        for record in self:
            if record.employee_id:
                record.is_employee = record.employee_id.user_id == current_user
            else:
                record.is_employee = False

    @api.depends('kra_ids', 'kra_ids.employee_weighted_score', 'manager_rating_ids',
                 'manager_rating_ids.manager_weighted_score')
    def _compute_totals(self):
        for record in self:
            # Initialize totals
            total_employee_score = 0.0
            total_manager_score = 0.0
            total_weightage = 0.0
            line_count_self = len(record.kra_ids) if record.kra_ids else 1
            line_count_manager = len(record.manager_rating_ids) if record.manager_rating_ids else 1

            # Calculate totals based on kra_ids
            for kra in record.kra_ids:
                total_employee_score += kra.employee_weighted_score
                total_weightage += kra.weightage

            # Calculate totals based on manager_rating_ids
            for manager_rating in record.manager_rating_ids:
                total_manager_score += manager_rating.manager_weighted_score

            # Assign computed values to the record
            record.total_score_employee = total_employee_score
            record.total_score_manager = total_manager_score
            record.total_employee_weighted_score =((record.total_score_employee/100)/100)* line_count_self
            record.total_manager_weighted_score = ((record.total_score_employee / 100)/100) * line_count_manager
            record.employee_final_score = round(record.total_employee_weighted_score, 1)
            record.manager_final_score = round(record.total_manager_weighted_score, 1)
            if record.manager_final_score > 4.7:
                record.pbvp_payout = 100
            elif 4.5 <= record.manager_final_score <= 4.7:
                record.pbvp_payout = 90
            elif 4.0 <= record.manager_final_score < 4.5:
                record.pbvp_payout = 80
            elif 3.5 <= record.manager_final_score < 4.0:
                record.pbvp_payout = 70
            elif 3.0 <= record.manager_final_score < 3.5:
                record.pbvp_payout = 50
            elif 2.5 <= record.manager_final_score < 3.0:
                record.pbvp_payout = 30
            else:
                record.pbvp_payout = 0

    def action_request_appraisal(self):
        for record in self:
            record.state = 'preparation'

    def action_submit_performance_review(self):
        """Move state to 'preparation_clarification' after submission."""
        for record in self:
            if any(not kra.employee_response or not kra.self_rating for kra in record.kra_ids):
                raise ValidationError(_("You must fill in the Employee Justification and Self Rating before submission."))
            record.state = 'preparation_clarification'

    def action_manager_review(self):
        """Move state to 'half_year_pending' after Manager Review."""
        for record in self:
            if any(not manager.manager_rating or not manager.manager_remark for manager in record.manager_rating_ids):
                raise ValidationError(_("You must fill in the Rating and Remark before proceeding."))
            record.state = 'half_year_pending'
            record.recommended_pbvp_payout = record.pbvp_payout

    def action_hod_review(self):
        """Move state to 'full_year_pending' after HOD Review."""
        for record in self:
            if not record.remark:
                raise ValidationError(_("You must fill in the Remark field before proceeding."))
            record.state = 'full_year_pending'

    def action_director_review(self):
        """Move state to 'review_completed' after Director Review."""
        for record in self:
            record.state = 'review_completed'

    def action_refuse_request(self):
        return {
            'name': 'Refuse Form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'performance.review.refuse.popup',
            'view_id': self.env.ref('hr_appraisal_extended.view_performance_review_refuse_popup').id,
            'target': 'new',
            'context': {'default_employee_rating_id': self.id},
        }

    def send_increment_letter_job_level_approved(self):
        for record in self:
            template_id = self.env.ref('hr_appraisal_extended.mail_increment_letters')
            if not template_id:
                raise UserError(_("Increment letter template not found."))

            compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=True)

            if not compose_form:
                raise UserError(_("Email composition form not found."))

            ctx = dict(
                default_model='hr.appraisal',
                default_res_ids=record.ids,
                default_template_id=template_id.id,
                default_composition_mode='comment',
                default_email_layout_xmlid="mail.mail_notification_light",
            )

            return {
                'name': _('Compose Increment Letter Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }

    def send_appraisal_letter(self):
        for record in self:
            template_id = self.env.ref('hr_appraisal_extended.mail_appraisal_letters')
            if not template_id:
                raise UserError(_("Increment letter template not found."))

            compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=True)

            if not compose_form:
                raise UserError(_("Email composition form not found."))

            ctx = dict(
                default_model='hr.appraisal',
                default_res_ids=record.ids,
                default_template_id=template_id.id,
                default_composition_mode='comment',
                default_email_layout_xmlid="mail.mail_notification_light",
            )

            return {
                'name': _('Compose Appraisal Letter Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }

    def send_annual_increment_promotion_letter(self):
        for record in self:
            template_id = self.env.ref('hr_appraisal_extended.mail_annual_increment_promotion_letters')
            if not template_id:
                raise UserError(_("Increment letter template not found."))

            compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=True)

            if not compose_form:
                raise UserError(_("Email composition form not found."))

            ctx = dict(
                default_model='hr.appraisal',
                default_res_ids=record.ids,
                default_template_id=template_id.id,
                default_composition_mode='comment',
                default_email_layout_xmlid="mail.mail_notification_light",
            )

            return {
                'name': _('Compose Annual Increment Promotion Letter Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }

    def send_increment_redesignation_letter(self):
        for record in self:
            template_id = self.env.ref('hr_appraisal_extended.mail_increment_redesignation_letter_iim_job_approved')
            if not template_id:
                raise UserError(_("Increment letter template not found."))

            compose_form = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=True)

            if not compose_form:
                raise UserError(_("Email composition form not found."))

            ctx = dict(
                default_model='hr.appraisal',
                default_res_ids=record.ids,
                default_template_id=template_id.id,
                default_composition_mode='comment',
                default_email_layout_xmlid="mail.mail_notification_light",
            )

            return {
                'name': _('Compose Increment & Redesignation Letter Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }


class PerformanceReviewKRA(models.Model):
    _name = 'performance.review.kra'
    _description = 'Performance Review KRA'

    rating_id = fields.Many2one('self.rating', string="Review")
    category = fields.Char(string="Category")
    kra = fields.Char(string="KRA")
    goal_description = fields.Text(string="Goal Description")
    weightage = fields.Float(string="Weightage (%)")


class SelfRatingKRA(models.Model):
    _name = 'self.rating.kra'
    _description = 'KRA Details'

    rating_id = fields.Many2one('self.rating', string="Self Rating Reference", ondelete='cascade')
    name = fields.Char(string="KRA")
    weightage = fields.Float(string="Weightage (%)")
    employee_response = fields.Text(string="Employee's Justification")
    appraiser_remarks = fields.Text(string="Appraiser's Remarks")
    self_rating = fields.Float(string="Self Rating", help="Rating given by the Employee")
    goal_description = fields.Text(string="Goal Description")
    achieved_percentage = fields.Integer(string="Achieved Percentage",compute="_compute_achieved_percentage", store=True)
    employee_weighted_score = fields.Float(string='Employee Weighted Score', compute='_compute_weighted_scores',
                                           store=True)

    @api.depends('weightage', 'achieved_percentage')
    def _compute_weighted_scores(self):
        for line in self:
            line.employee_weighted_score = (line.weightage * line.achieved_percentage)

    @api.depends('self_rating', 'weightage')
    def _compute_achieved_percentage(self):
        for record in self:
            if record.weightage:
                record.achieved_percentage = (record.self_rating / record.weightage) * 100
            else:
                record.achieved_percentage = 0

class ManagerRating(models.Model):
    _name = 'manager.rating'
    _description = 'Manager Rating'

    rating_id = fields.Many2one('self.rating', string="Self Rating", ondelete='cascade')
    name = fields.Char(string="KRA")
    weightage = fields.Float(string="Weightage (%)")
    manager_rating = fields.Float(string="Manager Rating", help="Rating given by the manager")
    manager_remark = fields.Text(string="Manager Remark")
    achieved_percentage = fields.Integer(string="Achieved Percentage",compute="_compute_achieved_percentage", store=True)
    manager_weighted_score = fields.Float(string='Manager Weighted Score', compute='_compute_weighted_scores',
                                          store=True)

    @api.depends('weightage', 'achieved_percentage')
    def _compute_weighted_scores(self):
        for line in self:
            line.manager_weighted_score = (line.weightage * line.achieved_percentage)

    @api.depends('manager_rating', 'weightage')
    def _compute_achieved_percentage(self):
        for record in self:
            if record.weightage:
                record.achieved_percentage = (record.manager_rating / record.weightage) * 100
            else:
                record.achieved_percentage = 0


# class DirectorRating(models.Model):
#     _name = 'director.rating'
#     _description = 'Director Rating'
#
#     rating_id = fields.Many2one('self.rating', string="Self Rating", ondelete='cascade')
#     name = fields.Char(string="KRA", readonly=True)
#     weightage = fields.Float(string="Weightage (%)", readonly=True)
#     overall_final_rating = fields.Float(string="Overall Final Rating", help="Final Rating given by the Director")
#     director_remark = fields.Text(string="Director Remark")


class SelfRatingAssessmentKRA(models.Model):
    _name = 'self.rating.assessment.kra'
    _description = 'Assessment KRA Details'

    rating_id = fields.Many2one('self.rating', string="Self Rating Reference", ondelete='cascade')
    name = fields.Char(string="KRA")
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
    action = fields.Char(string="Action")
    timeline = fields.Char(string="Time Line")
    by_whom = fields.Many2one('hr.employee', string="By Whom")
    remarks = fields.Text(string="Remarks")


class PerformanceReviewComment(models.Model):
    _name = 'performance.review.comment'
    _description = 'Performance Review Comment'

    rating_id = fields.Many2one('self.rating', string="Review")
    commented_by = fields.Many2one('res.users', string="Commented By")
    comments = fields.Text(string="Comments")
    commented_date = fields.Datetime(string="Commented Date", default=fields.Datetime.now)
    need_response_from = fields.Many2one('hr.employee', string="Need Response From")

class PerformanceReviewLine(models.Model):
    _name = 'performance.review.line'
    _description = 'Performance Review Line'

    review_id = fields.Many2one('self.rating', string='Performance Review', ondelete='cascade')
    kra = fields.Char(string='KRA')
    description = fields.Char(string='Description')
    weightage = fields.Float(string='Weightage (%)')
    employee_score = fields.Float(string='Employee Score (%)')
    employee_weighted_score = fields.Float(string='Employee Weighted Score', compute='_compute_weighted_scores', store=True)
    manager_weightage = fields.Float(string='Manager Weightage (%)')
    manager_score = fields.Float(string='Manager Score (%)')
    manager_weighted_score = fields.Float(string='Manager Weighted Score', compute='_compute_weighted_scores', store=True)

    @api.depends('weightage', 'employee_score', 'manager_weightage', 'manager_score')
    def _compute_weighted_scores(self):
        for line in self:
            line.employee_weighted_score = (line.weightage * line.employee_score)
            line.manager_weighted_score = (line.manager_weightage * line.manager_score)
