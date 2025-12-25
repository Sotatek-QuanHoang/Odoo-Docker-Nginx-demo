import base64

from odoo import http
from odoo.http import request


class SeikyushoUploadController(http.Controller):
    @http.route(["/seikyusho/upload"], type="http", auth="public", website=True, methods=["GET"], sitemap=False)
    def seikyusho_upload_form(self, **kwargs):
        return request.render("seikyusho_guest_upload.seikyusho_upload_form", {})

    @http.route(["/seikyusho/upload"], type="http", auth="public", website=True, methods=["POST"], sitemap=False)
    def seikyusho_upload_submit(self, **post):
        upload_date = post.get("upload_date")
        amount_raw = post.get("amount")

        pdf = request.httprequest.files.get("pdf")
        if not pdf or not getattr(pdf, "filename", None):
            return request.render(
                "seikyusho_guest_upload.seikyusho_upload_form",
                {"error": "Please select a PDF file to upload."},
            )

        filename = pdf.filename
        mimetype = getattr(pdf, "mimetype", "") or ""
        if mimetype != "application/pdf" and not filename.lower().endswith(".pdf"):
            return request.render(
                "seikyusho_guest_upload.seikyusho_upload_form",
                {"error": "Only PDF files are allowed."},
            )

        try:
            amount = float(amount_raw)
        except Exception:
            return request.render(
                "seikyusho_guest_upload.seikyusho_upload_form",
                {"error": "Amount must be a number."},
            )

        if amount < 0:
            return request.render(
                "seikyusho_guest_upload.seikyusho_upload_form",
                {"error": "Amount must be >= 0."},
            )

        try:
            content = pdf.read()
        except Exception:
            content = b""

        if not content:
            return request.render(
                "seikyusho_guest_upload.seikyusho_upload_form",
                {"error": "Uploaded file is empty."},
            )

        # Create with sudo so guest users don't need access rights.
        Attachment = request.env["ir.attachment"].sudo()
        Upload = request.env["seikyusho.upload"].sudo()

        attachment = Attachment.create(
            {
                "name": filename,
                "datas": base64.b64encode(content),
                "mimetype": mimetype or "application/pdf",
            }
        )

        record = Upload.create(
            {
                "upload_date": upload_date,
                "amount": amount,
                "currency_id": request.env.company.currency_id.id,
                "attachment_id": attachment.id,
                "uploader_ip": request.httprequest.remote_addr,
                "uploader_user_agent": request.httprequest.headers.get("User-Agent"),
            }
        )

        attachment.write({"res_model": "seikyusho.upload", "res_id": record.id})

        return request.render(
            "seikyusho_guest_upload.seikyusho_upload_success",
            {"record": record},
        )
