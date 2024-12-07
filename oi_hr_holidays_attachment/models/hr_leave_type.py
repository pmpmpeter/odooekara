'''
Created on Jan 9, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    attachment_required = fields.Boolean('Attachment Required')