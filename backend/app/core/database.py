import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("hostelshare.db")

db_url = settings.effective_database_url
target_host = db_url.split("@")[-1] if "@" in db_url else db_url

logger.info("HostelShare: Connecting directly to Supabase PostgreSQL at %s...", target_host)

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=True
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("HostelShare: Successfully connected to Supabase PostgreSQL!")
except Exception as e:
    logger.critical("CRITICAL: Failed to connect to Supabase PostgreSQL (%s): %s", target_host, e)
    raise RuntimeError(
        f"Failed to connect to Supabase PostgreSQL at {target_host}: {e}. "
        "Ensure your DATABASE_URL is set and uses the Supabase IPv4 Pooler string."
    ) from e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
