from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SeikyushoUpload(models.Model):
    _name = "seikyusho.upload"
    _description = "Seikyusho Upload"
    _order = "create_date desc"

    name = fields.Char(required=True, default=lambda self: self.env["ir.sequence"].next_by_code("seikyusho.upload") or "New")

    upload_date = fields.Date(required=True, default=fields.Date.context_today)
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    attachment_id = fields.Many2one(
        "ir.attachment",
        string="PDF",
        required=True,
        ondelete="restrict",
    )

    uploader_ip = fields.Char(readonly=True)
    uploader_user_agent = fields.Char(readonly=True)

    @api.constrains("attachment_id")
    def _check_pdf(self):
        for rec in self:
            if not rec.attachment_id:
                continue
            mimetype = rec.attachment_id.mimetype or ""
            name = rec.attachment_id.name or ""
            if mimetype != "application/pdf" and not name.lower().endswith(".pdf"):
                raise ValidationError("Only PDF files are allowed.")
