from odoo import models, fields, api
import xlsxwriter
import base64
import calendar
from io import BytesIO
from datetime import datetime

class AccountQuarterlyReportWizard(models.TransientModel):
    _name = 'account.quarterly.report.wizard'
    _description = 'Quarterly COA Report Wizard'

    report_file = fields.Binary('Report File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    account_ids = fields.Many2many("account.account", string="Accounts")

    def action_generate_report(self):
        data = self._fetch_coa_data()

        report_content = self._generate_excel_report(data)

        self.report_file = base64.b64encode(report_content)
        self.file_name = f"COA_Quarterly_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.quarterly.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _fetch_coa_data(self):
        """Fetch COA journal entries (Debit - Credit) for each month."""
        coa_data = {}
        year = fields.Date.today().year
        move_line_obj = self.env['account.move.line']
        months = [
            ('April', 4), ('May', 5), ('June', 6),
            ('July', 7), ('August', 8), ('September', 9),
            ('October', 10), ('November', 11), ('December', 12),
            ('January', 1), ('February', 2), ('March', 3)
        ]
        quarters = {
            'Q1': [4, 5, 6],
            'Q2': [7, 8, 9],
            'Q3': [10, 11, 12],
            'Q4': [1, 2, 3],
        }
        selected_accounts = self.account_ids or self.env['account.account'].sudo().search([])
        for coa in selected_accounts:
            coa_data[f"{coa.code}-{coa.name}"] = {}
            for month_name, month_num in months:
                last_day = calendar.monthrange(year, month_num)[1]
                total = move_line_obj.search([
                    ('account_id', '=', coa.id),
                    ('move_id.state', '=', 'posted'),
                    ('date', '>=', f'2024-{month_num:02}-01'),
                    ('date', '<=', f'2024-{month_num:02}-{last_day}')
                ]).mapped(lambda l: l.debit - l.credit)
                coa_data[f"{coa.code}-{coa.name}"][month_name] = sum(total)

            for quarter, months_list in quarters.items():
                quarter_total = sum(
                    coa_data[f"{coa.code}-{coa.name}"].get(month_name, 0) for month_name, m in months if m in months_list
                )
                coa_data[f"{coa.code}-{coa.name}"][quarter] = quarter_total

        return coa_data


    def _generate_excel_report(self, data):
        """Generate an Excel file from COA data."""
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Quarterly COA Report')
        header_format = workbook.add_format({
            'bold': True,              
            'bg_color': '#D9E1F2',     
            'font_color': '#000000',  
            'border': 1,              
            'align': 'center'        
        })
        headers = [
            'COA', 'April', 'May', 'June', 'Q1',
            'July', 'August', 'September', 'Q2',
            'October', 'November', 'December', 'Q3',
            'January', 'February', 'March', 'Q4'
        ]
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_format)

        row = 1
        for coa, values in data.items():
            sheet.write(row, 0, coa) 
            sheet.write(row, 1, values.get('April', 0))
            sheet.write(row, 2, values.get('May', 0))
            sheet.write(row, 3, values.get('June', 0))
            sheet.write(row, 4, values.get('Q1', 0))
            sheet.write(row, 5, values.get('July', 0))
            sheet.write(row, 6, values.get('August', 0))
            sheet.write(row, 7, values.get('September', 0))
            sheet.write(row, 8, values.get('Q2', 0))
            sheet.write(row, 9, values.get('October', 0))
            sheet.write(row, 10, values.get('November', 0))
            sheet.write(row, 11, values.get('December', 0))
            sheet.write(row, 12, values.get('Q3', 0))
            sheet.write(row, 13, values.get('January', 0))
            sheet.write(row, 14, values.get('February', 0))
            sheet.write(row, 15, values.get('March', 0))
            sheet.write(row, 16, values.get('Q4', 0))
            row += 1

        workbook.close()
        buffer.seek(0)
        return buffer.read()
