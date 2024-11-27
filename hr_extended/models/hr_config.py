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

class ContractType(models.Model):
    _name = 'hr.job.levels'
    _description = 'Job Levels'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    sequence = fields.Integer()
    country_id = fields.Many2one('res.country')

    @api.depends('name')
    def _compute_code(self):
        for job_levels in self:
            if job_levels.code:
                continue
            job_levels.code = job_levels.name