from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from datetime import datetime,date,timedelta
import calendar


class CashRequirementReport(models.Model):
    _name = 'cash.requirement.report'
    _description = 'Cash Requirement Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name",readonly=1, copy=False)
    state = fields.Selection([
        ('draft', 'New'),
        ('to approve','To Approve'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)
    requested_date = fields.Date(string="Request Date", readonly=True, tracking=True, copy=False, default=fields.Datetime.now)
    requested_by = fields.Many2one('res.users',string="Requested By", attachment=True, copy=False, default=lambda self: self.env.user)
    journal_bank  =fields.Many2many('account.journal',string='Bank',copy=False)
    cash_requirement_lines = fields.One2many('cash.requirement.lines','cash_req_id',string='Lines',copy=False)
    available_balance  =fields.Float(string='Available Amount Balance',copy=False)
    company_id = fields.Many2one('res.company',string ='Company', default=lambda self: self.env.company)
    minimum_balance = fields.Float(string='Minimum Balance',copy=False)
    amount_total = fields.Float(string='Amount Total', copy=False)
    total_fund_required = fields.Float(string='Total Fund Required', copy=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string='End Date')
    revision_reason = fields.Text(string="Revision Reasons", readonly=True, default="", copy=False)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    active = fields.Boolean(string='Active')

    @api.depends('journal_bank')
    def compute_available_balance(self):
        if self.journal_bank:
            total_val = 0
            for rec in self.journal_bank.ids:
                bank_balance = 0
                if rec:
                    journal = self.env['account.journal'].sudo().search([('id', '=', rec)])
                    query_result = journal._get_journal_dashboard_bank_running_balance()
                    self.has_statement_lines, bank_balance = query_result.get(journal.id)
                    total_val += bank_balance
                else:
                    self.available_balance = 0
            self.available_balance = total_val
        else:
            self.available_balance = 0

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)

        today = date.today()
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month.replace(day=1) - timedelta(days=1)
        defaults.update({
            'start_date': start_date,
            'end_date': end_date,
        })

        return defaults

    # def action_open_crr_report_consolidation(self):
    #     self.ensure_one()
    #     action = {
    #         'type': 'ir.actions.act_window',
    #         'name': 'CRR Report',
    #         'view_mode': 'tree',
    #         'res_model': 'cash.requirement.lines',
    #         # 'context': {'group_by': ['version_name']},
    #     }
    #     return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('cash.requirement.report')
            vals['active']  =True
        return super().create(vals_list)

    def button_done(self):
        if self.requested_by:
            self.activity_schedule(
                activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                summary=f"Cash Requirement Request - {self.name} ",
                note=f"The record {self.name} has been marked as done. Please take action if needed.",
                user_id=self.requested_by.id,
            )
        self.state = 'done'

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You can able to delete Draft records only')
        return super(CashRequirementReport, self).unlink()

    def reset_to_draft(self):
        self.state = 'draft'
        self.x_has_request_approval = False
        self.x_review_result = ''

    def button_cancel(self):
        self.state = 'cancel'

    # @api.onchange('journal_bank')
    # def onchange_journal_bank_test(self):
    #     if self.journal_bank:
    #         closing_balance = 0
    #         query_result = self.env['account.journal'].sudo()._get_journal_dashboard_bank_running_balance()
    #         for journal in self.journal_bank:
    #             print(journal, 'ffffffffffffff')
    #             journal.has_statement_lines, journal.current_statement_balance = query_result.get(journal.id)
    #
    #         for rec in self.journal_bank:
    #             query = """
    #                         select sum(balance) as balance FROM account_move_line aml
    #                         join account_move am on am.id=aml.move_id
    #                         where am.state='posted' and aml.account_id=%s and aml.date <= %s and aml.company_id = %s
    #                         """
    #             params = tuple(rec.default_account_id.ids), datetime.today().strftime('%Y-%m-%d'), self.company_id.id
    #             data_get8 = self.env.cr.execute(query, params)
    #             lines8 = self.env.cr.dictfetchall()
    #             if (lines8[0].get('balance') != None):
    #                 closing_balance += lines8[0].get('balance') or 0
    #         for record in self:
    #             record.available_balance = closing_balance
    #             if self.available_balance > 0:
    #                 if self.amount_total - self.available_balance > 0:
    #                      print(round(self.amount_total - self.available_balance))
    #                      self.total_fund_required = round(self.amount_total - self.available_balance)
    #                 else:
    #                      self.total_fund_required = 0
    #             else:
    #                 self.total_fund_required = round(self.amount_total)

    @api.onchange('cash_requirement_lines','minimum_balance')
    def onchange_minimum_balance(self):
            total = 0
            min_bal =0
            for rec in self.cash_requirement_lines:
                total = total + rec.amount
            self.amount_total = total
            if self.minimum_balance:
                min_bal = self.minimum_balance
            self.amount_total = total + min_bal
            if self.available_balance > 0:
                if self.amount_total - self.available_balance > 0:
                    self.total_fund_required = round(self.amount_total - self.available_balance)
                else:
                    self.total_fund_required = 0
            else:
                self.total_fund_required = round(self.amount_total)

    # @api.onchange('minimum_balance')
    # def onchange_min_bal(self):
    #     print('hf')


class CashRequirementLines(models.Model):
    _name = 'cash.requirement.lines'
    _description = 'Cash Requirement Lines'

    cash_req_id = fields.Many2one('cash.requirement.report', string='Cash Requirement')
    cash_account = fields.Many2one('account.account',string='Account', copy=False)
    partner_id = fields.Many2one('res.partner',string='Partner' ,copy=False)
    requirement_month = fields.Date(string='Date',copy=False, default=fields.Datetime.now)
    requirement_months = fields.Selection(
        selection=[('01', 'January'), ('02', 'February'), ('03', 'March'),
                   ('04', 'April'), ('05', 'May'), ('06', 'June'),
                   ('07', 'July'), ('08', 'August'), ('09', 'September'),
                   ('10', 'October'), ('11', 'November'), ('12', 'December')],
        string="Month",
    )
    amount = fields.Float('Amount', copy=False, tracking=True)
    remarks = fields.Char('Remarks')
    company_id = fields.Many2one('res.company',string ='Company', related='cash_req_id.company_id', store=True)
