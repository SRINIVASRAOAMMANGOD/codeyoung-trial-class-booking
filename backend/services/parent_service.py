"""
services/parent_service.py — Parent entity operations.

Provides get_or_create_parent for parent identity management.
Safely handles concurrent requests using PostgreSQL savepoints and unique constraints.
"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.parent import Parent


def get_or_create_parent(db: Session, name: str, email: str) -> Parent:
    """
    Retrieve an existing Parent by email, or create a new one if not found.

    Concurrency guarantee:
      Uses a SAVEPOINT (`db.begin_nested()`) when inserting so that any
      concurrent race condition triggering a unique constraint violation
      on `parents.email` is rolled back at the savepoint level, allowing
      the transaction to safely query and return the concurrently committed Parent.
    """
    clean_email = email.strip().lower()
    clean_name = name.strip()

    # 1. Check if parent already exists
    parent = (
        db.query(Parent)
        .filter(func.lower(Parent.email) == clean_email)
        .first()
    )
    if parent is not None:
        # Optionally update name if it changed
        if clean_name and parent.name != clean_name:
            parent.name = clean_name
            db.flush()
        return parent

    # 2. Attempt creation inside a nested transaction (savepoint)
    try:
        with db.begin_nested():
            parent = Parent(name=clean_name, email=clean_email)
            db.add(parent)
            db.flush()
        return parent
    except IntegrityError:
        # Unique constraint collision: another concurrent transaction created this parent
        parent = (
            db.query(Parent)
            .filter(func.lower(Parent.email) == clean_email)
            .first()
        )
        if parent is not None:
            return parent
        raise
