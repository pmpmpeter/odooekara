from odoo import models, fields, api
from datetime import datetime

class CashManagement(models.Model):
    _name = "cash.management"
    _description = "Cash Requirement Report"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter for tracking

    name = fields.Char(string="Reference", copy=False, readonly=True)

    submit_by = fields.Many2one('hr.employee',string="Submitted By",tracking=True,copy=False)
    submitted_date = fields.Datetime(string="Submitted Date", readonly=True,tracking=True,copy=False,default=datetime.now())
    submitted_file = fields.Binary(string="Submitted CRR Report",attachment=True,copy=False,required=True)
    submitted_name = fields.Char(string="Submitted File Name", attachment=True,copy=False)
    tax_entity = fields.Selection([('entity1', 'Tax Entity1'),
                                 ('entity2', 'Tax Entity2'),
                                 ('both', 'Both')], string="Tax Entity",default='entity1', tracking=True,copy=False)
    tax_entity_1 = fields.Many2one('res.users', string="Tax Entity 1 User",copy=False)
    tax_entity_2 = fields.Many2one('res.users', string="Tax Entity 2 User",copy=False)
    tax_entity_1_amount = fields.Float(string="Tax Entity 1 Amount",copy=False,tracking=True,)
    tax_entity_2_amount = fields.Float(string="Tax Entity 2 Amount",copy=False,tracking=True,)

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved')
    ], string="Approval Status", default='draft', tracking=True,copy=False)

    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True,copy=False)
    approved_date = fields.Datetime(string="Approved Date", readonly=True,copy=False)
    approved_file = fields.Binary(string="Approved CRR Report",copy=False)
    approved_name = fields.Char(string="Approved CRR Report",copy=False)
    revision_reason = fields.Text(string="Revision Reasons", readonly=True, default="")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company)
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)

    def action_submit(self):
        for rec in self:
            rec.submitted_date = datetime.now()
            rec.submit_by = self.env.user.employee_id.id
            rec.approval_status = 'submitted'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
                vals['name'] = self.env['ir.sequence'].next_by_code('cash.management')
        return super().create(vals_list)

    @api.depends('approval_document.type_id.state','approval_document.line_ids.state')
    def compute_approval_state(self):
        for record in self:
            print('aaaaaaaaaaaaaaaaaaaaa')
            if record.approval_document:
                print('sssssssssssssssssss')
                line_states = record.approval_document.line_ids.mapped('state')
                if all(state == 'Draft' for state in line_states):
                    record.approval_state = 'Waiting For Approval'
                elif 'Waiting for Approval' in line_states:
                    waiting_lines = record.approval_document.line_ids.filtered(lambda l: l.state == 'Waiting for Approval')
                    if waiting_lines:
                        print('gggggggggggggggggggggg')
                        record.approval_state = f"Waiting for {', '.join(waiting_lines.mapped('name'))} Approval"
                elif all(state == 'Approved' for state in line_states):
                    record.approval_state = 'Approved'
                elif 'Refused' in line_states:
                    record.approval_state = 'Rejected'
                elif 'Cancel' in line_states:
                    record.approval_state = 'Cancelled'
            else:
                rec = self.env['multi.approval.type'].sudo().search(
                    [('model_id', '=', 'cash.management'), ('state', '=', 'confirm')], limit=1)
                if rec:
                    record.approval_state = 'To Submit for Approval'
                else:
                    record.approval_state = 'Not Applicable'
