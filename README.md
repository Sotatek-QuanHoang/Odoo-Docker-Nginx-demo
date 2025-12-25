# Odoo Docker + Nginx Demo

Stack:
- Odoo 17 (`web`)
- Postgres 15 (`db`)
- Nginx reverse proxy (`nginx`) -> routes HTTP :80 to Odoo :8069

This repo also includes a custom Odoo addon that allows customers (guest session, no login) to upload a Seikyusho PDF with:
- Upload date
- Amount (price)

After upload, staff can see the created records in the Odoo backend.

## Prerequisites
- Docker Desktop (macOS) or any working Docker daemon
- Docker Compose v2 (`docker compose`)

## Quick start
1. Create the Postgres password secret file (required by Docker Compose secrets):
	- File: [odoo_pg_pass](odoo_pg_pass)
	- Content: a single line password, e.g. `odoo_demo_password`

2. Start services:
	- `docker compose up -d`

3. Open:
	- Public website (via Nginx): `http://localhost`
	- Odoo direct (bypass Nginx): `http://localhost:8069`

## Guest Seikyusho upload (no login)
Public upload page:
- `http://localhost/seikyusho/upload`

User flow:
1. Customer visits the URL above (no login form).
2. Uploads a PDF + fills upload date + amount.
3. On submit, Odoo creates a record and stores the PDF as an attachment.

Backend management:
- In Odoo backend, open menu: **Seikyusho → Uploads**

## What was added
- Custom addon: [addons/seikyusho_guest_upload](addons/seikyusho_guest_upload)
  - Model: `seikyusho.upload`
  - Routes:
	 - `GET /seikyusho/upload`
	 - `POST /seikyusho/upload`

## Configuration
Odoo config is mounted from:
- [config/odoo.conf](config/odoo.conf)

Key settings:
- `addons_path` includes `/mnt/extra-addons` (mounted from `./addons`)
- `db_host=db` so the Odoo container connects to Postgres container
- `proxy_mode=True` for running behind Nginx

Nginx config:
- [nginx/default.conf](nginx/default.conf)

## Troubleshooting
### "bind source path does not exist" for `odoo_pg_pass`
Docker secrets require the file to exist. Ensure:
- [odoo_pg_pass](odoo_pg_pass) exists in the repo root

### Public upload page returns 404
Make sure the addon is installed in your database.

For the default DB used here (`odoo-demo`), you can install the module from inside the container:
- `docker compose exec -T web bash -lc 'export PGPASSWORD="$(cat /run/secrets/postgresql_password)" && odoo -d odoo-demo -i seikyusho_guest_upload --stop-after-init --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --db_host=db --db_port=5432 --db_user=odoo --db_password="$PGPASSWORD" --without-demo=all'`
- `docker compose restart web`

Then re-check:
- `curl -I http://localhost/seikyusho/upload`

### View logs
- `docker compose logs -f web`
- `docker compose logs -f nginx`
