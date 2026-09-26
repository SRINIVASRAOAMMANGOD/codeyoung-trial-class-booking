"""
database.py — SQLAlchemy engine and session factory.

Concepts for reference:
- Engine: the connection pool to PostgreSQL.
- SessionLocal: a factory that creates individual DB sessions per request.
- Base: the declarative base class that all ORM models inherit from.
- get_db(): a FastAPI dependency that opens a session for a request
  and closes it when the request finishes (via the finally block).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    # pool_pre_ping checks if the DB connection is alive before using it.
    # This prevents errors after the DB restarts or idles for too long.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# All ORM model classes inherit from Base so SQLAlchemy knows about them.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a DB session for the duration of one request.
    The session is always closed in the finally block, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
