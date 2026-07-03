# Tool Inventory App — Product & Architecture Specification

> **Status:** Draft v1 · **Date:** 2026-07-03
> **One-line pitch:** A "where is my stuff" search engine for physical tools. Snap a photo of a desk/drawer/shelf, the app recognizes the tools in it and remembers *what* is *where*, so you never buy a duplicate again.

---

## 1. Problem Statement

In homes and small businesses people own many tools (drills, wrenches, screwdrivers, ladders, tape measures…). The pain is not owning them — it is **not knowing where a tool is**. When a tool can't be found, people waste time searching and then **buy a duplicate they already own**. That wastes money and creates clutter.

**The app solves this by making physical tools searchable.** Users photograph a *location*; AI vision detects the tools in the photo; each tool is stored against that location with the photo attached. Later the user asks *"where is my Phillips screwdriver?"* and gets the location + a photo to confirm. Before buying anything, they check the app first.

### Success looks like
- A user can find any owned tool in **under 10 seconds**.
- **Fewer duplicate purchases** — the app tells them "you already own this, it's in the Garage Pegboard."
- Adding inventory is **low-effort** — a photo does most of the work, not manual typing.

---

## 2. Personas

### 2.1 Home Owner / Customer (primary)
The everyday user with tools scattered around a house or small workshop.

**Needs / jobs-to-be-done**
- Photograph a location and have tools auto-detected and added.
- Search / ask "where is X" and get the location + photo.
- Manually add, edit, correct, or remove tools.
- Track tool status: *available, lent-out, lost, needs-repair*.
- Organize by location and category.

### 2.2 Admin (secondary / operator)
You (the operator) or a business manager overseeing the system.

**Needs / jobs-to-be-done**
- Manage users and roles.
- Oversee all inventory across users/organizations.
- View analytics: most-owned tools, likely duplicates, lost items, storage utilization.
- Moderate / curate the tool catalog the AI maps detections onto.
- Manage global categories and location templates.

> **Future persona (out of scope v1):** *Business / Team member* — multiple users sharing one organization's inventory. The data model below is designed so this can be added without a rewrite (see `Organization` and `owner_scope`).

---

## 3. Core Concept & User Flows

### 3.1 The model in one paragraph
A **User** owns **Locations** (named physical places). A user uploads a **Photo** of a location. A **vision AI** processes the photo into **Detections**. Each accepted detection becomes an **Item** (a real tool) linked to a **Location**, a **Category**, and the **Photo** it came from. Users **search** Items and get back the Item, its Location, and the Photo.

### 3.2 Key flows

**Flow A — Photo to inventory (headline feature)**
1. User creates/selects a Location ("Garage Pegboard").
2. User uploads/takes a photo of that location.
3. Backend stores the photo, calls the **Vision service**.
4. Vision returns a list of detected tools (label, confidence, bounding box, suggested category).
5. User sees the detections overlaid on the photo and **confirms / edits / rejects** each one (human-in-the-loop).
6. Confirmed detections become **Items** attached to the Location + Photo.

**Flow B — Find a tool**
1. User types or asks: *"where is my hammer?"*
2. Search returns matching Items with Location name and thumbnail.
3. User taps an Item → detail view with full photo, location, status, history.

**Flow C — Avoid a duplicate purchase**
1. Before buying, user searches the item.
2. If found → app shows "You own 1, in Garage Pegboard, status: available."
3. If not found → app confirms they don't have it (safe to buy).

**Flow D — Manual management**
- Add an Item by hand, move it to another location, change status (lent-out → who/when), mark lost, delete.

**Flow E — Admin**
- Dashboard of users, aggregate inventory, analytics, catalog moderation.

---

## 4. Architecture Principles ("UUID-level" design)

This is the core architectural constraint requested. Every principle below is non-negotiable for v1.

1. **UUID primary keys everywhere.** Every entity's primary key is a UUID (we use **UUIDv7** — time-ordered, so it indexes well like a sequential key while staying globally unique). No auto-increment integer IDs are ever exposed or used as PKs.
   - *Why:* globally unique, safe to expose in URLs/APIs, no enumeration attacks, clients/services can generate IDs without a round-trip, and merging data across databases/services never collides.
