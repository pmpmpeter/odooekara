import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomPortalInherit(CustomerPortal):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        # Call the original logic from the inherited function
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        partner_id = partner.id
        values.update({
            'error': {},
            'error_message': [],
        })

        uploaded_files = request.httprequest.files.getlist('attachment')
        uploaded_files1 = request.httprequest.files.getlist('attachment1')# Fetch all uploaded files
        uploaded_files2 = request.httprequest.files.getlist('attachment2')
        uploaded_files3 = request.httprequest.files.getlist('attachment3')
        attachment_ids = []
        attachment_ids1 = []
        attachment_ids2 = []
        attachment_ids3 = []
        if uploaded_files:
            filtered_files = [file for file in uploaded_files if file.filename]
            Attachments = request.env['ir.attachment']
            for file in filtered_files:
                file_name = file.filename
                attachment_id = Attachments.sudo().create({
                    'name': file_name,
                    'res_name': file_name,
                    'type': 'binary',
                    'res_model': 'res.partner',
                    'res_id': partner_id,
                    'datas': base64.b64encode(file.read()),
                    'public': True
                })
                attachment_ids.append(attachment_id)

            if attachment_ids:
                partner = request.env['res.partner'].sudo().browse(partner_id)
                partner.message_post(
                    body=f"{len(attachment_ids)} attachment(s) uploaded.",
                    attachment_ids=[attachment.id for attachment in attachment_ids]
                )
        if uploaded_files1:
            filtered_files = [file for file in uploaded_files1 if file.filename]
            Attachments = request.env['ir.attachment']
            for file in filtered_files:
                file_name = file.filename
                attachment_id1 = Attachments.sudo().create({
                    'name': file_name,
                    'res_name': file_name,
                    'type': 'binary',
                    'res_model': 'res.partner',
                    'res_id': partner_id,
                    'datas': base64.b64encode(file.read()),
                    'public': True
                })
                attachment_ids1.append(attachment_id1)

            if attachment_ids1:
                partner = request.env['res.partner'].sudo().browse(partner_id)
                partner.message_post(
                    body=f"MSME certificates uploaded",
                    attachment_ids=[attachment.id for attachment in attachment_ids1]
                )
        if uploaded_files2:
            filtered_files = [file for file in uploaded_files2 if file.filename]
            Attachments = request.env['ir.attachment']
            for file in filtered_files:
                file_name = file.filename
                attachment_id2 = Attachments.sudo().create({
                    'name': file_name,
                    'res_name': file_name,
                    'type': 'binary',
                    'res_model': 'res.partner',
                    'res_id': partner_id,
                    'datas': base64.b64encode(file.read()),
                    'public': True
                })
                attachment_ids2.append(attachment_id2)

            if attachment_ids2:
                partner = request.env['res.partner'].sudo().browse(partner_id)
                partner.message_post(
                    body=f"GST Certificate/Declaration uploaded.",
                    attachment_ids=[attachment.id for attachment in attachment_ids2]
                )
        if uploaded_files3:
            filtered_files = [file for file in uploaded_files3 if file.filename]
            Attachments = request.env['ir.attachment']
            for file in filtered_files:
                file_name = file.filename
                attachment_id3 = Attachments.sudo().create({
                    'name': file_name,
                    'res_name': file_name,
                    'type': 'binary',
                    'res_model': 'res.partner',
                    'res_id': partner_id,
                    'datas': base64.b64encode(file.read()),
                    'public': True
                })
                attachment_ids3.append(attachment_id3)

            if attachment_ids:
                partner = request.env['res.partner'].sudo().browse(partner_id)
                partner.message_post(
                    body=f"PAN documents uploaded.",
                    attachment_ids=[attachment.id for attachment in attachment_ids3]
                )

        if post and request.httprequest.method == 'POST':
            if not partner.can_edit_vat():
                post['country_id'] = str(partner.country_id.id)
            error =[]
            #
            # error, error_message = self.details_form_validate(post)
            # values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self._get_mandatory_fields()}
                values.update({key: post[key] for key in self._get_optional_fields() if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        if not partner.email:
            return request.redirect('/my/account?error=no_email')
        email_subject = "Profile Updation - " + str(partner.name)
        email_body = """
                <p>Dear {name},</p>
                <p>Updated profile informations.Kindly verify the updated details.</p>
                <p>Thank you!</p>
            """.format(name='Team')
        mail = request.env['mail.mail'].sudo().create({
            'subject': email_subject,
            'body_html': email_body,
            'email_to': request.env.user.company_id.email or 'noreply@example.com',
            'email_from':partner.email,
        })
        if mail:
            mail.send()

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route(['/my/send_email'], type='http', auth='user', website=True, methods=['POST'])
    def send_email(self, **kwargs):
        partner = request.env.user.partner_id

        if not partner.email:
            return request.redirect('/my/account?error=no_email')
        email_subject = "Profile Updation - " + str(partner.name)
        email_body = """
                <p>Dear {name},</p>
                <p>Updated profile informations.Kindly verify the updated details.</p>
                <p>Thank you!</p>
            """.format(name='Team')
        mail = request.env['mail.mail'].sudo().create({
            'subject': email_subject,
            'body_html': email_body,
            'email_to': request.env.user.company_id.email or 'noreply@example.com',
            'email_from':partner.email,
        })
        if mail:
            mail.send()

        return request.redirect('/my/account?success=email_sent')
