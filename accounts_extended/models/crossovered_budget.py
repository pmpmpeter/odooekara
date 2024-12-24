from odoo import api, fields, models, _, Command
from odoo.osv import expression

class BudgetInherit(models.Model):
    _inherit = 'crossovered.budget'

    state = fields.Selection(selection_add=[
        ('to approve', 'To Approve')],
        string="Status",
        index=True, required=True, readonly=True, copy=False, tracking=True,
        ondelete={'to approve':'set default'},
        default='draft')
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    revision_reason = fields.Text(string="Revision Reasons", readonly=True, default="")


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

    def action_budget_done(self):
        for rec in self.crossovered_budget_line:
            if not rec.is_budget_code:
                rec.is_budget_code = True
                rec.budget_code = self.env['ir.sequence'].next_by_code('budget.code')
        return super().action_budget_done()


class Crossoverbudgetlines(models.Model):
    _inherit='crossovered.budget.lines'

    name = fields.Char(compute="_compute_line_name", store=True)
    budget_code = fields.Char('Budget Code')
    is_budget_code = fields.Boolean('Is Budget Code')


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
