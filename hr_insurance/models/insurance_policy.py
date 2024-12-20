# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author:  Anjhana A K (<https://www.cybrosys.com>)
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class InsurancePolicy(models.Model):
    """used this model for insurance policy"""
    _name = 'insurance.policy'

    name = fields.Char(string='Name', required=True)
    note_field = fields.Html(string='Comment',
                             help="Notes for the insurance policy if any")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    active = fields.Boolean('Active', default=True, copy=False)

    def unlink(self):
        for record in self:
            if record.active != False:
                raise UserError(
                    _("You can only delete records in the Inactive.")
                )
        return super(InsurancePolicy, self).unlink()

