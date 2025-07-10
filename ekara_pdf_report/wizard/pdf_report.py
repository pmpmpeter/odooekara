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

    def get_invoice_data(self):
        account_moves = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('partner_id', '=', self.vendor_id.id),
            ('invoice_date', '>=', self.from_date),
            ('invoice_date', '<=', self.to_date),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ])

        result = []
        total_credit = 0.0

        for move in account_moves:
            for line in move.invoice_line_ids:
                amount = move.amount_residual
                result.append({
                    'date': move.invoice_date.strftime('%d-%b-%Y') if move.invoice_date else '',
                    'label': f"{line.account_id.code or ''} {line.account_id.name or ''}".strip(),
                    'amount': amount,
                })

                total_credit += amount

        return {
            'lines': result,
            'total_credit': total_credit,
        }

    def action_generate_pdf(self):
        self.ensure_one()
        return self.env.ref('ekara_pdf_report.action_pdf_report_creation').report_action(self)
