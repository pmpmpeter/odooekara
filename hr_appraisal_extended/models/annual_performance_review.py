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


    def generate_xlsx_report(self, workbook,data,rating_id):


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


        cell_format = workbook.add_format({'border': 1})
        worksheet.write(1, 1, "KRA", merge_format2)
        worksheet.write(1, 2, "Description", merge_format2)
        worksheet.write(1, 3, "Weightage", merge_format2)
        worksheet.write(1, 4, "Score", merge_format2)
        worksheet.write(1, 5, "Weighted Score", merge_format2)
        worksheet.write(1, 6, "Manager Weightage", merge_format2)
        worksheet.write(1, 7, "Score", merge_format2)
        worksheet.write(1, 8, "Weighted Score", merge_format2)
        row = 2 
        for line in rating_id.review_line_ids:
            worksheet.write(row, 1, line.kra, cell_format)
            worksheet.write(row, 2, line.description, cell_format)
            worksheet.write(row, 3, line.weightage, cell_format)
            worksheet.write(row, 4, line.employee_score, cell_format)
            worksheet.write(row, 5, str(line.employee_weighted_score)+'%', cell_format)
            worksheet.write(row, 6, line.manager_weightage, cell_format)
            worksheet.write(row, 7, line.manager_score, cell_format)
            worksheet.write(row, 8, str(line.manager_weighted_score)+'%', cell_format)
            row +=1
        merge_row = row+1
        worksheet.merge_range('B'+str(merge_row)+':E'+str(merge_row), 'Total', merge_format3)
        worksheet.merge_range('G'+str(merge_row)+':H'+str(merge_row), 'Total', merge_format3)
        worksheet.write(row, 5, str(rating_id.total_score_employee)+'%', merge_format3)
        worksheet.write(row, 8, str(rating_id.total_score_manager)+'%', merge_format3)
        row+=2
        worksheet.write(row, 4, "Score", merge_format3)
        worksheet.write(row, 5,rating_id.total_employee_weighted_score, merge_format3)
        worksheet.write(row, 7, "Total", merge_format3)
        worksheet.write(row, 8  ,rating_id.total_manager_weighted_score, merge_format3)
