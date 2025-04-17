# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _, _lt
from datetime import datetime,timedelta
from odoo.exceptions import UserError, ValidationError

class Project(models.Model):
    _inherit = "project.project"

    is_a_master = fields.Boolean(string='Is a Master')
    department_id = fields.Many2one('hr.department',string='Department')
    is_legal_notice = fields.Boolean(string="Is Legal Notice", default=False)
    is_statuory_notice = fields.Boolean(string="Is Statutory Notice", default=False)
    first_reminder_date = fields.Date(string="First Reminder Date")
    second_reminder_date = fields.Date(string="Second Reminder Date")
    date_of_notice = fields.Date(string="Date of Notice", default=fields.Date.context_today)
    last_date = fields.Date(string="Last Date")
    first_reminder = fields.Integer('First Reminder',readonly=0)
    second_reminder = fields.Integer('Second Reminder',readonly=0)
    is_done = fields.Boolean(string='Done')

    # @api.depends('date_of_notice', 'last_date')
    # def _compute_reminder_dates(self):
    #     for project in self:
    #         if project.date_of_notice and project.last_date:
    #             notice_date = fields.Date.from_string(project.date_of_notice)
    #             last_date = fields.Date.from_string(project.last_date)
    #
    #             # Calculate total duration between `date_of_notice` and `last_date`
    #             total_days = (last_date - notice_date).days
    #
    #             # Calculate First Reminder:
    #             first_reminder_days = total_days // 3
    #             first_reminder_date = notice_date + timedelta(days=first_reminder_days)
    #             project.first_reminder_date = first_reminder_date
    #             project.first_reminder = first_reminder_days
    #
    #             # Calculate Second Reminder: 2 days before `last_date`
    #             second_reminder_date = last_date - timedelta(days=2)
    #             project.second_reminder_date = second_reminder_date
    #
    #             # Calculate days between `date_of_notice` and `second_reminder_date`
    #             second_reminder_days = (second_reminder_date - notice_date).days
    #             project.second_reminder = second_reminder_days
    #         else:
    #             project.first_reminder_date = False
    #             project.first_reminder = 0
    #             project.second_reminder_date = False
    #             project.second_reminder = 0

    @api.onchange('last_date','first_reminder','second_reminder')
    def _onchange_dates(self):
        """
        Update reminder fields when the date_of_notice or last_date changes.
        """
        for project in self:
            if project.is_legal_notice or project.is_statuory_notice:
                if project.last_date:
                    date_of_notice = project.date_of_notice
                    last_date = project.last_date
                    if last_date < fields.Date.today():
                        raise UserError(_("Kindly provide the correct date."))
                    else:
                        if project.first_reminder:
                            first_reminder = project.first_reminder
                            project.first_reminder_date = last_date - timedelta(days=first_reminder)
                        if project.second_reminder:
                            second_reminder = project.second_reminder
                            project.second_reminder_date = last_date - timedelta(days=second_reminder)

    def send_reminder(self):
        today = fields.Date.today()
        legal_first_reminder = self.sudo().search([
            ('first_reminder_date', '=', today),('is_legal_notice','=',True)
        ])
        legal_second_reminder = self.sudo().search([
            ('second_reminder_date', '=', today),('is_legal_notice','=',True)
        ])
        statuory_first_reminder = self.sudo().search([
            ('first_reminder_date', '=', today),('is_statuory_notice','=',True)
        ])
        statuory_second_reminder = self.sudo().search([
            ('second_reminder_date', '=', today),('is_statuory_notice','=',True)
        ])
        if legal_first_reminder:
            self._schedule_activities_first_reminder_legal()
            self._send_first_reminder_email_notifications_legal(legal_first_reminder)
        if legal_second_reminder:
            self._schedule_activities_second_reminder_legal()
            self._send_second_reminder_email_notifications_legal(legal_second_reminder)
        if statuory_first_reminder:
            self._schedule_activities_first_reminder_statuory()
            self._send_first_reminder_email_notifications_statuory(statuory_first_reminder)
        if statuory_second_reminder:
            self._schedule_activities_second_reminder_statuory()
            self._send_second_reminder_email_notifications_statuory(statuory_second_reminder)

    @api.model
    def create(self,vals):
            account_manager_group = self.env.ref('account.group_account_manager')
            emails = [user.email for user in account_manager_group.users if user.email]
            if emails:
                if vals.get('is_legal_notice'):
                    template = self.env.ref('project_extended.legal_notice_creation_email_template')
                    template.write({'email_to': ', '.join(emails),
                                    'subject':'Legal Notice Project Creation - %s'%(vals.get('name'))})
                    template.send_mail(self.id, force_send=True)
                elif vals.get('is_statuory_notice'):
                    template = self.env.ref('project_extended.statuory_notice_creation_email_template')
                    template.write({'email_to': ', '.join(emails),
                                    'subject':'Statutory Notice Project Creation - %s'%(vals.get('name'))})
                    template.send_mail(self.id, force_send=True)
            res = super().create(vals)
            return res

    @api.model
    def read(self, fields=None, load='_classic_read'):
        result = super(Project, self).read(fields, load)
        for record in result:
            record['is_legal_notice'] = self.env.context.get('is_legal_notice_option', False)
            record['is_statuory_notice'] = self.env.context.get('is_statuory_notice_option', False)
        return result

    def _schedule_activities_first_reminder_legal(self):
        today = fields.Date.today()
        projects = self.search([
            ('first_reminder_date', '=', today),('is_legal_notice','=',True)
        ])
        for project in projects:
            project.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="First Reminder: Legal Notice Due",
                note="The legal notice deadline is approaching. Please take action.",
                user_id=project.user_id.id,
                date_deadline=fields.Date.today()
            )

    def _schedule_activities_first_reminder_statuory(self):
        today = fields.Date.today()
        projects = self.search([
            ('first_reminder_date', '=', today),('is_statuory_notice','=',True)
        ])
        for project in projects:
            project.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="First Reminder: Statutory Notice Due",
                note="The Statutory notice deadline is approaching. Please take action.",
                user_id=project.user_id.id,
                date_deadline=fields.Date.today()
            )

    def _schedule_activities_second_reminder_legal(self):
        today = fields.Date.today()
        projects = self.search([
            ('second_reminder_date', '=', today),('is_legal_notice','=',True)
        ])
        for project in projects:
            project.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="Second Reminder: Legal Notice Due",
                note="The legal notice deadline is approaching. Please take action.",
                user_id=project.user_id.id,
                date_deadline=fields.Date.today()
            )

    def _schedule_activities_second_reminder_statuory(self):
        today = fields.Date.today()
        projects = self.search([
            ('second_reminder_date', '=', today),('is_statuory_notice','=',True)
        ])
        for project in projects:
            project.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary="Second Reminder: Statutory Notice Due",
                note="The Statutory notice deadline is approaching. Please take action.",
                user_id=project.user_id.id,
                date_deadline=fields.Date.today()
            )

    def _send_first_reminder_email_notifications_legal(self,legal_first_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in legal_first_reminder:
                template = self.env.ref('project_extended.legal_notice_first_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)

    def _send_second_reminder_email_notifications_legal(self,legal_second_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in legal_second_reminder:
                template = self.env.ref('project_extended.legal_notice_second_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)

    def _send_first_reminder_email_notifications_statuory(self,statuory_first_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in statuory_first_reminder:
                template = self.env.ref('project_extended.statuory_notice_first_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)

    def _send_second_reminder_email_notifications_statuory(self,statuory_second_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in statuory_second_reminder:
                template = self.env.ref('project_extended.statuory_notice_second_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)


CLOSED_STATES = {
    '1_done': 'Done',
    '1_canceled': 'Canceled',
}
class ProjectTask(models.Model):
    _inherit = 'project.task'

    recurrence_reminder  =fields.Integer(string='First Remainder')
    recurrence_reminder2 = fields.Integer(string='Secondary Remainder')
    recurring_start_date = fields.Date(string="Start Date")
    first_reminder_date = fields.Date(string="First Reminder Date")
    second_reminder_date = fields.Date(string="Second Reminder Date")
    task_valid_from = fields.Date(string="Task Period From",default=fields.Date.context_today)

    @api.model
    def check_expired_tasks_recurring(self):
        expired_tasks = self.search([
            ('date_deadline', '<', fields.Date.today()),
            ('stage_id.name', '!=', 'Expired'),
            ('recurring_task','=',True),
        ])
        print(expired_tasks,'ggggggggggg')
        for task in expired_tasks:
            task.stage_id = self.env['project.task.type'].search([('name', '=', 'Expired'),
                                                                  ('project_ids', 'in', task.project_id.id)]).id
            # task.action_send_status_email()

    # def action_send_status_email(self):
    #     template = self.env.ref('project_extended.email_template_status_change_task')
    #     for task in self:
    #         template.send_mail(task.id, force_send=True)

    @api.onchange('recurrence_reminder','recurrence_reminder2')
    def _onchange_dates(self):
        """
        Update reminder fields when the date_of_notice or last_date changes.
        """
        for task in self:
            if task.recurring_task:

                if task.date_deadline:
                    end_date =  task.date_deadline
                    date_str = task.date_deadline.strftime("%Y-%m-%d")
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date < fields.Date.today():
                        raise UserError(_("Kindly provide the correct date."))
                    else:
                        if task.recurrence_reminder:
                            first_reminder = task.recurrence_reminder
                            task.first_reminder_date = date - timedelta(days=first_reminder)
                        if task.recurrence_reminder2:
                            second_reminder = task.recurrence_reminder2
                            task.second_reminder_date = date - timedelta(days=second_reminder)

    def send_recurring_reminder(self):
        today = fields.Date.today()
        recurring_first_reminder = self.sudo().search([
            ('first_reminder_date', '=', today),('recurring_task','=',True)
        ])
        recurring_second_reminder = self.sudo().search([
            ('second_reminder_date', '=', today),('recurring_task','=',True)
        ])
        if recurring_first_reminder:
            self._send_first_reminder_email_notifications_recurring(recurring_first_reminder)
        if recurring_second_reminder:
            self._send_second_reminder_email_notifications_recurring(recurring_second_reminder)

    def _send_second_reminder_email_notifications_recurring(self,recurring_second_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in recurring_second_reminder:
                template = self.env.ref('project_extended.recurring_second_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)

    def _send_first_reminder_email_notifications_recurring(self,recurring_first_reminder):
        account_manager_group = self.env.ref('account.group_account_manager')
        emails = [user.email for user in account_manager_group.users if user.email]
        if emails:
            for rec in recurring_first_reminder:
                template = self.env.ref('project_extended.recurring_first_reminder_email_template')
                template.write({'email_to': ', '.join(emails)})
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True)


    def _cron_inverse_state(self):
        today = fields.Date.today()
        start_of_day = today.strftime('%Y-%m-%d 00:00:00')
        end_of_day = today.strftime('%Y-%m-%d 23:59:59')

        task_obj = self.env['project.task'].search([
            ('planned_date_begin', '>=', start_of_day),
            ('planned_date_begin', '<=', end_of_day)
        ])
        print(task_obj,'lllll')
        for task in task_obj:
            last_task_id_per_recurrence_id = task.recurrence_id._get_last_task_id_per_recurrence_id()
            if task.state in CLOSED_STATES and task.id == last_task_id_per_recurrence_id.get(task.recurrence_id.id):
                task.recurrence_id._create_next_occurrence(task)
class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'
    # def _create_next_occurrence(self, occurrence_from):
    #     self.ensure_one()
    #     if self.repeat_type == 'until' and fields.Date.today() > self.repeat_until:
    #         return
    #     # Prevent double mail_followers creation
    #     self = self.with_context(mail_create_nosubscribe=True)
    #     print("fucntion triggered")
    #     # Check if the date field in the task matches today's date
    #     if occurrence_from.recurring_start_date and occurrence_from.recurring_start_date == fields.Date.today():
    #         print(occurrence_from.recurring_start_date,"recuring date")
    #         self.env['project.task'].sudo().create(
    #             self._create_next_occurrence_values(occurrence_from)
    #         )


    def _create_next_occurrence(self, occurrence_from):
        self.ensure_one()
        self = self.with_context(mail_create_nosubscribe=True)
        create_values = self._create_next_occurrence_values(occurrence_from)
        date_deadline = create_values['date_deadline']
        planned_date_begin = create_values['planned_date_begin']
        date_str = occurrence_from.planned_date_begin.strftime("%Y-%m-%d")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if not (self.repeat_type == 'until' and date_deadline and date_deadline.date() > self.repeat_until):
            if date == fields.Date.today():
                task = self.env['project.task'].sudo().create(create_values)
                task.write({
                    'recurrence_reminder':occurrence_from.recurrence_reminder,
                    'recurrence_reminder2':occurrence_from.recurrence_reminder2
                })
