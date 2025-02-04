from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning


class BudgetInherit(models.Model):
    _inherit = 'crossovered.budget'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('revision', 'To Revision'),
        ('confirm', 'Confirmed'),
        ('to approve', 'To Approve'),
        ('validate', 'Validated'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    revision_reason = fields.Text(string="Revision Reasons", readonly=True, default="")
    revision_history_ids = fields.One2many('revision.history','budget_id',string='Revesion History')


    @api.depends('approval_document.type_id.state','approval_document.line_ids.state')
    def compute_approval_state(self):
        for record in self:
            if record.approval_document:
                line_states = record.approval_document.line_ids.mapped('state')
                if all(state == 'Draft' for state in line_states):
                    record.approval_state = 'Waiting For Approval'
                elif 'Waiting for Approval' in line_states:
                    waiting_lines = record.approval_document.line_ids.filtered(lambda l: l.state == 'Waiting for Approval')
                    if waiting_lines:
                        record.approval_state = f"Waiting for {', '.join(waiting_lines.mapped('name'))} Approval"
                elif all(state == 'Approved' for state in line_states):
                    record.approval_state = 'Approved'
                elif 'Refused' in line_states:
                    record.approval_state = 'Rejected'
                elif 'Cancel' in line_states:
                    record.approval_state = 'Cancelled'
            else:
                rec = self.env['multi.approval.type'].sudo().search([('model_id','=','crossovered.budget'),('state','=','confirm')],limit=1)
                if rec:
                    record.approval_state = 'To Submit for Approval'
                else:
                    record.approval_state = 'Not Applicable'

    def action_revise(self):
        return {
            'name': 'Budget Revision',
            'type': 'ir.actions.act_window',
            'res_model': 'budget.revision.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def action_budget_confirm(self):
        for line in self.crossovered_budget_line:
            if not line.analytic_account_id:
                raise UserError('Kinldy add a Analytic Account for a Budget Line')

        return super().action_budget_confirm()

    def action_budget_done(self):
        for rec in self.crossovered_budget_line:
            if not rec.is_budget_code:
                rec.is_budget_code = True
                rec.budget_code = self.env['ir.sequence'].next_by_code('budget.code')
        return super().action_budget_done()


class Crossoverbudgetlines(models.Model):
    _inherit='crossovered.budget.lines'

    def _compute_balance_amount(self):
        for rec in self:
            rec.balance_amount = rec.planned_amount-(abs(rec.practical_amount)+rec.reserved_amount)

    @api.depends('additional_amount')
    def _compute_is_edited(self):
        for rec in self:
            rec.under_revision = False
            if rec.crossovered_budget_id.state == 'revision':
                if rec.additional_amount > 0:
                    rec.under_revision = True

    name = fields.Char(compute="_compute_line_name", store=True)
    budget_code = fields.Char('Budget Code')
    is_budget_code = fields.Boolean('Is Budget Code')
    reserved_amount = fields.Float('Reserved Amount')
    balance_amount = fields.Float('Balance Amount',compute='_compute_balance_amount')
    capex_opex = fields.Selection([
        ('capex', 'Capex'),
        ('opex', 'Opex'),
    ], 'Capex/Opex',default='capex',index=True,required=True,copy=False, tracking=True)
    department_id = fields.Many2one('hr.department',string='Department')
    additional_amount = fields.Float('Additional Amount')
    under_revision = fields.Boolean(string='Under Revision',default=False,compute='_compute_is_edited')

    def write(self, vals):
        if vals.get('planned_amount'):
            message = _("Planned Amount has been Updated: from"+str(self.planned_amount)+' to '+str(vals.get('planned_amount')))
            self.crossovered_budget_id.message_post(body=message)  # Logs message in parent Budget record
        return super(Crossoverbudgetlines, self).write(vals)

    @api.depends("crossovered_budget_id", "general_budget_id", "analytic_account_id", "budget_code")
    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        for record in self:
            computed_name = record.crossovered_budget_id.name
            if record.general_budget_id:
                computed_name += ' - ' + record.general_budget_id.name
            if record.analytic_account_id:
                computed_name += ' - ' + record.analytic_account_id.name
            if record.budget_code:
                computed_name += ' - ' + record.budget_code
            record.name = computed_name



class RevisionHistory(models.Model):
    _name = 'revision.history'
    _description = 'Revision History'



    name = fields.Char(string="Sequence", required=True, copy=False, default='/')
    budget_post_id = fields.Many2one('account.budget.post', string="Budgetary Position", required=True)
    budget_code = fields.Char(string="Budget Code", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", required=True)
    initial_allocate = fields.Float(string="Initial Allocation", required=True)
    additional_amount = fields.Float(string="Additional Amount")
    budget_id = fields.Many2one('crossovered.budget',string='Budget')
    revision_date = fields.Datetime(string='Revesion Date')
    
    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('revision.history') or 'New'
        return super(RevisionHistory, self).create(vals)
