from odoo import models, fields, api
from odoo.exceptions import *
from odoo.exceptions import ValidationError, UserError

class EmployeeKra(models.Model):
    _name = "employee.kra"
    _description = "Employee KRA"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    kra_date = fields.Date(string="Date", default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    emp_job_id = fields.Many2one('hr.job', string='Job Position')
    kra_master = fields.Many2one('kra.master', string="KRA")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_supervisor', 'Waiting Review'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    kra_details_ids = fields.One2many('employee.kra.details', 'emp_kra_id', string="Employee Details")
    employee_parent_id = fields.Many2one(related='employee_id.parent_id', readonly=False, related_sudo=False)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.emp_job_id = self.employee_id.job_id
            self.kra_master = self.emp_job_id.kra_master

    def action_submit_to_supervisor(self):
        for record in self:
            if not record.kra_details_ids:
                raise UserError("You cannot submit to supervisor as no KRA details are available for this employee.")
            record.state = 'submit_to_supervisor'
            template_id = self.env.ref('hr_extended.email_template_kra_submit')
            if template_id:
                template_id.send_mail(record.id, force_send=True)

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_approve(self):
        for record in self:
            record.state = 'done'

    def action_reset(self):
        for record in self:
            record.state = 'draft'

    def action_fetch_kra_details(self):
        if not self.kra_master:
            raise UserError("No KRA Master found for this employee.")
        self.kra_details_ids.unlink()

        for kra_detail in self.kra_master.details_ids:
            self.env['employee.kra.details'].create({
                'emp_kra_id': self.id,
                'category': kra_detail.category,
                'business_unit': kra_detail.business_unit,
                'goal_description': kra_detail.goal_description,
                'weightage': kra_detail.weightage,
            })

        return True

class KraDetails(models.Model):
    _name = "employee.kra.details"
    _description = "Employee KRA Details"

    emp_kra_id = fields.Many2one('employee.kra', string="KRA Questions", ondelete='cascade')

    category = fields.Char(string="Category", required=True)
    business_unit = fields.Text(string="Business Unit")
    goal_description = fields.Char(string="Goal Description")
    weightage = fields.Float(string="Weightage")
    employee_rating = fields.Float(string="Employee Rating")
    employee_remark = fields.Char(string="Employee Remark")
    manager_rating = fields.Float(string="Manager Rating")
    manager_remark = fields.Char(string="Manager Remark")
    final_score = fields.Float(string="Final Score", compute="_compute_final_score", store=True)

    @api.depends('weightage', 'employee_rating', 'manager_rating')
    def _compute_final_score(self):
        for record in self:
            # Ensure ratings do not exceed 100
            employee_rating = min(record.employee_rating, 100)
            manager_rating = min(record.manager_rating, 100)

            # Calculate weighted scores
            employee_weighted_score = (employee_rating / 100) * record.weightage
            manager_weighted_score = (manager_rating / 100) * record.weightage

            # Calculate final score
            record.final_score = employee_weighted_score + manager_weighted_score

