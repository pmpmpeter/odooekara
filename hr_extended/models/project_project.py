# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _, _lt

class Project(models.Model):
    _inherit = "project.project"

    is_a_master = fields.Boolean(string='Is a Master')
    department_id = fields.Many2one('hr.department',string='Department')