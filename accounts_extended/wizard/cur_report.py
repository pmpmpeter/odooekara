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

    def _generate_excel_report(self):
        """Generate an Excel file from CRR data, including company and transaction details."""
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Fund Utilization Report')
        title_format = workbook.add_format({'bold': True, 'font_size': 12, 'text_wrap': True})
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:D', 15)
        sheet.set_row(13, 30)
        sheet.freeze_panes(1, 0)
        # sheet.protect()
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'font_color': '#000000',
            # 'border': 1,
            'align': 'right',
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
        sheet.write(0, 0, 'Particulars  ', header_format)
        sheet.write(0, 1, 'GL Code', header_format)
        sheet.write(0, 2, 'Amount', header_format)
        sheet.write(0, 3, 'Amount', header_format)
        sheet.write(1, 0, 'Opening Balance as on %s' % (formatted_date), value_format)
        sheet.write(5, 0, 'Receipts:', header_format1)

        query = """
               SELECT 
                    aa.name AS account_name,
                    aa.code As account_code,
                    am.expense_type As expense_type,
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
                JOIN 
                    account_account jaa ON aj.default_account_id = jaa.id                    
                WHERE 
                    aj.type IN ('bank', 'cash')
                    AND jaa.account_type != 'liability_credit_card'
                    AND aml.parent_state != 'cancel' 
                    AND aa.account_type NOT IN ('asset_cash','liability_credit_card') and aa.code NOT IN ('100203','100204','100202','100801')
                    AND aml.date BETWEEN %s AND %s
            """
        # Add company_id condition if it exists
        if self.company_id:
            query += " AND aml.company_id = %s"
            query_params = (self.start_date, self.end_date, self.company_id.id)
        else:
            query_params = (self.start_date, self.end_date)
        query += """
                GROUP BY 
                    aa.name, aa.code, am.expense_type
                ORDER BY 
                    aa.name, aa.code, am.expense_type;   
            """
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
                
                where aa.account_type='asset_cash' and aml.date<%s and aml.parent_state = 'posted' and aa.code NOT IN ('100203','100204','100202','100801')
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
            WHERE aa.account_type = 'asset_cash'
                AND aml.parent_state = 'posted' 
              AND aml.date < %s
              AND aa.code NOT IN ('100203','100204','100202','100801')
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
        # end_balance = """
        #                     select sum(aml.debit-aml.credit) as balance
        #                     from account_move_line aml
        #                     join account_account aa on (aa.id = aml.account_id)
        #                     where aa.account_type='asset_cash' and aml.date<%s
        #                     AND aml.company_id = %s;
        #                 """
        # end_balance_params = (self.end_date, self.company_id.id)
        # end_balance = """
        #         select sum(aml.debit-aml.credit) as balance
        #         from account_move_line aml
        #         join account_account aa on (aa.id = aml.account_id)
        #         where aa.account_type='asset_cash' and aml.date<%s and aml.parent_state != 'cancel' and  aa.code NOT IN ('100203','100204','100202','100801')
        #     """

        end_balance1 = """SELECT aa.code AS account_code, aa.name AS account_name,
                   SUM(aml.debit - aml.credit) AS balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aa.account_type = 'asset_cash'
              AND aml.date <=%s
              AND aml.parent_state = 'posted' 
              AND aa.code NOT IN ('100203','100204','100202','100801')
        """

        # Add company_id condition if it exists
        if self.company_id:
            # end_balance += " AND aml.company_id = %s"
            end_balance1 += " AND aml.company_id = %s"
            end_balance1 += " GROUP BY aa.code, aa.name ORDER BY aa.code"
            end_balance_params = (self.end_date, self.company_id.id)
            end_balance_params1 = (self.end_date, self.company_id.id)
        else:
            end_balance_params = (self.end_date,)
            end_balance_params1 = (self.end_date,)
        # self.env.cr.execute(end_balance, end_balance_params)
        end_balance = self.env.cr.dictfetchall()
        self.env.cr.execute(end_balance1, end_balance_params1)
        end_balance1 = self.env.cr.dictfetchall()

        # query8 = """
        #         select sum(aml.debit-aml.credit) as balance
        #         from account_move_line aml
        #         join account_account aa on (aa.id = aml.account_id)
        #         where aa.account_type='asset_cash' and aml.date<%s and aa.code NOT IN ('100203','100204','100202','100801')
        #     """
        # end_balance_query = """
        #     SELECT aa.code AS account_code, aa.name AS account_name,
        #            SUM(aml.debit - aml.credit) AS balance
        #     FROM account_move_line aml
        #     JOIN account_account aa ON aa.id = aml.account_id
        #     WHERE aa.account_type = 'asset_cash'
        #       AND aml.date > %s
        #         AND aml.date < %s
        #       AND aa.code NOT IN ('100203','100204','100202','100801')
        # """
        # if self.company_id:
        #     end_balance_query += " AND aml.company_id = %s"
        #
        # # ✅ Add GROUP BY clause to fix the error
        # end_balance_query += " GROUP BY aa.code, aa.name ORDER BY aa.code"
        #
        # # Parameters
        # if self.company_id:
        #     end_balance_params_query = (self.start_date,self.end_date, self.company_id.id)
        # else:
        #     end_balance_params_query = (self.end_date,)
        #
        # # Execute and fetch
        # self.env.cr.execute(end_balance_query, end_balance_params_query)
        # end_balance_lines = self.env.cr.dictfetchall()

        if (end_balance1[0].get('balance') != None):
            end_balance_1 = end_balance1[0].get('balance')
        credit_accounts = [record for record in records if record['total_credit'] > 0]
        debit_accounts = [record for record in records if record['total_debit'] > 0]
        row_num = 7

        # for account in credit_accounts:
        #     print(account['account_name'],'jjjjjjjjjjjjjjjjjj')
        #     sheet.write(row_num, 0, account['account_name']['en_US'], value_format)
        #     sheet.write(row_num, 1, account['account_code'], value_format)
        #     sheet.write(row_num, 3, account['total_credit'], value_format) if account[
        #                                                                           'total_credit'] != 0 else sheet.write(
        #         row_num, 3, '', value_format)
        #     row_num += 1
        # Loop through summarized accounts (main group)
        for account in credit_accounts:
            # Write the main group row
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 3, account['total_credit'], value_format1)
            row_num += 2

            # Fetch detailed transactions for this account
            self.env.cr.execute("""
                SELECT
                    aml.name AS line_name,
                    rp.name AS partner_name,
                    SUM(aml.credit) AS line_credit
                    FROM account_move_line aml
                    LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                    JOIN 
                    account_journal aj ON aml.journal_id = aj.id
                    JOIN 
                    account_account aa ON aml.account_id = aa.id
                    JOIN account_account jaa ON aj.default_account_id = jaa.id

                    WHERE aml.account_id = (
                        SELECT id FROM account_account WHERE code = %s LIMIT 1
                    )
                    AND aj.type IN ('bank', 'cash')
                    AND jaa.account_type != 'liability_credit_card'
                    AND aml.parent_state = 'posted'
                    AND aa.account_type NOT IN ('asset_cash') and aa.code NOT IN ('100203','100204','100202','100801')
                    AND aml.date BETWEEN %s AND %s
                    AND aml.company_id = %s
                    GROUP BY aml.name, rp.name
            """, (account['account_code'], self.start_date, self.end_date, self.company_id.id))
            detail_records = self.env.cr.dictfetchall()
            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_credit') > 0:
                    sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                    sheet.write(row_num, 1, account['account_code'], value_format)
                    sheet.write(row_num, 3, detail.get('line_credit') or 0, value_format)
                    row_num += 1
        row_num += 1
        sheet.write(row_num, 0, 'Payments:', header_format1)
        row_num += 1
        # print(debit_accounts,'vcccccccccccxxxxxxxxxxxxx')
        capex_accounts = [account for account in debit_accounts if account['expense_type'] == 'capex']
        opex_accounts = [account for account in debit_accounts if account['expense_type'] == 'opex']
        sheet.write(row_num, 0, 'Vendor Payment CAPEX:', header_format1)
        row_num += 2
        for account in capex_accounts:
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 2, account['total_debit'], value_format1) if account[
                                                                                  'total_debit'] != 0 else sheet.write(
                row_num, 2, '', value_format)
            row_num += 2
            self.env.cr.execute("""
                            SELECT
                                aml.name AS line_name,
                                rp.name AS partner_name,
                                SUM(aml.debit) AS line_debit
                                FROM account_move_line aml
                                LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                                JOIN 
                                account_journal aj ON aml.journal_id = aj.id
                                JOIN 
                                account_account aa ON aml.account_id = aa.id
                                JOIN account_account jaa ON aj.default_account_id = jaa.id  -- join to journal's account

                                WHERE aml.account_id = (
                                    SELECT id FROM account_account WHERE code = %s LIMIT 1
                                )
                                AND aj.type IN ('bank', 'cash')
                                AND jaa.account_type != 'liability_credit_card'
                                AND aml.parent_state = 'posted' 
                                AND aa.account_type NOT IN ('asset_cash','liability_credit_card') and aa.code NOT IN ('100203','100204','100202','100801')
                                AND aml.date BETWEEN %s AND %s
                                AND aml.company_id = %s
                                GROUP BY aml.name, rp.name
                        """, (account['account_code'], self.start_date, self.end_date, self.company_id.id))
            detail_records = self.env.cr.dictfetchall()

            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_debit') > 0:
                    sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                    sheet.write(row_num, 1, account['account_code'], value_format)
                    sheet.write(row_num, 2, detail.get('line_debit') or 0, value_format)
                    row_num += 1

            row_num += 2
        sheet.write(row_num, 0, 'Vendor Payment OPEX:', header_format1)
        row_num += 2
        for account in opex_accounts:
            print(account['account_name']['en_US'],'jjjj')
            print( account['total_debit'],'oooooo')
            sheet.write(row_num, 0, account['account_name']['en_US'], value_format1)
            sheet.write(row_num, 1, account['account_code'], value_format1)
            sheet.write(row_num, 2, account['total_debit'], value_format1) if account[
                                                                                  'total_debit'] != 0 else sheet.write(
                row_num, 2, '', value_format)
            row_num += 2
            self.env.cr.execute("""
                            SELECT
                                        aml.name AS line_name,
                                        rp.name AS partner_name,
                                        SUM(aml.debit) AS line_debit
                                    FROM account_move_line aml
                                    LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                                    JOIN account_journal aj ON aml.journal_id = aj.id
                                    JOIN account_account aa ON aml.account_id = aa.id
                                    JOIN account_account jaa ON aj.default_account_id = jaa.id  -- join to journal's account
                                    
                                    WHERE aml.account_id = (
                                        SELECT id FROM account_account WHERE code = %s LIMIT 1
                                    )
                                    AND aj.type IN ('bank', 'cash')
                                    AND jaa.account_type != 'liability_credit_card'
                                    AND aml.parent_state = 'posted'
                                    AND aa.account_type NOT IN ('asset_cash','liability_credit_card')
                                    AND aa.code NOT IN ('100203','100204','100202','100801')
                                    AND aml.date BETWEEN %s AND %s
                                    AND aml.company_id = %s
                                    GROUP BY aml.name, rp.name
                        """, (account['account_code'], self.start_date, self.end_date, self.company_id.id))
            detail_records = self.env.cr.dictfetchall()

            # Write detailed rows below the main group
            for detail in detail_records:
                if detail.get('line_debit'):
                    sheet.write(row_num, 0, detail.get('partner_name') or detail.get('line_name'), value_format)
                    sheet.write(row_num, 1, account['account_code'], value_format)
                    sheet.write(row_num, 2, detail.get('line_debit') or 0, value_format)
                    row_num += 1
        row_num += 1
        # for account in debit_accounts:
        #     sheet.write(row_num, 0, account['account_name']['en_US'],value_format)
        #     sheet.write(row_num, 1, account['account_code'],value_format)
        #     sheet.write(row_num, 2, account['total_debit'],value_format) if account['total_debit'] != 0 else sheet.write(row_num, 2, '',value_format)
        #     row_num += 1
        total_d = 0.0
        total_c = 0.0
        for rec in debit_accounts:
            total_d = total_d + rec['total_debit']
        for rec in credit_accounts:
            total_c = total_c + rec['total_credit']
        sheet.write(row_num, 0, 'Total', header_format_num)
        sheet.write(row_num, 2, total_d, header_format_num)
        sheet.write(row_num, 3, total_c + opening_balance_1, header_format_num)
        row_num += 2
        sheet.write(row_num, 0, 'Total expense as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_d, header_format_num)
        row_num += 1
        sheet.write(row_num, 0, 'Total receipts as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_c + opening_balance_1, header_format_num)
        row_num += 2
        sheet.write(row_num, 0, 'Balance as per book as on %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 3, total_c + opening_balance_1 - (total_d), header_format_num)
        row_num += 1

        for line in end_balance1:
            sheet.write(row_num, 0, line['account_name']['en_US'],value_format)
            sheet.write(row_num, 1, line['account_code'],value_format)
            sheet.write(row_num, 3, line['balance'] or 0.0, value_format)
            row_num += 1
        workbook.close()
        buffer.seek(0)
        return buffer.read()
