from odoo import models, fields, api
from datetime import timedelta

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pip_30_day_reminder = fields.Integer(string="Reminder for 30-day PIP", default=15)
    pip_60_day_reminder = fields.Integer(string="Reminder interval for 60+ day PIP", default=30)
    pip_end_reminder = fields.Integer(string="Reminder before End Date", default=7)

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('hr_pip.pip_30_day_reminder', self.pip_30_day_reminder)
        self.env['ir.config_parameter'].sudo().set_param('hr_pip.pip_60_day_reminder', self.pip_60_day_reminder)
        self.env['ir.config_parameter'].sudo().set_param('hr_pip.pip_end_reminder', self.pip_end_reminder)

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            pip_30_day_reminder=int(ICP.get_param('hr_pip.pip_30_day_reminder', default=15)),
            pip_60_day_reminder=int(ICP.get_param('hr_pip.pip_60_day_reminder', default=30)),
            pip_end_reminder=int(ICP.get_param('hr_pip.pip_end_reminder', default=7)),
        )
        return res

class HrPerformanceImprovementPlan(models.Model):
    _name = 'hr.pip'
    _description = 'Performance Improvement Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee",domain="[('company_id', '=', company_id)]", required=True, tracking=True)
    supervisor_id = fields.Many2one('hr.employee', string="Supervisor",domain="[('company_id', '=', company_id)]", required=True, tracking=True)
    hod_id = fields.Many2one('hr.employee', string="HOD/Director",domain="[('company_id', '=', company_id)]", tracking=True)
    hr_head_id = fields.Many2one('hr.employee', string="HR Head",domain="[('company_id', '=', company_id)]", tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,
                                 domain=lambda self: [('id', '=', (self.env.company.id))])
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="Projected Completion Date", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancel', 'Canceled')
    ], string="Status", default='draft', tracking=True)
    improvement_goal_ids = fields.One2many('hr.pip.improvement.goal', 'pip_id', string="Improvement Goals")
    activity_goal_ids = fields.One2many('hr.pip.activity.goal', 'pip_id', string="Activity Goals")
    resource_ids = fields.One2many('hr.pip.resource', 'pip_id', string="Resources")
    expectation_ids = fields.One2many('hr.pip.expectation', 'pip_id', string="Expectations")
    progress_checkpoint_ids = fields.One2many('hr.pip.progress', 'pip_id', string="Progress Checkpoints")
    activities_ids = fields.One2many('hr.pip.activity', 'pip_id', string="Activity")
    observations = fields.Text(string="Observations/Previous Discussions")
    areas_of_concern = fields.Text(string="Areas of Concern")
    notes = fields.Text(string="Additional Notes")
    employee_sign_id = fields.Many2one('hr.employee',domain="[('company_id', '=', company_id)]", string="Employee Name")
    employee_signature = fields.Binary(string="Employee Signature")
    employee_signature_date = fields.Date(string="Employee Signature Date")
    supervisor_sign_id = fields.Many2one('hr.employee',domain="[('company_id', '=', company_id)]", string="Supervisor Name")
    supervisor_signature = fields.Binary(string="Supervisor Signature")
    supervisor_signature_date = fields.Date(string="Supervisor Signature Date")
    hod_sign_id = fields.Many2one('hr.employee',domain="[('company_id', '=', company_id)]", string="HOD Name ")
    hod_signature = fields.Binary(string="HOD/Director Signature")
    hod_signature_date = fields.Date(string="HOD/Director Signature Date")
    hr_head_sign_id = fields.Many2one('hr.employee', string="HR Head Name ")
    hr_head_signature = fields.Binary(string="HR Head Signature")
    hr_head_signature_date = fields.Date(string="HR Head Signature Date")

    @api.model
    def cron_pip_reminders(self):
        ICP = self.env['ir.config_parameter'].sudo()
        reminder_30 = int(ICP.get_param('hr_pip.pip_30_day_reminder', default=15))
        reminder_60 = int(ICP.get_param('hr_pip.pip_60_day_reminder', default=30))
        reminder_end = int(ICP.get_param('hr_pip.pip_end_reminder', default=7))

        today = fields.Date.today()
        records = self.search([('state', '=', 'in_progress'), ('end_date', '!=', False)])

        for record in records:
            duration = (record.end_date - today).days
            # Reminder for 30-day PIP
            if duration == (30 - reminder_30):
                record._create_activity("PIP Reminder – Midpoint Notification")

            # Reminder for 60+ day PIP (every 30 days)
            if duration % reminder_60 == 0 and duration > 30:
                record._create_activity("PIP Reminder – Periodic Notification")

            # Reminder before end date
            if duration == reminder_end:
                record._create_activity("PIP Reminder – Upcoming End Date")

    def _create_activity(self, summary):
        users = []
        if self.supervisor_id.user_id:
            users.append(self.supervisor_id.user_id)
        if self.hr_head_id.user_id:
            users.append(self.hr_head_id.user_id)

        for user in users:
            self.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary=summary,
                note=f"PIP for {self.employee_id.name} requires your attention.",
                user_id=user.id,
                date_deadline=fields.Date.today(),
            )

    def action_submit(self):
        for record in self:
            record.write({'state': 'in_progress'})

    def action_mark_completed(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_set_to_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})


class HrPipImprovementGoal(models.Model):
    _name = 'hr.pip.improvement.goal'
    _description = 'Improvement Goals'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    name = fields.Char(string="Improvement Goal", required=True)


class HrPipActivityGoal(models.Model):
    _name = 'hr.pip.activity.goal'
    _description = 'Activity Goals'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    goal = fields.Char(string="Goal #", required=True)
    activity = fields.Char(string="Activity", required=True)
    how_to = fields.Text(string="How to Accomplish")
    start_date = fields.Date(string="Start Date")
    completion_date = fields.Date(string="Projected Completion Date")


class HrPipResource(models.Model):
    _name = 'hr.pip.resource'
    _description = 'Resources'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    name = fields.Char(string="Resource", required=True)


class HrPipExpectation(models.Model):
    _name = 'hr.pip.expectation'
    _description = 'Expectations'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    name = fields.Char(string="Expectation", required=True)


class HrPipProgress(models.Model):
    _name = 'hr.pip.progress'
    _description = 'Progress Checkpoints'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    goal = fields.Char(string="Goal #", required=True)
    activity = fields.Char(string="Activity", required=True)
    checkpoint_date = fields.Date(string="Checkpoint Date")
    followup_type = fields.Selection([
        ('email', 'Email'),
        ('memo', 'Memo'),
        ('call', 'Call'),
        ('meeting', 'Meeting')
    ], string="Type of Follow-up")
    progress_expected = fields.Text(string="Progress Expected")
    notes = fields.Text(string="Notes")


class HrPipActivity(models.Model):
    _name = 'hr.pip.activity'
    _description = 'HR PIP Activity'

    pip_id = fields.Many2one('hr.pip', string="PIP Reference", ondelete='cascade')
    date_schedule = fields.Date(string="Date Schedule")
    activity_memo = fields.Selection([
        ('30_update_memo', '30-Day Update Memo'),
        ('60_update_memo', '60-Day Update Memo'),
        ('60_status_memo', '60-Day Status Memo'),
    ], string="Activity")
    conducted_by = fields.Many2one('hr.employee', string="Conducted by", tracking=True)
    completion_date = fields.Date(string="Completion Date")
