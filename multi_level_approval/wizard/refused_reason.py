##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import fields, models


class RefusedReason(models.TransientModel):
    _name = "refused.reason"
    _description = "Refused Reason"

    reason = fields.Text(required=True)

    def action_reason_apply(self):

        approval = self.env["multi.approval"].browse(self.env.context.get("active_ids"))
        return approval.action_refuse(reason=self.reason)

class ApproveReason(models.TransientModel):
    _name = "approve.reason"
    _description = "Approve Reason"

    reason = fields.Text(required=True)

    def action_approve_reason_apply(self):
        active_id = self.env.context.get('expense')
        expense_id = self.env['hr.expense.sheet'].browse(active_id)
        user = self.env.user
        current_datetime = fields.Datetime.now()
        approval_entry = f"User: {user.name}, Reason: {self.reason}, Date: {current_datetime}\n"
        if expense_id.reason_approved:
            expense_id.reason_approved += approval_entry
        else:
            expense_id.reason_approved = approval_entry

        # approval = self.env["multi.approval"].browse(self.env.context.get("active_ids"))
        return True
