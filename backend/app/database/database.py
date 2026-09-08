"""Database configuration and session management for SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Create the SQLAlchemy engine using the configured database URL.
# The app is intentionally compatible with MySQL when provided a valid URL,
# while remaining resilient in local development environments where the DB is unavailable.
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL)
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory used by FastAPI dependency injection.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for all ORM models.
Base = declarative_base()


def get_db():
    """Yield a database session for each request and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
