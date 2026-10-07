import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router
# Import all models so metadata knows about them before create_all
import app.models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("hostelshare.main")

from sqlalchemy import inspect, text

# Auto-generate database tables on startup
logger.info("Initializing database schema on engine: %s", engine.url)
Base.metadata.create_all(bind=engine)

def run_auto_migrations(db_engine):
    """
    Ensures backwards-compatible schema evolutions (e.g. adding 'email' column to 'users' table)
    on startup across both SQLite and Supabase PostgreSQL.
    """
    try:
        inspector = inspect(db_engine)
        table_names = inspector.get_table_names()
        if "users" in table_names:
            columns = [c["name"] for c in inspector.get_columns("users")]
            if "email" not in columns:
                logger.info("Auto-migrating: adding missing 'email' column to 'users' table...")
                with db_engine.begin() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(150);"))
                logger.info("Auto-migrating: 'email' column added successfully!")
    except Exception as e:
        logger.warning("Auto-migration check notice: %s", e)

run_auto_migrations(engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Campus Peer-to-Peer Rental and Utility-Sharing MVP API"
)

# Configure CORS for web app and deployment
cors_origins = settings.cors_origins
logger.info("Configured CORS Allowed Origins: %s", cors_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX if settings.ALLOWED_ORIGIN_REGEX else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive HTTP Cyber Defense & Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # Prevent MIME type sniffing attacks
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Prevent Clickjacking by disallowing embedding in iframes
    response.headers["X-Frame-Options"] = "DENY"
    # Enable browser XSS filtering
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Enforce strict referrer privacy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Disallow unauthorized hardware sensor access
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# Ensure local upload directories exist and mount static serving for local fallback
uploads_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(os.path.join(uploads_dir, "avatars"), exist_ok=True)
os.makedirs(os.path.join(uploads_dir, "items"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


# Include top-level API router under /api
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
