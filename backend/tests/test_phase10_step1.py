"""
tests/test_phase10_step1.py — Tests for Parent model, relationships, and migration integrity.
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models.mentor import Mentor
from models.parent import Parent
from models.booking import Booking
from services.parent_service import get_or_create_parent


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


class TestParentModelAndRelationships:
    """Verifies Parent entity, email uniqueness, and bidirectional relationships."""

    def test_parent_creation_and_fields(self, db):
        test_email = f"test_parent_{int(datetime.now().timestamp())}@example.com"
        parent = Parent(name="Alice Test", email=test_email)
        db.add(parent)
        db.commit()
        db.refresh(parent)

        try:
            assert parent.id is not None
            assert parent.name == "Alice Test"
            assert parent.email == test_email
            assert parent.created_at is not None
        finally:
            db.delete(parent)
            db.commit()

    def test_parent_email_uniqueness(self, db):
        unique_email = f"unique_{int(datetime.now().timestamp())}@example.com"
        p1 = Parent(name="Parent One", email=unique_email)
        db.add(p1)
        db.commit()

        try:
            p2 = Parent(name="Parent Two", email=unique_email)
            db.add(p2)
            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()
        finally:
            # Re-fetch p1 to clean up
            to_delete = db.query(Parent).filter(Parent.email == unique_email).first()
            if to_delete:
                db.delete(to_delete)
                db.commit()

    def test_parent_booking_bidirectional_relationship(self, db):
        unique_email = f"rel_test_{int(datetime.now().timestamp())}@example.com"
        parent = Parent(name="Relationship Parent", email=unique_email)
        db.add(parent)
        db.commit()
        db.refresh(parent)

        mentor = db.query(Mentor).filter(Mentor.is_active == True).first()  # noqa: E712
        assert mentor is not None

        # Create a booking linked to this parent
        test_slot = datetime(2030, 1, 1, 10, 0, tzinfo=timezone.utc)
        booking = Booking(
            parent_id=parent.id,
            child_name="Test Child",
            parent_timezone="America/New_York",
            slot_utc=test_slot,
            mentor_id=mentor.id,
            class_link="https://class.codeyoung.com/room/test-rel",
            status="confirmed",
            course_id=1,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        try:
            # Booking -> Parent
            assert booking.parent_id == parent.id
            assert booking.parent is not None
            assert booking.parent.name == "Relationship Parent"
            assert booking.parent_name == "Relationship Parent"
            assert booking.parent_email == unique_email

            # Booking -> Mentor
            assert booking.mentor_id == mentor.id
            assert booking.mentor is not None
            assert booking.mentor.name == mentor.name

            # Parent -> Bookings
            db.refresh(parent)
            assert len(parent.bookings) >= 1
            assert any(b.id == booking.id for b in parent.bookings)
        finally:
            db.delete(booking)
            db.delete(parent)
            db.commit()

    def test_get_or_create_parent(self, db):
        email = f"get_or_create_{int(datetime.now().timestamp())}@example.com"

        # 1. First call creates the parent
        p1 = get_or_create_parent(db, name="Initial Name", email=email)
        db.commit()
        assert p1.id is not None
        assert p1.name == "Initial Name"
        assert p1.email == email

        # 2. Second call reuses the existing parent
        p2 = get_or_create_parent(db, name="Updated Name", email=email)
        db.commit()
        assert p2.id == p1.id
        assert p2.name == "Updated Name"

        # Cleanup
        db.delete(p2)
        db.commit()


class TestMigrationIntegrity:
    """Verifies existing migration preserved all data and constraints."""

    def test_all_bookings_have_valid_parent(self, db):
        bookings = db.query(Booking).all()
        assert len(bookings) >= 1

        for b in bookings:
            assert b.parent_id is not None
            assert b.parent is not None
            assert b.parent.name is not None
            assert len(b.parent.name) > 0
            assert "@" in b.parent.email
            assert b.parent_name == b.parent.name
            assert b.parent_email == b.parent.email

    def test_mentors_count_and_assignment_intact(self, db):
        mentors = db.query(Mentor).all()
        assert len(mentors) == 10

        bookings = db.query(Booking).all()
        for b in bookings:
            assert b.mentor_id is not None
            assert b.mentor is not None

    def test_unique_mentor_slot_constraint_intact(self, db):
        # Taking an existing booking's mentor and slot_utc
        existing = db.query(Booking).first()
        assert existing is not None

        # Attempt to insert another booking with the exact same mentor and slot_utc
        duplicate = Booking(
            parent_id=existing.parent_id,
            child_name="Another Child",
            parent_timezone=existing.parent_timezone,
            slot_utc=existing.slot_utc,
            mentor_id=existing.mentor_id,
            class_link="https://class.codeyoung.com/room/test-dup",
            status="confirmed",
            course_id=1,
        )
        db.add(duplicate)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
