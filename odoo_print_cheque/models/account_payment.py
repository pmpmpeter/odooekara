# -*- coding: utf-8 -*-
###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#
#   Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Aslam A K( odoo@cybrosys.com )
#
#   You can modify it under the terms of the GNU AFFERO
#   GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   (AGPL v3) along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import models,fields,api
from num2words import num2words


class AccountPayment(models.Model):
    """
    This class inherits from the 'account.payment' model to add specific
    features and behavior related to printing checks and handling payment
    information. It overrides the 'print_checks' method to provide a custom
    wizard view for selecting and formatting cheque printing options.
    """
    _inherit = 'account.payment'



    cheque_format_id = fields.Many2one('cheque.format', string='Cheque Format',
                                       help='Cheque Print Formats')
    sr_no = fields.Char(string="Sr.No")
    assigned_by = fields.Many2one('res.users',string="Assigned By")
    managed_by = fields.Many2one('res.users',string="Managed By")
    comments = fields.Text(string="Comments")
    cheque_number = fields.Char(string="Cheque/Tax Number")
    towards = fields.Text(string="Towards")
    authorised_by = fields.Many2one('res.users',string="Authorised By")
    authorised_date = fields.Date(string="Authorised Date")
    is_cheque_cleared = fields.Boolean(string="Cheque Cleared")
    cheque_cleared_date = fields.Date(string="Date of Cheque Cleared")


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



    def print_checks(self):
        """
        Overriding print_checks button to generate a wizard view to print
        cheque by selecting a cheque print format.
        """
        if self.payment_method_line_id.payment_method_id.name == 'Checks':
            cheque_date = self.date
        elif self.payment_method_line_id.payment_method_id.name == 'PDC':
            cheque_date = self.effective_date
        return {
            'name': "Cheque Format",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cheque.types',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_cheque_amount_in_words': self.check_amount_in_words,
                'default_cheque_date': cheque_date,
                'default_cheque_amount': self.amount,
                'default_check_number': self.check_number,
                'default_payment_id': self.id
            }
        }


    def action_print_cheque_payment(self):
        if self.cheque_format_id:
            data = {
                'cheque_width': self.cheque_format_id.cheque_width,
                'cheque_height': self.cheque_format_id.cheque_height,
                'font_size': self.cheque_format_id.font_size,
                'is_account_payee': self.cheque_format_id.is_account_payee,
                'a_c_payee_top_margin': self.cheque_format_id.a_c_payee_top_margin,
                'a_c_payee_left_margin': self.cheque_format_id.a_c_payee_left_margin,
                'a_c_payee_width': self.cheque_format_id.a_c_payee_width,
                'a_c_payee_height': self.cheque_format_id.a_c_payee_height,
                'date_top_margin': self.cheque_format_id.date_top_margin,
                'date_left_margin': self.cheque_format_id.date_left_margin,
                'date_letter_spacing': self.cheque_format_id.date_letter_spacing,
                'beneficiary_top_margin': self.cheque_format_id.beneficiary_top_margin,
                'beneficiary_left_margin': self.cheque_format_id.beneficiary_left_margin,
                'amount_word_tm': self.cheque_format_id.amount_word_tm,
                'amount_word_lm': self.cheque_format_id.amount_word_lm,
                'amount_word_ls': self.cheque_format_id.amount_word_ls,
                'amount_digit_tm': self.cheque_format_id.amount_digit_tm,
                'amount_digit_lm': self.cheque_format_id.amount_digit_lm,
                'amount_digit_ls': self.cheque_format_id.amount_digit_ls,
                'partner': self.partner_id.name,
                # 'amount_in_words': self.cheque_amount_in_words,
                'amount_in_digit': self.amount,
                'cheque_date': self.date,
                'print_currency': self.cheque_format_id.print_currency,
                'currency_symbol': self.env.company.currency_id.symbol,
                'amount_digit_size': self.cheque_format_id.amount_digit_size,
                'print_cheque_number': self.cheque_format_id.print_cheque_number,
                'check_number': self.check_number,
                'cheque_no_tm': self.cheque_format_id.cheque_no_tm,
                'cheque_no_lm': self.cheque_format_id.cheque_no_lm
            }
            return self.env.ref('account.action_report_payment_receipt').report_action(self, data=data)



class AccountBatchPayment(models.Model):
    """
    This class inherits from the 'account.payment' model to add specific
    features and behavior related to printing checks and handling payment
    information. It overrides the 'print_checks' method to provide a custom
    wizard view for selecting and formatting cheque printing options.
    """
    _inherit = 'account.batch.payment'



    cheque_format_id = fields.Many2one('cheque.format', string='Cheque Format',
                                       help='Cheque Print Formats')
    cheque_number = fields.Char(string="Cheque/Tax Number")
    towards = fields.Text(string="Towards")
    authorised_by = fields.Many2one('res.users',string="Authorised By")
    authorised_date = fields.Date(string="Authorised Date")
    amount_total_words = fields.Char(
        string="Amount total in words",
        compute="_compute_amount_total_words",
    )


    @api.depends('amount', 'currency_id')
    def _compute_amount_total_words(self):
        for rec in self:
            rec.amount_total_words = rec.currency_id.amount_to_text(abs(rec.amount)).replace(',', '')
