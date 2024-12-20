from odoo import models, fields, api


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    report_type = fields.Selection([
        ('hr_compliances','HR Compliances'),
        ('form_f', 'Form F'),
        ('form_h', 'Form H'),
        ('form_t', 'Form T'),
    ], string='Report Type', required=True)

    def generate_pdf_report(self):
        data = {
            'company_id': self.company_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        if self.report_type == 'form_f':
            return self.env.ref('hr_attendance_extended.form_f_report').report_action(self)
        elif self.report_type == 'form_h':
            return self.env.ref('hr_attendance_extended.form_h_report').report_action(self)
        elif self.report_type == 'form_t':
            return self.env.ref('hr_attendance_extended.form_t_report').report_action(self)
        elif self.report_type == 'hr_compliances':
            return self.env.ref('hr_attendance_extended.get_hr_compliances').report_action(self)
