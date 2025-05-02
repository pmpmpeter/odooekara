# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import operator as py_operator
from operator import attrgetter
from re import findall as regex_findall, split as regex_split

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class StockLot(models.Model):
    _inherit = 'stock.lot'

    employee_id = fields.Many2one("hr.employee", string="Employee", copy=False)
    reference_no = fields.Char(string="Reference No.", copy=False)
