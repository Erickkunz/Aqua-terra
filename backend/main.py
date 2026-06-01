import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from database import Base, engine, SessionLocal
from ratelimit import limiter
from routes import home, about, pillars, shop, projects, blog, contact, dashboard, auth, admin, webpay, account

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aquaterra")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _validate_production_secrets():
    """Refuse to start in production with insecure default secrets."""
    if not settings.is_production:
        return
    problems = []
    if settings.SECRET_KEY in ("change-me", "change-me-in-production", ""):
        problems.append("SECRET_KEY is still the default - set a strong random value")
    if settings.ADMIN_PASSWORD in ("AquaTerra2026!", "", "admin"):
        problems.append("ADMIN_PASSWORD is still the default - change it")
    if "change_me" in settings.DATABASE_URL or "riego_pass_change_me" in settings.DATABASE_URL:
        problems.append("DATABASE_URL uses a default password - change it")
    if problems:
        raise RuntimeError(
            "Refusing to start in production with insecure defaults:\n  - "
            + "\n  - ".join(problems)
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_production_secrets()
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    if settings.SEED_ON_STARTUP:
        from seed import seed_if_empty
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()

    logger.info("App ready - %s [%s]", settings.SITE_NAME, settings.ENVIRONMENT)
    yield
    logger.info("App shutdown.")


app = FastAPI(
    title=settings.SITE_NAME,
    description=settings.SITE_TAGLINE,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=settings.SESSION_HTTPS_ONLY or settings.is_production,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/healthz", include_in_schema=False)
def healthz():
    """Lightweight liveness probe for load balancers."""
    return {"status": "ok"}


@app.get("/readyz", include_in_schema=False)
def readyz():
    """Readiness probe: confirms DB connectivity."""
    try:
        from sqlalchemy import text
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.warning("readiness probe failed: %s", e)
        return JSONResponse({"status": "degraded", "error": str(e)}, status_code=503)


@app.middleware("http")
async def add_global_context(request: Request, call_next):
    request.state.site_name = settings.SITE_NAME
    request.state.site_tagline = settings.SITE_TAGLINE
    return await call_next(request)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return JSONResponse({"error": "not_found"}, status_code=404)
    # Use base_ctx so the footer / nav have all expected context (sc, pillars, etc).
    from routes._common import base_ctx
    return templates.TemplateResponse(
        "404.html",
        base_ctx(request),
        status_code=404,
    )


app.include_router(home.router)
app.include_router(about.router)
app.include_router(pillars.router)
app.include_router(shop.router)
app.include_router(projects.router)
app.include_router(blog.router)
app.include_router(contact.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(webpay.router)
app.include_router(account.router)
