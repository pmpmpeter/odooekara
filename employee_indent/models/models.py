# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import *


class employee_indent(models.Model):
    _name = 'employee.indent'
    _description = 'Employee Indent'

    name = fields.Char(string='Employee Indent Name', required=True)
    tax_entity = fields.Char(string='Tax Entity',
                             # compute='_compute_tax_entity',
                             store=True)
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
        'hr.employee',
        string='Reporting To',
        help='Select the employee to whom this position reports.'
    )

    employment_type = fields.Many2one('hr.contract.type',string="Employment Type")

    target = fields.Integer(string='Target', required=True, help="Number of vacancies for this position.")

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
        'hr.employee',
        string='Unit Head',
        help="Select the Unit Head from available employees."
    )

    recruitment_spoc_mgr_id = fields.Many2one(
        'hr.employee',
        string='Recruitment SPOC/Mgr',
        help="Select the Recruitment SPOC/Mgr from available employees."
    )

    director_approval_id = fields.Many2one(
        'hr.employee',
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

    status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('open', 'Open'),
        ('close', 'Close')
    ], string='Status', default='draft', required=True, tracking=True)

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
            record.balance_budget =record.approved_budget - (record.budgeted_amount + record.utilized_budget)

    def action_approve(self):
        for record in self:
            record.status='waiting_approval'

    def action_open(self):
        for record in self:
            record.status='open'

    def action_close(self):
        for record in self:
            record.status='close'

    def action_reset(self):
        for record in self:
            record.status='draft'

    # @api.depends('company_id')
    # def _compute_tax_entity(self):
    #     for record in self:
    #         # Assuming we fetch the tax entity based on the user's company.
    #         record.tax_entity = record.env.user.company_id.name if record.env.user.company_id else 'Undefined'


