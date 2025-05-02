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
    vendor_code = fields.Char(string='Partner Code',readonly=1, copy=False)
    customer_code = fields.Char(string='Customer Code', readonly=1, copy=False)
    vat = fields.Char(string='GSTIN')
    tds_applicable = fields.Boolean('TDS Applicable?')
    tcs_applicable = fields.Boolean('TCS Applicable?')
    tds_tax_id = fields.Many2one('account.tax', string="TDS Tax", domain=[('type_tax_use', 'in', ['purchase','none'])], company_dependent=True)
    tcs_tax_id = fields.Many2one('account.tax', string="TCS Tax", domain=[('type_tax_use', '=', ['sale','none'])],company_dependent=True)
    tds_limit_amount_partner = fields.Float(
        'Maximum TDS Amount', help="By adding maximum limit amount will let users know about the TDS limit")
    tcs_limit_amount_partner = fields.Float(
        'Maximum TCS Amount', help="By adding maximum limit amount will let users know about the TCS limit")
    msme_status = fields.Selection([
        ('registered', 'Registered'),
        ('unregistered', 'Unregistered')
    ], string="MSME Status", default='unregistered')

    msme_number = fields.Char(string="MSME Number")
    msme_validity = fields.Date(string="MSME Validity")
    ldc_no = fields.Char(string="LDC Number")
    ldc_expiry_date = fields.Date(string="LDC Expiry Date")

    @api.model
    def name_get(self):
        result = []
        for record in self:
            if record.vendor_code:
                name = f"{record.vendor_code} {record.name}"
            else:
                name= record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|',('name', operator, name),('vendor_code', operator, name)]
        return self.search(domain + args, limit=limit).name_get()

    @api.depends('complete_name', 'email', 'vat', 'state_id', 'country_id', 'commercial_company_name')
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat', 'lang')
    def _compute_display_name(self):
        for partner in self:
            name = partner.with_context(lang=self.env.lang)._get_complete_name()
            if not partner.vendor_code:
                name = name
            if partner.vendor_code:
                name = partner.vendor_code + " " + name
            if partner._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = re.sub(r'\s+\n', '\n', name)
            if partner._context.get('partner_show_db_id'):
                name = f"{name} ({partner.id})"
            if partner._context.get('address_inline'):
                splitted_names = name.split("\n")
                name = ", ".join([n for n in splitted_names if n.strip()])
            if partner._context.get('show_email') and partner.email:
                name = f"{name} <{partner.email}>"
            if partner._context.get('show_vat') and partner.vat:
                name = f"{name} ‒ {partner.vat}"
            partner.display_name = name.strip() 


    @api.constrains('msme_number')
    def _check_msme_number(self):
        for record in self:
            if record.msme_status == 'registered' and record.msme_number:
                if not record.msme_number.isdigit() or len(record.msme_number) != 12:
                    raise ValidationError("MSME Number must contain exactly 12 digits.")


    @api.constrains('vat', 'state_id', 'l10n_in_pan')
    def _check_gst_number(self):
        for res in self:
            if res.state_id:
                state = self.env['res.country.state'].sudo().search([('id', '=', res.state_id.id)])
                
                if not state.l10n_in_tin:
                    raise ValidationError(_('First define the GST state code.'))
                
                if res.vat:
                    vat = res.vat.replace(" ", "")  # Remove any spaces in GST number

                    # Check length of GST number
                    if len(vat) != 15:
                        raise ValidationError(_("Invalid GST. GST number must be 15 characters. Please check."))

                    # Regex validation for GST format
                    if not re.match(r"(^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$)", vat):
                        raise ValidationError(_('Please Enter a Valid GST No Eg:33AAHHK3869G1Z3.'))

                    # Check state code in GST number
                    if state.l10n_in_tin != vat[0:2]:
                        raise ValidationError(_('The first two characters of GST Number must match the state code.'))

                    # Check PAN in GST number
                    if res.l10n_in_pan and res.l10n_in_pan != vat[2:12]:
                        raise ValidationError(
                            _('The characters between positions 3 and 12 in GST Number must match the PAN Number.'))

                # Check for duplicate GST numbers
                if res.vat:
                    duplicate_partner = self.env['res.partner'].sudo().search([
                        ('vat', '=', res.vat),
                        ('id', '!=', res.id),
                        ('company_type', '=', 'company'),
                        ('parent_id', '!=', res.id)
                    ])
                    if duplicate_partner:
                        raise ValidationError(
                            _('Alert! GST Number - %s already exists. Please enter a unique GST Number.') % res.vat)

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
            # if record.is_vendor and not record.property_purchase_currency_id and record.type=='contact' and record.is_company==True:
            #     raise UserError(_("Alert !! Kindly update Supplier Currency."))
            # if record.is_vendor and not record.vendor_code:
            #     raise UserError(_("Alert !! Kindly update Vendor Category."))
            record.write({'state': 'done'})

    def action_approve(self):
        for record in self.filtered(lambda m: m.state in 'done'):
            # if record.is_vendor and not record.property_purchase_currency_id and record.type=='contact' and record.is_company==True:
            #     raise UserError(_("Alert !! Kindly update Supplier Currency."))
            if not self.email:
                raise ValidationError("The Partner does not have a valid email address.")

            contact_creation = self.env['contact.creation'].search([('partner_id', '=', self.id)], limit=1)
            print('checking', contact_creation)

            if contact_creation:
                template = self.env.ref('res_partner_extended.approved_contact_information_mail')
                template.send_mail(self.id, force_send=True)

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
        # for record in self.filtered(lambda m: m.state not in 'draft'):
        #     record.write({'state': 'draft'})
        for record in self.filtered(lambda m: m.state not in 'draft'):
            query = """
                update res_partner set state='draft' where id = %s;
            """%(record.id)
            self.env.cr.execute(query)
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

    def write(self, vals):
        if 'l10n_in_pan' in vals and vals['l10n_in_pan']:
            existing_record = self.search([('l10n_in_pan', '=', vals['l10n_in_pan']), ('id', '!=', self.id)])
            if existing_record:
                raise ValidationError("The Pan number must be unique. This value already exists.")

        return super(ResPartner, self).write(vals)

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
