from odoo import api, fields, models, _, Command, tools
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
import re
import pdb
import datetime
from datetime import date, timedelta, datetime

class RecruitmentInvitation(models.Model):
    _name = 'recruitment.invitation.letter.config'
    _description = "Recruitment Invitation Configuration"

    name = fields.Html(string="Subject")
    active = fields.Boolean('Active', default=True, readonly=True, copy=False)

class ApplicantInvitation(models.Model):
    _name = "applicant.invitation.letter"
    _description = "Applicant Invitation Letter"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'id desc'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.job.nvitation.letter') or _('New')
        return super().create(vals_list)

    def _get_default_subject(self):
        subject_id = self.env['recruitment.invitation.letter.config'].sudo().search([], limit=1)
        return subject_id.name if subject_id else False

    name = fields.Char('Reference', required=True, index='trigram', copy=False, default='New', readonly=True)
    applicant_id = fields.Many2one('hr.applicant', 'Applicant', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', readonly=False)
    job_id = fields.Many2one('hr.job', 'Job Position', readonly=True, related='applicant_id.job_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, related='applicant_id.company_id', store=True)
    active = fields.Boolean('Active', default=True)
    invitation_date = fields.Date("Date", default=fields.Datetime.now)
    state = fields.Selection([
        ('draft','Draft'),('sent','Sent'),('active','Accepted'),('expired','Expired'),('cancel','Cancelled')
        ],default='draft', tracking=1, string='Status', readonly=True, copy=False)
    letter_subject = fields.Html(string="Subject", default=_get_default_subject)

    # @api.model
    # def get_views(self, views, options=None):
    #     res = super().get_views(views, options)
    #     if options and options.get('toolbar'):
    #         company_id = self.env.company
    #         get_print_values = []
    #         for view_data in res['views'].values():
    #             print_data_list = view_data.get('toolbar', {}).get('print')
    #             if print_data_list:
    #                 if company_id.company_code == 'GENI':
    #                     get_print_values.append(
    #                         self.env.ref('res_partner_extended.fsvp_letter_geni_report_format').id)
    #                     get_print_values.append(
    #                         self.env.ref('res_partner_extended.fsvp_letter_customer_geni_report_format').id)

    #                 view_data['toolbar']['print'] = [print_data for print_data in print_data_list if
    #                                                  print_data['id'] in get_print_values]
    #     return res


    # def get_subject_data(self, subject, lines, partner_id):
    #     product = ', '.join(map(lambda x: x.name, lines))        
    #     if subject and "[Ingredient(s)]" in subject:
    #         subject_new = subject.replace("[Ingredient(s)]", product)
    #         return subject_new

    # def get_assurance_data(self, subject, lines, partner_id):
    #     product = ', '.join(map(lambda x: x.name, lines))
    #     if subject and "[Ingredient(s)]" in subject and "[Company]" in subject:
    #         subject_new = subject.replace("[Ingredient(s)]", product)
    #         final_sub = subject_new.replace("[Company]", partner_id.name)
    #         return final_sub

    # def get_receiver_assurance_data(self, subject, partner_id):
    #     child_contacts = partner_id.child_ids.filtered(lambda l: l.type == 'contact')
    #     if not isinstance(subject, str):
    #         subject = ""
    #     if child_contacts:
    #         contact_name = child_contacts[0].name
    #     else:
    #         contact_name = partner_id.name
    #     if "[customer name]" in subject:
    #         subject_new = subject.replace("[customer name]", contact_name)
    #         return subject_new
    #     return subject

    # def action_draft(self):
    #     for fsvp in self:
    #         fsvp.write({
    #             'state': 'draft',
    #             'active': False,
    #         })

    # def action_expiry(self):
    #     for fsvp in self:
    #         fsvp.write({
    #             'state': 'expired',
    #             'active': False,
    #         })

    # def _update_all_fsvp_status(self):
    #     domain = [('state', '=', 'active'),('end_date', '<', datetime.today())]
    #     active_fsvp_ids = self.sudo().search(domain)
    #     # pdb.set_trace()
    #     for fsvp in active_fsvp_ids:
    #         fsvp.sudo().action_expiry()

    def action_draft(self):
        for record in self.filtered(lambda s: s.state not in ['draft']):
            record.write({'state': 'draft'})

    def action_set_as_accepted(self):
        for record in self.filtered(lambda s: s.state in ['sent']):
            record.write({'state': 'active'})
            first_level_stage = self.env['hr.recruitment.stage'].search([('stage', '=', 'first_level')], limit=1)
            if first_level_stage:
                record.applicant_id.stage_id = first_level_stage.id
            else:
                raise UserError("First Level Interview stage not found! Please create one in Recruitment stages.")   

    def action_cancel(self):
        for record in self.filtered(lambda s: s.state in ['sent']):
            record.write({'state': 'cancel'})

    def action_send_by_email(self):       
        self.ensure_one()
        for record in self:
            template_id = self.env.ref('hr_extended.recruitement_first_invitiation_email_template', raise_if_not_found=False)
            if not template_id:
                raise UserError(_("The email template for sending First Invitation letter for Recruitment does not exist."))
            recipient_email = record.applicant_id.email_from
            if not recipient_email:
                raise UserError(_("The recipient does not have a valid email address."))
            current_user_email = record.env.user.email
            if not current_user_email:
                raise UserError(_("The current user does not have a valid email address."))
            template_id.with_context(
                    email_to=record.applicant_id.email_from
                ).send_mail(
                    record.id, force_send=True
                )
            record.write({'state': 'sent'})
