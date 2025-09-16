from odoo import models, fields
from odoo.tools.misc import formatLang

class GeneratePdfReport(models.TransientModel):
    _name = 'generate.pdf.report'
    _description = 'Generate PDF Report Wizard'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )

    def get_paymenet_id(self, move):
        self._cr.execute('''
                           SELECT
                               payment.id as payment_ids,
                                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids
                           FROM account_payment payment
                           JOIN account_move move ON move.id = payment.move_id
                           JOIN account_move_line line ON line.move_id = move.id
                           JOIN account_partial_reconcile part ON
                               part.debit_move_id = line.id
                               OR
                               part.credit_move_id = line.id
                           JOIN account_move_line counterpart_line ON
                               part.debit_move_id = counterpart_line.id
                               OR
                               part.credit_move_id = counterpart_line.id
                           JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                           JOIN account_account account ON account.id = line.account_id
                           WHERE account.account_type IN ('asset_receivable', 'liability_payable')
                               AND invoice.id IN %(payment_ids)s
                               AND line.id != counterpart_line.id
                               AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                           GROUP BY payment.id, invoice.move_type
                       ''', {
            'payment_ids': tuple(move.ids)
        })
        query_res = self._cr.dictfetchall()
        return query_res

    def get_invoice_data(self):
        account_moves = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('partner_id', '=', self.vendor_id.id),
            ('invoice_date', '>=', self.from_date),
            ('invoice_date', '<=', self.to_date),
            ('state', '=', 'posted'),
            ('state', '=', 'posted')
        ],order='id')
        result = []
        pay_result = []
        payment_ids = []
        total_credit = 0.0
        total_debit = 0.0

        # payment_ids = self.env['account.payment'].search([('reconciled_bill_ids','in',account_moves.ids)],order='id')

        for move in account_moves:
            payment = self.get_paymenet_id(move)
            if payment and payment[0]['payment_ids'] not in payment_ids:
                pay = self.env['account.payment'].browse(payment[0]['payment_ids'])
                payment_ids.append(pay.id)
                debit_date = pay.date.strftime('%d-%b-%y') if pay.date else ''
                debit_label = pay.journal_id.display_name
                debit_amount = pay.amount
                total_debit += pay.amount
                for line in move.invoice_line_ids:
                    result.append({
                        'debit_date': debit_date,
                        'debit_label': debit_label,
                        'debit_amount': debit_amount,
                        'credit_date': move.invoice_date.strftime('%d-%b-%y') if move.invoice_date else '',
                        'credit_label': line.account_id.display_name,
                        'credit_amount': move.amount_total,
                    })
            else:
                for line in move.invoice_line_ids:
                    result.append({
                        'debit_date': '',
                        'debit_label': '',
                        'debit_amount': 0,
                        'credit_date': move.invoice_date.strftime('%d-%b-%y') if move.invoice_date else '',
                        'credit_label': line.account_id.display_name,
                        'credit_amount': move.amount_total,
                    })

            total_credit += move.amount_total
        return {
            'rows': result,
            'total_credit': total_credit,
            'total_debit': float(total_debit),
            'closing_balance_debit':total_credit-total_debit if total_credit > total_debit else 0,
            'closing_balance_credit':total_debit-total_credit if total_debit > total_credit else 0 ,
        }

    def action_generate_pdf(self):
        self.ensure_one()
        return self.env.ref('ekara_pdf_report.action_pdf_report_creation').report_action(self)
