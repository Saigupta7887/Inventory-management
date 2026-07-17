# Deployment Guide

Production stack: **PostgreSQL + FastAPI (Gunicorn/Uvicorn) + Nginx-served React**.

## 1. Quick start with Docker Compose

```bash
cp .env.docker.example .env
# Edit .env — set SECRET_KEY, ADMIN_PASSWORD, POSTGRES_PASSWORD, ALLOWED_ORIGINS
docker compose up --build -d
```

- Web app: http://localhost:8080
- The backend runs DB migrations (`alembic upgrade head`) on startup, then Gunicorn.
- Nginx serves the built frontend and proxies `/api` to the backend.

Generate a strong secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 2. Configuration

All config is via environment variables (see `backend/.env.example`). In
**production** (`ENVIRONMENT=production`) the app refuses to start unless:

- `SECRET_KEY` is set and ≥ 32 chars (not the dev default)
- `ALLOWED_ORIGINS` is an explicit list (not `*`)
- `ADMIN_PASSWORD` is changed from the default
- `S3_BUCKET` is set when `STORAGE_BACKEND=s3`

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | `development` \| `production` |
| `SECRET_KEY` | JWT signing secret (required in prod) |
| `ALLOWED_ORIGINS` | CORS allow-list, comma-separated |
| `DATABASE_URL` | `postgresql+psycopg://user:pass@host:5432/db` |
| `AUTO_CREATE_TABLES` | `false` in prod (use migrations) |
| `STORAGE_BACKEND` | `local` \| `s3` |
| `S3_BUCKET` / `S3_REGION` / `S3_ENDPOINT_URL` | object storage |
| `ANTHROPIC_API_KEY` | enables real Claude vision + task planning |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | seeded admin account |

## 3. Database migrations

Schema is managed by **Alembic** (source of truth in production).

```bash
cd backend
alembic upgrade head            # apply
alembic revision --autogenerate -m "describe change"   # create a new migration
alembic downgrade -1            # roll back one
```

`AUTO_CREATE_TABLES=true` (dev default) creates tables from models on boot so
you can run locally without migrations; set it to `false` in production.

## 4. Storage

- **local** (default): images stored on disk at `UPLOAD_DIR` (a Docker volume
  in compose). Fine for a single node.
- **s3**: set `STORAGE_BACKEND=s3` + `S3_BUCKET` (+ region / endpoint for
  S3-compatible providers). Image reads are served via short-lived presigned
  URLs. Requires the `boto3` dependency (already in `requirements.txt`).

## 5. Security notes

- **Auth**: session JWTs are sent in the `Authorization` header. Image `<img>`
  URLs use a separate **short-lived, read-only media token** (60 min) so the
  session token never appears in URLs, logs or referrers.
- **Passwords**: hashed with pbkdf2-sha256.
- **Headers**: `X-Content-Type-Options`, `X-Frame-Options: DENY`,
  `Referrer-Policy: no-referrer`, and HSTS in production.
- **CORS**: locked to `ALLOWED_ORIGINS` in production.
- **Uploads**: type-checked and capped at 15 MB.
- Put a TLS-terminating reverse proxy / load balancer in front (e.g. Caddy,
  Traefik, or your cloud LB) and set `ALLOWED_ORIGINS` to your HTTPS domain.

## 6. Running without Docker

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ENVIRONMENT=production SECRET_KEY=... DATABASE_URL=postgresql+psycopg://...
export ALLOWED_ORIGINS=https://app.example.com ADMIN_PASSWORD=...
alembic upgrade head
gunicorn -c gunicorn_conf.py app.main:app
```

Frontend:
```bash
cd frontend
npm ci && npm run build      # outputs static files to dist/
# serve dist/ with any static host; proxy /api to the backend
```

## 7. CI

`.github/workflows/ci.yml` runs on every push/PR:
- backend: install deps, run Alembic migrations, run `pytest`
- frontend: `npm ci` + `npm run build`
- docker: build both images

## 8. Health & readiness

- `GET /health` — liveness (process up)
- `GET /ready` — readiness (database reachable); returns 503 if the DB is down

Wire these to your orchestrator's liveness/readiness probes.