2. **IDs are the contract.** Services and clients reference each other only by UUID. Relationships are UUID foreign keys. This keeps modules loosely coupled — a service only needs an ID, not a shared table.
3. **Client-generatable IDs.** A client may generate an Item's UUID before the server confirms it, enabling optimistic UI and offline-first later. Server validates and accepts the provided UUID (idempotent creates).
4. **Every record is addressable & auditable.** Because every row has a stable UUID, every entity has a canonical URL (`/items/{uuid}`) and every change can be logged against that UUID in an `audit_log`.
5. **Modular services around stable IDs.** The system is split into services (Auth, Inventory, Vision, Search, Media, Admin) that talk over HTTP/JSON using UUIDs as the shared vocabulary. v1 ships as a modular monolith (one deployable) but with these boundaries drawn so services can be split out later without changing IDs or contracts.
6. **Soft deletes.** Rows are marked `deleted_at` rather than physically removed, so a UUID reference never dangles and history is preserved.
7. **Timestamps + versioning on every entity.** `created_at`, `updated_at`, and an integer `version` (optimistic concurrency) on all tables.

> If "Orion architecture" implies additional specifics on your side (event sourcing, a particular service mesh, naming conventions, tenancy model), tell me and I'll fold them in — the above is the faithful interpretation of a UUID-first, ID-as-contract, modular design.

---

## 5. Data Model

All primary keys are `UUID` (v7). All FKs are `UUID`. All tables carry `created_at`, `updated_at`, `deleted_at (nullable)`, `version`.

### 5.1 Entities

**User**
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| email | string, unique | |
| password_hash | string | (or external auth provider id) |
| display_name | string | |
| role | enum | `customer` \| `admin` |
| organization_id | UUID (FK, nullable) | for future team support |

**Organization** *(scaffolded for future; a solo user maps to a personal org)*
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| name | string | |
| owner_user_id | UUID (FK) | |

**Location**
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| owner_scope | enum | `user` \| `organization` |
| owner_id | UUID | user_id or org_id depending on scope |
| name | string | "Garage Pegboard" |
| description | string | |
| parent_location_id | UUID (FK, nullable) | nested locations (Toolbox → top tray) |

**Category**
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| name | string | "Screwdriver", "Power tool" |
| parent_category_id | UUID (FK, nullable) | hierarchy |
| is_global | bool | curated by admin vs user-created |

**Photo**
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| location_id | UUID (FK, nullable) | which location it depicts |
| uploaded_by | UUID (FK user) | |
| storage_key | string | object-store key |
| width / height | int | |
| status | enum | `uploaded` \| `processing` \| `processed` \| `failed` |

**Detection** *(AI output, pre-confirmation)*
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| photo_id | UUID (FK) | |
| label | string | raw model label |
| suggested_category_id | UUID (FK, nullable) | |
| confidence | float | 0–1 |
| bbox | json | [x,y,w,h] |
| status | enum | `pending` \| `accepted` \| `rejected` |
| item_id | UUID (FK, nullable) | set when accepted → Item |

**Item** *(a real, owned tool)*
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| owner_scope / owner_id | | same pattern as Location |
| name | string | "Phillips screwdriver #2" |
| category_id | UUID (FK) | |
| location_id | UUID (FK) | current location |
| primary_photo_id | UUID (FK, nullable) | |
| source_detection_id | UUID (FK, nullable) | provenance if AI-created |
| quantity | int | default 1 |
| status | enum | `available` \| `lent_out` \| `lost` \| `needs_repair` |
| lent_to | string, nullable | + `lent_since` date |
| notes | text | |

**AuditLog**
| field | type | notes |
|---|---|---|
| id | UUID (PK) | |
| entity_type / entity_id | string / UUID | what changed |
| actor_user_id | UUID (FK) | |
| action | enum | create/update/delete/move/status_change |
| diff | json | before/after |

### 5.2 Relationships (all by UUID)
- User 1—N Location, Item, Photo
- Location 1—N Item · Location self-referencing (nesting)
- Category 1—N Item · Category self-referencing (nesting)
- Photo 1—N Detection · Detection 0..1—1 Item
- Item 0..1—1 primary Photo, 0..1 source Detection

---

## 6. Services & Responsibilities

