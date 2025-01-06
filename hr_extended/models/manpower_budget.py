from odoo import models, fields, api

class ManpowerBudget(models.Model):
    _name = 'manpower.budget'
    _description = 'Manpower Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter functionality
    _rec_name = 'tax_entity_id'


    create_date = fields.Datetime(string="Creation Date", readonly=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, readonly=True)
    tax_entity_id = fields.Many2one('res.company', string="Tax Entity")
    category_id = fields.Many2one('hr.contract.type', string="Category")
    manpower_request_type = fields.Selection([
        ('existing', 'Existing'),
        ('additional', 'Additional')
    ], string="Type of Manpower Request")
    business_unit_id = fields.Many2one('business.units', string="Business Unit")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Role/Designation")
    job_level_id = fields.Many2one('hr.job.levels', string="Job Level/Grade")
    justification = fields.Char(string="Justification")
    ctc_month = fields.Float(string="CTC/Month")
    employee_monthly_ids = fields.One2many(
        'manpower.budget.employee.monthly',
        'budget_id',
        string="Employee Count by Month",
        default=lambda self: self._default_employee_monthly_ids(),
        tracking=True
    )

    @api.model
    def _default_employee_monthly_ids(self):
        """Generate default employee_monthly_ids for financial year months."""
        financial_year_months = [
            ('04', 'April'), ('05', 'May'), ('06', 'June'),
            ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December'),
            ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ]
        current_year = fields.Date.today().year
        next_year = current_year + 1

        employee_lines = []
        for month_code, month_name in financial_year_months:
            year = current_year if int(month_code) >= 4 else next_year
            employee_lines.append({
                'month': month_code,
                'employee_count': 0,  # Default employee count
            })
        return [(0, 0, line) for line in employee_lines]




class ManpowerBudgetEmployeeMonthly(models.Model):
    _name = 'manpower.budget.employee.monthly'
    _description = 'Manpower Budget Employee Monthly Count'

    budget_id = fields.Many2one('manpower.budget', string="Manpower Budget")
    month = fields.Selection([
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
    ], string="Month", required=True)
    employee_count = fields.Integer(string="Employee Count", required=True)