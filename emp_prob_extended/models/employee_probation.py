from odoo import models, fields, api, _
import base64
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import *

class Employee(models.Model):
    _inherit = 'hr.employee'

    def action_get_employee_probation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Probation',
            'view_mode': 'tree,form',
            'res_model': 'employee.probation',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'default_email': self.work_email,
                'default_department_id': self.department_id.id,
                'default_parent_id': self.parent_id.id,
            },
        }


class EmployeeProbation(models.Model):
    _name = 'employee.probation'
    _description = 'Employee Probation'
    _inherit = 'mail.thread'

    name = fields.Char('Sequence', readonly=True, index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', 'Employee')
    email = fields.Char('Email', related='employee_id.work_email')
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id')
    parent_id = fields.Many2one('hr.employee', 'Manager', related='employee_id.parent_id')
    employee_reviews_ids = fields.One2many('employee.reviews.details', 'probation_id', 'Employee Reviews')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
    ], string='State', default='draft', required=True, tracking=True)

    employee_prob_ids = fields.Many2many('hr.employee',
                                         compute='_compute_employee_prob',
                                         string='Employee Prob', copy=False)
    employee_prob_count = fields.Integer("Employee Prob Count",
                                         compute='_compute_employee_prob', default=0, copy=False)

    start_date = fields.Date('Start Date', compute='_compute_start_date', store=True)
    end_date = fields.Date('End Date', compute='_compute_end_date', store=True)

    @api.onchange('employee_id')
    def _compute_start_date(self):
        for record in self:
            if record.employee_id:
                resume_line = self.env['hr.resume.line'].search(
                    [('employee_id', '=', record.employee_id.id)],
                    order='date_start desc',
                    limit=1
                )
                record.start_date = resume_line.date_start if resume_line else False
            else:
                record.start_date = False

    @api.onchange('start_date')
    def _compute_end_date(self):
        for record in self:
            if record.start_date:
                record.end_date = (fields.Date.from_string(record.start_date) + relativedelta(months=3)).replace(
                    day=1) - timedelta(days=1)
            else:
                record.end_date = False

    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.probation.sequence') or 'New'
        return super(EmployeeProbation, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state == 'confirm':
                raise UserError("You cannot delete a record in the 'Confirmed' state.")
        return super(EmployeeProbation, self).unlink()

    def print_employee_probation(self):
        return self.env.ref('emp_prob_extended.employee_probation_pdf').report_action(self.id)

    def employee_probation_confirm(self):
        report = self.env.ref('emp_prob_extended.employee_probation_pdf')
        # pdf_content, content_type = report._render_qweb_pdf([self.id])
        data_record = base64.b64encode(
            self.env['ir.actions.report'].sudo()._render_qweb_pdf(
                report, [self.id], data=None)[0])
        # Create an attachment for the PDF
        attachment = self.env['ir.attachment'].create({
            'name': f"Probation_Confirmation_{self.employee_id.name}.pdf",
            'type': 'binary',
            'datas': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'employee.probation',
            'res_id': self.id,
        })

        # Send the email with the attachment
        template = self.env.ref('emp_prob_extended.probation_confirmation_email_template')
        template.send_mail(self.id, force_send=True, email_values={
            'attachment_ids': [(6, 0, [attachment.id])]
        })
        # if self.state == 'draft':
        self.state = 'confirm'

    def employee_probation_cancel(self):
        self.state = 'cancel'

    def employee_probation_review(self):
        self.state = 'review'

    def _compute_employee_prob(self):
        for record in self:
            domain = [('id', '=', record.employee_id.id)]
            employee_prob_ids = self.env['hr.employee'].sudo().search(domain)
            record.employee_prob_ids = employee_prob_ids
            record.employee_prob_count = len(employee_prob_ids)

    def action_open_employee(self):
        action = self.env.ref('hr.open_view_employee_tree')
        result = action.sudo().read()[0]
        result.pop('id', None)
        result['context'] = {}
        if len(self.employee_prob_ids.ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, self.employee_prob_ids.ids)) + "])]"
        elif len(self.employee_prob_ids.ids) == 1:
            res = self.env.ref('hr.view_employee_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.employee_prob_ids.ids and self.employee_prob_ids.ids[0] or False
        return result


class EmployeeProbationReview(models.Model):
    _name = 'employee.reviews.details'
    _description = 'Employee Probation Review Details'

    probation_id = fields.Many2one('employee.probation', 'Probation ID')
    date = fields.Date('Date')
    reviewer = fields.Many2one('hr.employee', 'Reviewer')
    review_details = fields.Text('Review Details')
    performance = fields.Selection(
        [('excellent ', 'Excellent '),
         ('good ', 'Good '), ('average ', 'Average '),
         ('poor ', 'Poor '), ('worst ', 'Worst ')],
        string="Performance",
        required=False
    )
    rating = fields.Selection(
        [('0 ', 'Low '), ('1 ', 'Worst '),
         ('2 ', 'Poor '), ('3 ', 'Good '),
         ('4 ', 'Average '), ('5', 'Excellent')],
        string="Rating",
    )
