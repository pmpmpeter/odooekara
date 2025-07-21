from ast import literal_eval

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number
from odoo.tools import remove_accents, groupby
from collections import defaultdict
import logging
import re

_logger = logging.getLogger(__name__)
import pdb

class AccountsJournal(models.Model):
    _inherit = 'account.journal'

    is_credit_card_bank = fields.Boolean(string='Is Credit Card Payment?')
    is_opening_balance = fields.Boolean(string='Is Opening Balance?')

    # def action_open_reconcile(self):
    #     self.ensure_one()

    #     if self.type in ('bank', 'cash'):
    #         return self.env['account.bank.statement.line']._action_open_bank_reconciliation_widget(
    #             default_context={
    #                 'default_journal_id': self.id,
    #                 'search_default_journal_id': self.id,
    #                 'search_default_not_matched': True,
    #             },
    #             extra_domain = [
    #                 ('journal_id', '!=', self.id)
    #             ]
    #         )
    #     else:
    #         # Open reconciliation view for customers/suppliers
    #         return self.env['ir.actions.act_window']._for_xml_id('account_accountant.action_move_line_posted_unreconciled')


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _get_default_amls_matching_domain(self):
        self.ensure_one()
        domain = super()._get_default_amls_matching_domain()
        if self.journal_id:
            domain.append(('journal_id', '=', self.journal_id.id))
        return domain