| Service | Responsibility | Key endpoints (all resources keyed by UUID) |
|---|---|---|
| **Auth** | Signup/login, JWT sessions, roles | `POST /auth/signup`, `POST /auth/login`, `GET /me` |
| **Inventory** | CRUD for Locations, Items, Categories; status/move | `GET/POST /items`, `GET/PATCH/DELETE /items/{id}`, `POST /items/{id}/move`, `.../locations`, `.../categories` |
| **Media** | Photo upload, storage, thumbnails | `POST /photos`, `GET /photos/{id}` |
| **Vision** | Run detection on a photo, return Detections | `POST /photos/{id}/detect`, `GET /photos/{id}/detections` |
| **Search** | Query items by text/natural language | `GET /search?q=...` |
| **Admin** | Users, global catalog, analytics | `GET /admin/users`, `GET /admin/analytics`, `GET/PATCH /admin/categories` |

v1 = one deployable (modular monolith) with these modules cleanly separated; each owns its tables and exposes an internal interface so it can be extracted later without changing UUID contracts.

---

## 7. AI / Vision Design (core from day one)

**Pipeline**
1. Photo uploaded → `Media` stores it, marks Photo `processing`.
2. `Vision` service sends the image to a **vision model** (Claude with vision, or a specialized object-detection model) with a structured prompt: *"List the tools/objects visible. For each return: label, a category from this list, confidence, and an approximate bounding box."*
3. Response parsed into **Detection** rows (`status = pending`).
4. Frontend renders detections over the photo; user confirms/edits/rejects (**human-in-the-loop** — AI proposes, human disposes).
5. Accepted detections → **Items**; provenance kept via `source_detection_id`.

**Natural-language search** — "where is my hammer" is turned into a structured query (category/name match) and, optionally, an LLM re-ranks results. Search returns Items + Location + thumbnail.

**Guardrails**
- Never auto-create Items without user confirmation (avoids garbage inventory).
- Store `confidence`; show low-confidence detections visually distinct.
- Keep the raw model label AND the mapped category for auditing/improvement.

---

## 8. Tech Stack (proposed)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **React** (Vite) + TypeScript, responsive/mobile-first | web-first, camera via browser, reusable if a mobile app follows |
| Backend | **Python + FastAPI** (Pydantic, async) | chosen — fast to build, great typing, first-class OpenAPI, strong AI/ML ecosystem |
| ORM / migrations | **SQLAlchemy 2.0 + Alembic** | UUID PKs, relationships, versioned migrations |
| Database | **PostgreSQL** | native UUID type, `gen_random_uuid()`/uuidv7, JSON columns for bbox/diff |
| Object storage | S3-compatible (or local disk in dev) | photos |
| AI | **Claude (vision)** for detection + NL search, via the Anthropic Python SDK | headline feature |
| Auth | JWT + bcrypt (`python-jose`, `passlib`) | simple, role-based |

> **Backend decision:** Python/FastAPI (confirmed). The architecture and UUID contracts are identical regardless of language.

---

## 9. Build Phases

**Phase 1 — Foundation**
- Repo scaffold (frontend + backend), Postgres, migrations
- UUIDv7 PK convention, base entity fields, soft delete, audit log skeleton
- Auth + roles (customer/admin)
- Entities: User, Organization, Location, Category

**Phase 2 — Manual inventory**
- Item CRUD, move, status flags (available/lent/lost/repair)
- Photo upload + attach + thumbnails
- Search & item detail views

**Phase 3 — AI (core)**
- Vision detection pipeline (photo → Detections → confirm → Items)
- Detection review UI with bounding boxes
- Natural-language search

**Phase 4 — Admin & polish**
- Admin dashboard: users, aggregate inventory, analytics (duplicates, most-owned, lost)
- Category/catalog moderation
- Notifications (return-a-lent-tool reminders), export

---

## 10. Out of Scope for v1
- Native mobile apps (web is mobile-responsive; backend reused later)
- Multi-user teams / shared org inventory (data model is ready, UI is not)
- Barcode/QR/RFID scanning
- Marketplace / buy-links integration

---

## 11. Open Questions
1. **"Orion architecture" specifics** — beyond UUID-first + ID-as-contract, does it prescribe event sourcing, a tenancy model, service-splitting, or naming conventions? If so I'll incorporate them.
2. ~~Backend language preference~~ — **Resolved: Python + FastAPI.**
3. Single-user (personal) only for v1, or should the Organization/team scaffolding be wired into the UI now?
4. Which vision approach for v1: **Claude vision** (fast to integrate, flexible) vs a dedicated object-detection model (more precise bounding boxes)?
