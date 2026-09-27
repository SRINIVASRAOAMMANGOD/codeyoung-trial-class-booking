"""
tests/test_admin.py — Unit and integration tests for operational administration and mentor portal.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models.booking import Booking
from models.mentor import Mentor
from models.parent import Parent
from schemas.booking import BookingCreate
from services.booking_service import create_booking

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


class TestAdminEndpoints:
    """Tests for admin overview, mentor management, parent inspection, and booking visibility."""

    def test_admin_overview_metrics(self):
        res = client.get("/api/v1/admin/overview")
        assert res.status_code == 200
        data = res.json()

        assert "total_mentors" in data
        assert "active_mentors" in data
        assert "total_parents" in data
        assert "total_bookings" in data
        assert "today_classes" in data
        assert "theoretical_capacity" in data
        assert "remaining_capacity" in data
        assert data["theoretical_capacity"] == data["active_mentors"] * 2

    def test_admin_mentors_list(self):
        res = client.get("/api/v1/admin/mentors")
        assert res.status_code == 200
        mentors = res.json()
        assert len(mentors) >= 10
        first = mentors[0]
        assert "today_classes" in first
        assert "capacity_label" in first
        assert "is_full_today" in first

    def test_create_and_delete_mentor_with_zero_bookings(self, db):
        unique_email = f"new_mentor_{int(datetime.now().timestamp())}@codeyoung.com"
        payload = {
            "name": "Test Coach",
            "email": unique_email,
            "timezone": "Asia/Kolkata",
        }

        # 1. Create mentor
        res = client.post("/api/v1/admin/mentors", json=payload)
        assert res.status_code == 201
        mentor_data = res.json()
        mentor_id = mentor_data["id"]
        assert mentor_data["name"] == "Test Coach"
        assert mentor_data["email"] == unique_email
        assert mentor_data["is_active"] is True

        # 2. Duplicate email rejected
        dup_res = client.post("/api/v1/admin/mentors", json=payload)
        assert dup_res.status_code == 409
        assert "already exists" in dup_res.json()["detail"]

        # 3. Hard delete allowed because zero bookings exist
        del_res = client.delete(f"/api/v1/admin/mentors/{mentor_id}")
        assert del_res.status_code == 200
        assert del_res.json()["id"] == mentor_id

        # Verify gone
        check = db.query(Mentor).filter(Mentor.id == mentor_id).first()
        assert check is None

    def test_mentor_status_toggle(self, db):
        # Pick first active mentor
        mentor = db.query(Mentor).filter(Mentor.is_active == True).first()  # noqa: E712
        assert mentor is not None

        # Deactivate
        deact_res = client.patch(
            f"/api/v1/admin/mentors/{mentor.id}/status",
            json={"is_active": False},
        )
        assert deact_res.status_code == 200
        assert deact_res.json()["is_active"] is False

        # Reactivate
        react_res = client.patch(
            f"/api/v1/admin/mentors/{mentor.id}/status",
            json={"is_active": True},
        )
        assert react_res.status_code == 200
        assert react_res.json()["is_active"] is True

    def test_reject_delete_mentor_with_existing_bookings(self, db):
        # Find mentor with at least one booking
        booking = db.query(Booking).first()
        assert booking is not None
        mentor_id = booking.mentor_id

        # Attempt deletion
        res = client.delete(f"/api/v1/admin/mentors/{mentor_id}")
        assert res.status_code == 400
        assert "historical booking" in res.json()["detail"]

    def test_inactive_mentor_excluded_from_new_bookings(self, db):
        # Create a temporary mentor who is inactive
        email = f"inactive_{int(datetime.now().timestamp())}@test.com"
        m = Mentor(name="Inactive Coach", email=email, timezone="Asia/Kolkata", is_active=False)
        db.add(m)
        db.commit()

        try:
            # Verify they are excluded from allocation
            slot = datetime(2026, 10, 1, 9, 30, tzinfo=timezone.utc)
            booking_in = BookingCreate(
                parent_name="Parent Test",
                parent_email="parent_test@test.com",
                child_name="Child Test",
                course_id=1,
                parent_timezone="America/New_York",
                slot_utc=slot,
            )
            booking = create_booking(db=db, booking_in=booking_in)
            assert booking.mentor_id != m.id
            # Cleanup booking
            db.delete(booking)
            db.commit()
        finally:
            db.delete(m)
            db.commit()

    def test_admin_parents_and_parent_bookings_listing(self):
        # Parents list
        res = client.get("/api/v1/admin/parents")
        assert res.status_code == 200
        parents = res.json()
        assert len(parents) >= 1
        first_parent_id = parents[0]["id"]

        # Parent detail bookings
        b_res = client.get(f"/api/v1/admin/parents/{first_parent_id}/bookings")
        assert b_res.status_code == 200
        bookings = b_res.json()
        assert isinstance(bookings, list)

    def test_admin_bookings_dual_timezone_listing(self):
        res = client.get("/api/v1/admin/bookings")
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1
        first = items[0]
        assert "parent_local_time" in first
        assert "mentor_ist_time" in first
        assert "IST" in first["mentor_ist_time"]

    def test_mentor_internal_schedule_endpoint(self, db):
        from models.mentor import Mentor
        booking = db.query(Booking).join(Mentor, Booking.mentor_id == Mentor.id).first()
        assert booking is not None
        mentor_id = booking.mentor_id

        res = client.get(f"/api/v1/admin/mentors/{mentor_id}/schedule")
        assert res.status_code == 200
        schedule = res.json()
        assert len(schedule) >= 1
        item = schedule[0]
        assert "class_time_ist" in item
        assert "IST" in item["class_time_ist"]
        assert "student_name" in item
        assert "class_link" in item
