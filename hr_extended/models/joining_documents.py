# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import *
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class JoiningDocuments(models.Model):
    _name = 'joining.documents'
    _description = 'Joining Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False, required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee Name", copy=False, required=True)
    department_id = fields.Many2one('hr.department', string="Department", copy=False)
    job_position_id = fields.Many2one('hr.job', string="Job Position", copy=False)
    joining_date = fields.Date(string="Joining Date", copy=False)
    reference_file = fields.Binary(string='Reference File', copy=False)
    reference_filename = fields.Char(string='Reference Filename', copy=False)
    submitted_file = fields.Binary(string='Submitted File', attachment="True", copy=False)
    submitted_filename = fields.Char(string='Submitted Filename', copy=False)
    subject = fields.Html(string="Subject")
    document_type = fields.Selection(
        [('it_declaration', 'IT Declaration'),  #
         ('ebp_claim', 'EBP Claim Form'),  #
         ('app_order_form', 'Appointment Order Form'),
         ('bgv', 'BGV Email Template'),  #
         ('code_of_conduct', 'CODE OF CONDUCT'),
         ('consent', 'Consent Form'),
         ('criminal_case', 'Criminal Case'),
         ('emp_verifi_form', 'Employee Verification Form'),
         ('epf', 'EPF Form 11 Declaration Doc'),  #
         ('ex_media_comm', 'External Media Communication - Declaration (IIM)'),
         ('gmc', 'GMC and GPA Details'),  #
         ('joining_form', 'Joining form'),  #
         ('nda', 'NDA (Intellectual Property) Form'),  #
         ('pf_nomination', 'PF Nomination Form'),
         ('emp_ref_check', 'Pre - Employment Reference Check Form'),  # check we have separate module for this
         ('she_nda', 'SHE NDA- 2022 updated Form')],
        string="Document Type")

    company_id = fields.Many2one('res.company', required=True)
    contact_id = fields.Many2one('res.partner', 'Contact', copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        # ('mail_sent','Mail Sent'),
        ('waiting_confirmation', 'Waiting Confirmation'),
        ('done', 'Done'),
        ('reject', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    def action_submit(self):
        for record in self:
            record.state = 'waiting_confirmation'

    def action_confirm(self):
        for record in self:
            record.state = 'done'

    def action_reset(self):
        for record in self:
            record.state = 'draft'

    def action_reject(self):
        for record in self:
            record.state = 'reject'

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only records in the 'Draft' state can be deleted."))
        return super(JoiningDocuments, self).unlink()

    def action_send_by_email(self):
        self.ensure_one()
        for record in self:
            template_id = self.env.ref('hr_extended.mail_template_bgv',
                                       raise_if_not_found=False)
            if not template_id:
                raise UserError(
                    _("The email template for sending Background Verfication does not exist."))

            recipient_email = record.contact_id.email
            if not recipient_email:
                raise UserError(_("The recipient does not have a valid email address."))

            current_user_email = record.env.user.email
            if not current_user_email:
                raise UserError(_("The current user does not have a valid email address."))

            attachment_ids = []
            if record.submitted_file:
                attachment = self.env['ir.attachment'].create({
                    'name': 'Submitted File',
                    'type': 'binary',
                    'datas': record.submitted_file,
                    'mimetype': 'application/octet-stream',
                    'res_model': 'joining.documents',
                    'res_id': record.id,
                })

                attachment_ids = [(4, attachment.id)]

            template_id.send_mail(record.id, force_send=True, email_values={'attachment_ids': attachment_ids})

            # record.write({'state': 'mail_sent'})

    def action_print_document(self):
        self.ensure_one()
        if not self.document_type:
            raise UserError("Please select a Document Type before printing.")

        if self.document_type == 'she_nda':
            return self._print_she_nda()

        elif self.document_type == 'app_order_form':
            return self._print_app_order_form()

        elif self.document_type == 'code_of_conduct':
            return self._print_code_of_conduct()

        elif self.document_type == 'consent':
            return self._print_consent()

        elif self.document_type == 'criminal_case':
            return self._print_criminal_case()

        elif self.document_type == 'emp_verifi_form':
            return self._print_emp_verifi_form()

        elif self.document_type == 'ex_media_comm':
            return self._print_ex_media_comm()

        elif self.document_type == 'pf_nomination':
            return self._print_pf_nomination()
        else:
            raise UserError(f"Printing for {self.document_type} is not implemented.")

    def _print_she_nda(self):
        return self.env.ref('hr_extended.nda_form_template').report_action(self)

    def _print_app_order_form(self):
        return self.env.ref('hr_extended.appointment_order_form_template').report_action(self)

    def _print_code_of_conduct(self):
        return self.env.ref('hr_extended.code_of_conduct_template').report_action(self)

    def _print_consent(self):
        return self.env.ref('hr_extended.consent_form_template').report_action(self)

    def _print_criminal_case(self):
        return self.env.ref('hr_extended.criminal_case_form_template').report_action(self)

    def _print_emp_verifi_form(self):
        return self.env.ref('hr_extended.employee_verification_form_template').report_action(self)

    def _print_ex_media_comm(self):
        return self.env.ref('hr_extended.media_declare_form_template').report_action(self)

    def _print_pf_nomination(self):
        return self.env.ref('hr_extended.report_nomination_form_template').report_action(self)