# 🤝 Bondly

**Bondly is a personal relationship manager (personal CRM).** It helps you stay
close to the people who matter — remember the details about them, track your
interactions, and get gentle nudges to reconnect before too much time passes.

The frontend is a **mobile-first** web app built to match the product's screen
designs: a phone-shaped layout with a bottom tab bar (Home · People · ➕ ·
Reminders · Insights), a warm purple/pink aesthetic, tabbed profiles, an emoji
mood picker, and a donut "Relationship Health" ring. It runs in any browser and
the same design can later wrap into a native shell.

- **Backend:** Python · FastAPI · SQLAlchemy 2
- **Frontend:** Vue 3 · Vite · Pinia · Vue Router
- **Database:** PostgreSQL
- **Auth:** email/password (JWT + bcrypt) **and Sign in with Google / Apple**
- **Runs everywhere:** responsive web · installable **PWA** · **native iOS/Android** (Capacitor)

## One app, every platform

The same Vue codebase runs three ways:

| Target | How | Notes |
|--------|-----|-------|
| **Responsive web** | `npm run dev` | Sidebar layout on desktop, bottom-tab phone UI on mobile |
| **PWA (installable)** | built automatically (`vite-plugin-pwa`) | "Add to Home Screen" on phone/desktop; offline shell + service worker |
| **Native iOS / Android** | Capacitor — see [`frontend/NATIVE.md`](frontend/NATIVE.md) | Wraps the web build into real App Store / Play Store apps |

## Authentication

- **Email + password** — works out of the box.
- **Sign in with Google / Apple** — fully wired; the buttons appear only once you
  provide OAuth client IDs. Real Google/Apple login needs credentials **you**
  create in the Google Cloud Console and Apple Developer portal (nobody can do
  this without them). Setup:
  - Backend: set `GOOGLE_CLIENT_ID` and/or `APPLE_CLIENT_IDS` in `backend/.env`
    (see `backend/.env.example`). The backend cryptographically verifies each
    provider's identity token before issuing a Bondly JWT.
  - Frontend: set `VITE_GOOGLE_CLIENT_ID` / `VITE_APPLE_CLIENT_ID` in
    `frontend/.env` (see `frontend/.env.example`).
  - `GET /api/auth/providers` reports which providers are enabled.

### 🎙️ "Hey Bondly" voice assistant

Tap the mic (or type) and speak naturally — Bondly parses the intent and *does*
it, then replies out loud:

- "note that Sarah loves matcha" → adds a categorized note
- "log a call with Nikhil about the launch" → logs an interaction
- "remind me to buy flowers for Priya at the grocery" → creates a place errand
- "who should I reconnect with?" → reads back who's overdue
- "add Meera as a friend", "who likes coffee?", "open insights" → and more

Tap-to-talk and an optional always-listen wake-word mode use the Web Speech
API (`src/components/VoiceAssistant.vue`, `src/lib/assistant.js`); a typed
fallback covers browsers without speech support. A true always-on wake word
is best added via a native wake-word engine in the Capacitor build.

### 📍 Nearby / context-aware reminders

Save an **errand** for someone tied to a *type of place* — e.g. "matcha for
Sarah" at a **grocery**. When you're near that kind of place, Bondly surfaces it:

- **GPS auto-detect** — uses the browser's geolocation to find saved places
  within range and shows their matching errands, plus contacts based nearby.
  (True background "you walked into a store" alerts need a native app; the web
  app detects when you open the Nearby screen.)
- **Manual check-in** — tap "I'm at a grocery" and get the relevant errands.
- Save your current spot as a place so GPS recognizes it next time.

---

## Quick start (Docker)

The fastest way to run the whole stack (Postgres + API + web):

```bash
docker compose up --build
```

- Web app → http://localhost:5173
- API docs → http://localhost:8000/docs

## Quick start (local dev)

**1. Database** — start Postgres (or use the compose db service):

```bash
docker compose up -d db
```

**2. Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload      # http://localhost:8000
```

**3. Frontend**

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173 (proxies /api to :8000)
```

## Tests

```bash
cd backend && pytest
```

---

## How the blueprint maps to the code

The product blueprint's phases are implemented as follows:

| Phase | Feature | Where |
|-------|---------|-------|
| 1 | Onboarding, auth, preferences, **Google/Apple sign-in** | `backend/app/api/routes/auth.py`, `services/oauth.py`, `frontend/.../Login.vue`, `SocialAuth.vue`, `Onboarding.vue` |
| 2 | Add person, priority, reminder interval | `models/person.py`, `routes/people.py`, `People.vue` |
| 3 | Notes + AI categorization + pinning | `models/note.py`, `services/ai.py`, `PersonProfile.vue` |
| 4 | Interaction tracking (channel, mood, follow-up) | `models/interaction.py`, `routes/people.py` |
| 5 | Reminder intelligence (reconnect / birthday) | `services/reminders.py`, `routes/reminders.py`, `Reminders.vue` |
| 6 | AI context card + message draft | `services/ai.py`, `routes/people.py` (`/context-card`) |
| 7 | Dashboard (needs attention / events / activity) | `routes/dashboard.py`, `Dashboard.vue` |
| 8 | Insights (health score, trends) | `routes/insights.py`, `Insights.vue` |
| 9 | Natural-language-ish search | `routes/search.py`, `People.vue` search bar |
| 10 | Context-aware / nearby reminders | `models/place.py`, `models/errand.py`, `services/location.py`, `routes/nearby.py`, `Nearby.vue`, `ErrandNew.vue` |

### A note on the "AI" layer

`backend/app/services/ai.py` ships **dependency-free heuristics** so the product
is fully functional out of the box with no API key. Note categorization,
suggested questions, and message drafts all work today. The function signatures
are the contract — swap the bodies for real **Claude API** calls when you want
smarter output, without touching the rest of the app.

---

## Project structure

```
bondly/
├── backend/            FastAPI app (see backend/README.md)
│   └── app/
│       ├── core/       config, db engine, security
│       ├── models/     User, Person, Note, Interaction, Reminder
│       ├── schemas/    Pydantic models
│       ├── services/   ai.py, reminders.py
│       └── api/routes/  auth, people, reminders, dashboard, insights, search
├── frontend/           Vue 3 + Vite app
│   └── src/
│       ├── views/       Welcome, Onboarding, Dashboard, People, PersonProfile,
│       │                Reminders, Insights, Settings, Login
│       ├── stores/      Pinia stores (auth, people)
│       ├── api/         axios client
│       └── router/      routes + auth guard
├── docker-compose.yml
└── README.md
```

## Roadmap (Phase 10)

- Replace heuristic AI with Claude API calls
- Voice notes, calendar integration, widgets
- Contact import
- Push/email notifications for reminders
- Shared family mode

## Deployment

Deployment target is intentionally undecided. The app is container-ready
(`docker-compose.yml` + per-service Dockerfiles), so it runs anywhere that
takes containers (Fly.io, Render, Railway, a VPS, or a managed Kubernetes
cluster) with a managed Postgres. Set `DATABASE_URL` and a strong `SECRET_KEY`
in the backend environment.
