# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    asset_tag_no = fields.Char(string="Assets Tag Number")
    end_date = fields.Date(string="End Date")
    life_of_asset = fields.Char(string="Life of Asset")
    employee_id = fields.Many2one('hr.employee', String="User")
    location = fields.Char(string="Location")