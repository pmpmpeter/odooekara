import pytz
import xlsxwriter
import base64

from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone

class DirectorFinalRatings(models.AbstractModel):
    _name = 'report.hr_appraisal_extended.report_director_final_ratings'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook,data,employee):

        # main_product = data
        # company_name = main_product['company_name']
        # company_id = main_product['company_id']
        # date_from = main_product['date_from']
        # date_to = main_product['date_to']

        worksheet = workbook.add_worksheet('Sales Collection Wise Report.xlsx')

        # worksheet.protect()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'border_color': '#000000',
            'valign': 'vcenter',
            'text_wrap': True,
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

        # merge_format3 = workbook.add_format({
        #     'align': 'center',
        #     'bold': 1,
        #     'border': 1,
        #     'font_size': 14,
        # })
        #
        # merge_format4 = workbook.add_format({
        #     'align': 'right',
        #     'bold': 1,
        #     'valign': 'vcenter', })
        # merge_format4.set_num_format('#,##0.00')
        #
        # merge_format8 = workbook.add_format({
        #     'align': 'right',
        #     'bold': 0,
        #     'valign': 'vcenter', })
        # merge_format8.set_num_format('#,##0.00')
        # merge_format200 = workbook.add_format({
        #     'align': 'right',
        #     'bold': 0,
        #     'valign': 'vcenter', })
        #
        # merge_format19 = workbook.add_format({
        #     'align': 'left',
        #     'bold': 0,
        #      })

        # format_date = workbook.add_format({
        #     'num_format': 'd mmm yyyy hh:mm AM/PM',
        #     'align': 'center',
        # })
        worksheet.set_row(1, 30)

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_row(1, 30)
        # worksheet.merge_range('A1:I1', 'director_final_ratings', merge_format2)

        # worksheet.merge_range('A2:I2', datetime.datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%d-%m-%Y') +' ' 'To' ' ' + datetime.datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d-%m-%Y'), format_date)
        worksheet.write(1, 0, "Name", merge_format2)
        worksheet.write(1, 1, "Designation", merge_format2)
        worksheet.write(1, 2, "Overall Final Rating", merge_format2)
        worksheet.write(1, 3, "Recommended Increment %", merge_format2)
        worksheet.write(1, 4, "Recommended PBVP Payout \n %(to be released on a pro-rata basis)", merge_format2)
        worksheet.write(1, 5, "Eligible for Promotion? (Y/N)", merge_format2)
        worksheet.write(1, 6, "New Designation (if applicable)", merge_format2)



