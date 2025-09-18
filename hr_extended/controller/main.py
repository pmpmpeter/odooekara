from odoo import http
from odoo.http import request
import base64


class ApplicantDocumentController(http.Controller):

    @http.route(['/applicant/upload/<int:applicant_id>'], type='http', auth="public", website=True)
    def applicant_upload_page(self, applicant_id, **kwargs):
        applicant = request.env['hr.applicant'].sudo().browse(applicant_id)
        if not applicant.exists():
            return "Invalid link."
        return request.render("hr_extended.applicant_document_upload_template", {
            'applicant': applicant,
        })

    @http.route(['/applicant/upload/submit'], type='http', auth="public", methods=['POST'], csrf=False, website=True)
    def applicant_upload_submit(self, applicant_id, **post):
        applicant = request.env['hr.applicant'].sudo().browse(int(applicant_id))
        files = request.httprequest.files.getlist('documents')
        for file in files:
            request.env['hr.applicant.document'].sudo().create({
                'applicant_id': applicant.id,
                'name': file.filename,
                'filename': file.filename,
                'file': base64.b64encode(file.read()),  # ✅ fixed here
            })
        return request.redirect('/applicant/upload/%s' % applicant.id)
