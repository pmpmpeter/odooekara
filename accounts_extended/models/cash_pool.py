from odoo import models, fields, api, _


class CashPool(models.Model):
    _name = "cash.pool"
    _description = "Cash Pool"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', copy=False)
    sequence = fields.Char(string='Sequence', copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, copy=False)
    amount = fields.Float(string='Amount')
    active = fields.Boolean('Active', default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        return super(CashPool, self).copy(default=default)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #             vals['sequence'] = self.env['ir.sequence'].next_by_code('cash.pool')
    #     return super().create(vals_list)


class CashPoolLines(models.Model):
    _name = 'cash.pool.lines'
    _description = "Cash Pool Lines"

    fund_management_id = fields.Many2one('fund.management', string="Fund ID")
    rev_fund_management_id = fields.Many2one('fund.management', string="Rev Fund ID")
    sequence = fields.Char(string='Sequence', copy=False)
    cash_pool = fields.Many2one('cash.pool', string='Cash Pool')
    april_cash_pool = fields.Float(string="Apr")
    may_cash_pool = fields.Float(string="May")
    june_cash_pool = fields.Float(string="Jun")
    july_cash_pool = fields.Float(string="Jul")
    august_cash_pool = fields.Float(string="Aug")
    september_cash_pool = fields.Float(string="Sep")
    october_cash_pool = fields.Float(string="Oct")
    november_cash_pool = fields.Float(string="Nov")
    december_cash_pool = fields.Float(string="Dec")
    january_cash_pool = fields.Float(string="Jan")
    febuary_cash_pool = fields.Float(string="Feb")
    march_cash_pool = fields.Float(string="Mar")
    quarter_1_cash_pool = fields.Float('Q1')
    quarter_2_cash_pool = fields.Float('Q2')
    quarter_3_cash_pool = fields.Float('Q3')
    quarter_4_cash_pool = fields.Float('Q4')
    version = fields.Integer("Version", default=1, readonly=True, store=True, copy=False)
    version_name = fields.Char("Version", compute='_compute_version_name', store=True, copy=False)
    revision_date = fields.Datetime(string="Revision Date")

    @api.depends('version')
    def _compute_version_name(self):
        for record in self:
            record.version_name = 'Version ' + str(record.version)

    # @api.depends("april_cash_pool","may_cash_pool","june_cash_pool")
    @api.onchange("april_cash_pool", "may_cash_pool", "june_cash_pool")
    def _compute_q1(self):
        self.quarter_1_cash_pool = self.april_cash_pool + self.may_cash_pool + self.june_cash_pool

    @api.onchange("july_cash_pool", "august_cash_pool", "september_cash_pool")
    def _compute_q2(self):
        self.quarter_2_cash_pool = self.july_cash_pool + self.august_cash_pool + self.september_cash_pool

    @api.onchange("october_cash_pool", "november_cash_pool", "december_cash_pool")
    def _compute_q3(self):
        self.quarter_3_cash_pool = self.october_cash_pool + self.november_cash_pool + self.december_cash_pool

    @api.onchange("january_cash_pool", "febuary_cash_pool", "march_cash_pool")
    def _compute_q4(self):
        self.quarter_4_cash_pool = self.january_cash_pool + self.febuary_cash_pool + self.march_cash_pool

    # @api.onchange('april_cash_pool', 'may_cash_pool', 'june_cash_pool', 'july_cash_pool', 'august_cash_pool','september_cash_pool',
    #               'october_cash_pool', 'november_cash_pool', 'december_cash_pool','january_cash_pool', 'febuary_cash_pool', 'march_cash_pool')
    # def _onchange_quarter_cal(self):
    #     print('gggggggggggggggggggggggg')
    #     for rec in self:
    #         rec.quarter_1_cash_pool = rec.april_cash_pool + rec.may_cash_pool + rec.june_cash_pool
    #         rec.quarter_2_cash_pool = rec.july_cash_pool + rec.august_cash_pool + rec.september_cash_pool
    #         rec.quarter_3_cash_pool = rec.october_cash_pool + rec.november_cash_pool + rec.december_cash_pool
    #         rec.quarter_4_cash_pool = rec.january_cash_pool + rec.febuary_cash_pool + rec.febuary_cash_pool
