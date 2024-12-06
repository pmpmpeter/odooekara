# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import *
from datetime import datetime


class JoiningDocuments(models.Model):
    _name = 'joining.documents'
    _description = 'Joining Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False, required = True)
    employee_id = fields.Many2one('hr.employee', string="Employee Name", copy=False, required=True)
    department_id = fields.Many2one('hr.department', string="Department", copy=False)
    job_position_id = fields.Many2one('hr.job', string="Job Position", copy=False)
    joining_date = fields.Date(string="Joining Date", copy=False)
    reference_file = fields.Binary(string='Reference File', tracking=True, copy=False)
    submitted_file = fields.Binary(string='Submitted File', tracking=True, copy=False)
    subject = fields.Html(string="Subject")
    document_type = fields.Selection(
        [('it_declaration', 'IT Declaration'),
         ('ebp_claim', 'EBP Claim Form'),
         ('app_order_form', 'Appointment Order Form'),
         ('bgv', 'BGV Email Template'),
         ('code_of_conduct', 'CODE OF CONDUCT'),
         ('consent', 'Consent Form'),
         ('criminal_case', 'Criminal Case'),
         ('emp_verifi_form', 'Employee Verification Form'),
         ('epf', 'EPF Form 11 Declaration Doc'),
         ('ex_media_comm', 'External Media Communication - Declaration (IIM)'),
         ('gmc', 'GMC and GPA Details'),
         ('joining_form', 'Joining form'),
         ('nda', 'NDA (Intellectual Property) Form'),
         ('pf_nomination', 'PF Nomination Form'),
         ('emp_ref_check', 'Pre - Employment Reference Check Form'),
         ('she_nda', 'SHE NDA- 2022 updated Form')],
        string="Document Type")

    company_id = fields.Many2one('res.company', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_confirmation', 'Waiting Confirmation'),
        ('done', 'Done'),
        ('reject', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    def action_submit(self):
        for record in self:
            record.state='waiting_confirmation'

    def action_confirm(self):
        for record in self:
            record.state='done'

    def action_reset(self):
        for record in self:
            record.state='draft'

    def action_reject(self):
        for record in self:
            record.state='reject'

    # def action_print_document(self):
    #     self.ensure_one()
    #     if not self.document_type:
    #         raise UserError("Please select a Document Type before printing.")
    #
    #     if self.document_type == 'it_declaration':
    #         return self._print_it_declaration()
    #     else:
    #         raise UserError(f"Printing for {self.document_type} is not implemented.")
    #
    # def _print_it_declaration(self):
    #     return self.env.ref('your_module_name.report_it_declaration').report_action(self)
