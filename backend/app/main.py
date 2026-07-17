import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import get_settings
from .database import Base, SessionLocal, engine
from .logging_config import configure_logging
from .routers import admin, auth, categories, items, locations, photos, search, tasks
from .seed import seed

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_for_production()
    if settings.auto_create_tables:
        # Dev convenience. In production, tables come from Alembic migrations.
        Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    logger.info("startup complete", extra={"request_id": "-"})
    yield


app = FastAPI(
    title="Tool Inventory API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled error", extra={"request_id": request_id})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "request_id": request_id},
        )
    response.headers["X-Request-ID"] = request_id
    # Security headers.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(photos.router)
app.include_router(search.router)
app.include_router(tasks.router)
app.include_router(admin.router)


@app.get("/health", tags=["meta"])
def health():
    """Liveness — the process is up."""
    return {"status": "ok", "vision": "claude" if settings.anthropic_api_key else "mock"}


@app.get("/ready", tags=["meta"])
def ready():
    """Readiness — dependencies (the database) are reachable."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not-ready", "db": "down"})
    return {"status": "ready", "db": "up"}
