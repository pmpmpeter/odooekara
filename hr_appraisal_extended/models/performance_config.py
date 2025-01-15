from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PerformanceConfig(models.Model):
    _name = 'performance.config'
    _description = '360 Performance Configuration'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    review_types = fields.Selection([('communication', 'Communication'),
                                     ('team_working','Team Working'),
                                     ('problem_solving','Problem-solving and Decision-Making'),
                                     ('continuous','Continuous Improvement'),
                                     ('organisation_time','Organisation and Time Management'),
                                     ('customer_focus','Customer Focus'),
                                     ('interpersonal_skills','Interpersonal Skills'),
                                     ('motivation','Motivation'),
                                     ], string="Review Type")
