from odoo import models, fields, api

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
