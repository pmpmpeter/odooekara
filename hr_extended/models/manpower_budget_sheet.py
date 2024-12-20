import pytz
import xlsxwriter
import base64

from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone


class ManpowerBudgetSheet(models.AbstractModel):
    _name = 'report.hr_extended.report_manpower_budget_sheet'
    _inherit = "report.report_xlsx.abstract"


    def generate_xlsx_report(self, workbook,data,employee):

        # main_product = data
        # company_name = main_product['company_name']
        # company_id = main_product['company_id']
        # date_from = main_product['date_from']
        # date_to = main_product['date_to']

        worksheet = workbook.add_worksheet('manpower_budget_sheet')

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
            'fg_color': '#c5e0b3',
            'text_wrap': True,
        })

        merge_format3 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#b4c6e7',
            'text_wrap': True,

        })

        merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#FFFF00',
            'text_wrap': True,
        })
        merge_format5 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#fbe4d5',
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
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:J', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)
        worksheet.set_column('S:S', 15)
        worksheet.set_column('T:T', 15)
        worksheet.set_column('U:U', 15)
        worksheet.set_column('V:V', 15)
        worksheet.set_column('W:W', 15)
        worksheet.set_column('X:X', 15)
        worksheet.set_column('Y:Y', 15)
        worksheet.set_column('Z:Z', 15)
        worksheet.set_column('AA:AA', 15)
        worksheet.set_column('AB:AB', 15)
        worksheet.set_column('AC:AC', 15)
        worksheet.set_column('AD:AD', 15)
        worksheet.set_column('AE:AE', 15)
        worksheet.set_column('AG:AG', 15)
        worksheet.set_column('AH:AH', 15)
        worksheet.set_column('AI:AI', 15)


        # worksheet.merge_range('B2:L2', 'GMC Details', merge_format1)

        # worksheet.merge_range('A2:I2', datetime.datetime.strptime(str(date_from), '%Y-%m-%d').strftime('%d-%m-%Y') +' ' 'To' ' ' + datetime.datetime.strptime(str(date_to), '%Y-%m-%d').strftime('%d-%m-%Y'), format_date)
        worksheet.write(5, 0, "Tax Entity", merge_format3)
        worksheet.write(0, 0, "Guideline", merge_format2)
        worksheet.write(3, 0, " Manpower for FY 202….", merge_format1)
        worksheet.write(5, 1, "Category", merge_format3)
        worksheet.write(5, 2, "Type of Manpower Request", merge_format3)
        worksheet.write(5, 3, "Business Unit", merge_format3)
        worksheet.write(5, 4, "Department", merge_format3)
        worksheet.write(5, 5, "Role/Designation", merge_format3)
        worksheet.write(5, 6, "Job Level/Grade", merge_format3)
        worksheet.write(5, 7, "Justification", merge_format3)
        worksheet.write(5, 8, "CTC/Month", merge_format3)
        worksheet.merge_range('J5:U5', 'No. of Employees', merge_format1)
        worksheet.merge_range('X5:AI5', 'Total Salary Per Month', merge_format1)
        worksheet.merge_range('D2:H2', 'If an employee is added in month 1, pls consider that employee for all the 12 months', merge_format1)
        worksheet.merge_range('D1:I1', 'Kindly fill the details of existing Manpower/additional Manpower to be recruited for Budget Year FY 202….', merge_format1)
        worksheet.write(5, 9, "Apr/25", merge_format4)
        worksheet.write(5, 10, "May/25", merge_format4)
        worksheet.write(5, 11, "Jun/25", merge_format4)
        worksheet.write(5, 12, "Jul/25", merge_format4)
        worksheet.write(5, 13, "Aug/25", merge_format4)
        worksheet.write(5, 14, "Sep/25", merge_format4)
        worksheet.write(5, 15, "Oct/25", merge_format4)
        worksheet.write(5, 16, "Nov/25", merge_format4)
        worksheet.write(5, 17, "Dec/25", merge_format4)
        worksheet.write(5, 18, "Jan/25", merge_format4)
        worksheet.write(5, 19, "Feb/25", merge_format4)
        worksheet.write(5, 20, "Mar/25", merge_format4)
        worksheet.write(5, 21, "FY 202….", merge_format4)
        worksheet.write(5, 22, "", merge_format5)
        worksheet.write(5, 23, "Apr/25", merge_format4)
        worksheet.write(5, 24, "May/25", merge_format4)
        worksheet.write(5, 25, "Jun/25", merge_format4)
        worksheet.write(5, 26, "Jul/25", merge_format4)
        worksheet.write(5, 27, "Aug/25", merge_format4)
        worksheet.write(5, 28, "Sep/25", merge_format4)
        worksheet.write(5, 29, "Oct/25", merge_format4)
        worksheet.write(5, 30, "Nov/25", merge_format4)
        worksheet.write(5, 31, "Dec/25", merge_format4)
        worksheet.write(5, 32, "Jan/25", merge_format4)
        worksheet.write(5, 33, "Feb/25", merge_format4)
        worksheet.write(5, 34, "Mar/25", merge_format4)



