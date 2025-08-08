from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    name = fields.Char('Remarks', compute='_compute_description', inverse='_inverse_description',
                       search='_search_description', compute_sudo=False, copy=False, required=True)
    holiday_status_id = fields.Many2one(
        "hr.leave.type", compute='_compute_from_employee_id',
        store=True, string="Leave Type",
        required=True, readonly=False,
        domain="""[
               ('company_id', 'in', [employee_company_id, False]),
               '|',
                   ('requires_allocation', '=', 'no'),
                   ('has_valid_allocation', '=', True),
           ]""",
        tracking=True)

    leave_subtype_id = fields.Many2one('hr.leave.sub.type', string="Leave Subcategory",
                                       domain="[('company_id','=', company_id),('leave_type_id','=',holiday_status_id)]")
    #to map the leave subcategory without leave type
    # leave_subtype_id = fields.Many2one('hr.leave.sub.type', string="Leave Subcategory",
    #                                    domain="[('company_id','=', company_id),'|',('leave_type_id','=',False),('leave_type_id','=',holiday_status_id)]")

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        """ Clears leave_subtype_id when holiday_status_id changes """
        self.leave_subtype_id = False

    @api.constrains('date_from', 'leave_subtype_id', 'holiday_status_id')
    def _check_leave_days(self):
        for record in self:
            if record.holiday_status_id:
                subtypes = self.env['hr.leave.sub.type'].search([
                    ('leave_type_id', '=', record.holiday_status_id.id)
                ])

                if subtypes and not record.leave_subtype_id:
                    raise ValidationError(_(
                        "You must select a Leave Subcategory because the selected Leave Type has subcategories."
                    ))

            if record.date_from:
                leave_date = record.date_from.date()
                today_date = fields.Date.today()

                if leave_date < today_date:
                    continue

            if record.leave_subtype_id and record.date_from:
                leave_date = record.date_from.date()
                today_date = fields.Date.today()
                required_days = record.leave_subtype_id.days

                if (leave_date - today_date).days < required_days:
                    raise ValidationError(_(
                        "You must request this leave at least %d days in advance." % required_days
                    ))

class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    sub_type_ids = fields.One2many(
        'hr.leave.sub.type',
        'leave_type_id',
        string="Leave Sub Types",
        compute="_compute_sub_types",
        store=False
    )

    @api.depends('sub_type_ids.leave_type_id')
    def _compute_sub_types(self):
        for record in self:
            record.sub_type_ids = self.env['hr.leave.sub.type'].search([('leave_type_id', 'in', record.ids)])



# class HolidayType(models.Model):
#     _inherit = "hr.leave.type"
#
#     leave_subtype_ids = fields.One2many('hr.leave.sub.type', 'leave_type_id', string="")
