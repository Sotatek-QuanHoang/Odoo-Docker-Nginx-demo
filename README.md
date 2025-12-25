# Odoo Docker + Nginx Demo

Stack:
- Odoo 17 (`web`)
- Nginx reverse proxy (`nginx`) -> routes HTTP :80 to Odoo

Local development additionally runs:
- Postgres 15 (`db`) via [docker-compose.local.yml](docker-compose.local.yml)

This repo also includes a custom Odoo addon that allows customers (guest session, no login) to upload a Seikyusho PDF with:
- Upload date
- Amount (price)

After upload, staff can see the created records in the Odoo backend.

## Prerequisites
- Docker Desktop (macOS) or any working Docker daemon
- Docker Compose v2 (`docker compose`)

## Local development (with Postgres container)
This mode uses:
- [docker-compose.local.yml](docker-compose.local.yml) to add the local Postgres container
- [.env](.env) for Odoo DB connection variables (safe to keep locally; it is git-ignored)

1. Create the DB password secret file (required by Docker Compose secrets):
	- File: [odoo_pg_pass](odoo_pg_pass)
	- Content: a single line password (used for Postgres user `odoo`)

2. Start services (base + local override):
	- `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d`

3. Open:
	- Public website (via Nginx): `http://localhost`
	- Odoo direct (dev): `http://localhost:8069`

## DigitalOcean deployment (Odoo + Nginx only)
Goal: run only `web` + `nginx` containers, and use DigitalOcean Managed PostgreSQL.

### 1) Create required files on the Droplet
On your droplet (or wherever you run Docker):

1. Put DB password in the secret file (do not commit this):
	- [odoo_pg_pass](odoo_pg_pass)

2. Set DB connection parameters via environment variables (recommended: a `.env` file alongside compose):
	- `DB_HOST` = DigitalOcean managed DB host
	- `DB_PORT` = usually `25060` (check DO panel)
	- `DB_USER` = managed DB user
	- `DB_NAME` = managed DB database name
	- `DB_SSLMODE` = `require` (typical for managed Postgres)

Example `.env`:
```env
DB_HOST=your-do-db-host
DB_PORT=25060
DB_USER=doadmin
DB_NAME=defaultdb
DB_SSLMODE=require
```

You can start from the committed template:
- Copy [.env.example](.env.example) to `.env` and edit values

### 2) Start only Odoo + Nginx
Run:
- `docker compose up -d`

Notes:
- The base [docker-compose.yml](docker-compose.yml) does not start a local Postgres container.
- Ensure your DigitalOcean managed Postgres allows connections from the droplet IP.
- If your DB requires `sslmode=verify-full` + CA certs, we can mount the CA cert and set `DB_SSLMODE=verify-full`.

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
- `proxy_mode=True` for running behind Nginx

Nginx config:
- [nginx/default.conf](nginx/default.conf)

## Troubleshooting
### "bind source path does not exist" for `odoo_pg_pass`
Docker secrets require the file to exist. Ensure:
- [odoo_pg_pass](odoo_pg_pass) exists in the repo root

### Public upload page returns 404
Make sure the addon is installed in your database.

For local default DB (`odoo-demo`), you can install the module from inside the container:
- `docker compose -f docker-compose.yml -f docker-compose.local.yml exec -T web sh -lc 'odoo -d odoo-demo -i seikyusho_guest_upload --stop-after-init --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --db_host=db --db_port=5432 --db_user=odoo --db_password="$(cat /run/secrets/postgresql_password)" --db_sslmode=prefer --without-demo=all'`
- `docker compose -f docker-compose.yml -f docker-compose.local.yml restart web`

Then re-check:
- `curl -I http://localhost/seikyusho/upload`

### View logs
- `docker compose logs -f web`
- `docker compose logs -f nginx`
