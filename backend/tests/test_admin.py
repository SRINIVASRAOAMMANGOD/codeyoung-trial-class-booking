"""
tests/test_admin.py — Unit and integration tests for operational administration and mentor portal.
"""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models.booking import Booking
from models.course import Course
from models.mentor import Mentor
from models.parent import Parent
from schemas.booking import BookingCreate
from services.booking_service import create_booking
from services.slot_service import get_available_slots
from services.timezone_service import get_ist_date_today

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

    def test_admin_upcoming_capacity_is_grouped_by_ist_date(self, db):
        suffix = int(datetime.now().timestamp() * 1000000)
        mentor = Mentor(
            name=f"Capacity Coach {suffix}",
            email=f"capacity_{suffix}@example.com",
            timezone="Asia/Kolkata",
            is_active=True,
        )
        parent = Parent(name=f"Capacity Parent {suffix}", email=f"capacity_{suffix}@example.com")
        course = db.query(Course).first()
        db.add_all([mentor, parent])
        db.commit()

        slots = [
            datetime(2035, 9, 28, 9, 30, tzinfo=timezone.utc),
            datetime(2035, 9, 29, 9, 30, tzinfo=timezone.utc),
            datetime(2035, 9, 29, 10, 30, tzinfo=timezone.utc),
        ]
        for slot in slots:
            db.add(Booking(
                parent_id=parent.id,
                child_name="Capacity Child",
                parent_timezone="America/New_York",
                slot_utc=slot,
                mentor_id=mentor.id,
                course_id=course.id,
                class_link=f"https://class.codeyoung.com/room/{suffix}-{slot.hour}",
                status="confirmed",
            ))
        db.commit()

        try:
            response = client.get("/api/v1/admin/mentors")
            assert response.status_code == 200
            item = next(m for m in response.json() if m["id"] == mentor.id)
            assert item["upcoming_capacity"] == [
                {"ist_date": "2035-09-28", "classes_booked": 1, "capacity": 2},
                {"ist_date": "2035-09-29", "classes_booked": 2, "capacity": 2},
            ]
        finally:
            db.query(Booking).filter(Booking.mentor_id == mentor.id).delete(synchronize_session=False)
            db.delete(parent)
            db.delete(mentor)
            db.commit()

    def test_admin_course_management_and_inactive_filter(self):
        suffix = int(datetime.now().timestamp() * 1000000)
        payload = {
            "name": f"Test Course {suffix}",
            "description": "A course created by the admin test.",
            "age_range": "Ages 9-12",
            "level": "Beginner",
        }

        created = client.post("/api/v1/admin/courses", json=payload)
        assert created.status_code == 201
        course_id = created.json()["id"]

        try:
            duplicate = client.post("/api/v1/admin/courses", json=payload)
            assert duplicate.status_code == 409

            updated = client.patch(
                f"/api/v1/admin/courses/{course_id}",
                json={"description": "Updated description.", "level": "Intermediate"},
            )
            assert updated.status_code == 200
            assert updated.json()["description"] == "Updated description."
            assert updated.json()["level"] == "Intermediate"

            deactivated = client.patch(
                f"/api/v1/admin/courses/{course_id}/status",
                json={"is_active": False},
            )
            assert deactivated.status_code == 200
            assert deactivated.json()["is_active"] is False

            public_courses = client.get("/api/v1/courses")
            assert course_id not in {course["id"] for course in public_courses.json()}
            admin_courses = client.get("/api/v1/admin/courses")
            assert any(course["id"] == course_id and not course["is_active"] for course in admin_courses.json())
        finally:
            with SessionLocal() as cleanup_db:
                course = cleanup_db.query(Course).filter(Course.id == course_id).first()
                if course:
                    cleanup_db.delete(course)
                    cleanup_db.commit()

    def test_inactive_course_keeps_existing_booking_visible(self, db):
        suffix = int(datetime.now().timestamp() * 1000000)
        created = client.post("/api/v1/admin/courses", json={
            "name": f"Historical Course {suffix}",
            "description": "Course retained for historical booking coverage.",
            "age_range": "Ages 10-14",
            "level": "Intermediate",
        })
        assert created.status_code == 201
        course_id = created.json()["id"]

        mentor = db.query(Mentor).filter(Mentor.is_active == True).first()  # noqa: E712
        parent = Parent(name=f"Historical Parent {suffix}", email=f"historical_{suffix}@example.com")
        db.add(parent)
        db.commit()
        booking = Booking(
            parent_id=parent.id,
            child_name="Historical Child",
            parent_timezone="America/New_York",
            slot_utc=datetime(2040, 2, 1, 9, 30, tzinfo=timezone.utc),
            mentor_id=mentor.id,
            course_id=course_id,
            class_link=f"https://class.codeyoung.com/room/historical-{suffix}",
            status="confirmed",
        )
        db.add(booking)
        db.commit()

        try:
            deactivated = client.patch(
                f"/api/v1/admin/courses/{course_id}/status",
                json={"is_active": False},
            )
            assert deactivated.status_code == 200

            bookings = client.get("/api/v1/admin/bookings")
            assert any(
                item["id"] == booking.id and item["course_name"] == f"Historical Course {suffix}"
                for item in bookings.json()
            )
        finally:
            db.delete(booking)
            db.delete(parent)
            db.commit()
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                db.delete(course)
                db.commit()

    def test_create_and_delete_mentor_with_zero_bookings(self, db):
        unique_email = f"new_mentor_{int(datetime.now().timestamp())}@democodeyoung.com"
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

    def test_mentor_edit(self, db):
        # Create a mentor to edit
        unique_email = f"edit_mentor_{int(datetime.now().timestamp())}@democodeyoung.com"
        create_res = client.post("/api/v1/admin/mentors", json={
            "name": "To Edit",
            "email": unique_email,
            "timezone": "Asia/Kolkata",
        })
        assert create_res.status_code == 201
        mentor_id = create_res.json()["id"]

        # Edit the mentor
        edit_res = client.patch(f"/api/v1/admin/mentors/{mentor_id}", json={
            "name": "Edited Name",
            "is_active": False
        })
        assert edit_res.status_code == 200
        assert edit_res.json()["name"] == "Edited Name"
        assert edit_res.json()["is_active"] is False
        assert edit_res.json()["email"] == unique_email # shouldn't change

        # Delete it to cleanup
        client.delete(f"/api/v1/admin/mentors/{mentor_id}")

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
            slot = None
            for offset in range(1, 8):
                slots = get_available_slots(
                    get_ist_date_today() + timedelta(days=offset),
                    "America/New_York",
                    db,
                )
                if slots:
                    slot = datetime.fromisoformat(slots[0]["utc_iso"])
                    break
            assert slot is not None, "No isolated available slot found for the inactive mentor test."
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
