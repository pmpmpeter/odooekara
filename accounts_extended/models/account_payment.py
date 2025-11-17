from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from datetime import timedelta
import pdb

class AccountReimbursementLine(models.Model):
    _name = 'payment.other.charges.lines'
    _description = 'Payment Other Charges'

    payment_id = fields.Many2one('account.payment', string="Payment Reference", readonly=True)
    account_id = fields.Many2one('account.account', string="Account")
    other_charge = fields.Float('Amount')

class AccountPayment(models.Model):
    _inherit = "account.payment"

    utr_number = fields.Char('UTR Number', copy=False)
    is_utr_updated = fields.Boolean(string='UTR Updated',copy=False)
    old_utr_number = fields.Char('OLD UTR Number', copy=False)
    is_fund_requsiting = fields.Boolean(string='Fund Requisition', copy=False)
    is_contra_payment = fields.Boolean(string='Contra Payment', copy=False)
    is_credit_payment = fields.Boolean(string='Credit Payment', copy=False)
    approval_state = fields.Char(string='Approval Status', compute='compute_approval_state', store=True, copy=False,
                                 tracking=True)
    approval_document = fields.Many2one('multi.approval', string='Approval Record', copy=False)
    reason_approved = fields.Text(string='Approval comments', copy=False)
    partner_cl_balance = fields.Float(compute='_get_partner_cl_balance', string='Partner Balance')
    closing_balance = fields.Float(compute='_get_closing_balance', string='Closing Balance')
    type = fields.Selection([
        ("capex", "Capex"),
        ("opex", "Opex")], default='opex', string="Capex/Opex")
    payment_purchase_id = fields.Many2one('purchase.order',copy=False, string='Purchase Order')
    recurring = fields.Boolean(string='Recurring Payment', copy=False)
    recurring_days = fields.Integer(string='Recurring Days', default="1", copy=False)
    recurring_until_date = fields.Date(string='Recurring Until Date', copy=False)
    is_cheque_details_freeze = fields.Boolean(string='Is Cheque Details Freezed')
    other_charges_lines = fields.One2many('payment.other.charges.lines', 'payment_id', string="Other Charges", copy=True)


    @api.model
    def _get_trigger_fields_to_synchronize(self):
        return (
            'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
            'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'journal_id', 'other_charges_lines'
        )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        self.ensure_one()

        # Call super with same signature so parent logic can use inputs if needed
        res = super(AccountPayment, self)._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals, force_balance=force_balance
        )

        if not self.other_charges_lines:
            return res

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set "
                "either on the %s payment method in the %s journal."
            ) % (self.payment_method_line_id.name, self.journal_id.display_name))

        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x.get('amount_currency', 0.0) for x in write_off_line_vals_list)
        write_off_balance = sum(x.get('balance', 0.0) for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        if not write_off_line_vals and force_balance is not None:
            sign = 1 if liquidity_amount_currency > 0 else -1
            liquidity_balance = sign * abs(force_balance)
        else:
            liquidity_balance = liquidity_amount_currency

        counterpart_balance = -liquidity_balance
        counterpart_amount_currency = -liquidity_amount_currency

        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

        line_vals_list = []
        other_charges_list = []

        for line in self.other_charges_lines.filtered(lambda l: l.account_id and l.payment_id.state == 'draft'):
            # skip zero amounts
            if not line.other_charge:
                continue

            # Determine amount sign based on payment_type
            if self.payment_type == 'inbound':
                other_amount_1 = line.other_charge
            elif self.payment_type == 'outbound':
                other_amount_1 = -line.other_charge
            else:
                other_amount_1 = 0.0

            # Compute balance for this other-charge line (preserve original force_balance behaviour)
            if not write_off_line_vals and force_balance is not None:
                sign = 1 if other_amount_1 > 0 else -1
                other_balance_1 = sign * abs(force_balance)
            else:
                other_balance_1 = other_amount_1

            # decrease counterpart by this other charge
            # counterpart_amount_currency -= other_amount_1
            # counterpart_balance -= other_balance_1

            liquidity_amount_currency -= other_amount_1
            liquidity_balance -= other_balance_1

            other_charges_vals = {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': other_amount_1,
                'debit': other_balance_1 if other_balance_1 > 0.0 else 0.0,
                'credit': -other_balance_1 if other_balance_1 < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': line.account_id.id,
                'other_charges_payment_line': True,
            }
            other_charges_list.append(other_charges_vals)

        # Liquidity line (always included)
        liquidity_vals = {
            'name': liquidity_line_name,
            'date_maturity': self.date,
            'amount_currency': liquidity_amount_currency,
            'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
            'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.outstanding_account_id.id,
        }
        line_vals_list.append(liquidity_vals)

        # Receivable / Payable line (adjusted by other charges)
        ar_ap_vals = {
            'name': counterpart_line_name,
            'date_maturity': self.date,
            'amount_currency': counterpart_amount_currency,
            'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
            'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.destination_account_id.id,
        }
        line_vals_list.append(ar_ap_vals)

        # Attach other charge lines (if any)
        if other_charges_list:
            line_vals_list.extend(other_charges_list)

        return line_vals_list


    # def action_update_account_payment_outstanding_payment(self):
    #     ###Update Outstanding Payments
    #     records = self.env['account.payment'].browse(self._context.get('active_ids', False))
    #     for record in records:
    #         # pdb.set_trace()
    #         for line in record.move_id.line_ids.filtered(lambda l: l.account_id.account_type in ['asset_cash']):
    #             domain1 =[('code','=', 100204),('company_id','=', record.journal_id.company_id.id)]
    #             coa_id = self.env['account.account'].sudo().search(domain1, order='id desc', limit=1)
    #             # print("dffrt45555556". record.name)
    #             # pdb.set_trace()
    #             if coa_id:
    #                 print("Case1222222222222222222222222222222222222222")
    #             line.write({'account_id': coa_id.id})



    def print_cheque_format(self):
        return self.env.ref('odoo_print_cheque.print_cheque_payment').report_action(self)

    def action_freeze_cheque_details(self):
        for rec in self:
            rec.is_cheque_details_freeze = True

    def send_vendor_mail(self):
        form_view = self.env.ref('mail.email_compose_message_wizard_form')

        ctx = {
            'default_model': 'account.payment',
            'default_res_ids': self.ids,
            'default_template_id': self.env.ref('account.mail_template_data_payment_receipt').id,
            'default_attachment_ids': [],
            'force_email': True,
        }

        return {
            'name': _('Send By Mail'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'views': [(form_view.id, 'form')],
            'target': 'new',
            'context': ctx
        }
        return self.env.ref('account.account_send_payment_receipt_by_email_action')

    def action_create_recurring_payments(self):
        for rec in self:
            print("rec", rec)
            if rec.recurring and rec.recurring_days > 0 and rec.recurring_until_date and rec.state == 'posted':
                print("if condition")
                current_date = fields.Date.today()
                next_payment_date = rec.date + timedelta(days=rec.recurring_days)
                while next_payment_date <= rec.recurring_until_date:
                    print("while condition")
                    print(next_payment_date, "nexx")
                    if next_payment_date == current_date:
                        print(next_payment_date,"nex11111")
                        new_payment = rec.copy(default={
                            'state': 'draft',
                            'date': next_payment_date,
                            'recurring': True,  # Disable recurring for the copied record
                            'recurring_days': rec.recurring_days,
                            'recurring_until_date': rec.recurring_until_date,
                        })
                        print(new_payment, "new_payment")
                    next_payment_date += timedelta(days=rec.recurring_days)

    @api.model
    def create_batch_payment(self):
        res = super().create_batch_payment()
        print(self,'llllllllll')
        check_numbers = self.mapped('cheque_number')
        if len(set(check_numbers)) == 1:
            same_check_number = check_numbers[0]
        else:
            raise UserError("Selected payments must have the same cheque number.")
        batch_payment_id = self.env['account.batch.payment'].browse(res.get('res_id'))
        print(batch_payment_id,'hqqqq')
        batch_payment_id['cheque_number'] = same_check_number
        return res

    def _get_closing_balance(self):
        closing_balance = 0
        query = """
            select sum(balance) as balance FROM account_move_line aml 
            join account_move am on am.id=aml.move_id 
            where am.state='posted' and aml.account_id=%s
            """
        params = tuple(self.journal_id.default_account_id.ids)
        data_get8 = self.env.cr.execute(query, params)
        lines8 = self.env.cr.dictfetchall()
        if (lines8[0].get('balance') != None):
            closing_balance = lines8[0].get('balance') or 0
        for record in self:
            # pdb.set_trace()
            record.closing_balance = closing_balance

    @api.onchange('partner_id')
    def _get_partner_cl_balance(self):
        partner_cl_balance = 0
        if self.partner_id:
            query = """
                select sum(balance) as balance FROM account_move_line aml 
                join account_move am on am.id=aml.move_id 
                join account_account ac on ac.id=aml.account_id 
                where am.state='posted' and aml.partner_id=%s and ac.account_type in ('asset_receivable', 'liability_payable')
                """
            params = tuple(self.partner_id.ids)
            data_get8 = self.env.cr.execute(query, params)
            lines8 = self.env.cr.dictfetchall()
            if (lines8[0].get('balance') != None):
                partner_cl_balance = lines8[0].get('balance') or 0
            for record in self:
                record.partner_cl_balance = partner_cl_balance
        else:
            self.partner_cl_balance = 0

    def action_update_utr_number(self):
        for rec in self:
            if rec.state == 'posted' and rec.utr_number:
                if rec.move_id:
                    for line in rec.move_id.line_ids:
                        if line.account_id == rec.outstanding_account_id:
                            if rec.old_utr_number:
                                line.name = line.name.replace(rec.old_utr_number, rec.utr_number)
                            else:
                                line.name += ('-' + rec.utr_number)
                    rec.old_utr_number = rec.utr_number
                    rec.is_utr_updated = True

    @api.depends('approval_document.type_id.state', 'approval_document.line_ids.state')
    def compute_approval_state(self):
        for record in self:
            if record.approval_document:
                line_states = record.approval_document.line_ids.mapped('state')
                if all(state == 'Draft' for state in line_states):
                    record.approval_state = 'Waiting For Approval'
                elif 'Waiting for Approval' in line_states:
                    waiting_lines = record.approval_document.line_ids.filtered(
                        lambda l: l.state == 'Waiting for Approval')
                    if waiting_lines:
                        record.approval_state = f"Waiting for {', '.join(waiting_lines.mapped('name'))} Approval"
                elif all(state == 'Approved' for state in line_states):
                    record.approval_state = 'Approved'
                elif 'Refused' in line_states:
                    record.approval_state = 'Rejected'
                elif 'Cancel' in line_states:
                    record.approval_state = 'Cancelled'
            else:
                rec = self.env['multi.approval.type'].sudo().search(
                    [('model_id', '=', 'account.payment'), ('state', '=', 'confirm')], limit=1)
                if rec:
                    record.approval_state = 'To Submit for Approval'
                else:
                    record.approval_state = 'Not Applicable'

    @api.depends('partner_id', 'journal_id', 'destination_journal_id')
    def _compute_is_internal_transfer(self):
        for payment in self:
            if 'is_internal_transfer' in self.env.context:
                if self.env.context['is_internal_transfer']:
                    payment.is_internal_transfer = True
            else:
                payment.is_internal_transfer = payment.partner_id \
                                               and payment.partner_id == payment.journal_id.company_id.partner_id \
                                               and payment.destination_journal_id

    @api.onchange('type')
    def onchange_type(self):
        for rec in self:
            # print('rrrrrr',rec.type,rec.move_id._origin.id)
            move = self.env['account.move'].sudo().search([('id', '=', rec.move_id._origin.id)])
            move.expense_type = rec.type

    def action_post(self):
        for pay in self:
            if pay.state != 'approved' and pay.payment_type == 'outbound':
                raise ValidationError('You cannot confirm payments that are not Approved.')
            # if pay.payment_method_line_id.name == 'Cheque' and not pay.is_cheque_cleared and pay.payment_type == 'outbound':
            #     raise UserError(_("Alert !! Kindly Clear the cheque"))
            # if not pay.utr_number and (pay.payment_type == 'outbound' or pay.is_fund_requsiting):
            #     raise UserError(_("Alert !! Kindly update the UTR Number."))
            if pay.amount <= 0:
                raise UserError(_("Alert !! Amount should be greated than Zero"))
            if pay.move_id and pay.utr_number:
                for line in pay.move_id.line_ids:
                    if line.account_id == pay.outstanding_account_id:
                        line.name += ('-' + pay.utr_number)
                pay.old_utr_number = pay.utr_number
            user_email = pay.expense_sheet_id.user_id.email if pay.expense_sheet_id.user_id else ''
            employee_email = pay.expense_sheet_id.employee_id.work_email if pay.expense_sheet_id.employee_id else ''
            template = self.env.ref('account.mail_template_data_payment_receipt')
            template.write({'email_to': ', '.join(filter(None, [user_email, employee_email]))})
            template.send_mail(pay.id, force_send=True)
        res = super(AccountPayment, self).action_post()
        return res

    def action_approve_payment(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def action_reject_payment(self):
        for rec in self:
            rec.write({'state': 'cancel'})

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    def action_print_bank_advice_payment_pdf(self):
        return self.env.ref('account_batch_payment.action_print_batch_payment').report_action(self)
