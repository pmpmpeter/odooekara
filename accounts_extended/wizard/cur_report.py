from odoo import models, fields, api
import xlsxwriter
import base64
import calendar
from io import BytesIO
from datetime import date, timedelta, datetime


class AccountCURReportWizard(models.TransientModel):
    _name = 'account.cur.report.wizard'
    _description = 'Cash Utilization Report Wizard'

    def _default_start_date(self):
        """Calculate the start date of the current financial year."""
        today = date.today()
        return date(today.year, today.month, 1)

    def _default_end_date(self):
        """Set the end date to the current date."""
        return date.today()

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    start_date = fields.Date(string='Start Date', default=_default_start_date, required=True, )
    end_date = fields.Date(
        string='End Date',
        default=_default_end_date,
        required=True,
    )
    groupby_month = fields.Boolean(string='Group By Month')
    report_file = fields.Binary('Report File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)

    def action_generate_cur_report(self):
        report_content = self._generate_excel_report()
        self.report_file = base64.b64encode(report_content)
        self.file_name = f"Cash_Utilization_Report_{datetime.now().strftime('%d%m%y')}.xlsx"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.cur.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def get_month_list(self,start, end):
        months = []
        current = start.replace(day=1)  # Start from 1st of month
        while current <= end:
            months.append(current.strftime("%b").upper())  # 'APR', 'MAY'
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return months


    def _generate_excel_report(self):
        """Generate an Excel file from CRR data, including company and transaction details."""
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Fund Utilization Report')
        title_format = workbook.add_format({'bold': True, 'font_size': 12, 'text_wrap': True})
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:Z', 15)
        sheet.set_row(13, 30)
        sheet.freeze_panes(1, 0)
        # sheet.protect()
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'font_color': '#000000',
            # 'border': 1,
            'align': 'center',
        })
        header_format1 = workbook.add_format({
            'bold': True,
            'font_color': '#000000',
            # 'border': 1,
            'align': 'right',
        })
        header_format_num = workbook.add_format({
            'bold': True,
            'font_color': '#000000',
            'num_format': '#,##0.00',
            # 'border': 1,
            'align': 'right',
        })
        total_format1 = workbook.add_format({
            'bold': True,
            'font_color': '#000000',
            # 'border': 1,
            'align': 'right',
            'num_format': '#,##0',
        })
        value_format = workbook.add_format(
            {'num_format': '#,##0.00',
             # 'border': 1,
             'align': 'right'})  # Float format and border
        value_format1 = workbook.add_format(
            {'num_format': '#,##0.00',
             # 'border': 1,
             'align': 'right',
             'bg_color': '#FFFF00', })

        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            # 'border': 1,
            'align': 'right',
            'num_format': '#,##0',
        })
        formatted_date = self.start_date.strftime('%d-%b-%Y')
        formatted_en_date = self.end_date.strftime('%d-%b-%Y')
        month_list = self.get_month_list(self.start_date, self.end_date)
        sheet.write(0, 0, 'Particulars  ', header_format)
        sheet.write(0, 1, 'GL Code', header_format)
        sheet.write(0, 2, 'Amount', header_format)
        sheet.write(0, 3, 'Amount', header_format)
        sheet.write(1, 0, 'Opening Balance as on %s' % (formatted_date), value_format)
        # base_col = 2
        # for idx, month in enumerate(month_list):
        #     sheet.write(5, base_col + idx, month, header_format)
        #     base_col += 1
        query = """
                             select
                    -- aml.id AS move_line_id
                    aml.account_id,
                  ba.code AS account_code,
                 ba.name AS account_name,
                    sum(aml.debit) AS total_debit,
                    sum(aml.credit) AS total_credit,
                    am.expense_type As expense_type
                from account_move_line aml 
                join account_move am on aml.move_id = am.id
                join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                WHERE 
                    aml.company_id = %s
                    AND aml.date BETWEEN %s AND %s
                    AND am.active = 'True'
                    AND am.state = 'posted'
                group by 
                    aml.account_id,
                     ba.name,
                     ba.code,
                     am.expense_type
                ORDER BY 
                    ba.code,
                    am.expense_type,
                    ba.name;
                    -- aml.date
            """
        # Add company_id condition if it exists
        query_params = (self.company_id.id,self.start_date, self.end_date)
        self.env.cr.execute(query, query_params)
        records = self.env.cr.dictfetchall()

        opening_balance_1 = 0
        end_balance_1 = 0
        # query8 = """
        #             select sum(aml.debit-aml.credit) as balance
        #             from account_move_line aml
        #             join account_account aa on (aa.id = aml.account_id)
        #             where aa.account_type='asset_cash' and aml.date<%s
        #             AND aml.company_id = %s;
        #         """
        # query_params8 = (self.start_date, self.company_id.id)

        query8 = """
                select sum(aml.debit-aml.credit) as balance
                from account_move_line aml
                join account_account aa on (aa.id = aml.account_id)
                join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                and aml.date<%s and 
                aml.parent_state = 'posted'
            """
        # Add company_id condition if it exists
        if self.company_id:
            query8 += " AND aml.company_id = %s"
            query_params8 = (self.start_date, self.company_id.id)
        else:
            query_params8 = (self.start_date,)

        self.env.cr.execute(query8, query_params8)
        lines8 = self.env.cr.dictfetchall()
        if (lines8[0].get('balance') != None):
            opening_balance_1 = lines8[0].get('balance')
            sheet.write(1, 3, opening_balance_1, value_format)
        query9 = """
            SELECT aa.code AS account_code, aa.name AS account_name,
                   SUM(aml.debit - aml.credit) AS balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                AND aml.parent_state = 'posted' 
              AND aml.date < %s
        """

        if self.company_id:
            query9 += " AND aml.company_id = %s"

        query9 += " GROUP BY aa.code, aa.name ORDER BY aa.code"

        if self.company_id:
            query_params9 = (self.start_date, self.company_id.id)
        else:
            query_params9 = (self.start_date,)

        self.env.cr.execute(query9, query_params9)
        split_lines = self.env.cr.dictfetchall()
        row_num = 2  # Starting row just below the total
        # sheet.write(row_num, 2, "Account", header_format)
        # sheet.write(row_num, 3, "Balance", header_format)
        # row_num += 1

        for line in split_lines:
            sheet.write(row_num, 0, line['account_name']['en_US'], value_format)
            sheet.write(row_num, 1, line['account_code'], value_format)
            sheet.write(row_num, 3, line['balance'] or 0.0, value_format)
            row_num += 1
        row_num +=1
        if self.groupby_month:
            base_col = 2
            for idx, month in enumerate(month_list):
                start_col = base_col + (idx * 2)
                end_col = start_col + 1
                sheet.merge_range(row_num, start_col, row_num, end_col, month, header_format)
            row_num += 1
        sheet.write(row_num, 0, 'Receipts:', header_format1)

        end_balance1 = """SELECT aa.code AS account_code, aa.name AS account_name,
                   SUM(aml.debit - aml.credit) AS balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
              AND aml.date <=%s
              AND aml.parent_state = 'posted' 
        """
        if self.company_id:
            end_balance1 += " AND aml.company_id = %s"
            end_balance1 += " GROUP BY aa.code, aa.name ORDER BY aa.code"
            end_balance_params = (self.end_date, self.company_id.id)
            end_balance_params1 = (self.end_date, self.company_id.id)
        else:
            end_balance_params = (self.end_date,)
            end_balance_params1 = (self.end_date,)
        end_balance = self.env.cr.dictfetchall()
        self.env.cr.execute(end_balance1, end_balance_params1)
        end_balance1 = self.env.cr.dictfetchall()

        if (end_balance1[0].get('balance') != None):
            end_balance_1 = end_balance1[0].get('balance')
        credit_accounts = [record for record in records if record['total_credit'] > 0]
        debit_accounts = [record for record in records if record['total_debit'] > 0]
        row_num = 8
        for account in debit_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 3, account['total_debit'], value_format1) if not self.groupby_month else sheet.write(
                row_num, 3, '', value_format)
            row_num += 2
            self.env.cr.execute("""
                select
                    aml.id AS move_line_id,
                    aml.account_id,
                    ba.code AS account_code,
                    ba.name AS account_name,
                    aml.name AS line_name,
                    rp.name AS partner_name,
                    aml.debit AS line_debit,
                    aml.credit AS line_credit,
                    aml.date AS date,
                    aml.move_id,
                    am.active
                from account_move_line aml 
                join account_move am on aml.move_id = am.id
                LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                WHERE 
                    aml.company_id = %s
                    AND aml.date BETWEEN %s AND %s
                    AND am.active = 'True'
                    AND am.state = 'posted'
                ORDER BY 
                    ba.code,
                    ba.name,
                    aml.name,
                    rp.name,
                    aml.date;
            """, (self.company_id.id,self.start_date, self.end_date))
            detail_records = self.env.cr.dictfetchall()
            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_debit') > 0:
                    if account['account_name']['en_US'] == detail['account_name']['en_US']:
                        detail_month = detail['date'].strftime('%b').upper()
                        if not self.groupby_month:
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, 3, detail.get('line_debit') or 0, value_format)
                        if self.groupby_month and detail_month in month_list:
                            base_month_col = 3
                            month_index = month_list.index(detail_month)
                            col_number = base_month_col + (month_index * 2)
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, col_number, detail.get('line_debit') or 0, value_format)
                        row_num += 1
        row_num += 1
        sheet.write(row_num, 0, 'Payments:', header_format1)
        row_num += 1
        capex_accounts = [account for account in credit_accounts if account['expense_type'] == 'capex']
        opex_accounts = [account for account in credit_accounts if account['expense_type'] == 'opex']
        sheet.write(row_num, 0, 'Vendor Payment CAPEX:', header_format1)
        row_num += 2
        for account in capex_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 2, account['total_credit'], value_format1) if account[
                                                                                  'total_credit'] != 0 and not self.groupby_month else sheet.write(
                row_num, 2, '', value_format)
            row_num += 2
            self.env.cr.execute("""
                            select
                    aml.id AS move_line_id,
                    aml.account_id,
                    ba.code AS account_code,
                    ba.name AS account_name,
                    rp.name AS partner_name,
                    aml.name AS line_name,
                    aml.debit AS line_debit,
                    aml.credit AS line_credit,
                    am.expense_type As expense_type,
                    aml.date,
                    aml.move_id,
                    am.active
                from account_move_line aml 
                join account_move am on aml.move_id = am.id
                LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                WHERE 
                    aml.company_id = %s
                    AND aml.date BETWEEN %s AND %s
                    AND am.active = 'True'
                    AND am.state = 'posted'
                ORDER BY 
                    ba.code,
                    ba.name,
                    rp.name,
                    aml.name,
                    aml.date;
                        """, (self.company_id.id,self.start_date, self.end_date))
            detail_records = self.env.cr.dictfetchall()

            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_credit') > 0:
                    if account['account_name']['en_US'] == detail['account_name']['en_US']:
                        detail_month = detail['date'].strftime('%b').upper()
                        if not self.groupby_month:
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, 2, detail.get('line_credit') or 0, value_format)

                        if self.groupby_month and detail_month in month_list:
                            base_month_col = 3
                            month_index = month_list.index(detail_month)
                            col_number = base_month_col + (month_index * 2)
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, col_number, detail.get('line_credit') or 0, value_format)
                        row_num += 1

            row_num += 2
        sheet.write(row_num, 0, 'Vendor Payment OPEX:', header_format1)
        row_num += 2
        for account in opex_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 2, account['total_credit'], value_format1) if account[
                                                                                  'total_credit'] != 0 and not self.groupby_month else sheet.write(
                row_num, 2, '', value_format)
            row_num += 2
            self.env.cr.execute("""
                           select
                    aml.id AS move_line_id,
                    aml.account_id,
                    ba.code AS account_code,
                    ba.name AS account_name,
                    aml.name AS line_name,
                    aml.debit AS line_debit,
                    aml.credit AS line_credit,
                    rp.name AS partner_name,
                    am.expense_type As expense_type,
                    aml.date,
                    aml.move_id,
                    am.active
                from account_move_line aml 
                LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                join account_move am on aml.move_id = am.id
                join 
                (select aa.id,aa.code, aa.name from account_account aa join account_journal aj on aj.default_account_id = aa.id
                                where aa.account_type='asset_cash') ba 
                            on ba.id = aml.account_id
                WHERE 
                    aml.company_id = %s
                    AND aml.date BETWEEN %s AND %s
                    AND am.active = 'True'
                    AND am.state = 'posted'
                ORDER BY 
                    ba.code,
                    ba.name,
                    rp.name,
                    aml.name,
                    aml.date;
                    
                        """, (self.company_id.id,self.start_date, self.end_date))
            detail_records = self.env.cr.dictfetchall()

            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_credit'):
                    if account['account_name']['en_US'] == detail['account_name']['en_US']:
                        detail_month = detail['date'].strftime('%b').upper()
                        if not self.groupby_month:
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, 2, detail.get('line_credit') or 0, value_format)
                        if self.groupby_month and detail_month in month_list:
                            base_month_col = 2
                            month_index = month_list.index(detail_month)
                            col_number = base_month_col + (month_index * 2)
                            sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, col_number, detail.get('line_credit') or 0, value_format)
                        row_num += 1
        row_num += 1
        total_d = 0.0
        total_c = 0.0
        if records:
            for rec in records:
                total_d = total_d + rec['total_credit']
                total_c = total_c + rec['total_debit']
        if not self.groupby_month:
            sheet.write(row_num, 0, 'Total', header_format_num)
            sheet.write(row_num, 2, total_d, header_format_num)
            sheet.write(row_num, 3, total_c + opening_balance_1, header_format_num)
            row_num += 2
        sheet.write(row_num, 0, 'Total expense as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_d, header_format_num)
        row_num += 1
        sheet.write(row_num, 0, 'Total receipts as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_c, header_format_num)
        row_num += 2
        sheet.write(row_num, 0, 'Balance as per book as on %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 3, total_c + opening_balance_1 - (total_d), header_format_num)
        row_num += 1

        for line in end_balance1:
            sheet.write(row_num, 0, line['account_name']['en_US'], value_format)
            sheet.write(row_num, 1, line['account_code'], value_format)
            sheet.write(row_num, 3, line['balance'] or 0.0, value_format)
            row_num += 1
        workbook.close()
        buffer.seek(0)
        return buffer.read()
