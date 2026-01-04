{
    "name": "Seikyusho Guest Upload",
    "summary": "Public (no-login) PDF upload form for seikyusho with backend management list.",
    "version": "17.0.1.0.0",
    "category": "Website",
    "license": "LGPL-3",
    "depends": ["base", "web", "website"],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/seikyusho_upload_views.xml",
        "views/seikyusho_upload_templates.xml",
    ],
    "application": True,
    "installable": True,
}
