from odoo import api, fields, models, _, Command, tools
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
import re
import pdb
import datetime
from datetime import date, timedelta, datetime



class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month


    def _create_invoices(self, **kwargs):
        invoice_vals = super(SaleOrderInherit, self)._create_invoices(**kwargs)
        invoices = self.mapped('invoice_ids')
        print(self)
        print(self.order_line)
        for order in self.filtered_domain([('is_subscription', '=', True)]):
            start_date = order.next_invoice_date
            end_date = order.end_date
            no_of_months = order.diff_month(end_date, start_date)
            for i in range(no_of_months):
                next_month = order.next_invoice_date.month + 1
                # pdb.set_trace()
                # order.write({'next_invoice_date': order.next_invoice_date.replace(month=next_month)})
                # order._create_recurring_invoice()
                new_invoice = invoices[0].copy()
                next_invoice_date = order.next_invoice_date + timedelta(days=30 * (i + 1))
                new_invoice.write({
                    'invoice_date': next_invoice_date,
                })
                for line in order.order_line:
                    invoice_line = new_invoice.invoice_line_ids.filtered(lambda l: l.product_id == line.product_id and l.quantity == line.product_uom_qty)
                    if invoice_line:
                        invoice_line.write({'sale_line_ids': [(6, 0, line.ids)]})
                        print(invoice_line.sale_line_ids, "Updated sale_line_ids in duplicated invoice")
        return invoice_vals
