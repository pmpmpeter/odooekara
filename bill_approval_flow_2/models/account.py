from odoo import models, api, _,fields
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_id = fields.Many2one('bill.approval', string="Approvals")

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

    # ---------------- BILL LIMIT CHECK ----------------
    def _check_bill_limit(self, approval):
        self.ensure_one()

        moves = self.env['account.move'].search([
            ('approval_id', '=', approval.id),('move_type', '!=', 'entry'),
        ])

        total = sum(moves.mapped('amount_total'))

        if total > approval.total_value:
            raise UserError(_(
                "Bill limit exceeded!\nAllowed: %s\nUsed: %s"
            ) % (approval.total_value, total))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec, vals in zip(records, vals_list):
            if vals.get('approval_id'):
                approval = self.env['bill.approval'].browse(vals['approval_id'])
                rec._copy_approval_attachments(vals['approval_id'])
                rec._check_bill_limit(approval)

        return records

    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if rec.approval_id:
                rec._copy_approval_attachments(rec.approval_id.id)
                rec._check_bill_limit(rec.approval_id)

        return res

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    approval_id = fields.Many2one('bill.approval', string='Bill Approval')

    def _copy_approval_attachments(self, approval_id):
        if not approval_id:
            return

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'bill.approval'),
            ('res_id', '=', approval_id)
        ])

        for att in attachments:
            existing = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.payment'),
                ('res_id', '=', self.id),
                ('name', '=', att.name),
            ], limit=1)

            if not existing:
                att.copy({
                    'res_model': 'account.payment',
                    'res_id': self.id,
                })

    # ---------------- PAYMENT LIMIT CHECK ----------------
    def _check_payment_limit(self, approval):
        self.ensure_one()

        payments = self.env['account.payment'].search([
            ('approval_id', '=', approval.id)
        ])

        total = sum(payments.mapped('amount'))

        if total > approval.total_value:
            raise UserError(_(
                "Payment limit exceeded!\nAllowed: %s\nUsed: %s"
            ) % (approval.total_value, total))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec, vals in zip(records, vals_list):
            if vals.get('approval_id'):
                approval = self.env['bill.approval'].browse(vals['approval_id'])
                rec._copy_approval_attachments(vals['approval_id'])
                rec._check_payment_limit(approval)

        return records

    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if rec.approval_id:
                rec._copy_approval_attachments(rec.approval_id.id)
                rec._check_payment_limit(rec.approval_id)

        return res