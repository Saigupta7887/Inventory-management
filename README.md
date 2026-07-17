# 🔧 ToolFinder — Tool Inventory App

A "where is my stuff" search engine for physical tools. Photograph a desk,
drawer, shelf or pegboard; AI detects the tools in the photo and remembers
*what* is *where*. Later just ask *"where is my hammer?"* — so you never buy
a duplicate you already own.

This repo contains a **fully working prototype**: a Python/FastAPI backend and
a React frontend, built on a **UUID-first architecture** (every entity keyed
by a time-ordered UUIDv7, IDs as the contract between modules).

> See [`docs/SPEC.md`](docs/SPEC.md) for the full product & architecture spec.

---

## Features

- **Scan-to-inventory (core):** photograph a location → Claude vision detects
  the tools → you confirm which to add → they become inventory items. On a
  phone the scanner opens the **camera** directly. Works out of the box with a
  **built-in mock detector** if no API key is set.
- **"Before you buy" check (core):** search a tool and get a clear verdict —
  *"You already own 1 in Garage Pegboard"* vs *"safe to buy"* — so you never
  buy a duplicate. (`GET /items/check`)
- **"How do I…?" task assistant:** describe a job in plain language
  ("change my car tire") → get the **tools it needs** (checked against your
  inventory: ✓ owned + where, ✗ missing), **step-by-step instructions**,
  **safety tips**, and a **how-to video**. Uses Claude when a key is set, with
  a built-in knowledge base + generic fallback otherwise. (`POST /tasks/plan`)
- **Fast image thumbnails:** small JPEG thumbnails are generated on upload and
  served to grids/cards for quick loading. (`GET /photos/{id}/thumb`)
- **🧰 Inventory management:** add/edit/move tools, statuses (available,
  lent-out, lost, needs-repair), lend tracking, categories & nested locations.
- **👤 Two personas / roles:** *customer* (home owner) and *admin* (dashboard
  with users, aggregate stats, likely-duplicate detection).
- **UUID-first:** UUIDv7 primary keys everywhere, soft deletes, audit log,
  optimistic-concurrency versioning.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python · FastAPI · SQLAlchemy 2.0 · Pydantic v2 |
| Auth | JWT (PyJWT) + pbkdf2 password hashing |
| AI | Claude vision via the Anthropic SDK (mock fallback) |
| DB | SQLite (prototype) — Postgres-ready, same UUID contracts |
| Frontend | React 18 · React Router · Vite |

---

## Quick start

### 1. Backend (http://localhost:8000)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional; safe defaults work as-is
uvicorn app.main:app --reload --port 8000
```

- Interactive API docs: http://localhost:8000/docs
- On first run it creates the SQLite DB, seeds global categories, and creates
  the admin account (`admin@example.com` / `admin1234`).
- To enable **real** Claude vision, set `ANTHROPIC_API_KEY` in `.env`.
  Without it the app uses a deterministic mock detector so every flow still works.

### 2. Frontend (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to the backend on port 8000, so there's no
CORS or environment setup. Open http://localhost:5173 and sign up.

---

## Try it

1. **Sign up** as a home owner.
2. Create a **Location** ("Garage Pegboard").
3. Go to **📷 Scan**, pick the location, upload any photo → confirm the
   detected tools → they're added to your inventory.
4. Go to **🔍 Find** and ask *"where is my hammer?"*.
5. Log in as **admin** (`admin@example.com` / `admin1234`) to see the
   analytics dashboard.

---

## Project layout

```
backend/
  app/
    main.py            # FastAPI app + startup (create tables, seed)
    config.py          # settings (.env)
    ids.py             # UUIDv7 generator
    database.py        # SQLAlchemy engine/session/Base
    models.py          # UUID-first ORM models
    schemas.py         # Pydantic request/response models
    auth.py deps.py    # JWT + password hashing + dependencies
    vision.py          # Claude vision detection (+ mock fallback)
    audit.py seed.py
    routers/           # auth, locations, categories, items, photos, search, admin
frontend/
  src/
    api.js auth.jsx App.jsx
    pages/             # Login, Dashboard, Scan, Search, Items, Locations, Admin
docs/SPEC.md           # product & architecture specification
```

## API overview

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/signup` · `POST /auth/login` · `GET /auth/me` |
| Locations | `GET/POST /locations` · `DELETE /locations/{id}` |
| Categories | `GET/POST /categories` |
| Items | `GET/POST /items` · `GET/PATCH/DELETE /items/{id}` · `GET /items/check?q=...` ("before you buy") |
| Photos / AI | `POST /photos` · `POST /photos/{id}/detect` · `POST /photos/{id}/accept` · `GET /photos/{id}/file` · `GET /photos/{id}/thumb` |
| Search | `GET /search?q=...` |
| Task assistant | `POST /tasks/plan` (body `{"task": "change my car tire"}`) |
| Admin | `GET /admin/users` · `GET /admin/analytics` |

All resources are addressed by UUID.
