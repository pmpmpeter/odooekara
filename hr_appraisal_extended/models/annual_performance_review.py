import pytz
import xlsxwriter
import base64

from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone


class AnnualPerformanceReview(models.AbstractModel):
    _name = 'report.hr_appraisal_extended.report_annual_performance_review'
    _inherit = "report.report_xlsx.abstract"


    def generate_xlsx_report(self, workbook,data,employee):

        # main_product = data
        # company_name = main_product['company_name']
        # company_id = main_product['company_id']
        # date_from = main_product['date_from']
        # date_to = main_product['date_to']

        worksheet = workbook.add_worksheet('annual_performance_review')

        worksheet.protect()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'text_wrap': True,
            'valign': 'vcenter',
        })

        merge_format2 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#e7e6e6',
            'text_wrap': True,
        })

        merge_format3 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#fbe4d5',
            'text_wrap': True,

        })

        merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#e2eeda',
            'text_wrap': True,
        })



        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)


        # worksheet.merge_range('B2:L2', 'GMC Details', merge_format1)

        # worksheet.merge_range('A2:I2', datetime.datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%d-%m-%Y') +' ' 'To' ' ' + datetime.datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d-%m-%Y'), format_date)
        worksheet.write(1, 1, "KRA", merge_format2)
        worksheet.write(1, 2, "Description", merge_format2)
        worksheet.write(1, 3, "Weightage", merge_format2)
        worksheet.write(1, 4, "Score", merge_format2)
        worksheet.write(1, 5, "Weighted Score", merge_format2)
        worksheet.write(1, 6, "Manager Weightage", merge_format2)
        worksheet.write(1, 7, "Score", merge_format2)
        worksheet.write(1, 8, "Weighted Score", merge_format2)
        worksheet.merge_range('B9:E9', 'Total', merge_format3)
        worksheet.write('F9', "", merge_format3)
        worksheet.write('F11', "", merge_format3)
        worksheet.write('I9', "", merge_format3)
        worksheet.write('I11', "", merge_format3)
        worksheet.write('F12', "", merge_format4)
        worksheet.write('I12', "", merge_format4)
        worksheet.write('H9', "", merge_format3)
        # worksheet.merge_range('G9:H9', 'Total', merge_format3)

        worksheet.write(10, 4, "Score", merge_format3)
        worksheet.write(8, 6, "Total", merge_format3)
        worksheet.write(11, 4, "Employee Final Score", merge_format4)
        worksheet.write(10, 7, "Manager Score", merge_format3)
        worksheet.write(11, 7, "Manager Final Score", merge_format4)
