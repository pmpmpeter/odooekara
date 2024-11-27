# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PositionNames(models.Model):
    _name = 'hr.position.names'
    _description = 'Positions/Designation'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    sequence = fields.Integer()

    @api.depends('name')
    def _compute_code(self):
        for position_names in self:
            if position_names.code:
                continue
            position_names.code = position_names.name
