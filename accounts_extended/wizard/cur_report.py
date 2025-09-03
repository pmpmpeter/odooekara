from odoo import models, fields, api
import xlsxwriter
import base64
import calendar
from io import BytesIO
from datetime import date, timedelta, datetime
from collections import defaultdict,Counter


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
        name_format = workbook.add_format({
            'align': 'right',
        })
        formatted_date = self.start_date.strftime('%d-%b-%Y')
        formatted_en_date = self.end_date.strftime('%d-%b-%Y')
        month_list = self.get_month_list(self.start_date, self.end_date)
        sheet.write(0, 0, 'Particulars  ', header_format)
        sheet.write(0, 1, 'GL Code', header_format)
        sheet.write(0, 2, 'Amount', header_format)
        sheet.write(0, 3, 'Amount', header_format)
        sheet.write(1, 0, 'Opening Balance as on %s' % (formatted_date), value_format)

        records_debit = self.get_cash_bank_utilization_debit(self.start_date, self.end_date, self.company_id)
        records_credit = self.get_cash_bank_utilization_credit(self.start_date, self.end_date, self.company_id)

        opening_balance_1 = 0
        query8 = """
                select sum(aml.debit-aml.credit) as balance
                from account_move_line aml
                join account_account aa on (aa.id = aml.account_id)

                where aa.account_type='asset_cash' and aml.date<%s and aml.parent_state = 'posted' and aa.code NOT IN ('100203','100204','100202')
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
            JOIN account_journal aj ON aj.id = aml.journal_id
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
        row_num = 2
        for line in split_lines:
            sheet.write(row_num, 0, line['account_name']['en_US'], value_format)
            sheet.write(row_num, 1, line['account_code'], value_format)
            sheet.write(row_num, 3, line['balance'] or 0.0, value_format)
            row_num += 1
        row_num += 1
        sheet.write(row_num, 0, 'Receipts:', header_format1)
        row_num += 1
        print(row_num,'kkkkkkkkkkkkkkkk')
        if self.groupby_month:
            base_col = 4
            for idx, month in enumerate(month_list):
                print('vvvvvvvv')
                start_col = base_col + idx
                sheet.write(row_num,start_col, month, header_format)
                sheet.set_column(row_num, start_col, 15)
            row_num += 1
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

        if (end_balance1[0].get('balance') != None):
            end_balance_1 = end_balance1[0].get('balance')
        credit_accounts = [record for record in records_credit if record['total_credit'] > 0]
        debit_accounts = [record for record in records_debit if record['total_debit'] > 0]
        row_num = row_num+2
        for account in credit_accounts:
            if not self.groupby_month:
                sheet.write(row_num, 0, account['account_name'], value_format1)
                sheet.write(row_num, 1, account['account_code'], value_format1)
                sheet.write(row_num, 3, account['total_credit'], value_format1)
                row_num += 2
                for detail in account['entries']:
                        if detail.get('credit'):
                                sheet.write(row_num, 0, detail.get('partner_id'),name_format)
                                sheet.write(row_num, 1, account['account_code'], value_format)
                                sheet.write(row_num, 3, detail.get('credit') or 0, value_format)
                                row_num += 1
            else:
                monthly_totals = defaultdict(float)
                for detail in account['entries']:
                    if detail.get('credit'):
                        detail_month = detail.get('date').strftime('%b').upper()
                        monthly_totals[detail_month] += detail.get('credit')
                sheet.write(row_num, 0, account['account_name'], name_format)
                sheet.write(row_num, 1, account['account_code'], value_format)

                base_month_col = 4
                for month, amount in monthly_totals.items():
                    if month in month_list:
                        month_index = month_list.index(month)
                        col_number = base_month_col + month_index
                        sheet.write(row_num, col_number, amount, value_format)

                row_num += 1
        row_num += 1
        sheet.write(row_num, 0, 'Payments:', header_format1)
        row_num += 1
        capex_accounts = [account for account in debit_accounts if account['expense_type'] == 'capex']
        opex_accounts = [account for account in debit_accounts if account['expense_type'] == 'opex']
        sheet.write(row_num, 0, 'Vendor Payment CAPEX:', header_format1)
        row_num += 2
        for account in capex_accounts:
            if not self.groupby_month:
                sheet.write(row_num, 0, account['account_name'], value_format1)
                sheet.write(row_num, 1, account['account_code'], value_format1)
                sheet.write(row_num, 2, account['total_debit'], value_format1) if account[
                                                                                      'total_debit'] != 0 else sheet.write(
                    row_num, 2, '', value_format)
                row_num += 2
                for detail in account['entries']:
                        if detail.get('debit'):
                            if not self.groupby_month:
                                sheet.write(row_num, 0, detail.get('partner_id'),name_format)
                                sheet.write(row_num, 1, account['account_code'], value_format)
                                sheet.write(row_num, 2, detail.get('debit') or 0, value_format)
                                row_num += 1

            else:
                monthly_totals = defaultdict(float)
                for detail in account['entries']:
                    if detail.get('debit'):
                        detail_month = detail.get('date').strftime('%b').upper()
                        monthly_totals[detail_month] += detail.get('debit')
                sheet.write(row_num, 0, account['account_name'], name_format)
                sheet.write(row_num, 1, account['account_code'], value_format)

                base_month_col = 4
                for month, amount in monthly_totals.items():
                    if month in month_list:
                        month_index = month_list.index(month)
                        col_number = base_month_col + month_index
                        sheet.write(row_num, col_number, amount, value_format)

                row_num += 1
        sheet.write(row_num, 0, 'Vendor Payment OPEX:', header_format1)
        row_num += 2
        grand_totals = defaultdict(float)
        for account in opex_accounts:
            if not self.groupby_month:
                sheet.write(row_num, 0, account['account_name'], value_format1)
                sheet.write(row_num, 1, account['account_code'], value_format1)
                sheet.write(row_num, 2, account['total_debit'], value_format1) if account[
                                                                                      'total_debit'] != 0 else sheet.write(
                    row_num, 2, '', value_format)
                row_num += 2
                for detail in account['entries']:
                    if detail.get('debit'):
                        if not self.groupby_month:
                            sheet.write(row_num, 0, detail.get('partner_id'), name_format)
                            sheet.write(row_num, 1, account['account_code'], value_format)
                            sheet.write(row_num, 2, detail.get('debit') or 0, value_format)
                            row_num += 1

            else:
                monthly_totals = defaultdict(float)
                for detail in account['entries']:
                    if detail.get('debit'):
                        detail_month = detail.get('date').strftime('%b').upper()
                        monthly_totals[detail_month] += detail.get('debit')
                sheet.write(row_num, 0, account['account_name'], name_format)
                sheet.write(row_num, 1, account['account_code'], value_format)
                base_month_col = 4
                print(monthly_totals,'ggggggggggggggggggggg')
                for month, amount in monthly_totals.items():
                    grand_totals = 0
                    if month in month_list:
                        month_index = month_list.index(month)
                        col_number = base_month_col + month_index
                        sheet.write(row_num, col_number, amount, value_format)
                        grand_totals += amount
                        # print(grand_totals,'ggggggggggggg')
                row_num += 1
        row_num += 1
        total_d = 0.0
        total_c = 0.0
        for rec in debit_accounts:
            total_d = total_d + rec['total_debit']
        for rec in credit_accounts:
            total_c = total_c + rec['total_credit']
        if not self.groupby_month:
            sheet.write(row_num, 0, 'Total', header_format_num)
            sheet.write(row_num, 2, total_d, header_format_num)
            sheet.write(row_num, 3, total_c + opening_balance_1, header_format_num)
            row_num += 2
        sheet.write(row_num, 0, 'Total expense as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_d, header_format_num)
        row_num += 1
        sheet.write(row_num, 0, 'Total receipts as on  %s' % (formatted_en_date), header_format_num)
        sheet.write(row_num, 2, total_c , header_format_num)
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

    def get_cash_bank_utilization_debit(self, date_from, date_to,company_id):
        """
        Get cash/bank utilization summary using ORM (no raw SQL).
        """
        # Get moves in given date range, posted, with bank_date filter
        moves = self.env['account.move.line'].sudo().search([
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type','=','entry'),
            ('move_id.journal_id.type', 'in', ('bank', 'cash')),
            ('move_id.company_id','=',company_id.id),
        ])
        grouped = defaultdict(list)
        duplicates = defaultdict(list)
        stat_line = set()
        l = set()
        l_grp =  defaultdict(list)
        state_grp = defaultdict(list)
        outstanding =[]
        for line in moves:
            if line.matching_number:
                grouped[line.matching_number].append(line)
            elif not line.matching_number and line.statement_line_id:
                if line.move_id.journal_id.default_account_id.account_type in 'asset_cash' and line.date >= date_from and line.date <= date_to:
                    stat_line.add((line.move_id.name, line.id))
                    state_grp[line.move_name].append(line)
        for name, lines in list(state_grp.items()):
            for line in lines:
                move_line = self.env['account.move.line'].sudo().search([('move_id','=',line.move_id.id),('debit','=',line.credit)])
                if move_line:
                    for rec in move_line:
                        if not rec.matching_number:
                            outstanding.append(rec)
                else:
                    move_line = self.env['account.move.line'].sudo().search(
                        [('move_id', '=', line.move_id.id),('matching_number','=',False),('debit','!=',0)])
                    for rec in move_line:
                        outstanding.append(rec)
        result = defaultdict(lambda: {
            'account_name': '',
            'account_code': '',
            'expense_type': '',
            'total_debit': 0.0,
            'total_credit': 0.0,
            'entries': []
        })
        for match_no, group_lines in grouped.items():
            statement_line = next((l for l in group_lines if l.statement_line_id), None)

            if not statement_line:
                continue
            if statement_line.journal_id.default_account_id.account_type == 'asset_cash':
                stmt_date = statement_line.statement_line_id.date
                if not (date_from <= stmt_date <= date_to):
                    continue
                for line in group_lines:
                    if not line.statement_line_id:
                        move_line = line.move_id
                        if move_line.journal_id.type in ('bank','cash'):
                            for rec in move_line.line_ids:
                                if rec.debit > 0 and rec.account_id.code not in ('100202','100203'):
                                    l.add((rec.move_id.name, rec.id))
                                    key = (rec.account_id.id, line.move_id.expense_type)

                                    result[key]['account_name'] = rec.account_id.name
                                    result[key]['account_code'] = rec.account_id.code
                                    result[key]['expense_type'] = rec.move_id.expense_type
                                    result[key]['total_debit'] += rec.debit
                                    result[key]['entries'].append({
                                        'move_name':rec.move_id.name,
                                        'mov_id':rec.id,
                                        'partner_id': rec.move_id.journal_id.name if rec.move_id.payment_id and rec.move_id.payment_id.is_internal_transfer
                                                      else rec.partner_id.name if rec.partner_id
                                                      else rec.account_id.name,
                                        'debit': rec.debit,
                                        'date': rec.date,
                                    })

        for rec in outstanding:
            print(rec.move_id.name,rec.id,'gggggggggggggggggggggggggggg')
            if rec.debit > 0 :
                 key = (rec.account_id.id, rec.move_id.expense_type)
                 result[key]['account_name'] = rec.account_id.name
                 result[key]['account_code'] = rec.account_id.code
                 result[key]['expense_type'] = rec.move_id.expense_type
                 result[key]['total_debit'] += rec.debit
                 result[key]['entries'].append({
                                    'move_name':rec.move_id.name,
                                    'mov_id':rec.id,
                                    'partner_id':  rec.move_id.journal_id.name if rec.move_id.payment_id and rec.move_id.payment_id.is_internal_transfer
                                                      else rec.partner_id.name if rec.partner_id
                                                      else rec.account_id.name,
                                    'debit': rec.debit,
                                    'date': rec.date,
                                })
        return list(result.values())

    def get_cash_bank_utilization_credit(self, date_from, date_to,company_id):
        """
        Get cash/bank utilization summary using ORM (no raw SQL).
        """
        # Get moves in given date range, posted, with bank_date filter
        moves = self.env['account.move.line'].sudo().search([
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type','=','entry'),
            ('move_id.journal_id.type', 'in', ('bank', 'cash')),
            ('move_id.company_id','=',company_id.id),
        ])
        no_match_entries = []
        grouped = defaultdict(list)
        duplicates = defaultdict(list)
        stat_line = set()
        l = set()
        state_grp = defaultdict(list)
        # stat_line =  defaultdict(list)
        for line in moves:
            if line.matching_number:
                grouped[line.matching_number].append(line)
            elif not line.matching_number and line.statement_line_id:
                # lines = self.env['account.move.line'].sudo().search([('statement_line_id','=',line.statement_line_id.id),('move_id.journal_id.default_account_id.account_type','=','asset_cash'),('date','>=',date_from),('date','<=',date_to)])
                if line.move_id.journal_id.default_account_id.account_type in 'asset_cash' and line.date >= date_from and line.date <= date_to:
                    stat_line.add((line.move_id.name,line.id))
        # print(grouped,'tttttttttttttt')
        result = defaultdict(lambda: {
            'account_name': '',
            'account_code': '',
            'expense_type': '',
            'total_credit': 0.0,
            'entries': []
        })

        for move_name, line_id in stat_line:
            state_grp[move_name].append(line_id)
        for match_no, group_lines in grouped.items():
            statement_line = next((l for l in group_lines if l.statement_line_id), None)
            # print(statement_line,'gggggggggg')
            if not statement_line:
                continue
            if statement_line.journal_id.default_account_id.account_type == 'asset_cash':
                stmt_date = statement_line.statement_line_id.date
                if not (date_from <= stmt_date <= date_to):
                    continue
                # print(group_lines,'xxxxxxxxxxxxxxxx')
                for line in group_lines:
                    if not line.statement_line_id:
                        move_line = line.move_id
                        if move_line.journal_id.type in ('bank','cash'):
                            for rec in move_line.line_ids:
                                # print(rec.move_id.name,rec.id,'ddddddddddddddddddddd')
                                if rec.credit > 0 and rec.account_id.code not in ('100203','100204','100801'):
                                    key = (rec.account_id.id, line.move_id.expense_type)
                                    result[key]['account_name'] = rec.account_id.name
                                    result[key]['account_code'] = rec.account_id.code
                                    result[key]['expense_type'] = rec.move_id.expense_type
                                    result[key]['total_credit'] += rec.credit
                                    result[key]['entries'].append({
                                        'move_name':rec.move_id.name,
                                        'mov_id':rec.id,
                                        'partner_id': rec.move_id.journal_id.name if rec.move_id.payment_id and rec.move_id.payment_id.is_internal_transfer
                                                      else rec.partner_id.name if rec.partner_id
                                                      else rec.account_id.name,
                                        'credit': rec.credit,
                                        'date':rec.date,
                                    })

        # stop
        return list(result.values())
