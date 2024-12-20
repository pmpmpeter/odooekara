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
    active = fields.Boolean('Active', default=True, copy=False)

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
    active = fields.Boolean('Active', default=True, copy=False)
    country_id = fields.Many2one('res.country')

    @api.depends('name')
    def _compute_code(self):
        for job_levels in self:
            if job_levels.code:
                continue
            job_levels.code = job_levels.name

class BusinessUnits(models.Model):
    _name = 'business.units'
    _description = 'Business Units'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(compute='_compute_code', store=True, readonly=False)
    tax_entity = fields.Many2one('res.company', string='Tax Entity', default=lambda self: self.env.company)
    sequence = fields.Integer()
    active = fields.Boolean('Active', default=True, copy=False)

    @api.depends('name')
    def _compute_code(self):
        for business_units in self:
            if business_units.code:
                continue
            business_units.code = business_units.name
