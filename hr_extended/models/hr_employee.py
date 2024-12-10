from odoo import models, fields, api, _
from odoo.exceptions import *
from odoo.exceptions import ValidationError, UserError


class HrEmployeeSmartButton(models.Model):
    _inherit = "hr.employee"

    kra_record_ids = fields.Many2many(
        'employee.kra',
        compute='_compute_kra_records',
        string='KRA Records',
        copy=False
    )
    kra_record_count = fields.Integer(
        "KRA Record Count",
        compute='_compute_kra_records',
        default=0,
        copy=False
    )

    joining_documents_ids = fields.Many2many(
        'joining.documents',
        compute='_compute_joining_document_records',
        string='KRA Records',
        copy=False
    )
    joining_documents_count = fields.Integer(
        "Joining Documents",
        compute='_compute_joining_document_records',
        default=0,
        copy=False
    )
    project_ids = fields.Many2many(
        'project.task',
        compute='_compute_project_records',
        string='Project',
        copy=False
    )
    project_count = fields.Integer(
        "Project",
        compute='_compute_project_records',
        default=0,
        copy=False
    )

    def _compute_project_records(self):
        for employee in self:
            user = employee.user_id
            if user:
                project_records = self.env['project.task'].sudo().search([('user_ids', 'in', user.id)])
                employee.project_ids = project_records
                employee.project_count = len(project_records)
            else:
                employee.project_ids = False
                employee.project_count = 0

    def _compute_joining_document_records(self):
        for employee in self:
            kra_records = self.env['joining.documents'].sudo().search([('employee_id', '=', employee.id)])
            employee.joining_documents_ids = kra_records
            employee.joining_documents_count = len(kra_records)

    def _compute_kra_records(self):
        for employee in self:
            kra_records = self.env['employee.kra'].sudo().search([('employee_id', '=', employee.id)])
            employee.kra_record_ids = kra_records
            employee.kra_record_count = len(kra_records)

    def action_open_kra_records(self):
        action = self.env.ref('hr_extended.action_view_employee_kra')
        result = action.sudo().read()[0]
        result.pop('id', None)

        kra_records = self.env['employee.kra'].sudo().search([('employee_id', '=', self.id)])
        if len(kra_records) > 1:
            result['domain'] = [('id', 'in', kra_records.ids)]
        elif len(kra_records) == 1:
            res = self.env.ref('hr_extended.view_employee_kra_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = kra_records.ids[0]

        return result

    def action_get_joining_documents(self):
        self.ensure_one()
        return {
            'name': 'Joining Documents',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'joining.documents',
            'domain': [('employee_id', '=', self.id)],
            'target': 'current',
        }

    def action_get_project_task(self):
        self.ensure_one()
        user = self.user_id
        if not user:
            return {
                'type': 'ir.actions.act_window_close'
            }
        return {
            'name': 'Project',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('user_ids', 'in', user.id)],
            'target': 'current',
        }

    def action_send_appointment_letter_emp_mail(self):
        template = self.env.ref('hr_extended.mail_appointment_letter_employee')
        for rec in self:
            recipient_email = rec.private_email
            if not recipient_email:
                raise UserError(_("The recipient does not have a valid email address."))

            template.send_mail(rec.id, force_send=True)
