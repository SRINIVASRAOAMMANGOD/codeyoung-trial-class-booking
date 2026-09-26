"""
db/init_db.py — Creates all database tables.

Run this script once to create the schema:
    python -m db.init_db        (from backend/ directory)

It is safe to run multiple times: SQLAlchemy's create_all() uses
"CREATE TABLE IF NOT EXISTS" semantics — it will not drop or modify
existing tables.

This replaces a migration tool (e.g. Alembic) for Phase 3.
If the schema needs to change in later phases, migrations will be
handled explicitly at that point.
"""

import sys
import os

# Ensure the backend/ directory is on the path so imports work
# when this script is run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
import models  # noqa: F401 — registers Mentor and Booking with Base.metadata


def init_db() -> None:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created (or already existed):")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")


if __name__ == "__main__":
    init_db()
