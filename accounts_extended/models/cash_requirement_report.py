from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from datetime import datetime


class CashRequirementReport(models.Model):
    _name = 'cash.requirement.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name",readonly=1, copy=False)
    state = fields.Selection([
        ('draft', 'New'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)
    requested_date = fields.Date(string="Request Date", readonly=True, tracking=True, copy=False, default=fields.Datetime.now)
    requested_by = fields.Many2one('res.users',string="Requested By", attachment=True, copy=False, default=lambda self: self.env.user)
    journal_bank  =fields.Many2one('account.journal',string='Bank',copy=False, company_dependent=True, domain=[('type', '=', 'bank')])
    cash_requirement_lines = fields.One2many('cash.requirement.lines','cash_req_id',string='Lines',copy=False)
    available_balance  =fields.Float(string='Available Amount Balance',copy=False)
    company_id = fields.Many2one('res.company',string ='Company', default=lambda self: self.env.company)
    minimum_balance = fields.Float(string='Minimum Balance',copy=False)
    amount_total = fields.Float(string='Amount Total', copy=False)
    total_fund_required = fields.Float(string='Total Fund Required', copy=False)
    start_date = fields.Date(string="Start Date",default=fields.Datetime.now)
    end_date = fields.Date(string='End Date')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('cash.requirement.report')
        return super().create(vals_list)

    def button_done(self):
        self.state = 'done'

    def reset_to_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    @api.onchange('journal_bank')
    def onchange_journal_bank(self):
        if self.journal_bank:
            closing_balance = 0
            query = """
                        select sum(balance) as balance FROM account_move_line aml 
                        join account_move am on am.id=aml.move_id 
                        where am.state='posted' and aml.account_id=%s and aml.date <= %s and aml.company_id = %s
                        """
            # print(datetime.today().strftime('%Y-%m-%d'),'yyffffff')
            params = tuple(self.journal_bank.default_account_id.ids), datetime.today().strftime('%Y-%m-%d'), self.company_id.id
            data_get8 = self.env.cr.execute(query, params)
            lines8 = self.env.cr.dictfetchall()
            if (lines8[0].get('balance') != None):
                closing_balance = lines8[0].get('balance') or 0
            for record in self:
                record.available_balance = closing_balance
                record.total_fund_required = record.amount_total - abs(record.available_balance)

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
            self.total_fund_required = self.amount_total - abs(self.available_balance)

    # @api.onchange('minimum_balance')
    # def onchange_min_bal(self):
    #     print('hf')


class CashRequirementLines(models.Model):
    _name = 'cash.requirement.lines'
    _description = 'Cash Requirement Lines'

    cash_req_id = fields.Many2one('cash.requirement.report', string='Cash Requirement')
    cash_account = fields.Many2one('account.account',string='Account', copy=False, company_dependent=True)
    partner_id = fields.Many2one('res.partner',string='Partner' ,copy=False)
    requirement_month = fields.Date(string='Month',copy=False, default=fields.Datetime.now)
    amount = fields.Float('Amount', copy=False, tracking=True)
    remarks = fields.Char('Remarks')
    company_id = fields.Many2one('res.company',string ='Company', related='cash_req_id.company_id', store=True)
