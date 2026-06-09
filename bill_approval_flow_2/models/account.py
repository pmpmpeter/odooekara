from odoo import models, api, _,fields,exceptions
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_id = fields.Many2one('bill.approval',string="Approvals")

    def _copy_approval_attachments(self, approval_id):
        if not approval_id:
            return

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'bill.approval'),
            ('res_id', '=', approval_id)
        ])

        for att in attachments:
            existing = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', self.id),
                ('name', '=', att.name),
            ], limit=1)

            if not existing:
                att.copy({
                    'res_model': 'account.move',
                    'res_id': self.id,
                })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for record, vals in zip(records, vals_list):
            approval_id = vals.get('approval_id')
            record._copy_approval_attachments(approval_id)

        return records

    def write(self, vals):
        res = super().write(vals)

        if vals.get('approval_id'):
            for record in self:
                record._copy_approval_attachments(record.approval_id.id)

        return res

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    approval_id = fields.Many2one(
        'bill.approval',
        string='Bill Approval'
    )

