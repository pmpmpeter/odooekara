from odoo import models, fields, api
import xlsxwriter
import base64
import calendar
from io import BytesIO
from datetime import date, timedelta,datetime


class AccountCURReportWizard(models.TransientModel):
    _name = 'account.cur.report.wizard'
    _description = 'Fund Utilization Report Wizard'

    def _default_start_date(self):
        """Calculate the start date of the current financial year."""
        today = date.today()
        return date(today.year, today.month, 1)

    def _default_end_date(self):
        """Set the end date to the current date."""
        return date.today()

    start_date = fields.Date(string='Start Date',default=_default_start_date,required=True,)
    end_date = fields.Date(
        string='End Date',
        default=_default_end_date,
        required=True,
    )
    report_file = fields.Binary('Report File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)

    def action_generate_cur_report(self):

        report_content = self._generate_excel_report()

        self.report_file = base64.b64encode(report_content)
        self.file_name = f"Fund_Utilization_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.cur.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _generate_excel_report(self):
        """Generate an Excel file from CRR data, including company and transaction details."""
        print('qqqqqqqqq',self.start_date,self.end_date)
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Fund Utilization Report')
        title_format = workbook.add_format({'bold': True, 'font_size': 12, 'text_wrap': True})
        sheet.set_column('A:A', 45)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:D', 25)
        sheet.set_row(13, 30)
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'font_color': '#000000',
            'border': 1,
            'align': 'right',
        })
        header_format1 = workbook.add_format({
            'bold': True,
            'font_color': '#000000',
            'border': 1,
            'align': 'right',
        })
        total_format1 = workbook.add_format({
            'bold': True,
            'font_color': '#000000',
            'border': 1,
            'align': 'right',
            'num_format': '#,##0',
        })
        value_format = workbook.add_format({'num_format': '#,##0', 'border': 1, 'align': 'right'})  # Float format and border

        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1,
            'align': 'right',
            'num_format': '#,##0',
        })
        formatted_date = self.start_date.strftime('%d-%b-%Y')
        formatted_en_date = self.end_date.strftime('%d-%b-%Y')
        sheet.write(0, 0, 'Particulars  ', header_format)
        sheet.write(0, 1, 'GL Code', header_format)
        sheet.write(0, 2, 'Amount', header_format)
        sheet.write(0, 3, 'Amount', header_format)
        sheet.write(1, 0, 'Opening Balance as on %s'%(formatted_date),value_format)
        sheet.write(2, 0, 'Receipts:', header_format1)
        query = """
           SELECT 
    aa.name AS account_name,
    aa.code As account_code,
    SUM(aml.debit) AS total_debit,
    SUM(aml.credit) AS total_credit
FROM 
    account_move_line aml
JOIN 
    account_move am ON aml.move_id = am.id
JOIN 
    account_journal aj ON aml.journal_id = aj.id
JOIN 
    account_account aa ON aml.account_id = aa.id
WHERE 
    aj.type IN ('bank', 'cash') 
    AND aa.account_type NOT IN ('asset_cash')
    AND aml.date BETWEEN %s AND %s
GROUP BY 
    aa.name,aa.code
ORDER BY 
    aa.name,aa.code;   
        """
        query1 = """
                   SELECT 
            aa.name AS account_name,
            aa.code As account_code,
            SUM(aml.debit) AS total_debit,
            SUM(aml.credit) AS total_credit
        FROM 
            account_move_line aml
        JOIN 
            account_move am ON aml.move_id = am.id
        JOIN 
            account_journal aj ON aml.journal_id = aj.id
        JOIN 
            account_account aa ON aml.account_id = aa.id
        WHERE 
            aa.account_type IN ('asset_cash')
            AND aml.date <= %s
        GROUP BY 
            aa.name,aa.code
        ORDER BY 
            aa.name,aa.code;   
                """
        query2 = """
                           SELECT 
                    aa.name AS account_name,
                    aa.code As account_code,
                    SUM(aml.debit) AS total_debit,
                    SUM(aml.credit) AS total_credit
                FROM 
                    account_move_line aml
                JOIN 
                    account_move am ON aml.move_id = am.id
                JOIN 
                    account_journal aj ON aml.journal_id = aj.id
                JOIN 
                    account_account aa ON aml.account_id = aa.id
                WHERE 
                    aa.account_type IN ('asset_cash')
                    AND aml.date <= %s
                GROUP BY 
                    aa.name,aa.code
                ORDER BY 
                    aa.name,aa.code;   
                        """

        self.env.cr.execute(query,(self.start_date,self.end_date))
        records = self.env.cr.dictfetchall()

        opening_balance_1 = 0
        end_balance_1 = 0
        query8 = """
                    select sum(aml.debit-aml.credit) as balance
                    from account_move_line aml
                    join account_account aa on (aa.id = aml.account_id)
                    where aa.account_type='asset_cash' and aml.date<%s;
                """
        query_params8 = ([self.start_date])
        self.env.cr.execute(query8, query_params8)
        lines8 = self.env.cr.dictfetchall()
        if (lines8[0].get('balance') != None):
            opening_balance_1 = lines8[0].get('balance')
            sheet.write(1, 3, opening_balance_1, value_format)

        end_balance = """
                            select sum(aml.debit-aml.credit) as balance
                            from account_move_line aml
                            join account_account aa on (aa.id = aml.account_id)
                            where aa.account_type='asset_cash' and aml.date<%s;
                        """
        end_balance_params = ([self.end_date])
        self.env.cr.execute(end_balance, end_balance_params)
        end_balance = self.env.cr.dictfetchall()
        if (end_balance[0].get('balance') != None):
            end_balance_1 = end_balance[0].get('balance')
        credit_accounts = [record for record in records if record['total_credit'] > 0]
        debit_accounts = [record for record in records if record['total_debit'] > 0]
        row_num = 3
        for account in credit_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'],value_format)
            sheet.write(row_num, 1, account['account_code'],value_format)
            sheet.write(row_num, 3, account['total_credit'],value_format) if account['total_credit'] != 0 else sheet.write(row_num, 3, '',value_format)
            row_num += 1
        sheet.write(row_num, 0, 'Payments:', header_format1)
        row_num +=1
        for account in debit_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'],value_format)
            sheet.write(row_num, 1, account['account_code'],value_format)
            sheet.write(row_num, 2, account['total_debit'],value_format) if account['total_debit'] != 0 else sheet.write(row_num, 2, '',value_format)
            row_num += 1
        total_d =0.0
        total_c =0.0
        for rec in debit_accounts:
            total_d =total_d+ rec['total_debit']
        for rec in credit_accounts:
            total_c =total_c+ rec['total_credit']
        sheet.write(row_num, 0, 'Total', header_format1)
        sheet.write(row_num, 2, total_d, total_format1)
        sheet.write(row_num, 3, total_c, total_format1)
        row_num +=2
        sheet.write(row_num, 0, 'Total expense as on  %s' %(formatted_en_date) ,header_format1)
        sheet.write(row_num, 2, total_d,value_format)
        row_num += 1
        sheet.write(row_num, 0, 'Total receipts as on  %s' %(formatted_en_date),header_format1)
        sheet.write(row_num, 2, total_c,value_format)
        row_num += 2
        sheet.write(row_num, 0, 'Balance as per book as on %s' %(formatted_en_date), header_format1)
        sheet.write(row_num, 3, end_balance_1, value_format)


        workbook.close()
        buffer.seek(0)
        return buffer.read()
