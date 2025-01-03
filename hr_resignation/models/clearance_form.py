from odoo import models, fields, api, _
from odoo.exceptions import *
from odoo.exceptions import ValidationError, UserError


class ClearanceForm(models.Model):
    _name = 'clearance.form'
    _description = 'Clearance Form'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee',string='Employee Name', required=True, tracking=True)
    designation_id = fields.Many2one('hr.job',string="Designation",tracking=True)
    date_of_joining = fields.Date(string='Date of Joining', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    last_working_day = fields.Date(string='Last Working Day', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ], string='State', default='draft', tracking=True)
    asset_ids = fields.One2many('clearance.asset', 'clearance_form_id', string='Assets')
    function_head_ids = fields.One2many('clearance.function.head', 'clearance_form_id',
                                        string='Clearance by Function Heads')

    @api.onchange('employee_id')
    def _compute_start_date(self):
        for record in self:
            if record.employee_id:
                record.designation_id = record.employee_id.job_id
                record.department_id = record.employee_id.department_id
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id)],
                    order='date_start asc',
                    limit=1
                )
                if contract and contract.date_start:
                    record.date_of_joining = contract.date_start
                else:
                    raise ValidationError(
                        "No contract found for the selected employee. Please ensure the employee has a valid contract."
                    )
            else:
                record.date_of_joining = False

    def clearance_form_submit(self):
        for record in self:
            record.state = 'submitted'

    def clearance_form_complete(self):
        for record in self:
            record.state = 'completed'

class ClearanceAsset(models.Model):
    _name = 'clearance.asset'
    _description = 'Clearance Asset'

    asset_type = fields.Selection([
        ('laptop', 'Laptop'),
        ('sim_card', 'SIM Card'),
        ('mobile_handset', 'Mobile Handset'),
        ('ipad', 'iPad'),
        ('data_card', 'Data Card/Dongle'),
        ('access_card', 'Access Card'),
        ('photo_id', 'Photo ID'),
        ('system', 'System'),
        ('email_gpm', 'Email & GPM - ID/PW'),
        ('library_books', 'Library Books'),
    ], string='Asset', required=True)
    returned_to = fields.Many2one('hr.employee', string='Returned To', required=True)
    remarks = fields.Text(string='Remarks')
    signature = fields.Binary(string='Signature')
    clearance_form_id = fields.Many2one('clearance.form', string='Clearance Form', required=True)

class ClearanceFunctionHead(models.Model):
    _name = 'clearance.function.head'
    _description = 'Clearance by Function Head'

    function = fields.Selection([
        ('business_head', 'Business Head'),
        ('reporting_manager', 'Reporting Manager'),
        ('admin', 'Admin'),
        ('it', 'IT'),
        ('accounts', 'Accounts'),
        ('corporate_hr', 'Corporate HR'),
    ], string='Function', required=True)

    remarks = fields.Text(string='Remarks')
    signature = fields.Binary(string='Signature')

    clearance_form_id = fields.Many2one('clearance.form', string='Clearance Form', required=True)
