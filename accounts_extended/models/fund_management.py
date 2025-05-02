from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import calendar
from datetime import datetime


class FundManagementCRR(models.Model):
    _name = "fund.management"
    _description = "Fund Requirement Report"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'),
                              ('inprogress', 'In Progress'),
                              ('done', 'Done')], string='', default='draft')
    crr_share_line = fields.One2many('crr.share.line', 'fund_id', string='CRR Lines')
    cash_pool_line = fields.One2many('cash.pool.lines', 'fund_management_id', string='Cash Pool')
    cash_pool = fields.Many2many('cash.pool', string='Cash Pool')
    te_consolidate_id = fields.Many2one('te.consolidation', string="TE Consolidation", ondelete='cascade')
    is_share_updated = fields.Boolean('Is share Updated', default=False)
    version = fields.Integer("Version", default=1, readonly=True, store=True, copy=False)
    revision_date = fields.Datetime(string="Revision Date")

    @api.onchange('cash_pool_line')
    def _onchange_cash_pool_line(self):
        for record in self:
            for line in record.cash_pool_line:
                if line.cash_pool and line.cash_pool.current_balance <= 0:
                    raise ValidationError("The selected cash pool has a current balance of 0.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('fund.management')
        return super().create(vals_list)

    # @api.constrains('april_cash_pool','may_cash_pool','june_cash_pool','july_cash_pool','august_cash_pool','september_cash_pool',
    #               'october_cash_pool','november_cash_pool','december_cash_pool','january_cash_pool','febuary_cash_pool','march_cash_pool')
    @api.constrains('start_date', 'end_date')
    def _change_date_constrains(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise UserError('End Date Cannot be before Start Date.')

    def _action_revise(self):
        for rec in self:
            prev_version = rec.version
            version = rec.version + 1
            rec.cash_pool_line.sudo().write({
                'version': version,
                # 'revision_date': fields.Datetime.now(),
            })
            # pool_lines_history = self.env['crr.budget.line'].sudo().search(
            #     ['|', ('fund_management_id', 'in', rec.ids), ('rev_fund_management_id', 'in', rec.ids)])
            # sequence = len(pool_lines_history) + 1
            for line in rec.cash_pool_line:
                line.copy({
                    # 'sequence': sequence,
                    # 'revision_date': fields.Datetime.now(),
                    'fund_management_id': False,
                    'rev_fund_management_id': rec.id,
                    'version': prev_version,
                })
                # sequence += 1

            rec.sudo().write({
                'version': version,
                'revision_date': fields.Datetime.now(),
            })

    def _allocate_cash_pool(self):
        for rec in self:
            # rec._action_revise()
            rec.cash_pool_line.sudo().write({
                'revision_date': fields.Datetime.now(),
            })
            rec.state = 'done'
            if rec.te_consolidate_id:
                rec.te_consolidate_id.state = 'done'

    # @api.constrains('cash_pool_line')
    def share_amount_validate(self):
        for rec in self:
            for line in rec.cash_pool_line:
                if line.cash_pool and line.cash_pool.current_balance <= 0:
                    raise ValidationError(
                        f"The cash pool '{line.cash_pool.name}' has a current balance of 0."
                    )
            if not rec.crr_share_line:
                raise UserError('Share Amount is not Available.')
            if not rec.cash_pool_line:
                raise UserError('Please Add Cash Pool lines.')
            if rec.state == 'draft':
                rec.state = 'inprogress'
            if rec.state == 'inprogress':
                april_total = 0.0
                may_total = 0.0
                june_total = 0.0
                july_total = 0.0
                august_total = 0.0
                september_total = 0.0
                october_total = 0.0
                november_total = 0.0
                december_total = 0.0
                january_total = 0.0
                february_total = 0.0
                march_total = 0.0
                months = list(calendar.month_name)[1:]
                current_month = datetime.now().strftime("%B")
                Q1 = ['April', 'May', 'June']
                Q2 = ['July', 'August', 'September']
                Q3 = ['October', 'November', 'December']
                Q4 = ['January', 'February', 'March']
                for rec1 in rec.cash_pool_line:
                    april_total += rec1.april_cash_pool
                    may_total += rec1.may_cash_pool
                    june_total += rec1.june_cash_pool
                    july_total += rec1.july_cash_pool
                    august_total += rec1.august_cash_pool
                    september_total += rec1.september_cash_pool
                    october_total += rec1.october_cash_pool
                    november_total += rec1.november_cash_pool
                    december_total += rec1.december_cash_pool
                    january_total += rec1.january_cash_pool
                    february_total += rec1.febuary_cash_pool
                    march_total += rec1.march_cash_pool
                # if current_month in Q1:
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_april')), 2)) != abs(april_total):
                #         raise UserError(_("Total Share for April month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_may')), 2)) != abs(may_total):
                #         raise UserError(_("Total Share for May month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_june')), 2)) != abs(june_total):
                #         raise UserError(_("Total Share for June month does not match."))
                # if current_month in Q2:
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_july')), 2)) != abs(july_total):
                #         raise UserError(_("Total Share for July month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_august')), 2)) != abs(august_total):
                #         raise UserError(_("Total Share for August month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_september')), 2)) != abs(september_total):
                #         raise UserError(_("Total Share for September month does not match."))
                # if current_month in Q3:
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_october')), 2)) != abs(october_total):
                #         raise UserError(_("Total Share for October month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_november')), 2)) != abs(november_total):
                #         raise UserError(_("Total Share for November month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_december')), 2)) != abs(december_total):
                #         raise UserError(_("Total Share for December month does not match."))
                # if current_month in Q4:
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_january')), 2)) != abs(january_total):
                #         raise UserError(_("Total Share for January month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_february')), 2)) != abs(february_total):
                #         raise UserError(_("Total Share for February month does not match."))
                #     if abs(round(sum(rec.crr_share_line.mapped('crr_share_march')), 2)) != abs(march_total):
                #         raise UserError(_("Total Share for March month does not match."))
                rec._allocate_cash_pool()
                # rec.state = 'done'
                # if rec.te_consolidate_id:
                #     rec.te_consolidate_id.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_update_share_lines(self):
        for record in self:
            for line in record.cash_pool_line:
                if line.cash_pool and line.cash_pool.current_balance <= 0:
                    raise ValidationError(
                        f"The cash pool '{line.cash_pool.name}' has a current balance of 0."
                    )
        if not self.te_consolidate_id and not self.start_date or not self.end_date:
            raise UserError('kindly update Start and End date.')
        # share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from','>=',self.start_date),('budget_id.date_to','<=',self.end_date),('entity','=',self.company_id.id),('budget_id.state','=','to approve')])
        if self.te_consolidate_id:
            share_ids = self.te_consolidate_id.sudo().crr_share_line_ids
            self.start_date = self.te_consolidate_id.start_date
            self.end_date = self.te_consolidate_id.end_date
        else:
            share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
                                                                  ('budget_id.date_to', '<=', self.end_date),
                                                                  ('entity', '=', self.company_id.id),
                                                                  ('budget_id.state', '=', 'to approve')])

        self.crr_share_line = share_ids
        for rec in self.crr_share_line:
            if rec.sudo().budget_id.user_type == 'odoo':
                rec.ref_company = rec.sudo().budget_id.company_id.name
            elif rec.sudo().budget_id.user_type == 'non_odoo':
                rec.ref_company = rec.sudo().budget_id.partner_id.name
            rec.fund_id = self.id
        self.is_share_updated = True
        self.state = 'inprogress'

    def action_update_cash_pool(self):
        cash_lines = []
        if not self.cash_pool:
            raise UserError('Kindly Provide Cash Pool Lines')
        else:
            if self.cash_pool:
                for rec in self.cash_pool:
                    cash_lines.append((0, 0, {
                        'cash_pool': rec.id,
                        'april_cash_pool': (sum(line.crr_share_april for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'may_cash_pool': (sum(line.crr_share_may for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'june_cash_pool': (sum(line.crr_share_june for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'quarter_1_cash_pool': (sum(line.crr_share_q1 for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'july_cash_pool': (sum(line.crr_share_july for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'august_cash_pool': (sum(line.crr_share_august for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'september_cash_pool': (sum(line.crr_share_september for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'quarter_2_cash_pool': (sum(line.crr_share_q2 for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'october_cash_pool': (sum(line.crr_share_october for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'november_cash_pool': (sum(line.crr_share_november for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'december_cash_pool': (sum(line.crr_share_december for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'quarter_3_cash_pool': (sum(line.crr_share_q3 for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'january_cash_pool': (sum(line.crr_share_january for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'febuary_cash_pool': (sum(line.crr_share_february for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'march_cash_pool': (sum(line.crr_share_march for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                        'quarter_4_cash_pool': (sum(line.crr_share_q4 for line in self.crr_share_line) / len(
                            self.crr_share_line)) if self.crr_share_line else 0,
                    }))
                self.cash_pool_line = cash_lines

    def action_open_cash_pool(self):
        self.ensure_one()
        # pool_id = self.env['cash.pool.lines'].sudo().search(
        #     ['|', ('fund_management_id', 'in', self.ids), ('rev_fund_management_id', 'in', self.ids)])
        # pool_id = self.env['cash.pool.lines'].sudo().search(
        #     [('id', 'in', self.cash_pool_line.ids)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cash Pool',
            'view_mode': 'tree',
            'view_id': self.env.ref('accounts_extended.cash_pool_tree_view_extend').id,
            'res_model': 'cash.pool.lines',
            'context': {'group_by': ['version_name']},
            'domain': ['|', ('fund_management_id', 'in', self.ids), ('rev_fund_management_id', 'in', self.ids)],
        }

    def action_consolidate_crr_lines_non_odoo(self):
        self.ensure_one()
        budget_id = self.env['crossovered.budget'].sudo().search(
            [('id', 'in', self.crr_share_line.budget_id.ids), ('user_type', '=', 'non_odoo')])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget(Non-Odoo)',
            'view_mode': 'tree',
            'view_id': self.env.ref('account_budget.crossovered_budget_view_tree').id,
            'res_model': 'crossovered.budget',
            'domain': [('id', 'in', budget_id.ids)],
        }

    def action_consolidate_crr_lines_odoo(self):
        self.ensure_one()
        budget_id = self.env['crossovered.budget'].sudo().search(
            [('id', 'in', self.crr_share_line.budget_id.ids), ('user_type', '=', 'odoo')])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget(Odoo)',
            'view_mode': 'tree',
            'view_id': self.env.ref('account_budget.crossovered_budget_view_tree').id,
            'res_model': 'crossovered.budget',
            'domain': [('id', 'in', budget_id.ids)],
            'context': {'show_all_companies': True},  # Allows viewing records across companies

        }

    def action_breakup_crr_lines_odoo(self):
        self.ensure_one()
        crr_ids = self.env['crr.budget.line'].sudo().search(
            [('budget_id', 'in', self.crr_share_line.budget_id.ids), ('budget_id.user_type', '=', 'odoo')])
        return {
            'type': 'ir.actions.act_window',
            'name': 'CRR Line Items',
            'view_mode': 'tree',
            'view_id': self.env.ref('accounts_extended.crr_budget_line_extend1').id,
            'res_model': 'crr.budget.line',
            'domain': [('id', 'in', crr_ids.ids)],
        }

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You can able to delete Draft records only')
        return super(FundManagementCRR, self).unlink()

    # def action_done(self):
    #     self.state = 'done'


class TeConsolidation(models.Model):
    _name = "te.consolidation"
    _description = "TE Consolidation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default=lambda self: _('New'))
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    revised_date = fields.Date(string="Last Revised Date")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'),
                              ('inprogress', 'In Progress'),
                              ('done', 'Done')], string='', default='draft')
    crr_consolidate_ids = fields.One2many('te.consolidation.line', 'te_consolidate_id',
                                          string="Cash Outflow/Cash Inflow - Consolidate")
    crr_company_share = fields.One2many('crr.company.share', 'te_consolidate_id', string='Company Share')
    is_consolidate_updated = fields.Boolean(string='Is Consolidation Updated', default=False, copy=False)
    is_fund_management = fields.Boolean(string='Is Fund Management', default=False, copy=False)
    crr_other_share_line = fields.One2many('crr.other.share.line', 'te_consolidate_id', string='CRR Lines')
    crr_share_line_ids = fields.One2many('crr.share.line', 'te_consolidate_id', string='CRR Consolidation Lines')

    @api.constrains('start_date', 'end_date', 'company_id')
    def _check_date_range_overlap(self):
        for record in self:
            # Skip if dates are not set
            if not record.start_date or not record.end_date:
                continue

            # Check for overlapping date ranges in the same company
            overlapping = self.search([
                ('id', '!=', record.id),
                ('company_id', '=', record.company_id.id),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date)
            ], limit=1)

            if overlapping:
                raise ValidationError(
                    "Date range cannot overlap with existing records for the same Entity!\nExisting Record: %s" % overlapping.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('te.consolidation')
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You can able to delete Draft records only.')
        return super(TeConsolidation, self).unlink()

    def action_revise(self):
        for rec in self:
            rec.state = 'inprogress'
            rec.revised_date = fields.Date.today()
            fund_id = self.env['fund.management'].sudo().search([('te_consolidate_id', '=', self.id)])
            fund_id._action_revise()
            fund_id.state = 'inprogress'

    @api.constrains('start_date', 'end_date')
    def _change_date_constrains(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise UserError('End Date Cannot be before Start Date.')

    def action_update_consolidate_crr(self):
        self.crr_consolidate_ids.unlink()
        # if not self.start_date or not self.end_date:
        #     raise UserError('kindly update Start and End date')
        # share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
        #                                                       ('budget_id.date_to', '<=', self.end_date),
        #
        #                                                       ('budget_id.state', 'in', ['to approve', 'done'])])
        # print(share_ids,'gggggg')
        # print(share_ids.entity.name,'kkkkkkkk')
        # share_ids = share_ids.filtered(lambda l: l.entity.id == self.company_id.id)
        # other_share_ids = share_ids.filtered(lambda l: l.entity.id != self.company_id.id)
        # print(share_ids,'fffffff')
        # print(other_share_ids,'hhhhhhhh')
        #
        # # Avoid conflict by ensuring no overlap in assignments
        # self.crr_share_line_ids = share_ids
        # self.crr_other_share_line = other_share_ids
        share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
                                                              ('budget_id.date_to', '<=', self.end_date),
                                                              ('entity', '=', self.company_id.id),
                                                              ('budget_id.state', 'in', ['to approve', 'done'])])
        self.crr_share_line_ids = share_ids
        # share_ids1 = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
        #                                                       ('budget_id.date_to', '<=', self.end_date),
        #                                                       ('entity', '!=', self.company_id.id),
        #                                                       ('budget_id.state', 'in', ['to approve', 'done'])])
        # print(share_ids1,'hhhh')
        # created_others=[]
        # for rec in share_ids1:
        #     share_vals = {
        #         'ref_company': rec.company_id.name if rec.budget_id.user_type == 'odoo' else rec.budget_id.partner_id.name,
        #         'crr_share_april': rec.crr_share_april,
        #         'crr_share_may': rec.crr_share_may,
        #         'crr_share_june': rec.crr_share_june,
        #         'crr_share_july': rec.crr_share_july,
        #         'crr_share_august': rec.crr_share_august,
        #         'crr_share_september': rec.crr_share_september,
        #         'crr_share_october': rec.crr_share_october,
        #         'crr_share_november': rec.crr_share_november,
        #         'crr_share_december': rec.crr_share_december,
        #         'crr_share_january': rec.crr_share_january,
        #         'crr_share_february': rec.crr_share_february,
        #         'crr_share_march': rec.crr_share_march,
        #         'crr_share_q1': rec.crr_share_q1,
        #         'crr_share_q2': rec.crr_share_q2,
        #         'crr_share_q3': rec.crr_share_q3,
        #         'crr_share_q4': rec.crr_share_q4,
        #     }
        #
        #     created = self.env['crr.other.share.line'].sudo().create(share_vals)
        #     created_others.append(created.id)
        # self.write({'crr_other_share_line': [(6, 0, created_others)]})
        created_shares = []

        for rec in self.crr_share_line_ids:
            budget = rec.budget_id.sudo()
            line = False

            if budget.user_type == 'odoo':
                line = self.env['crr.budget.line.consolidate'].sudo().search([
                    ('budget_id', '=', budget.id),
                    ('is_actual_surples', '=', True)
                ])
            elif budget.user_type == 'non_odoo':
                line = self.env['crr.budget.line'].sudo().search([
                    ('budget_id', '=', budget.id),
                    ('is_actual_surples', '=', True)
                ])

            if line:
                share_vals = {
                    'partner_ref':line.budget_id.company_id.name if line.budget_id.user_type == 'odoo' else line.budget_id.partner_id.name,
                    'april_crr_budget_plan': line.april_crr_budget_plan,
                    'may_crr_budget_plan': line.may_crr_budget_plan,
                    'june_crr_budget_plan': line.june_crr_budget_plan,
                    'july_crr_budget_plan': line.july_crr_budget_plan,
                    'august_crr_budget_plan': line.august_crr_budget_plan,
                    'september_crr_budget_plan': line.september_crr_budget_plan,
                    'october_crr_budget_plan': line.october_crr_budget_plan,
                    'november_crr_budget_plan': line.november_crr_budget_plan,
                    'december_crr_budget_plan': line.december_crr_budget_plan,
                    'january_crr_budget_plan': line.january_crr_budget_plan,
                    'febuary_crr_budget_plan': line.febuary_crr_budget_plan,
                    'march_crr_budget_plan': line.march_crr_budget_plan,
                    'quarter_1_crr_budget_plan': line.quarter_1_crr_budget_plan,
                    'quarter_2_crr_budget_plan': line.quarter_2_crr_budget_plan,
                    'quarter_3_crr_budget_plan': line.quarter_3_crr_budget_plan,
                    'quarter_4_crr_budget_plan': line.quarter_4_crr_budget_plan,
                }

                created = self.env['crr.company.share'].sudo().create(share_vals)
                created_shares.append(created.id)
        self.write({'crr_company_share': [(6, 0, created_shares)]})

        for rec in share_ids:
            if rec.budget_id.user_type == 'odoo':
                rec.ref_company = rec.budget_id.company_id.name
            elif rec.budget_id.user_type == 'non_odoo':
                rec.ref_company = rec.budget_id.partner_id.name
            rec.te_consolidate_id = self.id
        seq = 1
        budget_lines = self.env['crr.budget.line'].sudo().search([
            ('budget_id', 'in', share_ids.mapped('budget_id').ids), ('budget_id.state', 'in', ['to approve', 'done'])
        ])
        companies = budget_lines.mapped('budget_id').mapped('company_id')
        partner = budget_lines.mapped('budget_id').mapped('partner_id')
        for company in companies:
            for budget_type in ['opex', 'capex']:
                for user_type in ['odoo', 'non_odoo']:
                    filtered_lines = budget_lines.filtered(
                        lambda
                            l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.company_id == company)
                    if any(line.user_type == 'odoo' for line in filtered_lines):
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            # 'budget_name':user_type,
                            'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
                                'odoo'),
                            'budget_type': budget_type,
                            'user_type': 'odoo',
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').company_id.name,
                        })
                        filtered_lines = budget_lines.filtered(
                            lambda
                                l: l.budget_type == budget_type and l.user_type == 'odoo' and l.budget_id.company_id == company)
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            'budget_name': 'Operating Expenditure (OPEX)' if budget_type == 'opex' else 'Capital  Expenditure (CAPEX)',
                            'budget_type': budget_type,
                            'user_type': 'odoo',
                            'is_budget_sum_line': True,
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').company_id.name,
                        })
            filtered_lines = budget_lines.filtered(lambda l: l.budget_type in ['opex',
                                                                               'capex'] and l.user_type == 'odoo' and l.budget_id.company_id == company)
            if filtered_lines:
                outflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Outflow',
                                                                       'te_consolidate_id': self.id,
                                                                       'april_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'april_crr_budget_plan')),
                                                                       'may_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'may_crr_budget_plan')),
                                                                       'june_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'june_crr_budget_plan')),
                                                                       'july_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'july_crr_budget_plan')),
                                                                       'august_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'august_crr_budget_plan')),
                                                                       'september_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'september_crr_budget_plan')),
                                                                       'october_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'october_crr_budget_plan')),
                                                                       'november_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'november_crr_budget_plan')),
                                                                       'december_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'december_crr_budget_plan')),
                                                                       'january_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'january_crr_budget_plan')),
                                                                       'febuary_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'febuary_crr_budget_plan')),
                                                                       'march_crr_budget_plan': sum(
                                                                           filtered_lines.mapped(
                                                                               'march_crr_budget_plan')),
                                                                       'cash_type': 'cash_payment',
                                                                       'budget_type': budget_type,
                                                                       'user_type': 'odoo',
                                                                       'is_budget_sum_line': True,
                                                                       'company_id': company.id,
                                                                       'requested_from': filtered_lines.mapped(
                                                                           'budget_id').company_id.name,

                                                                       })
            else:
                outflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Outflow',
                                                                       'te_consolidate_id': self.id,
                                                                       'april_crr_budget_plan': 0,
                                                                       'may_crr_budget_plan': 0,
                                                                       'june_crr_budget_plan': 0,
                                                                       'july_crr_budget_plan': 0,
                                                                       'august_crr_budget_plan': 0,
                                                                       'september_crr_budget_plan': 0,
                                                                       'october_crr_budget_plan': 0,
                                                                       'november_crr_budget_plan': 0,
                                                                       'december_crr_budget_plan': 0,
                                                                       'january_crr_budget_plan': 0,
                                                                       'febuary_crr_budget_plan': 0,
                                                                       'march_crr_budget_plan': 0,
                                                                       'cash_type': 'cash_payment',
                                                                       'budget_type': budget_type,
                                                                       'user_type': 'odoo',
                                                                       'is_budget_sum_line': True,
                                                                       'company_id': company.id,
                                                                       'requested_from': company.name,

                                                                       })
            for budget_type in ['ocif', 'noocif']:
                for user_type in ['odoo', 'non_odoo']:
                    filtered_lines = budget_lines.filtered(
                        lambda
                            l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.company_id == company)
                    if any(line.user_type == 'odoo' for line in filtered_lines):
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
                                'odoo'),
                            # 'budget_name':user_type,
                            'budget_type': budget_type,
                            'user_type': 'odoo',
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').company_id.name,

                        })
                        filtered_lines = budget_lines.filtered(
                            lambda
                                l: l.budget_type == budget_type and l.user_type == 'odoo' and l.budget_id.company_id == company)
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            'budget_name': 'Operating Cash-In-Flow (OCIF)' if budget_type == 'ocif' else 'Non-Operating Cash-In-Flow (NOCIF)',
                            'budget_type': budget_type,
                            'user_type': 'odoo',
                            'is_budget_sum_line': True,
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').company_id.name,

                        })
            filtered_lines = budget_lines.filtered(
                lambda l: l.budget_type in ['ocif',
                                            'noocif'] and l.user_type == 'odoo' and l.budget_id.company_id == company)
            if filtered_lines:
                inflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Inflow',
                                                                      'te_consolidate_id': self.id,
                                                                      'april_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'april_crr_budget_plan')),
                                                                      'may_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'may_crr_budget_plan')),
                                                                      'june_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'june_crr_budget_plan')),
                                                                      'july_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'july_crr_budget_plan')),
                                                                      'august_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'august_crr_budget_plan')),
                                                                      'september_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'september_crr_budget_plan')),
                                                                      'october_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'october_crr_budget_plan')),
                                                                      'november_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'november_crr_budget_plan')),
                                                                      'december_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'december_crr_budget_plan')),
                                                                      'january_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'january_crr_budget_plan')),
                                                                      'febuary_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'febuary_crr_budget_plan')),
                                                                      'march_crr_budget_plan': sum(
                                                                          filtered_lines.mapped(
                                                                              'march_crr_budget_plan')),
                                                                      'cash_type': 'cash_payment',
                                                                      'budget_type': budget_type,
                                                                      'user_type': 'odoo',
                                                                      'is_budget_sum_line': True,
                                                                      'company_id': company.id,
                                                                      'requested_from': filtered_lines.mapped(
                                                                          'budget_id').company_id.name,

                                                                      })
            else:
                inflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Inflow',
                                                                      'te_consolidate_id': self.id,
                                                                      'april_crr_budget_plan': 0,
                                                                      'may_crr_budget_plan': 0,
                                                                      'june_crr_budget_plan': 0,
                                                                      'july_crr_budget_plan': 0,
                                                                      'august_crr_budget_plan': 0,
                                                                      'september_crr_budget_plan': 0,
                                                                      'october_crr_budget_plan': 0,
                                                                      'november_crr_budget_plan': 0,
                                                                      'december_crr_budget_plan': 0,
                                                                      'january_crr_budget_plan': 0,
                                                                      'febuary_crr_budget_plan': 0,
                                                                      'march_crr_budget_plan': 0,
                                                                      'cash_type': 'cash_payment',
                                                                      'budget_type': budget_type,
                                                                      'user_type': 'odoo',
                                                                      'is_budget_sum_line': True,
                                                                      'company_id': company.id,
                                                                      'requested_from': company.name,

                                                                      })
            self.env['te.consolidation.line'].create({'budget_name': 'Surplus/ Deficit(IN-OUT)',
                                                      'te_consolidate_id': self.id,
                                                      'april_crr_budget_plan': sum(
                                                          inflow_id.mapped('april_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('april_crr_budget_plan')),
                                                      'may_crr_budget_plan': sum(
                                                          inflow_id.mapped('may_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('may_crr_budget_plan')),
                                                      'june_crr_budget_plan': sum(
                                                          inflow_id.mapped('june_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('june_crr_budget_plan')),
                                                      'july_crr_budget_plan': sum(
                                                          inflow_id.mapped('july_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('july_crr_budget_plan')),
                                                      'august_crr_budget_plan': sum(
                                                          inflow_id.mapped('august_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('august_crr_budget_plan')),
                                                      'september_crr_budget_plan': sum(
                                                          inflow_id.mapped('september_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('september_crr_budget_plan')),
                                                      'october_crr_budget_plan': sum(
                                                          inflow_id.mapped('october_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('october_crr_budget_plan')),
                                                      'november_crr_budget_plan': sum(
                                                          inflow_id.mapped('november_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('november_crr_budget_plan')),
                                                      'december_crr_budget_plan': sum(
                                                          inflow_id.mapped('december_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('december_crr_budget_plan')),
                                                      'january_crr_budget_plan': sum(
                                                          inflow_id.mapped('january_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('january_crr_budget_plan')),
                                                      'febuary_crr_budget_plan': sum(
                                                          inflow_id.mapped('febuary_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('febuary_crr_budget_plan')),
                                                      'march_crr_budget_plan': sum(
                                                          inflow_id.mapped('march_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('march_crr_budget_plan')),
                                                      'cash_type': 'cash_payment',
                                                      'budget_type': budget_type,
                                                      'user_type': 'odoo',
                                                      'is_budget_sum_line': True,
                                                      'company_id': company.id,
                                                      'requested_from': company.name,

                                                      })

        for partners in partner:
            for budget_type in ['opex', 'capex']:
                for user_type in ['odoo', 'non_odoo']:
                    filtered_lines = budget_lines.filtered(
                        lambda
                            l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.partner_id == partners)
                    if any(line.user_type == 'non_odoo' for line in filtered_lines):
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            # 'budget_name':user_type,
                            'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
                                'non_odoo'),
                            'budget_type': budget_type,
                            'user_type': 'non_odoo',
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').partner_id.name,
                        })
                        filtered_lines = budget_lines.filtered(
                            lambda
                                l: l.budget_type == budget_type and l.user_type == 'non_odoo' and l.budget_id.partner_id == partners)
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            'budget_name': 'Operating Expenditure (OPEX)' if budget_type == 'opex' else 'Capital  Expenditure (CAPEX)',
                            'budget_type': budget_type,
                            'user_type': 'non_odoo',
                            'is_budget_sum_line': True,
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').partner_id.name,

                        })
            filtered_lines = budget_lines.filtered(
                lambda l: l.budget_type in ['opex',
                                            'capex'] and l.user_type == 'non_odoo' and l.budget_id.partner_id == partners)
            if filtered_lines:
                outflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Outflow',
                                                                   'te_consolidate_id': self.id,
                                                                   'april_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('april_crr_budget_plan')),
                                                                   'may_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('may_crr_budget_plan')),
                                                                   'june_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('june_crr_budget_plan')),
                                                                   'july_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('july_crr_budget_plan')),
                                                                   'august_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('august_crr_budget_plan')),
                                                                   'september_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'september_crr_budget_plan')),
                                                                   'october_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'october_crr_budget_plan')),
                                                                   'november_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'november_crr_budget_plan')),
                                                                   'december_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'december_crr_budget_plan')),
                                                                   'january_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'january_crr_budget_plan')),
                                                                   'febuary_crr_budget_plan': sum(
                                                                       filtered_lines.mapped(
                                                                           'febuary_crr_budget_plan')),
                                                                   'march_crr_budget_plan': sum(
                                                                       filtered_lines.mapped('march_crr_budget_plan')),
                                                                   'cash_type': 'cash_payment',
                                                                   'budget_type': budget_type,
                                                                   'user_type': 'non_odoo',
                                                                   'is_budget_sum_line': True,
                                                                   'company_id': company.id,
                                                                   'requested_from': filtered_lines.mapped(
                                                                       'budget_id').partner_id.name,

                                                                   })
            else:
                outflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Outflow',
                                                                       'te_consolidate_id': self.id,
                                                                       'april_crr_budget_plan': 0,
                                                                       'may_crr_budget_plan': 0,
                                                                       'june_crr_budget_plan': 0,
                                                                       'july_crr_budget_plan': 0,
                                                                       'august_crr_budget_plan': 0,
                                                                       'september_crr_budget_plan':0,
                                                                       'october_crr_budget_plan': 0,
                                                                       'november_crr_budget_plan': 0,
                                                                       'december_crr_budget_plan': 0,
                                                                       'january_crr_budget_plan': 0,
                                                                       'febuary_crr_budget_plan': 0,
                                                                       'march_crr_budget_plan': 0,
                                                                       'cash_type': 'cash_payment',
                                                                       'budget_type': budget_type,
                                                                       'user_type': 'non_odoo',
                                                                       'is_budget_sum_line': True,
                                                                       'company_id': company.id,
                                                                       'requested_from': filtered_lines.mapped(
                                                                           'budget_id').partner_id.name,

                                                                       })
            for budget_type in ['ocif', 'noocif']:
                for user_type in ['odoo', 'non_odoo']:
                    filtered_lines = budget_lines.filtered(
                        lambda
                            l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.partner_id == partners)
                    if filtered_lines and any(line.user_type == 'non_odoo' for line in filtered_lines):
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
                                'non_odoo'),
                            # 'budget_name':user_type,
                            'budget_type': budget_type,
                            'user_type': 'non_odoo',
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').partner_id.name,

                        })
                        filtered_lines = budget_lines.filtered(
                            lambda
                                l: l.budget_type == budget_type and l.user_type == 'non_odoo' and l.budget_id.partner_id == partners)
                        self.env['te.consolidation.line'].create({
                            'te_consolidate_id': self.id,
                            'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
                            'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
                            'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
                            'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
                            'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
                            'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
                            'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
                            'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
                            'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
                            'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
                            'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
                            'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
                            'cash_type': 'cash_payment',
                            'budget_name': 'Operating Cash-In-Flow (OCIF)' if budget_type == 'ocif' else 'Non-Operating Cash-In-Flow (NOCIF)',
                            'budget_type': budget_type,
                            'user_type': 'non_odoo',
                            'is_budget_sum_line': True,
                            'company_id': company.id,
                            'requested_from': filtered_lines.mapped('budget_id').partner_id.name,

                        })
            filtered_lines = budget_lines.filtered(
                lambda l: l.budget_type in ['ocif',
                                            'noocif'] and l.user_type == 'non_odoo' and l.budget_id.partner_id == partners)
            inflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Inflow',
                                                                  'te_consolidate_id': self.id,
                                                                  'april_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'april_crr_budget_plan')),
                                                                  'may_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'may_crr_budget_plan')),
                                                                  'june_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'june_crr_budget_plan')),
                                                                  'july_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'july_crr_budget_plan')),
                                                                  'august_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'august_crr_budget_plan')),
                                                                  'september_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'september_crr_budget_plan')),
                                                                  'october_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'october_crr_budget_plan')),
                                                                  'november_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'november_crr_budget_plan')),
                                                                  'december_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'december_crr_budget_plan')),
                                                                  'january_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'january_crr_budget_plan')),
                                                                  'febuary_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'febuary_crr_budget_plan')),
                                                                  'march_crr_budget_plan': sum(
                                                                      filtered_lines.mapped(
                                                                          'march_crr_budget_plan')),
                                                                  'cash_type': 'cash_payment',
                                                                  'budget_type': budget_type,
                                                                  'user_type': 'non_odoo',
                                                                  'is_budget_sum_line': True,
                                                                  'company_id': company.id,
                                                                  'requested_from': filtered_lines.mapped(
                                                                      'budget_id').partner_id.name,

                                                                  })
            self.env['te.consolidation.line'].create({'budget_name': 'Surplus/ Deficit(IN-OUT)',
                                                      'te_consolidate_id': self.id,
                                                      'april_crr_budget_plan': sum(
                                                          inflow_id.mapped('april_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('april_crr_budget_plan')),
                                                      'may_crr_budget_plan': sum(
                                                          inflow_id.mapped('may_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('may_crr_budget_plan')),
                                                      'june_crr_budget_plan': sum(
                                                          inflow_id.mapped('june_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('june_crr_budget_plan')),
                                                      'july_crr_budget_plan': sum(
                                                          inflow_id.mapped('july_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('july_crr_budget_plan')),
                                                      'august_crr_budget_plan': sum(
                                                          inflow_id.mapped('august_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('august_crr_budget_plan')),
                                                      'september_crr_budget_plan': sum(
                                                          inflow_id.mapped('september_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('september_crr_budget_plan')),
                                                      'october_crr_budget_plan': sum(
                                                          inflow_id.mapped('october_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('october_crr_budget_plan')),
                                                      'november_crr_budget_plan': sum(
                                                          inflow_id.mapped('november_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('november_crr_budget_plan')),
                                                      'december_crr_budget_plan': sum(
                                                          inflow_id.mapped('december_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('december_crr_budget_plan')),
                                                      'january_crr_budget_plan': sum(
                                                          inflow_id.mapped('january_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('january_crr_budget_plan')),
                                                      'febuary_crr_budget_plan': sum(
                                                          inflow_id.mapped('febuary_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('febuary_crr_budget_plan')),
                                                      'march_crr_budget_plan': sum(
                                                          inflow_id.mapped('march_crr_budget_plan')) - sum(
                                                          outflow_id.mapped('march_crr_budget_plan')),
                                                      'cash_type': 'cash_payment',
                                                      'budget_type': budget_type,
                                                      'user_type': 'non_odoo',
                                                      'is_budget_sum_line': True,
                                                      'company_id': company.id,
                                                      'requested_from': filtered_lines.mapped(
                                                          'budget_id').partner_id.name,
                                                      })

        fund_id = self.env['fund.management'].sudo().search([('te_consolidate_id', '=', self.id)])
        if fund_id:
            fund_id.action_update_share_lines()
        self.is_consolidate_updated = True
        self.state = 'inprogress'
        return True

    # def action_update_consolidate_crr(self):
    #     self.crr_consolidate_ids.unlink()
    #     if not self.start_date or not self.end_date:
    #         raise UserError('kindly update Start and End date')
    #     share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
    #                                                           ('budget_id.date_to', '<=', self.end_date),
    #                                                           ('entity', '=', self.company_id.id),
    #                                                           ('budget_id.state', 'in', ['to approve','done'])])
    #     self.crr_share_line_ids = share_ids
    #     for rec in share_ids:
    #         if rec.budget_id.user_type == 'odoo':
    #             rec.ref_company = rec.budget_id.company_id.name
    #         elif rec.budget_id.user_type == 'non_odoo':
    #             rec.ref_company = rec.budget_id.partner_id.name
    #         rec.te_consolidate_id = self.id
    #     seq = 1
    #     budget_lines = self.env['crr.budget.line'].sudo().search([
    #         ('budget_id', 'in', share_ids.mapped('budget_id').ids), ('budget_id.state', 'in', ['to approve','done'])
    #     ])
    #     companies = budget_lines.mapped('budget_id').mapped('company_id')
    #     for company in companies:
    #         for budget_type in ['opex', 'capex']:
    #             for user_type in ['odoo', 'non_odoo']:
    #                 filtered_lines = budget_lines.filtered(
    #                     lambda
    #                         l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.company_id == company)
    #                 self.env['te.consolidation.line'].create({
    #                     'te_consolidate_id': self.id,
    #                     'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
    #                     'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
    #                     'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
    #                     'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
    #                     'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
    #                     'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
    #                     'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
    #                     'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
    #                     'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
    #                     'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
    #                     'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
    #                     'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
    #                     'cash_type': 'cash_payment',
    #                     # 'budget_name':user_type,
    #                     'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
    #                         user_type),
    #                     'budget_type': budget_type,
    #                     'user_type': user_type,
    #                     'company_id': company.id,
    #                 })
    #             filtered_lines = budget_lines.filtered(
    #                 lambda l: l.budget_type == budget_type and l.budget_id.company_id == company)
    #             self.env['te.consolidation.line'].create({
    #                 'te_consolidate_id': self.id,
    #                 'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
    #                 'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
    #                 'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
    #                 'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
    #                 'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
    #                 'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
    #                 'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
    #                 'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
    #                 'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
    #                 'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
    #                 'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
    #                 'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
    #                 'cash_type': 'cash_payment',
    #                 'budget_name': 'Operating Expenditure (OPEX)' if budget_type == 'opex' else 'Capital  Expenditure (CAPEX)',
    #                 'budget_type': budget_type,
    #                 # 'user_type': user_type,
    #                 'is_budget_sum_line': True,
    #                 'company_id': company.id,
    #             })
    #
    #         filtered_lines = budget_lines.filtered(
    #             lambda l: l.budget_type in ['opex', 'capex'] and l.budget_id.company_id == company)
    #         outflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Outflow',
    #                                                                'te_consolidate_id': self.id,
    #                                                                'april_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('april_crr_budget_plan')),
    #                                                                'may_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('may_crr_budget_plan')),
    #                                                                'june_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('june_crr_budget_plan')),
    #                                                                'july_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('july_crr_budget_plan')),
    #                                                                'august_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('august_crr_budget_plan')),
    #                                                                'september_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'september_crr_budget_plan')),
    #                                                                'october_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'october_crr_budget_plan')),
    #                                                                'november_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'november_crr_budget_plan')),
    #                                                                'december_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'december_crr_budget_plan')),
    #                                                                'january_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'january_crr_budget_plan')),
    #                                                                'febuary_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped(
    #                                                                        'febuary_crr_budget_plan')),
    #                                                                'march_crr_budget_plan': sum(
    #                                                                    filtered_lines.mapped('march_crr_budget_plan')),
    #                                                                'cash_type': 'cash_payment',
    #                                                                'budget_type': budget_type,
    #                                                                # 'user_type': user_type,
    #                                                                'is_budget_sum_line': True,
    #                                                                'company_id': company.id,
    #                                                                })
    #
    #         # for company in companies:
    #         for budget_type in ['ocif', 'noocif']:
    #             for user_type in ['odoo', 'non_odoo']:
    #                 filtered_lines = budget_lines.filtered(
    #                     lambda
    #                         l: l.budget_type == budget_type and l.user_type == user_type and l.budget_id.company_id == company)
    #                 self.env['te.consolidation.line'].create({
    #                     'te_consolidate_id': self.id,
    #                     'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
    #                     'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
    #                     'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
    #                     'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
    #                     'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
    #                     'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
    #                     'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
    #                     'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
    #                     'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
    #                     'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
    #                     'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
    #                     'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
    #                     'budget_name': dict(self.env['crossovered.budget']._fields['user_type'].selection).get(
    #                         user_type),
    #                     # 'budget_name':user_type,
    #                     'budget_type': budget_type,
    #                     'user_type': user_type,
    #                     'company_id': company.id,
    #                 })
    #             filtered_lines = budget_lines.filtered(
    #                 lambda l: l.budget_type == budget_type and l.budget_id.company_id == company)
    #             self.env['te.consolidation.line'].create({
    #                 'te_consolidate_id': self.id,
    #                 'april_crr_budget_plan': sum(filtered_lines.mapped('april_crr_budget_plan')),
    #                 'may_crr_budget_plan': sum(filtered_lines.mapped('may_crr_budget_plan')),
    #                 'june_crr_budget_plan': sum(filtered_lines.mapped('june_crr_budget_plan')),
    #                 'july_crr_budget_plan': sum(filtered_lines.mapped('july_crr_budget_plan')),
    #                 'august_crr_budget_plan': sum(filtered_lines.mapped('august_crr_budget_plan')),
    #                 'september_crr_budget_plan': sum(filtered_lines.mapped('september_crr_budget_plan')),
    #                 'october_crr_budget_plan': sum(filtered_lines.mapped('october_crr_budget_plan')),
    #                 'november_crr_budget_plan': sum(filtered_lines.mapped('november_crr_budget_plan')),
    #                 'december_crr_budget_plan': sum(filtered_lines.mapped('december_crr_budget_plan')),
    #                 'january_crr_budget_plan': sum(filtered_lines.mapped('january_crr_budget_plan')),
    #                 'febuary_crr_budget_plan': sum(filtered_lines.mapped('febuary_crr_budget_plan')),
    #                 'march_crr_budget_plan': sum(filtered_lines.mapped('march_crr_budget_plan')),
    #                 'cash_type': 'cash_payment',
    #                 'budget_name': 'Operating Cash-In-Flow (OCIF)' if budget_type == 'ocif' else 'Non-Operating Cash-In-Flow (NOCIF)',
    #                 'budget_type': budget_type,
    #                 # 'user_type': user_type,
    #                 'is_budget_sum_line': True,
    #                 'company_id': company.id,
    #             })
    #
    #         filtered_lines = budget_lines.filtered(
    #             lambda l: l.budget_type in ['ocif', 'noocif'] and l.budget_id.company_id == company)
    #         inflow_id = self.env['te.consolidation.line'].create({'budget_name': 'Total Cash Inflow',
    #                                                               'te_consolidate_id': self.id,
    #                                                               'april_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('april_crr_budget_plan')),
    #                                                               'may_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('may_crr_budget_plan')),
    #                                                               'june_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('june_crr_budget_plan')),
    #                                                               'july_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('july_crr_budget_plan')),
    #                                                               'august_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('august_crr_budget_plan')),
    #                                                               'september_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped(
    #                                                                       'september_crr_budget_plan')),
    #                                                               'october_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('october_crr_budget_plan')),
    #                                                               'november_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped(
    #                                                                       'november_crr_budget_plan')),
    #                                                               'december_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped(
    #                                                                       'december_crr_budget_plan')),
    #                                                               'january_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('january_crr_budget_plan')),
    #                                                               'febuary_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('febuary_crr_budget_plan')),
    #                                                               'march_crr_budget_plan': sum(
    #                                                                   filtered_lines.mapped('march_crr_budget_plan')),
    #                                                               'cash_type': 'cash_payment',
    #                                                               'budget_type': budget_type,
    #                                                               # 'user_type': user_type,
    #                                                               'is_budget_sum_line': True,
    #                                                               'company_id': company.id,
    #                                                               })
    #         self.env['te.consolidation.line'].create({'budget_name': 'Surplus/ Deficit(IN-OUT)',
    #                                                   'te_consolidate_id': self.id,
    #                                                   'april_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('april_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('april_crr_budget_plan')),
    #                                                   'may_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('may_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('may_crr_budget_plan')),
    #                                                   'june_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('june_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('june_crr_budget_plan')),
    #                                                   'july_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('july_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('july_crr_budget_plan')),
    #                                                   'august_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('august_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('august_crr_budget_plan')),
    #                                                   'september_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('september_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('september_crr_budget_plan')),
    #                                                   'october_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('october_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('october_crr_budget_plan')),
    #                                                   'november_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('november_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('november_crr_budget_plan')),
    #                                                   'december_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('december_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('december_crr_budget_plan')),
    #                                                   'january_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('january_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('january_crr_budget_plan')),
    #                                                   'febuary_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('febuary_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('febuary_crr_budget_plan')),
    #                                                   'march_crr_budget_plan': sum(
    #                                                       inflow_id.mapped('march_crr_budget_plan')) - sum(
    #                                                       outflow_id.mapped('march_crr_budget_plan')),
    #                                                   'cash_type': 'cash_payment',
    #                                                   'budget_type': budget_type,
    #                                                   # 'user_type': user_type,
    #                                                   'is_budget_sum_line': True,
    #                                                   'company_id': company.id,
    #                                                   })
    #
    #     fund_id = self.env['fund.management'].sudo().search([('te_consolidate_id', '=', self.id)])
    #     if fund_id:
    #         fund_id.action_update_share_lines()
    #     self.is_consolidate_updated = True
    #     self.state = 'inprogress'
    #     return True

    def action_open_share_view(self):
        share_ids = self.env['crr.share.line'].sudo().search([('budget_id.date_from', '>=', self.start_date),
                                                              ('budget_id.date_to', '<=', self.end_date),
                                                              ('budget_id.state', 'in', ['to approve', 'done'])])
        if share_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'View Share',
                'view_mode': 'tree',
                'res_model': 'crr.share.line',
                'domain': [('id', 'in', share_ids.ids)],
                'context': {'group_by': ['ref_company']},
            }

    def action_create_fund_management(self):
        fund_id = self.env['fund.management'].sudo().search([('te_consolidate_id', '=', self.id)])
        if not fund_id:
            fund_id = self.env['fund.management'].create({
                'start_date': self.start_date,
                'end_date': self.end_date,
                'te_consolidate_id': self.id
            })
        fund_id.action_update_share_lines()
        fund_id.is_share_updated = True
        self.is_fund_management = True
        self.state = 'inprogress'
        return True

    def action_open_fund_management(self):
        self.ensure_one()
        fund_id = self.env['fund.management'].sudo().search([('te_consolidate_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fund Management',
            'view_mode': 'form',
            'view_id': self.env.ref('accounts_extended.view_fund_mangemnt_view').id,
            'res_model': 'fund.management',
            'context': {'create': False},
            'res_id': fund_id.id,  # Pass the fund record ID here
            'target': 'current',
        }

    def action_open_consolidation(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'CRR Consolidation',
            'view_mode': 'tree',
            'res_model': 'te.consolidation.line',
            'domain': [('id', 'in', self.crr_consolidate_ids.ids)],
            'context': {'group_by': ['user_type', 'requested_from']},
        }


class TeConsolidationLine(models.Model):
    _name = 'te.consolidation.line'
    _description = 'Te Consolidation Line'

    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     print(groupby, "read_group called")
    #
    #     conditions = domain.copy()
    #     result = super(TeConsolidationLine, self).read_group(
    #         domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy
    #     )
    #     print(groupby, 'wwwwwwwwwwwwwwwwwww')
    #     # if groupby == ['user_type']:
    #     print("Custom logic for groupby = ['user_type']")
    #
    #     record_ids = self.sudo().search(conditions)
    #     conditions += [
    #         ('id', 'in', record_ids.ids),
    #         ('budget_name', '=', 'Surplus/ Deficit(IN-OUT)')
    #     ]
    #
    #     for res in result:
    #         user_type = res.get('user_type')
    #         if isinstance(user_type, (list, tuple)):
    #             user_type_id = user_type[0]
    #         else:
    #             user_type_id = user_type
    #
    #         test = conditions.copy()
    #         test.append(('user_type', '=', user_type_id))
    #
    #         if isinstance(res, dict):
    #             if 'april_crr_budget_plan' in res:
    #                 rec_ids = self.search(test + res['__domain'])
    #                 print('hhhhhhhhhhhhhhhhhhhhhhhhh ', len(rec_ids))
    #                 amount_total = 0
    #                 if rec_ids:
    #                     amount_total = sum(rec_ids.mapped('april_crr_budget_plan'))
    #                 res['april_crr_budget_plan'] = amount_total
    #
    #     return result

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        result = super(TeConsolidationLine, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy
        )
        if groupby == ['user_type']:
            for res in result:
                user_type = res.get('user_type')
                if isinstance(user_type, (list, tuple)):
                    user_type_id = user_type[0]
                else:
                    user_type_id = user_type
                sub_domain = domain + [('user_type', '=', user_type_id),
                                       ('budget_name', '=', 'Surplus/ Deficit(IN-OUT)')]
                lines = self.search(sub_domain)
                updated_values = {}
                for f in fields:
                    if f in groupby or f == '__domain':
                        continue
                    updated_values[f] = 0.0

                for line in lines:
                    for f in updated_values:
                        val = getattr(line, f, 0.0)
                        if isinstance(val, (int, float)):
                            updated_values[f] += val
                for f in updated_values:
                    res[f] = updated_values[f]
        if groupby == ['requested_from'] or 'requested_from' in groupby:
            records = self.search(domain)
            surplus_lines = records.filtered(lambda r: r.budget_name == 'Surplus/ Deficit(IN-OUT)')
            surplus_map = {}
            for rec in surplus_lines:
                company_id = rec.requested_from
                if company_id not in surplus_map:
                    surplus_map[company_id] = {f: 0.0 for f in fields if f not in groupby and f != '__domain'}

                for f in surplus_map[company_id]:
                    val = getattr(rec, f, 0.0)
                    if isinstance(val, (int, float)):
                        surplus_map[company_id][f] += val
            for res in result:
                company_info = res.get('requested_from')
                if isinstance(company_info, (list, tuple)):
                    company_id = company_info[0]
                else:
                    company_id = company_info
                if company_id in surplus_map:
                    for f, val in surplus_map[company_id].items():
                        if f in res:
                            res[f] = val

        return result

    @api.depends('quarter_1_crr_budget_plan', 'quarter_2_crr_budget_plan', 'quarter_3_crr_budget_plan',
                 'quarter_4_crr_budget_plan')
    def _compute_to_get_total(self):
        for rec in self:
            rec.crr_budget_total = rec.quarter_1_crr_budget_plan + rec.quarter_2_crr_budget_plan + rec.quarter_3_crr_budget_plan + rec.quarter_4_crr_budget_plan

    @api.depends(
        'quarter_1_crr_budget_plan', 'quarter_2_crr_budget_plan', 'quarter_3_crr_budget_plan',
        'quarter_4_crr_budget_plan',
        'april_crr_budget_plan', 'may_crr_budget_plan', 'june_crr_budget_plan', 'july_crr_budget_plan',
        'august_crr_budget_plan',
        'september_crr_budget_plan', 'october_crr_budget_plan', 'november_crr_budget_plan', 'december_crr_budget_plan',
        'january_crr_budget_plan', 'febuary_crr_budget_plan', 'march_crr_budget_plan'
    )
    def _compute_to_get_quarter_values(self):
        for record in self:
            record.quarter_1_crr_budget_plan = record.april_crr_budget_plan + record.may_crr_budget_plan + record.june_crr_budget_plan
            record.quarter_2_crr_budget_plan = record.july_crr_budget_plan + record.august_crr_budget_plan + record.september_crr_budget_plan
            record.quarter_3_crr_budget_plan = record.october_crr_budget_plan + record.november_crr_budget_plan + record.december_crr_budget_plan
            record.quarter_4_crr_budget_plan = record.january_crr_budget_plan + record.febuary_crr_budget_plan + record.march_crr_budget_plan

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    te_consolidate_id = fields.Many2one('te.consolidation', string="TE Consolidation", ondelete='cascade')
    user_type = fields.Selection([('odoo', 'Odoo User'),
                                  ('non_odoo', 'Non-Odoo User')], string="User Type")
    budget_position_id = fields.Many2one('account.budget.post', string="Budget \n Position")
    budget_type = fields.Selection([('capex', 'Capex'),
                                    ('opex', 'Opex'),
                                    ('ocif', 'OCIF'),
                                    ('noocif', 'NOOCIF')], string="Budget Type")
    april_crr_budget_plan = fields.Float(string="Apr")
    requested_from = fields.Char(string='Requested By')
    may_crr_budget_plan = fields.Float(string="May")
    june_crr_budget_plan = fields.Float(string="Jun")
    july_crr_budget_plan = fields.Float(string="Jul")
    august_crr_budget_plan = fields.Float(string="Aug")
    september_crr_budget_plan = fields.Float(string="Sep")
    october_crr_budget_plan = fields.Float(string="Oct")
    november_crr_budget_plan = fields.Float(string="Nov")
    december_crr_budget_plan = fields.Float(string="Dec")
    january_crr_budget_plan = fields.Float(string="Jan")
    febuary_crr_budget_plan = fields.Float(string="Feb")
    march_crr_budget_plan = fields.Float(string="Mar")
    cash_type = fields.Selection([('cash_payment', 'Cash Payment'),
                                  ('cash_receipt', 'Cash Receipt')], string="Cash Type")
    quarter_1_crr_budget_plan = fields.Float('Q1', compute='_compute_to_get_quarter_values')
    quarter_2_crr_budget_plan = fields.Float('Q2', compute='_compute_to_get_quarter_values')
    quarter_3_crr_budget_plan = fields.Float('Q3', compute='_compute_to_get_quarter_values')
    quarter_4_crr_budget_plan = fields.Float('Q4', compute='_compute_to_get_quarter_values')
    crr_budget_total = fields.Float('Total', compute='_compute_to_get_total')
    budget_name = fields.Char('Budget Position')
    is_budget_sum_line = fields.Boolean('Is Budget Line', default=False)
    # is_budget_in_sum_line = fields.Boolean('Is Budget Line',default=False)
    # is_budget_surples_sum_line = fields.Boolean('Is Budget Line',default=False)
    # sequence = fields.Integer('SEQ')


class CRRCompanyShare(models.Model):
    _name = 'crr.company.share'
    _description = 'crr.company.share'

    partner_ref = fields.Char(string='Company')
    te_consolidate_id = fields.Many2one('te.consolidation', string="TE Consolidation", ondelete='cascade')
    april_crr_budget_plan = fields.Float(string="Apr")
    may_crr_budget_plan = fields.Float(string="May")
    june_crr_budget_plan = fields.Float(string="Jun")
    july_crr_budget_plan = fields.Float(string="Jul")
    august_crr_budget_plan = fields.Float(string="Aug")
    september_crr_budget_plan = fields.Float(string="Sep")
    october_crr_budget_plan = fields.Float(string="Oct")
    november_crr_budget_plan = fields.Float(string="Nov")
    december_crr_budget_plan = fields.Float(string="Dec")
    january_crr_budget_plan = fields.Float(string="Jan")
    febuary_crr_budget_plan = fields.Float(string="Feb")
    march_crr_budget_plan = fields.Float(string="Mar")
    quarter_1_crr_budget_plan = fields.Float('Q1')
    quarter_2_crr_budget_plan = fields.Float('Q2')
    quarter_3_crr_budget_plan = fields.Float('Q3')
    quarter_4_crr_budget_plan = fields.Float('Q4')
