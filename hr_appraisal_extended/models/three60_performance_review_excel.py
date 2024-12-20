import pytz
import xlsxwriter
import base64

from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone


class PerformanceReview(models.AbstractModel):
    _name = 'report.hr_appraisal_extended.report_360_performance_review'
    _inherit = "report.report_xlsx.abstract"


    def generate_xlsx_report(self, workbook,data,employee):

        # main_product = data
        # company_name = main_product['company_name']
        # company_id = main_product['company_id']
        # date_from = main_product['date_from']
        # date_to = main_product['date_to']

        worksheet = workbook.add_worksheet('360_performance_review')

        worksheet.protect()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
            'text_wrap': True,
            'valign': 'vcenter', })

        merge_format2 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#d8d8d8',
            'text_wrap': True,
        })

        merge_format3 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#f2f2f2',
            'text_wrap': True,
        })

        merge_format4 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#4472c4',
            'text_wrap': True,
        })
        merge_format5 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#ed7d31',
            'text_wrap': True,
        })
        merge_format6 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#70ad47',
            'text_wrap': True,
        })
        merge_format7 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#f7caac',
            'text_wrap': True,
        })
        merge_format8 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#ffc000',
            'text_wrap': True,
        })
        merge_format9 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#000000',
            'fg_color': '#FFFF00',
            'text_wrap': True,
        })



        worksheet.set_column('A:A', 2)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 2)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 5)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 25)
        worksheet.set_column('J:J', 15)
        # worksheet.merge_range('B2:L2', 'GMC Details', merge_format1)
        # worksheet.set_row(1, 5)
        # worksheet.set_row(2, 5)
        # worksheet.set_row(3, 5)
        # worksheet.set_row(4, 5)
        # worksheet.set_row(5, 5)
        # worksheet.set_row(2:28, 20)
        # worksheet.set_row('G:G', 5)


        worksheet.write(1, 1, "Who are you leaving feedback for? (Employee Name)", merge_format2)
        worksheet.write(2, 1, "What is their job title:", merge_format2)
        worksheet.write(3, 1, "Grade (if applicable):", merge_format2)
        worksheet.merge_range('B5:F5', 'Please rate the above Employee in accordance with the criteria below:', merge_format3)
        worksheet.merge_range('C2:F2', '', merge_format1)
        worksheet.merge_range('C3:F3', '', merge_format1)
        worksheet.merge_range('C4:F4', '', merge_format1)

        worksheet.write(5, 1, "Communication ", merge_format4)
        worksheet.write(6, 1, "Shares information widely and does not withhold information from others: ", merge_format1)
        worksheet.write(7, 1, "Actively listens and is receptive to others’ opinions and points of view: ", merge_format1)
        worksheet.write(8, 1, "Stays focused and is easily understood in conversation: ", merge_format1)
        worksheet.write(9, 1, "Encourages dialogue in an open and direct way: ", merge_format1)
        worksheet.write(5, 2, "Rating ", merge_format4)
        worksheet.write(6, 2, "B ", merge_format2)
        worksheet.write(7, 2, "B ", merge_format2)
        worksheet.write(8, 2, "B ", merge_format2)
        worksheet.write(9, 2, "B ", merge_format2)

        worksheet.write(5, 4, "Team working  ", merge_format4)
        worksheet.write(6, 4, "Works as an effective member of the team:", merge_format1)
        worksheet.write(7, 4, "Is willing to pitch in and help other members of the team: ", merge_format1)
        worksheet.write(8, 4, "Willingly shares own knowledge and expertise with team membersy:", merge_format1)
        worksheet.write(9, 4, "Shares credit and recognition with the rest of the team: ", merge_format1)
        worksheet.write(5, 5, "Rating ", merge_format4)
        worksheet.write(6, 5, "B ", merge_format2)
        worksheet.write(7, 5, "B ", merge_format2)
        worksheet.write(8, 5, "B ", merge_format2)
        worksheet.write(9, 5, "B ", merge_format2)

        worksheet.write(11, 1, "Problem-solving and decision-making   ", merge_format5)
        worksheet.write(12, 1, "Gathers information from a range of sources before making a decision:", merge_format1)
        worksheet.write(13, 1, "Focuses on the key issues of a problem and does not get diverted\ in unnecessary detail: ", merge_format1)
        worksheet.write(14, 1, "Flexibility/Change Orientation:", merge_format1)
        worksheet.write(15, 1, "Considers the impact and implications of a decision before taking action: ", merge_format1)
        worksheet.write(11, 2, "Rating ", merge_format5)
        worksheet.write(12, 2, "B ", merge_format2)
        worksheet.write(13, 2, "B ", merge_format2)
        worksheet.write(14, 2, "B ", merge_format2)
        worksheet.write(15, 2, "B ", merge_format2)

        worksheet.write(11, 4, "Continuous improvement    ", merge_format6)
        worksheet.write(12, 4, "Is adaptable and willing to work with new systems and processes:", merge_format1)
        worksheet.write(13, 4, "Does not resist the ideas of others:", merge_format1)
        worksheet.write(14, 4, "Actively seeks and promotes new ways of working:", merge_format1)
        worksheet.write(15, 4, "Strives for innovation:", merge_format1)
        worksheet.write(11, 5, "Rating ", merge_format6)
        worksheet.write(12, 5, "B ", merge_format2)
        worksheet.write(13, 5, "B ", merge_format2)
        worksheet.write(14, 5, "B ", merge_format2)
        worksheet.write(15, 5, "B ", merge_format2)

        worksheet.write(17, 1, "Organisation and Time Management     ", merge_format2)
        worksheet.write(18, 1, "Is able to manage competing priorities effectively:", merge_format1)
        worksheet.write(19, 1, "Meets deadlines and obligations on time:", merge_format1)
        worksheet.write(20, 1, "Delivers well in stressful or time-pressured situations:", merge_format1)
        worksheet.write(21, 1, "Has a methodical and structured approach:", merge_format1)
        worksheet.write(17, 2, "Rating ", merge_format2)
        worksheet.write(18, 2, "B ", merge_format2)
        worksheet.write(19, 2, "B ", merge_format2)
        worksheet.write(20, 2, "B ", merge_format2)
        worksheet.write(21, 2, "B ", merge_format2)

        worksheet.write(17, 4, "Customer focus     ", merge_format4)
        worksheet.write(18, 4, "Works to resolve internal conflict among team members:", merge_format1)
        worksheet.write(19, 4, "Recognises the value of people with different skills and talents:", merge_format1)
        worksheet.write(20, 4, "Is tactful, compassionate and able to consider the needs of others:", merge_format1)
        worksheet.write(21, 4, "Delivers difficult or sensitive information openly, honestly and with empathy:", merge_format1)
        worksheet.write(17, 5, "Rating ", merge_format4)
        worksheet.write(18, 5, "B ", merge_format2)
        worksheet.write(19, 5, "B ", merge_format2)
        worksheet.write(20, 5, "B ", merge_format2)
        worksheet.write(21, 5, "B ", merge_format2)

        worksheet.write(23, 4, "Motivation    ", merge_format7)
        worksheet.write(24, 4, "Is able to make a case for his/her views and opinions", merge_format1)
        worksheet.write(25, 4, "Can effectively persuade others to build commitment to ideas:", merge_format1)
        worksheet.write(26, 4, "Helps create a positive atmosphere which encourages others to achieve:", merge_format1)
        worksheet.write(27, 4, "Is able to take risks and views honest mistakes as a learning experience:", merge_format1)
        worksheet.write(23, 5, "Rating ", merge_format7)
        worksheet.write(24, 5, "B ", merge_format2)
        worksheet.write(25, 5, "B ", merge_format2)
        worksheet.write(26, 5, "B ", merge_format2)
        worksheet.write(27, 5, "B ", merge_format2)

        worksheet.write(23, 1, "Interpersonal skills      ", merge_format8)
        worksheet.write(24, 1,
                        "Works to resolve internal conflict among team members:",
                        merge_format1)
        worksheet.write(25, 1, "Recognises the value of people with different skills and talents:",
                        merge_format1)
        worksheet.write(26, 1,
                        "Is tactful, compassionate and able to consider the needs of others:",
                        merge_format1)
        worksheet.write(27, 1, "Delivers difficult or sensitive information openly, honestly and with empathy:",
                        merge_format1)
        worksheet.write(23, 2, "Rating ", merge_format8)
        worksheet.write(24, 2, "B ", merge_format2)
        worksheet.write(25, 2, "B ", merge_format2)
        worksheet.write(26, 2, "B ", merge_format2)
        worksheet.write(27, 2, "B ", merge_format2)

        worksheet.write(29, 1, "Review submitted by (Employee Name, Designation , Department , BU) ", merge_format9)
        worksheet.write(30, 1, "Date and Time ", merge_format9)

        worksheet.merge_range('C30:F30', '', merge_format1)
        worksheet.merge_range('C31:F31', '', merge_format1)







