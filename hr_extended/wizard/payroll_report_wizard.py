from odoo import models, fields, api
from datetime import datetime
import base64
from io import BytesIO
import xlsxwriter

class PayrollReportWizard(models.TransientModel):
    _name = 'payroll.report.wizard'
    _description = 'Payroll Report Wizard'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    salary_structure_id = fields.Many2one('hr.payroll.structure', string="Salary Structure")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify'),
        ('paid', 'Paid'),
        ('done', 'Done')
    ], string="PaySheet Status", required=True, default='verify')
    report_based_on = fields.Selection([
        ('batch', 'Batch'),
        ('department', 'Department'),
        ('date', 'Only From and To Date'),
    ], string="Report Based on", required=True, default='batch')
    batch_id = fields.Many2one('hr.payslip.run',string='Batch')
    department_id = fields.Many2one('hr.department',string='Department')
    report_file = fields.Binary(string="Report File", readonly=True)
    file_name = fields.Char(string="File Name", readonly=True)

    def action_generate_report(self):
        workbook = self._prepare_excel_workbook()
        self.report_file = base64.b64encode(workbook)
        self.file_name = f"Payroll_Report.xlsx"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payroll.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _prepare_excel_workbook(self):
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Payroll Data')

        # Define styles
        title_format = workbook.add_format({'bold': True, 'align': 'left', 'font_size': 14})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        data_format = workbook.add_format({'align': 'left', 'border': 1,'num_format': '0.00'})
        char_format = workbook.add_format({'align': 'left', 'border': 1})
        merge_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'bold': True,
                'border': 1
            })

        # Title
        sheet.merge_range('A1:Z1','ENTITY - '+self.env.company.name, title_format)
        sheet.merge_range('A2:Z2', f'Payroll Data for {datetime.now().strftime("%B %Y")}', title_format)
        sheet.set_column('A:B',10)
        sheet.set_column('C:C',20)
        sheet.set_column('D:E',10)
        sheet.set_column('F:F',15)
        sheet.set_column('G:H',20)
        sheet.set_column('I:I',15)
        sheet.set_column('J:J',25)
        sheet.set_column('K:AB',15)
        sheet.set_row(3,28)
        # Headers
        headers = [
            "Sl #", "Employee", "Employment Status", "Empl. No.", "UAN", "Date of Joining",
            "Date of Resignation\n Acceptance", "Last Working Day", "Location", "Annual Compensation",
            "Days Paid \nThis Month"]
        if self.report_based_on == 'batch':
            payslips = self.env['hr.payslip'].search([
                ('payslip_run_id', '=', self.batch_id.id),
                ('state', '=', self.state)
            ])
        elif self.report_based_on == 'department':
            payslips = self.env['hr.payslip'].search([
                ('date_from','>=', self.from_date),
                ('date_to', '<=', self.to_date),
                ('employee_id.department_id', '=', self.department_id.id),
                ('state', '=', self.state)
            ])
        elif self.report_based_on =='date':
            payslips = self.env['hr.payslip'].search([
                ('date_from','>=', self.from_date),
                ('date_to', '<=', self.to_date),
                ('state', '=', self.state)
            ])
        row = 3
        col = 0
        for header in headers:
            sheet.merge_range(2,col,3,col,header, merge_format)
            col += 1
        work_col = col
        for leave_name in payslips.worked_days_line_ids.mapped('work_entry_type_id.name'):
            sheet.write(row,work_col,leave_name,header_format)
            work_col +=1
        wrk_names = payslips.worked_days_line_ids.mapped('work_entry_type_id.name')
        comp_col = work_col
        for comp_name in payslips.struct_id.rule_ids.mapped('name'):
            sheet.write(row,comp_col,comp_name,header_format)
            comp_col +=1
        sheet.merge_range(2,comp_col,3,comp_col,'Remarks',merge_format)
        sheet.merge_range(2,col,2,work_col-1, 'Worked and Leave Days', merge_format) if len(wrk_names) > 1 else sheet.write(2,col,'Worked and Leave Days',header_format)
        sheet.merge_range(2,work_col,2,comp_col-1, 'Components', merge_format)
        comp_names = payslips.struct_id.rule_ids.mapped('name')
        row = 4
        comp_fin_list = []
        wrk_fin_list = []
        for slip in payslips:
            comp_list = []
            wrk_list = []
            for line in slip.line_ids:
                comp_list.append({line.name:line.total})
            comp_fin_list.append(comp_list)
            for line in slip.worked_days_line_ids:
                wrk_list.append({line.work_entry_type_id.name:line.number_of_days})
            wrk_fin_list.append(wrk_list)
        start_row = row
        start_col = col
        for wrk in wrk_fin_list:
            for idx, work in enumerate(wrk_names):
                for item in wrk:
                    value = 0
                    if work in item:
                        value = item[work]
                        break 
                sheet.write(start_row, start_col + idx, value, data_format)
            start_row += 1
        start_row = row
        start_col = work_col
        for comp in comp_fin_list:
            for idx, component in enumerate(comp_names):
                for item in comp:
                    value = 0
                    if component in item:
                        value = item[component]
                        break 
                sheet.write(start_row, start_col + idx, value, data_format)
            start_row += 1
        for idx, slip in enumerate(payslips, start=1):
            col = 0
            resig_date = self.env['hr.resignation'].search([('employee_id','=',slip.employee_id.id),('state','=','hr_approved')])
            sheet.write(row, col, idx, char_format)  # Sl #
            sheet.write(row, col + 1, slip.employee_id.name, char_format)  # Employee
            sheet.write(row, col + 2, (slip.employee_id.state).capitalize(),char_format)  # Employment Status
            sheet.write(row, col + 3, slip.employee_id.employee_number if slip.employee_id.employee_number else '', char_format)  # Employee No.
            sheet.write(row, col + 4, slip.employee_id.uan_no if slip.employee_id.uan_no else '', char_format)  # UAN
            sheet.write(row, col + 5, datetime.strftime((slip.employee_id.joining_date),"%d-%m-%Y") if slip.employee_id.joining_date else '' , char_format)  # Date of Joining
            sheet.write(row, col + 6, datetime.strftime((resig_date.hr_approved_reliving_date),"%d-%m-%Y") if resig_date else '', char_format)  # Date of Resignation Acceptance
            sheet.write(row, col + 7, datetime.strftime(resig_date.expected_revealing_date,"%d-%m-%Y") if resig_date.expected_revealing_date else '' , char_format)  # Last Working Day
            sheet.write(row, col + 8, slip.employee_id.work_location_id.name if slip.employee_id.work_location_id else '', char_format)  # Location
            sheet.write(row, col + 9, slip.contract_id.final_yearly_costs, data_format)  # Annual Compensation
            sheet.write(row, col + 10, sum(slip.worked_days_line_ids.mapped('number_of_days')), data_format)  # Days Paid
            sheet.write(row, col + comp_col,'', data_format) 
            row += 1

        workbook.close()
        buffer.seek(0)
        return buffer.read()

