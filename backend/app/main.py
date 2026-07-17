from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    dashboard,
    errands,
    insights,
    nearby,
    people,
    places,
    reminders,
    search,
)
from app.core.config import settings
from app.core.database import Base, engine

# Import models so they register with the metadata before create_all.
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For local/dev convenience we create tables on startup. In production,
    # use Alembic migrations instead (see backend/README).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(people.router)
app.include_router(reminders.router)
app.include_router(dashboard.router)
app.include_router(insights.router)
app.include_router(search.router)
app.include_router(places.router)
app.include_router(errands.router)
app.include_router(nearby.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}
