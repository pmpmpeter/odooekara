from odoo import models, fields
import io
import base64
import xlsxwriter
from datetime import datetime,date
import calendar

class ExcelReportWizard(models.TransientModel):
    _name = 'pf.report.wizard'
    _description = 'PF Report Wizard'

    file_name = fields.Char(string="File Name", default="report.xlsx")
    file_data = fields.Binary(string="Excel File")
    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string="Month")

    year = fields.Selection(
        selection=lambda self: [(str(y), str(y)) for y in range(2000, datetime.today().year + 2)],
        string='Year',
        default=lambda self: str(datetime.today().year)
    )
    date_from = fields.Date(string='Date From', default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Date To', default=lambda self: date.today().replace(
            day=calendar.monthrange(date.today().year, date.today().month)[1]))
    company_id = fields.Many2one('res.company',string='Company',default=lambda self:self.env.company)

    def generate_excel_report(self):
        # Generate Excel file in memory
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        bold = workbook.add_format({'bold': True,'font_size':16})
        header_bold = workbook.add_format({'bold': True,'font_size': 12,'border':True})
        text_bold = workbook.add_format({'border':True})
        wrap_format = workbook.add_format({
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'fg_color': '#D3D3D3',
            'bold':True,
            'border':True
        })
        start_date = self.date_from
        fy_start = start_date.year
        fy_end = fy_start + 1
        financial_year = f"{fy_start}-{str(fy_end)[-2:]}"  # "2025-26"

        month_year = start_date.strftime("%B %Y")  # "October 2025"
        amount_format = workbook.add_format({'num_format': '#,##0.00','border':True})
        amount_format1 = workbook.add_format({'num_format': '#,##0.00','fg_color': '#D3D3D3','border':True})
        worksheet = workbook.add_worksheet('Prov.Fund')
        worksheet.merge_range('A1:H1',self.company_id.name, bold)
        worksheet.merge_range('A3:H3','')
        # worksheet.merge_range(5,0,6,7,'')
        worksheet.write(3, 0, f"Financial Year {financial_year}", header_bold)
        worksheet.write(3, 3, f"Month Year {month_year}", header_bold)
        worksheet.merge_range(5,0,7,1,'Person',wrap_format)
        worksheet.merge_range(5,2,7,2, 'UAN',wrap_format)
        worksheet.merge_range(5,3,7,3, 'Date of Severance',wrap_format)
        worksheet.merge_range(5,4,7,4, 'Choice',wrap_format)
        worksheet.merge_range(5,5,7,5, 'Gross Pay for the month',wrap_format)
        worksheet.merge_range(5, 6, 6, 7, 'Basic', wrap_format)
        worksheet.set_column(7, 7, 23)
        worksheet.set_column(6, 6, 12)
        worksheet.write(7, 6, 'Actual',wrap_format)
        worksheet.write(7, 7, 'For PF',wrap_format)
        worksheet.merge_range(5,8,7,8, "Employee's contribution @ 12%", wrap_format)
        worksheet.set_column(8, 8, 18)
        worksheet.merge_range( 5,9,5,11,"Employer's contribution", wrap_format)
        worksheet.merge_range( 6,9,7,9,"to PF", wrap_format)
        worksheet.merge_range( 6,10,6,11,"to EDLI", wrap_format)
        worksheet.write( 7,10,"Basic for EDLI", wrap_format)
        worksheet.write( 7,11,"Employer's contribution @ 8.33%", wrap_format)
        worksheet.set_column(11, 11, 20)
        worksheet.merge_range(5, 12, 7, 12, 'A/c No 01', wrap_format)
        worksheet.merge_range(5, 13, 7, 13, ' A/c No 02 ', wrap_format)
        worksheet.merge_range(5, 14, 7, 14, ' A/c No 10 ', wrap_format)
        worksheet.merge_range(5, 15, 7, 15, ' A/c No 21 ', wrap_format)


        # month  = self.month
        # current_year = date.today().year
        # selected_month = int(self.month)
        # from_date = date(current_year, selected_month, 1)
        # if selected_month == 12:
        #     to_date = date(current_year + 1, 1, 1)
        # else:
        #     to_date = date(current_year, selected_month + 1, 1)

        payslips = self.env['hr.payslip'].search([
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),('company_id','=',self.company_id.id)
        ])
        total_salary_per_month = 0
        basic_da_per_month = 0
        total_to_ac_21 = 0
        total_to_ac_2 = 0
        total_to_emp_con = 0
        total_to_pf = 0
        total_pf = 0
        total_contribution = 0
        row = 8
        for index, line in enumerate(payslips, start=1):
            worksheet.merge_range(row,0,row,1, line.employee_id.name or '',text_bold)
            worksheet.write(row, 2, line.employee_id.uan_no or '',text_bold)
            worksheet.write(row, 3, '',text_bold)
            worksheet.write(row, 4, '12% of Rs. 15000',text_bold)
            worksheet.write(row, 5, line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].total_salary_per_month or '0.0', amount_format)
            worksheet.write(row, 6, line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].basic_da_per_month or '0.0', amount_format)
            pf = 15000 if line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].total_salary_per_month > 15000 else line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].total_salary_per_month
            worksheet.write(row, 7,pf,text_bold)
            contribution = pf * 0.12
            worksheet.write(row, 8, contribution, text_bold)
            to_pf = pf*0.0367
            worksheet.write(row, 9, round(to_pf), text_bold)
            worksheet.write(row, 10, pf, text_bold)
            emp_con = pf*0.0833
            worksheet.write(row, 11, round(emp_con), text_bold)
            worksheet.write(row, 12, round(to_pf), text_bold)
            ac_2 = pf*0.005
            worksheet.write(row, 13, ac_2, text_bold)
            worksheet.write(row, 14, round(emp_con), text_bold)
            ac_21 = pf*0.005
            worksheet.write(row, 15, ac_21, text_bold)
            total_salary_per_month = total_salary_per_month+line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].total_salary_per_month
            basic_da_per_month = basic_da_per_month+line.employee_id.contract_ids.filtered(lambda x:x.state=='open')[0].basic_da_per_month
            total_pf +=pf
            total_contribution +=contribution
            total_to_pf +=to_pf
            total_to_emp_con +=emp_con
            total_to_ac_2 +=ac_2
            total_to_ac_21 +=ac_21

            row += 1
        row = row + 1
        worksheet.write(row, 0, '', wrap_format)
        worksheet.write(row, 1, '', wrap_format)
        worksheet.write(row, 2, 'Total',wrap_format)
        worksheet.write(row, 3, '', wrap_format)
        worksheet.write(row, 4, '', wrap_format)
        worksheet.write(row, 5, total_salary_per_month,amount_format1)
        worksheet.write(row, 6, basic_da_per_month,amount_format1)
        worksheet.write(row, 7, total_pf,amount_format1)
        worksheet.write(row, 8, total_contribution,amount_format1)
        worksheet.write(row, 9, total_to_pf,amount_format1)
        worksheet.write(row, 10, total_contribution,amount_format1)
        worksheet.write(row, 11, total_to_emp_con,amount_format1)
        worksheet.write(row, 12, total_to_pf,amount_format1)
        worksheet.write(row, 13, total_to_ac_2,amount_format1)
        worksheet.write(row, 14, total_to_emp_con,amount_format1)
        worksheet.write(row, 15, total_to_ac_21,amount_format1)

        worksheet.set_column(5, 0, 15)
        worksheet.set_column(5, 1, 10)
        worksheet.set_column(5, 2, 10)
        worksheet.set_column(5, 4, 10)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(2, 2, 13)
        worksheet.set_column(10,10, 13)
        worksheet.set_column(14,14, 13)
        workbook.close()
        buffer.seek(0)

        # Save file to binary field
        file_data = base64.b64encode(buffer.read())
        buffer.close()
        attachment = self.env['ir.attachment'].create({
            'name': f'PF_Report.xlsx',
            'type': 'binary',
            'datas': file_data,
            'store_fname': f'PF_Report.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'pf.report.wizard',
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


