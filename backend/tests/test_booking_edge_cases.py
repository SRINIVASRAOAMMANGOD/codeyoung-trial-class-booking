"""Focused booking invariants, validation, and concurrency coverage."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from main import app
from models.booking import Booking
from models.course import Course
from models.mentor import Mentor
from models.parent import Parent
from schemas.booking import BookingCreate
from services.booking_service import BookingConflictError, create_booking
from services.timezone_service import get_ist_date_today

client = TestClient(app)
IST = ZoneInfo("Asia/Kolkata")


def booking_input(slot: datetime, email: str, course_id: int = 1) -> BookingCreate:
    return BookingCreate(
        parent_name="Edge Test Parent",
        parent_email=email,
        child_name="Edge Test Child",
        course_id=course_id,
        parent_timezone="America/New_York",
        slot_utc=slot,
    )


def cleanup_booking(db, booking):
    parent_id = booking.parent_id
    db.delete(booking)
    db.commit()
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if parent:
        db.delete(parent)
        db.commit()


@pytest.fixture
def single_mentor_pool():
    db = SessionLocal()
    suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
    mentor = Mentor(
        name=f"Edge Mentor {suffix}",
        email=f"edge-mentor-{suffix}@democodeyoung.com",
        timezone="Asia/Kolkata",
        is_active=True,
    )
    db.add(mentor)
    db.commit()
    statuses = {m.id: m.is_active for m in db.query(Mentor).all()}
    for existing in db.query(Mentor).all():
        existing.is_active = existing.id == mentor.id
    db.commit()
    try:
        yield db, mentor
    finally:
        db.rollback()
        for booking in db.query(Booking).filter(Booking.mentor_id == mentor.id).all():
            db.delete(booking)
        db.commit()
        for existing in db.query(Mentor).all():
            if existing.id in statuses:
                existing.is_active = statuses[existing.id]
        db.delete(mentor)
        db.commit()
        db.close()


def future_slot(ist_date: date, hour: int = 15) -> datetime:
    return datetime(
        ist_date.year,
        ist_date.month,
        ist_date.day,
        hour,
        tzinfo=IST,
    ).astimezone(timezone.utc)


def test_valid_booking_assigns_one_active_mentor(single_mentor_pool):
    db, mentor = single_mentor_pool
    booking = create_booking(
        db,
        booking_input(future_slot(date(2045, 1, 10)), "edge-valid@example.test"),
    )
    try:
        assert booking.mentor_id == mentor.id
        assert booking.mentor.is_active is True
        assert booking.status == "confirmed"
        assert booking.class_link.startswith("https://class.codeyoung.com/room/")
    finally:
        cleanup_booking(db, booking)


def test_same_mentor_cannot_receive_exact_slot_twice(single_mentor_pool):
    db, mentor = single_mentor_pool
    slot = future_slot(date(2045, 1, 11))
    first = create_booking(db, booking_input(slot, "edge-duplicate-a@example.test"))
    try:
        with pytest.raises(BookingConflictError):
            create_booking(db, booking_input(slot, "edge-duplicate-b@example.test"))
        assert db.query(Booking).filter(Booking.mentor_id == mentor.id, Booking.slot_utc == slot).count() == 1
    finally:
        cleanup_booking(db, first)


def test_zero_one_two_daily_classes_and_next_ist_date(single_mentor_pool):
    db, mentor = single_mentor_pool
    ist_day = date(2045, 1, 12)
    bookings = []
    try:
        bookings.append(create_booking(db, booking_input(future_slot(ist_day, 15), "edge-cap-a@example.test")))
        bookings.append(create_booking(db, booking_input(future_slot(ist_day, 16), "edge-cap-b@example.test")))
        with pytest.raises(BookingConflictError):
            create_booking(db, booking_input(future_slot(ist_day, 17), "edge-cap-c@example.test"))
        next_day = create_booking(db, booking_input(future_slot(ist_day + timedelta(days=1), 15), "edge-cap-next@example.test"))
        bookings.append(next_day)
        assert all(booking.mentor_id == mentor.id for booking in bookings)
    finally:
        for booking in bookings:
            cleanup_booking(db, booking)


def test_multiple_same_slot_bookings_use_different_active_mentors():
    db = SessionLocal()
    slot = future_slot(date(2045, 1, 13))
    bookings = []
    try:
        for index in range(3):
            bookings.append(create_booking(db, booking_input(slot, f"edge-multi-{index}@example.test")))
        mentor_ids = [booking.mentor_id for booking in bookings]
        assert len(set(mentor_ids)) == 3
        assert all(db.query(Mentor).filter(Mentor.id == mentor_id, Mentor.is_active.is_(True)).count() == 1 for mentor_id in mentor_ids)
    finally:
        for booking in bookings:
            cleanup_booking(db, booking)
        db.close()


def test_unique_database_constraint_rejects_same_mentor_slot():
    db = SessionLocal()
    existing = db.query(Booking).first()
    assert existing is not None
    duplicate = Booking(
        parent_id=existing.parent_id,
        child_name="Constraint Child",
        parent_timezone=existing.parent_timezone,
        slot_utc=existing.slot_utc,
        mentor_id=existing.mentor_id,
        course_id=existing.course_id,
        class_link="https://class.codeyoung.com/room/constraint-test",
        status="confirmed",
    )
    try:
        db.add(duplicate)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


@pytest.mark.parametrize("payload, expected_detail", [
    ({"parent_timezone": "Not/AZone"}, "Invalid timezone"),
    ({"slot_utc": "not-a-datetime"}, "valid datetime"),
    ({"slot_utc": "2045-01-10T09:30:00"}, "timezone-aware UTC"),
    ({"slot_utc": "2045-01-10T09:31:00Z"}, "top of an hour"),
    ({"slot_utc": "2045-01-10T08:30:00Z"}, "outside the daily booking window"),
])
def test_invalid_booking_input_is_rejected(payload, expected_detail):
    base = {
        "parent_name": "Invalid Edge Parent",
        "parent_email": "invalid-edge@example.test",
        "child_name": "Invalid Edge Child",
        "course_id": 1,
        "parent_timezone": "America/New_York",
        "slot_utc": "2045-01-10T09:30:00Z",
    }
    base.update(payload)
    response = client.post("/api/v1/bookings", json=base)
    assert response.status_code == 422
    assert expected_detail.lower() in response.text.lower()


def test_course_and_required_course_validation():
    base = {
        "parent_name": "Course Edge Parent",
        "parent_email": "course-edge@example.test",
        "child_name": "Course Edge Child",
        "parent_timezone": "America/New_York",
        "slot_utc": "2045-01-10T09:30:00Z",
    }
    invalid = client.post("/api/v1/bookings", json={**base, "course_id": 999999})
    assert invalid.status_code == 422
    missing = client.post("/api/v1/bookings", json=base)
    assert missing.status_code == 422

    db = SessionLocal()
    course = Course(
        name=f"Inactive Edge Course {datetime.now().strftime('%f')}",
        description="Inactive course for validation",
        age_range="Ages 10-12",
        level="Beginner",
        is_active=False,
    )
    db.add(course)
    db.commit()
    try:
        inactive = client.post("/api/v1/bookings", json={**base, "course_id": course.id})
        assert inactive.status_code == 422
    finally:
        db.delete(course)
        db.commit()
        db.close()


def test_booking_window_boundaries_are_validated():
    today = get_ist_date_today()
    base = {
        "parent_name": "Window Edge Parent",
        "parent_email": "window-edge@example.test",
        "child_name": "Window Edge Child",
        "course_id": 1,
        "parent_timezone": "America/New_York",
    }
    past = client.get("/api/v1/slots", params={"date": (today - timedelta(days=1)).isoformat(), "timezone": "America/New_York"})
    assert past.status_code == 422
    tomorrow = client.get("/api/v1/slots", params={"date": (today + timedelta(days=1)).isoformat(), "timezone": "America/New_York"})
    assert tomorrow.status_code == 200
    last = client.get("/api/v1/slots", params={"date": (today + timedelta(days=7)).isoformat(), "timezone": "America/New_York"})
    assert last.status_code == 200
    after = client.get("/api/v1/slots", params={"date": (today + timedelta(days=8)).isoformat(), "timezone": "America/New_York"})
    assert after.status_code == 422


def test_utc_midnight_maps_to_next_ist_calendar_date():
    utc_midnight_boundary = datetime(2045, 1, 10, 18, 30, tzinfo=timezone.utc)
    assert utc_midnight_boundary.astimezone(IST).date() == date(2045, 1, 11)
    assert utc_midnight_boundary.astimezone(IST).hour == 0


def test_all_active_mentors_unavailable_returns_conflict_without_booking(single_mentor_pool):
    db, mentor = single_mentor_pool
    slot = future_slot(date(2045, 1, 14))
    existing = [
        create_booking(db, booking_input(slot, "edge-exhausted@example.test")),
        create_booking(db, booking_input(future_slot(date(2045, 1, 14), 16), "edge-exhausted-1@example.test")),
    ]
    try:
        with pytest.raises(BookingConflictError):
            create_booking(db, booking_input(future_slot(date(2045, 1, 14), 17), "edge-exhausted-2@example.test"))
        assert db.query(Booking).filter(Booking.slot_utc == future_slot(date(2045, 1, 14), 17)).count() == 0
    finally:
        for booking in existing:
            cleanup_booking(db, booking)


def test_concurrent_same_slot_requests_keep_database_consistent():
    slot = future_slot(date(2045, 1, 15))

    def attempt(index):
        db = SessionLocal()
        try:
            with patch("services.booking_service.send_booking_notifications", return_value={"parent": True, "mentor": True}):
                try:
                    booking = create_booking(db, booking_input(slot, f"edge-concurrent-{index}@example.test"))
                    return ("success", booking.id, booking.mentor_id)
                except BookingConflictError:
                    return ("conflict", None, None)
                except Exception as exc:
                    return (type(exc).__name__, None, None)
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(attempt, range(5)))

    db = SessionLocal()
    try:
        successes = [result for result in results if result[0] == "success"]
        persisted = db.query(Booking).filter(Booking.slot_utc == slot).all()
        assert len({result[2] for result in successes}) == len(successes)
        assert len({booking.mentor_id for booking in persisted}) == len(persisted)
        assert len(persisted) == len(successes)
        assert len(persisted) <= 5
        parent_ids = [booking.parent_id for booking in persisted]
        for booking in persisted:
            db.delete(booking)
        db.commit()
        for parent_id in parent_ids:
            parent = db.query(Parent).filter(Parent.id == parent_id).first()
            if parent:
                db.delete(parent)
        db.commit()
    finally:
        db.close()
