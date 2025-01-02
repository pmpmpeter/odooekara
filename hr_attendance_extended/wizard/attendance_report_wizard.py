from odoo import models, fields, api
import calendar
from datetime import datetime

class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    report_type = fields.Selection([
        ('hr_compliances','HR Compliances'),
        ('form_f', 'Form F'),
        ('form_h', 'Form H'),
        ('form_t', 'Form T'),
    ], string='Report Type', required=True)
    month = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string="Select Month",
    )
    year = fields.Integer(
        string="Year",
        default=lambda self: fields.Date.today().year
    )

    @api.model
    def get_days_in_month(self):
        if self.month and self.year:
            month = int(self.month)
            year = self.year
            return calendar.monthrange(year, month)[1]  # Returns (weekday, number_of_days)
        return 0

    @api.model
    def get_start_datetime(self):
        if self.month and self.year:
            # Start of the month
            start_datetime = datetime(int(self.year), int(self.month), 1, 00, 00, 00)

            # Last day of the month
            _, last_day = calendar.monthrange(int(self.year), int(self.month))
            end_datetime = datetime(int(self.year), int(self.month), last_day, 23, 59, 59)
            print(start_datetime,'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
            return start_datetime
        return None

    @api.model
    def get_end_datetime(self):
        if self.month and self.year:
            # Start of the month
            start_datetime = datetime(int(self.year), int(self.month), 1, 00, 00, 00)

            # Last day of the month
            _, last_day = calendar.monthrange(int(self.year), int(self.month))
            end_datetime = datetime(int(self.year), int(self.month), last_day, 23, 59, 59)
            print(end_datetime,'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            return end_datetime
        return None

    def generate_pdf_report(self):
        attendance_rec=[]
        emp_rec=[]
        employee = self.env['hr.employee'].sudo().search([('state','=','employment')])
        for rec in employee:
            emp_rec.append(rec.id)
        for rec in employee:
            attendance_rec.append(rec)
        data = {
            'company_id': self.company_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            # 'attendance':attendance_rec,
        }
        leaves_types = []
        leave_types = self.env['hr.leave.type'].sudo().search([])
        for rec in leave_types:
            leaves_types.append(rec.name)

        days_in_month = self.get_days_in_month()
        startdate = self.get_start_datetime()
        enddate = self.get_end_datetime()
        data1 = {
            'month_name': calendar.month_name[int(self.month)],
            'days_in_month': days_in_month,
            'employee': emp_rec,
            'leaves_types': leaves_types,
            'startdate':startdate,
            'enddate':enddate,
        }

        if self.report_type == 'form_f':
            return self.env.ref('hr_attendance_extended.form_f_report').report_action(self,data=data)
        elif self.report_type == 'form_h':
            return self.env.ref('hr_attendance_extended.form_h_report').report_action(self,data=data)
        elif self.report_type == 'form_t':
            return self.env.ref('hr_attendance_extended.form_t_report').report_action(self,data=data1)
        elif self.report_type == 'hr_compliances':
            return self.env.ref('hr_attendance_extended.get_hr_compliances').report_action(self)
