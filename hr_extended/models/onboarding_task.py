# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OnboardingTask(models.Model):
    _name = 'onboarding.task'
    _description = 'Onboarding Task'

    name = fields.Char(string="Task Name", required=True)
    description = fields.Text(string="Task Description")
    is_active = fields.Boolean(string="Active", default=True)
