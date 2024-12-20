from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    document_type_id = fields.Many2one('document.type', string="Document Type",
                                       help="Select the type of document for this project.")
    validity_start_date = fields.Date(string="Validity Start Date")
    validity_end_date = fields.Date(string="Validity End Date")
    is_document_validity_management = fields.Boolean(string="Is Document Validity Management", default=False)

    def _create_default_task_stages(self):
        context = self.env.context
        stage_names = []
        if context.get('is_legal_notice_option') or context.get('is_statuory_notice_option'):
            stage_names = ['Draft', 'In Progress', 'Review', 'Done']
        if context.get('default_is_document_validity_management'):
            stage_names = ['Draft', 'To Renew', 'Active', 'Expired']
        if stage_names:
            for name in stage_names:
                stage = self.env['project.task.type'].search([('name', '=', name),('project_ids', 'in',self._origin.id)], limit=1)
                if not stage:
                    stage = self.env['project.task.type'].create({
                        'name': name,
                        'sequence': stage_names.index(name),
                        'fold': name in ['Expired'],
                    })
                if self.id not in stage.project_ids.ids:
                    stage.project_ids = [(4, self._origin.id)]

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        projects._create_default_task_stages()
        return projects

    @api.onchange('document_type_id', 'validity_start_date')
    def _onchange_document_type(self):
        if not self.document_type_id:
            self.validity_end_date = self.validity_start_date = False
        if self.document_type_id and self.validity_start_date:
            self.validity_end_date = self.validity_start_date + timedelta(
                days=self.document_type_id.default_validity_period
            )

    @api.constrains('validity_start_date', 'validity_end_date')
    def _check_date_order(self):
        for record in self:
            if record.validity_end_date < record.validity_start_date:
                raise UserError("The end date cannot be earlier than the start date.")
            if record.validity_start_date > record.validity_end_date:
                raise UserError("The start date cannot be later than the end date.")

class ProjectTask(models.Model):
    _inherit = 'project.task'

    document_type_id = fields.Many2one('document.type', string="Document Type",
                                       help="Select the type of document for this project.")
    validity_start_date = fields.Date(string="Validity Start Date")
    validity_end_date = fields.Date(string="Validity End Date")
    stage_id = fields.Many2one('project.task.type', string="Stage", required=True)
    is_document_validity_management = fields.Boolean(string="Is Document Validity Management", default=False)

    @api.model
    def create(self,vals):
        project_id = self.project_id.browse(vals.get('project_id'))
        
        if project_id.is_document_validity_management:
            vals['is_document_validity_management'] = True
            vals['document_type_id'] = project_id.document_type_id.id or False
            if not vals.get('validity_start_date'):
                vals['validity_start_date'] = project_id.validity_start_date
            if not vals.get('validity_end_date'):
                vals['validity_end_date'] = project_id.validity_end_date
        res = super().create(vals)
        return res

    @api.onchange('document_type_id', 'validity_start_date')
    def _onchange_document_type(self):
        if not self.document_type_id:
            self.validity_end_date = self.validity_start_date = False
        if self.document_type_id and self.validity_start_date:
            self.validity_end_date = self.validity_start_date + timedelta(
                days=self.document_type_id.default_validity_period
            )

    @api.constrains('validity_start_date', 'validity_end_date')
    def _check_date_order(self):
        for record in self:
            if record.validity_end_date < record.validity_start_date:
                raise UserError("The end date cannot be earlier than the start date.")
            if record.validity_start_date > record.validity_end_date:
                raise UserError("The start date cannot be later than the end date.")

    def action_send_status_email(self):
        template = self.env.ref('document_validity_management.email_template_status_change')
        for task in self:
            template.send_mail(task.id, force_send=True)

    def action_send_status_email_salesperson(self):
        template = self.env.ref('document_validity_management.email_template_notify_person')
        for task in self:
            template.send_mail(task.id, force_send=True)

    @api.model
    def check_active_tasks(self):
        active_tasks = self.search([
            ('validity_start_date', '<=', fields.Date.today()),
            ('validity_end_date', '>=', fields.Date.today()),
            ('stage_id.name', '!=', 'Active'),
            ('stage_id.name', '!=', 'Expired'),
        ])
        for task in active_tasks:
            task.stage_id = self.env['project.task.type'].search([('name', '=', 'Active'),('project_ids', 'in',task.project_id.id)]).id
            task.action_send_status_email()
            task.action_send_status_email_salesperson()

    @api.model
    def check_expired_tasks(self):
        expired_tasks = self.search([
            ('validity_end_date', '<', fields.Date.today()),
            ('stage_id.name', '!=', 'Expired'),
        ])
        for task in expired_tasks:
            task.stage_id = self.env['project.task.type'].search([('name', '=', 'Expired'),
                                                                  ('project_ids', 'in',task.project_id.id)]).id
            if task.validity_start_date and task.validity_end_date:
                date_diff = task.validity_end_date - task.validity_start_date
                
                # Set new start and end dates
                new_start_date = task.validity_end_date + timedelta(days=1)  # Start next day after old end date
                new_end_date = new_start_date + date_diff  # Add the same duration
            self.create({
                'name': f"{task.name}",
                'project_id': task.project_id.id,
                'document_type_id': task.document_type_id.id,
                'partner_id': task.project_id.partner_id.id if task.project_id.partner_id else False,
                'user_ids': [(6, 0, task.user_ids.ids)],
                'stage_id': self.env['project.task.type'].search([('name', '=', 'Draft'),
                                                                  ('project_ids', 'in', task.project_id.id)]).id,
                'validity_start_date': new_start_date,
                'validity_end_date': new_end_date,
            })
            task.action_send_status_email()
            task.action_send_status_email_salesperson()
