from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError,ValidationError
import logging, re
from odoo.tools import SQL
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'To Validate'), ('approve', 'Approved')],
        string='Status', default='draft', readonly=True, copy=False, tracking=True,)
    is_vendor = fields.Boolean(string='Is Supplier')
    is_customer = fields.Boolean(string='Is Customer')
    vendor_code = fields.Char(string='Supplier Code',readonly=1, copy=False)
    customer_code = fields.Char(string='Customer Code', readonly=1, copy=False)
    vat = fields.Char(string='GSTIN')
    tds_applicable = fields.Boolean('TDS Applicable?')
    tcs_applicable = fields.Boolean('TCS Applicable?')
    tds_tax_id = fields.Many2one('account.tax', string="TDS Tax", domain=[('type_tax_use', 'in', ['purchase','none'])])
    tcs_tax_id = fields.Many2one('account.tax', string="TCS Tax", domain=[('type_tax_use', '=', ['sale','none'])])
    tds_limit_amount_partner = fields.Float(
        'Maximum TDS Amount', help="By adding maximum limit amount will let users know about the TDS limit")
    tcs_limit_amount_partner = fields.Float(
        'Maximum TCS Amount', help="By adding maximum limit amount will let users know about the TCS limit")

    @api.onchange('is_customer','is_vendor')
    def onchange_product(self):
        if self.is_customer and not self.is_vendor:
            self.customer_rank = 1
            self.supplier_rank = 0
        elif self.is_customer and self.is_vendor:
            self.customer_rank = 1
            self.supplier_rank = 1
        elif not self.is_customer and self.is_vendor:
            self.customer_rank = 0
            self.supplier_rank = 1

    def action_draft(self):
        for record in self.filtered(lambda m: m.state not in 'draft'):
            record.write({'state': 'draft'})

    def action_approve(self):
        for record in self.filtered(lambda m: m.state not in 'approve'):
            record.write({'state': 'approve'})
        # self.write({'state': 'approve'})

    def action_validate(self):
        for record in self.filtered(lambda m: m.state in 'draft'):
            if record.is_vendor and not record.property_purchase_currency_id and record.type=='contact' and record.is_company==True:
                raise UserError(_("Alert !! Kindly update Supplier Currency."))
            # if record.is_vendor and not record.vendor_code:
            #     raise UserError(_("Alert !! Kindly update Vendor Category."))
            record.write({'state': 'done'})

    def action_approve(self):
        for record in self.filtered(lambda m: m.state in 'done'):
            if record.is_vendor and not record.property_purchase_currency_id and record.type=='contact' and record.is_company==True:
                raise UserError(_("Alert !! Kindly update Supplier Currency."))
            if record.is_customer:
                customer_code = self.env['ir.sequence'].next_by_code('contact.debtor.code')
                if customer_code != '' and not self.customer_code:
                    record.write({'customer_code': customer_code})
            if record.is_vendor:
                vendor_code = self.env['ir.sequence'].next_by_code('contact.creditor.code')
                if vendor_code != '' and not self.vendor_code:
                    record.write({'vendor_code': vendor_code})
            record.write({'state': 'approve'})
            # Retrieve the action with the ID 'contacts.action_contacts'
        # domain1= [('id', '=', self.env.ref('contacts.action_contacts').id)]
        # action = self.env['ir.actions.act_window'].sudo().search(domain1, limit=1)
        # action.context = {'default_is_company': True,'edit':False}
        # action_to_return = {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Contacts',
        #     'res_model': 'res.partner',
        #     'view_mode': 'kanban,tree,form,activity',
        #     'context': action.context,
        # }

        # # Return the action with a page refresh
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',  # This will refresh the page
        #     'params': action_to_return  # Include the action that opens contacts
        # }

    def action_validate_partner_state(self):
        records = self.env['res.partner'].browse(self._context.get('active_ids', False))
        if records:
            if self.env.user.has_group('dev_customer_flow.can_validate_partner') and self.env.user.has_group('dev_customer_flow.can_approve_partner'):
                for vals in records:
                    if vals.state == 'draft':
                        vals.update({'state': 'done'})
                    else:
                        raise UserError(_("Alert !! %s should be in draft state.")%vals.name)
            else:
                raise UserError(_("You do not have access to trigger this action."))

    def action_approve_partner_state(self):
        records = self.env['res.partner'].browse(self._context.get('active_ids', False))
        if records:
            if self.env.user.has_group('dev_customer_flow.can_validate_partner') and self.env.user.has_group('dev_customer_flow.can_approve_partner'):
                for res in records:
                    if res.state == 'done':
                        res.sequence = self.env['ir.sequence'].next_by_code(
                            'res.partner') or 'RP/'
                        res.update({'state': 'approve'})
                    else:
                        raise UserError(_("Alert !! %s should be in validate state.")%res.name)
            else:
                raise UserError(_("You do not have access to trigger this action."))

    def reset_to_draft(self):
        for record in self.filtered(lambda m: m.state not in 'draft'):
            record.write({'state': 'draft'})
        # domain1 = [('id', '=', self.env.ref('contacts.action_contacts').id)]
        # action = self.env['ir.actions.act_window'].sudo().search(domain1, limit=1)
        # action.context = {'default_is_company': True,'edit':True}
        # action_to_return = {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Contacts',
        #     'res_model': 'res.partner',
        #     'view_mode': 'kanban,tree,form,activity',
        #     'context': action.context,
        # }

        # # Return the action with a page refresh
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',  # This will refresh the page
        #     'params': action_to_return  # Include the action that opens contacts
        # }

    def unlink(self):
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("You do not have access to trigger this action."))
        # Prevent deletion if the state is 'approved'
        for record in self:
            if record.state in ('approve','done'):
                raise UserError(_("You cannot delete a record in the Approved or Done state."))
        return super(ResPartner, self).unlink()

    def toggle_active(self):
        # Prevent archiving if the state is 'approved'
        for record in self:
            if record.state in ('approve','done'):
                raise UserError(_("You cannot archive a record in the Approved or Done state."))
        return super(ResPartner, self).toggle_active()


    @api.constrains("l10n_in_pan")
    def _check_pan_number_format(self):
        for rec in self:
            if rec.type not in ('delivery', 'invoice') and rec.l10n_in_pan:
                regex = "[A-Za-z]{5}\d{4}[A-Za-z]{1}"
                p = re.compile(regex)
                if(re.search(p, rec.l10n_in_pan)):
                    pass
                else:
                    raise ValidationError(
                        _(
                            "PAN Number is not valid,Please use format like Ex:ABCDE9999K"
                        )
                    )

    @api.constrains("mobile")
    def _check_mobile_number_format(self):
        if self.mobile:
            regex = re.compile("^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$")
            p = re.compile(regex)
            if (re.search(p, self.mobile)):
                pass
            else:
                raise ValidationError(
                    _(
                        "Mobile Number is not valid,Please use Correct format"
                    )
                )

    @api.constrains("phone")
    def _check_phone_number_format(self):
        if self.phone:
            regex = re.compile("^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$")            
            p = re.compile(regex)
            if (re.search(p, self.phone)):
                pass
            else:
                raise ValidationError(
                    _(
                        "Phone Number is not valid,Please use Correct format"
                    )
                )

    # @api.model
    # def create(self, vals):
    #     if  vals.get('is_vendor'):
    #         if vals.get('vendor_category'):
    #             categ = self.env['category.res.partner.vendor'].sudo().search([('id','=',vals.get('vendor_category'))])
    #             seq = self.env['ir.sequence'].sudo().search([('id','=',categ.sequence.id)])
    #             vals['vendor_code'] = seq.next_by_code(seq.code)
    #     if vals.get('is_customer'):
    #         if vals.get('partner_category'):
    #             categ = self.env['category.res.partner'].sudo().search([('id', '=', vals.get('partner_category'))])
    #             seq = self.env['ir.sequence'].sudo().search([('id', '=', categ.sequence.id)])
    #             vals['customer_code'] = seq.next_by_code(seq.code)
    #     res = super(ResPartner, self).create(vals)
    #     return res

    # def write(self, vals):
    #     if  vals.get('is_vendor'):
    #         if vals.get('vendor_category'):
    #             categ = self.env['category.res.partner.vendor'].sudo().search([('id','=',vals.get('vendor_category'))])
    #             seq = self.env['ir.sequence'].sudo().search([('id','=',categ.sequence.id)])
    #             vals['vendor_code'] = seq.next_by_code(seq.code)
    #     if vals.get('is_customer'):
    #         if vals.get('partner_category'):
    #             categ = self.env['category.res.partner'].sudo().search([('id', '=', vals.get('partner_category'))])
    #             seq = self.env['ir.sequence'].sudo().search([('id', '=', categ.sequence.id)])
    #             vals['customer_code'] = seq.next_by_code(seq.code)
    #     res = super(ResPartner, self).write(vals)
    #     return res
