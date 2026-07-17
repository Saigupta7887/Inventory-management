# 🤝 Bondly

**Bondly is a personal relationship manager (personal CRM).** It helps you stay
close to the people who matter — remember the details about them, track your
interactions, and get gentle nudges to reconnect before too much time passes.

- **Backend:** Python · FastAPI · SQLAlchemy 2
- **Frontend:** Vue 3 · Vite · Pinia · Vue Router
- **Database:** PostgreSQL
- **Auth:** JWT (bcrypt-hashed passwords)

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
| 1 | Onboarding, auth, preferences | `backend/app/api/routes/auth.py`, `frontend/.../Login.vue`, `Onboarding.vue` |
| 2 | Add person, priority, reminder interval | `models/person.py`, `routes/people.py`, `People.vue` |
| 3 | Notes + AI categorization + pinning | `models/note.py`, `services/ai.py`, `PersonProfile.vue` |
| 4 | Interaction tracking (channel, mood, follow-up) | `models/interaction.py`, `routes/people.py` |
| 5 | Reminder intelligence (reconnect / birthday) | `services/reminders.py`, `routes/reminders.py`, `Reminders.vue` |
| 6 | AI context card + message draft | `services/ai.py`, `routes/people.py` (`/context-card`) |
| 7 | Dashboard (needs attention / events / activity) | `routes/dashboard.py`, `Dashboard.vue` |
| 8 | Insights (health score, trends) | `routes/insights.py`, `Insights.vue` |
| 9 | Natural-language-ish search | `routes/search.py`, `People.vue` search bar |
| 10 | Future features | see **Roadmap** below |

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
