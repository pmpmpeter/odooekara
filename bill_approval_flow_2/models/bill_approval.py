from odoo import models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup

class BillApprovalStepLog(models.Model):
    _name = 'bill.approval.step.log'
    _description = 'Bill Approval Step Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'

    bill_id = fields.Many2one('bill.approval', ondelete='cascade', required=True)
    step_name = fields.Char(string='Step')
    action = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('bill_created', 'Bill Created'),
        ('payment_created', 'Payment Created'),
    ])
    user_id = fields.Many2one('res.users', string='By', default=lambda s: s.env.uid)
    date = fields.Datetime(default=fields.Datetime.now)
    note = fields.Text(string='Note')
    account_move_id = fields.Many2one('account.move', string='Bill / JE')
    payment_id = fields.Many2one('account.payment', string='Payment')


class BillApproval(models.Model):
    _name = 'bill.approval'
    _description = 'Bill Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ── Reference ─────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Reference', default='New', readonly=True, copy=False,
    )

    # ── Supplier ───────────────────────────────────────────────────────────────
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    supplier_name = fields.Many2one(
        'res.partner', string='Supplier Name', required=True, tracking=True,
    )
    email = fields.Char(
        string='Email Address', related='supplier_name.email', readonly=True,
    )

    # ── Classification ─────────────────────────────────────────────────────────
    capex_opex = fields.Selection([
        ('capex', 'Capex'),
        ('opex', 'Opex'),
    ], string='Capex/Opex', tracking=True)

    expense_head_capex = fields.Many2one(
        'account.account',
        string='Expense/GL Head',
        domain="[('account_type', '!=', 'expense')]"
    )

    expense_head_opex = fields.Many2one(
        'account.account',
        string='Expense/GL Head',
        domain="[('account_type','=','expense')]"
    )

    expense_head = fields.Many2one(
        'account.account',
        string='Expense/GL Head',
        compute='_compute_expense_head',
        store=True
    )

    @api.depends('expense_head_capex', 'expense_head_opex', 'capex_opex')
    def _compute_expense_head(self):
        for rec in self:

            if rec.capex_opex == 'capex':
                rec.expense_head = rec.expense_head_capex

            elif rec.capex_opex == 'opex':
                rec.expense_head = rec.expense_head_opex

            else:
                rec.expense_head = False

    invoice_no = fields.Char(string='Document No')
    # invoice_type = fields.Selection([
    #     ('tax', 'Tax Invoice'),
    #     ('proforma', 'Proforma Invoice'),
    # ], string='Type of Document', tracking=True)
    document_type = fields.Many2one('bill.approval.document',string='Document Type',tracking=True)
    invoice_date = fields.Date(string='Document Date')

    # ── Amounts ────────────────────────────────────────────────────────────────
    taxable_value = fields.Float(string='Taxable Value')
    gst = fields.Float(string='GST')
    total_value = fields.Float(
        string='Total Invoice Value', tracking=True,
        compute='_compute_total_value', store=True,
    )

    @api.depends('taxable_value', 'gst')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.taxable_value + rec.gst

    # ── Others ─────────────────────────────────────────────────────────────────
    description = fields.Text(string='Description')
    attachment_link = fields.Char(string='Attachment Link')
    reviewer_comment = fields.Text(string='Reviewer Comment')
    # payment_status = fields.Char(string='Payment Status', tracking=True)
    # payment_date = fields.Date(string='Payment Date')

    # ═══════════════════════════════════════════════════════════════════════════
    # 3-LEVEL STATIC GROUP APPROVAL
    # L1 → group_bill_approver_l1
    # L2 → group_bill_approver_l2
    # L3 → group_bill_approver_l3
    # ═══════════════════════════════════════════════════════════════════════════

    approver_status = fields.Selection([
        ('draft',      'Draft'),
        ('waiting_l1', 'Waiting L1'),
        ('waiting_l2', 'Waiting L2'),
        ('waiting_l3', 'Waiting L3'),
        ('approved',   'Approved'),
        ('rejected',   'Rejected'),
    ], default='draft', string='Status', tracking=True, copy=False)

    # L1
    l1_status = fields.Selection([
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
    ], default='pending', string='L1 Status', tracking=True, copy=False)
    l1_user_id  = fields.Many2one('res.users', string='L1 By', readonly=True, copy=False)
    l1_date     = fields.Datetime(string='L1 Date', readonly=True, copy=False)
    l1_comment  = fields.Text(string='L1 Comment', copy=False)

    # L2
    l2_status = fields.Selection([
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
    ], default='pending', string='L2 Status', tracking=True, copy=False)
    l2_user_id  = fields.Many2one('res.users', string='L2 By', readonly=True, copy=False)
    l2_date     = fields.Datetime(string='L2 Date', readonly=True, copy=False)
    l2_comment  = fields.Text(string='L2 Comment', copy=False)

    # L3
    l3_status = fields.Selection([
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
    ], default='pending', string='L3 Status', tracking=True, copy=False)
    l3_user_id  = fields.Many2one('res.users', string='L3 By', readonly=True, copy=False)
    l3_date     = fields.Datetime(string='L3 Date', readonly=True, copy=False)
    l3_comment  = fields.Text(string='L3 Comment', copy=False)

    # ── Linked accounting records ───────────────────────────────────────────────
    step_log_ids = fields.One2many(
        'bill.approval.step.log', 'bill_id', string='History',
    )
    account_move_ids = fields.Many2many(
        'account.move',
        'bill_approval_move_rel', 'bill_id', 'move_id',
        string='Bills / Journal Entries',
    )
    payment_ids = fields.Many2many(
        'account.payment',
        'bill_approval_payment_rel', 'bill_id', 'payment_id',
        string='Payments',
    )
    move_count    = fields.Integer(compute='_compute_counts')
    payment_count = fields.Integer(compute='_compute_counts')

    @api.depends('account_move_ids', 'payment_ids')
    def _compute_counts(self):
        for rec in self:
            rec.move_count    = len(rec.account_move_ids)
            rec.payment_count = len(rec.payment_ids)

    # ── Button visibility (computed per user/group) ─────────────────────────────
    can_approve_l1    = fields.Boolean(compute='_compute_visibility')
    can_approve_l2    = fields.Boolean(compute='_compute_visibility')
    can_approve_l3    = fields.Boolean(compute='_compute_visibility')
    can_reject        = fields.Boolean(compute='_compute_visibility')
    can_create_bill   = fields.Boolean(compute='_compute_visibility')
    can_create_payment = fields.Boolean(compute='_compute_visibility')
    move_status = fields.Char(
        compute="_compute_latest_status",
        store=True,
        string="Doc Status"
    )

    payment_status_display = fields.Char(
        compute="_compute_latest_status",
        store=True,
        string="Payment Status"
    )

    payment_status_refresh = fields.Char(
        compute="_compute_latest_status",
        store=False,
        string="Refresh Trigger"
    )

    is_history_dup = fields.Boolean(
        compute='_compute_is_history',
        store=False
    )

    is_history = fields.Boolean(
        compute='_compute_is_history',
        store=True
    )

    @api.depends(
        'account_move_ids.state',
        'payment_ids.state'
    )
    def _compute_latest_status(self):
        Move = self.env['account.move']
        Payment = self.env['account.payment']

        for rec in self:
            move = Move.search(
                [('approval_id', '=', rec.id)],
                order='create_date desc, id desc',
                limit=1
            )

            payment = Payment.search(
                [('approval_id', '=', rec.id)],
                order='create_date desc, id desc',
                limit=1
            )
            move_state = move.state if move else False
            pay_state = payment.state if payment else False
            rec.move_status = move_state
            rec.payment_status_display = pay_state

            # Dummy value just to force execution
            rec.payment_status_refresh = str(fields.Datetime.now())

    @api.depends('move_status', 'payment_status_display')
    def _compute_is_history(self):
        for rec in self:
            value = (
                    rec.move_status == 'posted'
                    and (
                            not rec.payment_status_display
                            or rec.payment_status_display in ('paid', 'reconciled')
                    )
            )

            rec.is_history = value
            rec.is_history_dup = value

    @api.depends('approver_status')
    def _compute_visibility(self):
        uid = self.env.user

        def in_group(xml):
            try:
                return uid in self.env.ref(xml).users
            except Exception:
                return False

        l1 = in_group('bill_approval_flow_2.group_bill_approver_l1')
        l2 = in_group('bill_approval_flow_2.group_bill_approver_l2')
        l3 = in_group('bill_approval_flow_2.group_bill_approver_l3')

        for rec in self:
            s = rec.approver_status
            rec.can_approve_l1     = s == 'waiting_l1' and l1
            rec.can_approve_l2     = s == 'waiting_l2' and l2
            rec.can_approve_l3     = s == 'waiting_l3' and l3
            rec.can_reject         = s in ('waiting_l1', 'waiting_l2', 'waiting_l3') \
                                     and (l1 or l2 or l3)
            rec.can_create_bill    = s in ('approved', 'done')
            rec.can_create_payment = s in ('approved', 'done')

    # ── Sequence ───────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('bill.approval') or 'BA-0001'
                )
        return super().create(vals_list)



    # ─────────────────────────────────────────────────────────────
    # Activity Helpers
    # ─────────────────────────────────────────────────────────────

    def _create_approval_activity(self, group_xmlid, note):
        self.ensure_one()

        activity_type = self.env.ref(
            'bill_approval_flow_2.mail_activity_type_bill_approval'
        )

        group = self.env.ref(group_xmlid)

        for user in group.users:

            existing = self.activity_ids.filtered(
                lambda a:
                a.user_id.id == user.id and
                a.activity_type_id.id == activity_type.id
            )

            if not existing:
                self.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=user.id,
                    note=note,
                )

    def _mark_current_activity_done(self, feedback=None):
        self.ensure_one()

        activity_type = self.env.ref(
            'bill_approval_flow_2.mail_activity_type_bill_approval'
        )

        activities = self.activity_ids.filtered(
            lambda a:
            a.user_id.id == self.env.user.id and
            a.activity_type_id.id == activity_type.id
        )

        activities.action_feedback(
            feedback=feedback or 'Done'
        )

    def action_submit(self):
        self.ensure_one()

        if self.approver_status != 'draft':
            raise UserError(_('Only Draft records can be submitted.'))

        self.write({
            'approver_status': 'waiting_l1',
            'l1_status': 'pending',
            'l2_status': 'pending',
            'l3_status': 'pending',
        })

        # Create L1 Activity
        self._create_approval_activity(
            'bill_approval_flow_2.group_bill_approver_l1',
            'Level 1 approval required.'
        )

        self.message_post(
            body=Markup(
                _('🚀 <b>Submitted for Approval</b> — Awaiting <b>Level 1</b>.')
            )
        )

        self._notify_group(
            'bill_approval_flow_2.group_bill_approver_l1',
            'Level 1'
        )

    # ── L1 ─────────────────────────────────────────────────────

    def action_approve_l1(self):
        self.ensure_one()

        self._check_group(
            'bill_approval_flow_2.group_bill_approver_l1',
            'Level 1'
        )

        return self._open_wizard(
            'approve_l1',
            'Level 1 Approval — Add Comment'
        )

    def _do_approve_l1(self, comment):

        self._mark_current_activity_done('L1 Approved')

        self.write({
            'l1_status': 'approved',
            'l1_user_id': self.env.uid,
            'l1_date': fields.Datetime.now(),
            'l1_comment': comment,
            'approver_status': 'waiting_l2',
        })

        # Create L2 Activity
        self._create_approval_activity(
            'bill_approval_flow_2.group_bill_approver_l2',
            'Level 2 approval required.'
        )

        self._log('Level 1 Approval', 'approved', comment)

        body = _(
            '✅ <b>L1 Approved</b> by <b>%s</b> — Awaiting <b>Level 2</b>.'
        ) % self.env.user.name

        if comment:
            body += '<br/><i>%s</i>' % comment

        self.message_post(body=Markup(body))

        self._notify_group(
            'bill_approval_flow_2.group_bill_approver_l2',
            'Level 2'
        )

    # ── L2 ─────────────────────────────────────────────────────

    def action_approve_l2(self):
        self.ensure_one()

        self._check_group(
            'bill_approval_flow_2.group_bill_approver_l2',
            'Level 2'
        )

        return self._open_wizard(
            'approve_l2',
            'Level 2 Approval — Add Comment'
        )

    def _do_approve_l2(self, comment):

        self._mark_current_activity_done('L2 Approved')

        self.write({
            'l2_status': 'approved',
            'l2_user_id': self.env.uid,
            'l2_date': fields.Datetime.now(),
            'l2_comment': comment,
            'approver_status': 'waiting_l3',
        })

        # Create L3 Activity
        self._create_approval_activity(
            'bill_approval_flow_2.group_bill_approver_l3',
            'Final approval required.'
        )

        self._log('Level 2 Approval', 'approved', comment)

        body = _(
            '✅ <b>L2 Approved</b> by <b>%s</b> — Awaiting <b>Level 3</b>.'
        ) % self.env.user.name

        if comment:
            body += '<br/><i>%s</i>' % comment

        self.message_post(body=Markup(body))

        self._notify_group(
            'bill_approval_flow_2.group_bill_approver_l3',
            'Level 3'
        )

    # ── L3 (Final) ─────────────────────────────────────────────

    def action_approve_l3(self):
        self.ensure_one()

        self._check_group(
            'bill_approval_flow_2.group_bill_approver_l3',
            'Level 3'
        )

        return self._open_wizard(
            'approve_l3',
            'Level 3 — Final Approval'
        )

    def _do_approve_l3(self, comment):

        self._mark_current_activity_done('Final Approved')

        self.write({
            'l3_status': 'approved',
            'l3_user_id': self.env.uid,
            'l3_date': fields.Datetime.now(),
            'l3_comment': comment,
            'approver_status': 'approved',
        })

        self._log('Level 3 Approval', 'approved', comment)

        body = _(
            '✅ <b>L3 Approved</b> by <b>%s</b><br/>'
            '🎉 <b>Fully Approved!</b> Bill and Payment can now be created.'
        ) % self.env.user.name

        if comment:
            body += '<br/><i>%s</i>' % comment

        self.message_post(body=Markup(body))

    # ── Reject ─────────────────────────────────────────────────

    def action_reject(self):
        self.ensure_one()

        return self._open_wizard(
            'reject',
            'Reject — Provide Reason'
        )

    def _do_reject(self, reason):

        self._mark_current_activity_done('Rejected')

        level_label = {
            'waiting_l1': 'Level 1',
            'waiting_l2': 'Level 2',
            'waiting_l3': 'Level 3',
        }.get(self.approver_status, '')

        self.write({
            'approver_status': 'rejected',
            'reviewer_comment': reason,
        })

        self._log(
            f'{level_label} Rejection',
            'rejected',
            reason
        )

        body = _(
            '❌ <b>Rejected</b> at <b>%s</b> by <b>%s</b>'
        ) % (
                   level_label,
                   self.env.user.name
               )

        if reason:
            body += '<br/><b>Reason:</b> %s' % reason

        self.message_post(body=Markup(body))

    def action_view_bills(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills & Journals',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('approval_id', '=', self.id)],
            'context': {
                'default_approval_id': self.id,
                'default_move_type': 'in_invoice',
            },
        }
    def action_view_payments(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('approval_id', '=', self.id)],
            'context': {
                'default_approval_id': self.id,
            },
        }

    def action_open_bill(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'in_invoice',
                'default_approval_id': self.id,
                'default_partner_id': self.supplier_name.id,
                'default_narration': self.description,
            'default_invoice_date': self.invoice_date}
        }

    def action_open_invoice(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'out_invoice',
                'default_approval_id': self.id,
                'default_partner_id': self.supplier_name.id,
            'default_narration': self.description,
            'default_invoice_date': self.invoice_date}
        }

    def action_open_credit_notes(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Notes',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'out_refund',
                'default_approval_id': self.id,
                'default_partner_id': self.supplier_name.id,
            'default_narration': self.description}
        }

    def action_open_debit_notes(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Debit Notes',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'in_refund',
                'default_approval_id': self.id,
                'default_partner_id': self.supplier_name.id,
            'default_narration': self.description}
        }

    def action_open_journal(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journals',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_type': 'entry',
                'default_approval_id': self.id,  # ✅ only this
                'default_narration': self.description
            }
        }
    def action_open_credit_expense(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Card Expense',
            'res_model': 'account.move',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_move_type':'entry','default_is_payment_approval':True,'default_approval_id': self.id,'default_narration': self.description}
        }
    def action_open_credit_card_payment(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Card Payment',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_is_credit_payment': True,'is_internal_transfer': True,'default_payment_type':'outbound','default_approval_id': self.id,}
        }
    def action_open_payment(self):
        self.ensure_one()
        # self.hide_bill_creation = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_payment_type':'outbound','default_approval_id': self.id,}
        }


    # ── Create Bill ─────────────────────────────────────────────────────────────
    def action_create_bill(self):
        self.ensure_one()
        if self.approver_status not in ('approved', 'done'):
            raise UserError(_('Bill can only be created after full approval.'))
        return self._open_wizard('bill', 'Create Bill / Journal Entry')

    def _do_create_bill(self, journal_type, partner_id, account_id, note):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', journal_type),
             ('company_id', '=', self.env.company.id)],
            limit=1,
        )
        if not journal:
            raise UserError(_('No %s journal found.', journal_type))

        move_type = {
            'purchase': 'in_invoice',
            'sale':     'out_invoice',
            'general':  'entry',
        }.get(journal_type, 'in_invoice')

        move_vals = {
            'move_type':    move_type,
            'journal_id':   journal.id,
            'invoice_date': self.invoice_date or fields.Date.today(),
            'ref':          self.invoice_no or self.name,
            'narration':    note or self.description,
            'partner_id':   partner_id or self.supplier_name.id,
        }
        aid = account_id or (self.expense_head.id if self.expense_head else False)
        if move_type != 'entry' and aid:
            move_vals['invoice_line_ids'] = [(0, 0, {
                'name':        self.description or self.expense_head.name or 'Bill Line',
                'quantity':    1,
                'price_unit':  self.taxable_value,
                'account_id':  aid,
                'tax_ids':     [],
            })]

        move = self.env['account.move'].create(move_vals)
        self.account_move_ids = [(4, move.id)]
        self._log('Bill Created', 'bill_created', note, move_id=move.id)
        self.message_post(body=_(
            '🧾 <b>Bill Created:</b> <a href="/web#model=account.move&id=%s">%s</a>'
            ' by <b>%s</b>',
            move.id, move.name, self.env.user.name,
        ))
        return move

    # ── Register Payment ────────────────────────────────────────────────────────
    def action_create_payment(self):
        self.ensure_one()
        if self.approver_status not in ('approved', 'done'):
            raise UserError(_('Payment can only be registered after full approval.'))
        return self._open_wizard('payment', 'Register Payment')

    def _do_create_payment(self, journal_id, amount, note):
        self.ensure_one()
        journal = (
            self.env['account.journal'].browse(journal_id)
            if journal_id
            else self.env['account.journal'].search(
                [('type', 'in', ['bank', 'cash']),
                 ('company_id', '=', self.env.company.id)],
                limit=1,
            )
        )
        if not journal:
            raise UserError(_('No payment journal found.'))

        payment = self.env['account.payment'].create({
            'payment_type':  'outbound',
            'partner_type':  'supplier',
            'partner_id':    self.supplier_name.id,
            'journal_id':    journal.id,
            'amount':        amount or self.total_value,
            # 'date':          payment_date or fields.Date.today(),
            'ref':           self.invoice_no or self.name,
            'memo':          note or self.description,
        })
        self.write({
            'payment_ids':    [(4, payment.id)],
            # 'payment_date':   payment_date or fields.Date.today(),
            # 'payment_status': 'Payment Created',
            'approver_status': 'done',
        })
        self._log('Payment Registered', 'payment_created', note, pay_id=payment.id)
        self.message_post(body=_(
            '💳 <b>Payment Registered:</b> %s %s via <b>%s</b> by <b>%s</b>',
            self.env.company.currency_id.symbol,
            amount, journal.name, self.env.user.name,
        ))
        return payment

    # ── Reset ───────────────────────────────────────────────────────────────────
    def action_reset_to_draft(self):
        self.write({
            'approver_status': 'draft',
            'l1_status': 'pending', 'l1_user_id': False,
            'l1_date': False,       'l1_comment': False,
            'l2_status': 'pending', 'l2_user_id': False,
            'l2_date': False,       'l2_comment': False,
            'l3_status': 'pending', 'l3_user_id': False,
            'l3_date': False,       'l3_comment': False,
        })
        self.message_post(body=_('🔄 Reset to Draft.'))

    # ── Smart button links ──────────────────────────────────────────────────────
    def action_view_moves(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills / Journal Entries',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.account_move_ids.ids)],
        }

    def action_view_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }

    # ── Internal helpers ────────────────────────────────────────────────────────
    def _open_wizard(self, wizard_type, title):
        return {
            'type': 'ir.actions.act_window',
            'name': _(title),
            'res_model': 'bill.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bill_id':    self.id,
                'default_wizard_type': wizard_type,
                'default_partner_id': self.supplier_name.id,
                'default_amount':     self.total_value,
                'default_account_id': self.expense_head.id if self.expense_head else False,
            },
        }

    def _check_group(self, xmlid, label):
        try:
            grp = self.env.ref(xmlid)
        except Exception:
            raise UserError(_('Group %s not found.', xmlid))
        if self.env.user not in grp.users:
            raise UserError(_('Only %s users can perform this action.', label))

    def _notify_group(self, xmlid, label):
        try:
            grp = self.env.ref(xmlid)
            pids = grp.users.mapped('partner_id').ids
            if pids:
                self.message_post(
                    body=_('👤 <b>Action Required — %s:</b> Please review and approve.', label),
                    partner_ids=pids,
                )
        except Exception:
            pass

    def _log(self, step_name, action, note, move_id=None, pay_id=None):
        vals = {
            'bill_id':   self.id,
            'step_name': step_name,
            'action':    action,
            'user_id':   self.env.uid,
            'note':      note,
        }
        if move_id:
            vals['account_move_id'] = move_id
        if pay_id:
            vals['payment_id'] = pay_id
        self.env['bill.approval.step.log'].create(vals)


class approvalDocument(models.Model):
    _name = 'bill.approval.document'

    name = fields.Char(required=True)