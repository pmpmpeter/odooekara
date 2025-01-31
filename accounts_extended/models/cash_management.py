from odoo import models, fields, api
from datetime import datetime

class CashManagement(models.Model):
    _name = "cash.management"
    _description = "Cash Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter for tracking

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True, 
                       default=lambda self: self.env['ir.sequence'].next_by_code('cash.management'))
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user, readonly=True)
    created_date = fields.Datetime(string="Created Date", default=datetime.now(), readonly=True)

    submit_by = fields.Many2one('hr.employee',string="Submitted By",tracking=True,copy=False)
    submitted_date = fields.Datetime(string="Submitted Date", readonly=True,tracking=True,copy=False)
    submitted_file = fields.Binary(string="Submitted File", attachment=True,copy=False,required=True)
    submitted_name = fields.Char(string="Submitted File Name", attachment=True,copy=False)

    tax_entity_1 = fields.Many2one('res.users', string="Tax Entity(1)",copy=False)
    tax_entity_2 = fields.Many2one('res.users', string="Tax Entity(2)",copy=False)

    amount_1 = fields.Float(string="Amount (1)",copy=False)
    amount_2 = fields.Float(string="Amount (2)",copy=False)
    both_amount= fields.Float(string="If Both Give Shared amount",copy=False)

    approval_status = fields.Selection([
        ('draft', 'Draft'),
        # ('submitted', 'Submitted'),
        ('to approve', 'To Approve'),
        # ('torevised', 'Revised')
        ('approved', 'Approved')
    ], string="Approval Status", default='draft', tracking=True,copy=False)

    approved_by = fields.Many2one('res.users', string="Approved By", readonly=True,copy=False)
    approved_date = fields.Datetime(string="Approved Date", readonly=True,copy=False)
    approved_file = fields.Binary(string="Approved File",copy=False)
    approved_name = fields.Char(string="Approved File Name",copy=False)
    revision_reason = fields.Text(string="Revision Reasons", readonly=True, default="")

    def action_submit(self):
        for rec in self:
            rec.submitted_date = datetime.now()
            rec.submit_by = self.env.user.employee_id.id
            rec.approval_status = 'submitted'
