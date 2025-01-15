# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PositionNames(models.Model):
    _name = 'grievance.type.names'
    _description = 'Grievance Type'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    sequence = fields.Integer()
    active = fields.Boolean('Active', default=True, copy=False)
    respective_hod_id = fields.Many2one('hr.employee',string="HOD", copy=False)


    @api.depends('name')
    def _compute_code(self):
        for grievance_types in self:
            if grievance_types.code:
                continue
            grievance_types.code = grievance_types.name
