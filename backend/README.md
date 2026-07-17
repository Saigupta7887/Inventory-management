# Bondly Backend (FastAPI)

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit DATABASE_URL / SECRET_KEY

uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

By default the app connects to Postgres via `DATABASE_URL`. Tables are
auto-created on startup for convenience. For production, replace that with
Alembic migrations.

## Tests

```bash
pytest          # uses a throwaway SQLite database
```

## Structure

```
app/
  core/       config, database engine, security (JWT + bcrypt)
  models/     SQLAlchemy models: User, Person, Note, Interaction, Reminder
  schemas/    Pydantic request/response models
  services/   ai.py (note categorization + drafts), reminders.py (intelligence)
  api/routes/ auth, people (+ notes/interactions/context-card), reminders,
              dashboard, insights, search
```

## Notes on the "AI" layer

`app/services/ai.py` ships dependency-free heuristics so the product works
without an API key. The function signatures are the contract — swap the bodies
for real Claude API calls when you're ready.
