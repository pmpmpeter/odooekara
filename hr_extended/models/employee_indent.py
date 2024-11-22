# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import *
from datetime import datetime


class employee_indent(models.Model):
    _name = 'employee.indent'
    _description = 'Employee Indent'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    tax_entity = fields.Many2one('res.company', string='Tax Entity', default=lambda self: self.env.company)
    organization = fields.Many2one('res.company', string='Organization', default=lambda self: self.env.company)
    location = fields.Many2one(
        'res.partner', "Job Location",
        domain=lambda self: self._address_id_domain(),
        help="Select the location where the applicant will work. Addresses listed here are defined on the company's contact information.")

    department = fields.Many2one(
        'hr.department',  # The model name of the HR department
        string='Department',
        required=True,
        help="Select the department from HR departments"
    )

    grade_job_level = fields.Many2one('hr.job.levels', string='Grade/ Job Level', required=True)

    position_name = fields.Many2one('hr.position.names', string='Position Name / Designations', required=True)

    reporting_to = fields.Many2one(
        'res.users',
        string='Reporting To',
        help='Select the employee to whom this position reports.'
    )

    employment_type = fields.Many2one('hr.contract.type',string="Employment Type")

    target = fields.Integer(string='Target', required=True,default=1, help="Number of vacancies for this position.")

    is_replacement =fields.Boolean(string='Is Replacement?', default=False, copy=False, help="Indicate if this position is a replacement.")

    replacement_employee_id = fields.Many2one(
        'hr.employee',
        string='Replacement Employee Name',
        help='Select the employee being replaced if this is a replacement position.'
    )

    expected_indent_closure_date = fields.Date(
        string='Expected Indent Closure Date',
        required=True,
        help='Select the expected date for closing this indent.'
    )

    budgeting_unit = fields.Selection([
        ('ekara_capex', 'Ekara Partnership - Capex'),
        ('ekara_opex', 'Ekara Partnership - Opex'),
        ('statutory_payments', 'Statutory Payments & Other B/S Items')
    ], string='Budgeting Units', help="Select the appropriate budgeting unit.")

    is_budgeted =fields.Boolean(string='Is Budgeted?', default=False, copy=False, help="Indicate if this position is budgeted.")

    #have to add the BU/Department Total Approved Budget (dont know about that)
    start_date = fields.Date(string='Fiscal Year',default=fields.Date.today)
    end_date = fields.Date(string='End Date')

    approved_budget = fields.Monetary(
        string='BU/Department Total Approved Budget',
        currency_field='currency_id',
        help="Specify the total approved budget for the Business Unit (BU) or Department."
    )

    budgeted_amount = fields.Monetary(
        string='Budgeted Amount for Position',
        currency_field='currency_id',
        help="Specify the budgeted amount for this position."
    )

    utilized_budget = fields.Monetary(
        string='Utilized Budget',
        currency_field='currency_id',
        help="Amount already utilized from the budget for this position."
    )

    balance_budget = fields.Monetary(
        string='Balance Budget',
        compute='_compute_balance_budget',
        currency_field='currency_id',
        store=True,
        help="Remaining budget after utilization."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        help="Currency for the budget amounts."
    )

    unit_head_id = fields.Many2one(
        'res.users',
        string='Unit Head',
        help="Select the Unit Head from available employees."
    )

    recruitment_spoc_mgr_id = fields.Many2one(
        'res.users',
        string='Recruitment SPOC/Mgr',
        help="Select the Recruitment SPOC/Mgr from available employees."
    )

    director_approval_id = fields.Many2one(
        'res.users',
        string='Director Approval',
        help="Select the Director for approval."
    )

    preferences = fields.Text(
        string='Preferences',
        help="Enter any specific preferences related to the indent."
    )

    notes = fields.Text(
        string='Notes',
        help="Add any relevant notes or comments here."
    )

    survey_id = fields.Many2one(
        'survey.survey', "Interview Form",
        help="Choose a form for this job position")

    request_date = fields.Date(copy=False)
    submit_date = fields.Date(readonly=True,copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('open', 'Open'),
        ('job_created', 'Job Position Created')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    def action_open_related_jobs(self):
        self.ensure_one()  # Ensure it's called for one record
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Jobs',
            'view_mode': 'tree,form',
            'res_model': 'hr.job',
            'domain': [('name', '=', self.position_name.name)],
            'target': 'current',
        }

    def _address_id_domain(self):
        return ['|', '&', '&', ('type', '!=', 'contact'), ('type', '!=', 'private'),
                ('id', 'in', self.sudo().env.companies.partner_id.child_ids.ids),
                ('id', 'in', self.sudo().env.companies.partner_id.ids)]

    @api.constrains('budgeted_amount', 'utilized_budget', 'approved_budget')
    def _check_budget(self):
        for record in self:
            total_spent = record.budgeted_amount + record.utilized_budget
            if total_spent > record.approved_budget:
                raise ValidationError("The total budgeted and utilized amount exceeds the approved budget!")

    @api.depends('approved_budget', 'budgeted_amount', 'utilized_budget')
    def _compute_balance_budget(self):
        for record in self:
            record.balance_budget = record.approved_budget - (record.budgeted_amount + record.utilized_budget)

    def action_send_mail(self):
        template = self.env.ref('hr_extended.job_creation_email_template')
        for rec in self:
            if rec.director_approval_id.email:
                print("inside",rec.director_approval_id.email)
                template.send_mail(rec.id, force_send=True)
            else:
                print("else",rec.director_approval_id.email)

    def action_approve(self):
        approval_type_model = self.env['multi.approval.type']
        approval_type_line_model = self.env['multi.approval.type.line']

        for record in self:
            record.state = 'waiting_approval'
            self.submit_date = fields.Datetime.now()

            approval_type = approval_type_model.search([
                ('model_id', '=', 'employee.indent'),
                ('domain', '=', '[("state", "=", "waiting_approval")]')
            ], limit=1)

            if not approval_type:
                raise ValueError("No matching approval type found for the Employee Indent.")

            lines = approval_type_line_model.search([('type_id', '=', approval_type.id)])

            if len(lines) != 2:
                raise ValueError(
                    "There must be exactly two records in 'multi.approval.type.line' with the same 'type_id'.")

            for index, line in enumerate(lines):
                line.write({
                    'user_id': [(6, 0, [])]
                })
                if index == 0:
                    unit_head_user = record.unit_head_id.id
                    recruitment_spoc_mgr_user = record.recruitment_spoc_mgr_id.id

                    if unit_head_user and recruitment_spoc_mgr_user:
                        line.write({
                            'user_id': [(4, unit_head_user), (4, recruitment_spoc_mgr_user)]
                        })
                    else:
                        raise ValueError("Unit Head or Recruitment SPOC Manager does not have a corresponding user.")
                    print(f"Line ID: {line.id}, Updated User IDs: {line.user_id}")

                elif index == 1:
                    director_approval_user = record.director_approval_id.id

                    if director_approval_user:
                        line.write({
                            'user_id': [(4, director_approval_user)]
                        })
                    else:
                        raise ValueError("Director Approval does not have a corresponding user.")
                    print(f"Line ID: {line.id}, Updated User IDs: {line.user_id}")


    def action_open(self):
        for record in self:
            record.state='open'

    def action_create_job_position(self):
        hr_job_model = self.env['hr.job']
        for record in self:
            record.state = 'job_created'
            existing_job = hr_job_model.search([('name', '=', record.position_name.name)], limit=1)

            if existing_job:
                existing_job.write({
                    'no_of_recruitment': existing_job.no_of_recruitment + record.target,
                    'website_published': True,
                })
                print(f"Updated HR Job: {existing_job.name}, New Recruitment Count: {existing_job.no_of_recruitment}")
            else:
                hr_job_model.create({
                    'name': record.position_name.name,
                    'department_id': record.department.id,
                    'address_id': record.location.id,
                    'contract_type_id': record.employment_type.id,
                    'company_id': record.organization.id,
                    'no_of_recruitment': record.target,
                    'user_id': record.reporting_to.id,
                    'website_published': True,
                })
                print(f"Created HR Job: {record.position_name.name}")

    def action_reset(self):
        for record in self:
            record.state='draft'

    def get_survey_url(self):
        """
        Generates the start URL for the survey associated with this employee indent,
        including the survey access token if available.
        """
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if not self.survey_id:
            raise ValueError("No survey associated with this employee indent.")

        survey_token = self.survey_id.access_token
        survey_url = f"{base_url}/survey/start/"
        if survey_token:
            survey_url += f"{survey_token}"
            return survey_url
