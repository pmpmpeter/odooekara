# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    active = fields.Boolean(string="Active",default=True, copy=False)