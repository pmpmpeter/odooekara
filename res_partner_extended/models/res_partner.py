from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError,ValidationError
import logging
from odoo.tools import SQL
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_vendor = fields.Boolean(string='Is Supplier')
    is_customer = fields.Boolean(string='Is Customer')

    @api.model
    def _build_vat_error_message(self, country_code, wrong_vat, record_label):
        # OVERRIDE account
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company

        vat_label = _("VAT")
        if country_code and company.country_id and country_code == company.country_id.code.lower() and company.country_id.vat_label:
            vat_label = company.country_id.vat_label

        # expected_format = _ref_vat.get(country_code, "'CC##' (CC=Country Code, ##=VAT Number)")

        # Catch use case where the record label is about the public user (name: False)
        # if 'False' not in record_label:
        #     return '\n' + _(
        #         'The %(vat_label)s number [%(wrong_vat)s] for %(record_label)s does not seem to be valid. \nNote: the expected format is %(expected_format)s',
        #         vat_label=vat_label,
        #         wrong_vat=wrong_vat,
        #         record_label=record_label,
        #         expected_format=expected_format,
        #     )
        # else:
        #     return '\n' + _(
        #         'The %(vat_label)s number [%(wrong_vat)s] does not seem to be valid. \nNote: the expected format is %(expected_format)s',
        #         vat_label=vat_label,
        #         wrong_vat=wrong_vat,
        #         expected_format=expected_format,
        #     )

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