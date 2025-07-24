# -*- coding: utf-8 -*-
from contextlib import nullcontext

from odoo import api, fields, models, _, tools, Command
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import SQL
from bisect import bisect_left
from collections import defaultdict
import logging
import re

_logger = logging.getLogger(__name__)

ACCOUNT_REGEX = re.compile(r'(?:(\S*\d+\S*))?(.*)')
ACCOUNT_CODE_REGEX = re.compile(r'^[A-Za-z0-9.]+$')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    active = fields.Boolean(string="Active",default=True, copy=False)
    is_cash_rounding = fields.Boolean(string="Disable Budget Code",copy=False)

    @api.model
    def _load_precommit_update_opening_move(self):
        """ precommit callback to recompute the opening move according the opening balances that changed.
        This is particularly useful when importing a csv containing the 'opening_balance' column.
        In that case, we don't want to use the inverse method set on field since it will be
        called for each account separately. That would be quite costly in terms of performances.
        Instead, the opening balances are collected and this method is called once at the end
        to update the opening move accordingly.
        """
        data = self._cr.precommit.data.pop('import_account_opening_balance', {})
        accounts = self.browse(data.keys())

        accounts_per_company = defaultdict(lambda: self.env['account.account'])
        for account in accounts:
            accounts_per_company[account.company_id] |= account

        # for company, company_accounts in accounts_per_company.items():
        #     company._update_opening_move({account: data[account.id] for account in company_accounts})

        self.env.flush_all()
