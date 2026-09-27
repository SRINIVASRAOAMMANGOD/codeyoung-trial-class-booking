"""
test_courses.py — Tests for the course API and booking integration.
"""

from fastapi.testclient import TestClient
from datetime import date, timedelta

from database import Base, engine, SessionLocal
from main import app
from models.booking import Booking
from models.course import Course
from models.parent import Parent
from services.timezone_service import get_ist_date_today

import pytest

client = TestClient(app)

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_get_active_courses():
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    names = {c["name"] for c in data}
    assert {
        "Coding Fundamentals",
        "Python Programming",
        "Web Development",
        "AI & Robotics",
        "Game Development",
        "App Development",
        "Data & Analytics",
    }.issubset(names)

def test_book_with_valid_course(db):
    course = db.query(Course).filter(Course.name == "Coding Fundamentals").first()
    course_id = course.id

    slot_utc = None
    for offset in range(1, 8):
        requested_date = get_ist_date_today() + timedelta(days=offset)
        response = client.get(
            "/api/v1/slots",
            params={"date": requested_date.isoformat(), "timezone": "America/New_York"},
        )
        if response.status_code == 200 and response.json()["slots"]:
            slot_utc = response.json()["slots"][0]["utc_iso"]
            break
    assert slot_utc is not None, "No isolated available slot found for the booking test."

    payload = {
        "parent_name": "Course Test Parent",
        "parent_email": "coursetest@example.com",
        "child_name": "Course Child",
        "course_id": course_id,
        "parent_timezone": "America/New_York",
        "slot_utc": slot_utc
    }

    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == course_id
    assert data["course_name"] == "Coding Fundamentals"

    booking = db.query(Booking).filter(Booking.id == data["id"]).one()
    parent_id = booking.parent_id
    db.delete(booking)
    db.commit()
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if parent:
        db.delete(parent)
        db.commit()

def test_book_with_invalid_course(db):
    payload = {
        "parent_name": "Course Test Parent",
        "parent_email": "coursetest2@example.com",
        "child_name": "Course Child",
        "course_id": 99999,
        "parent_timezone": "America/New_York",
        "slot_utc": "2026-10-01T09:30:00Z"
    }

    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 422
    assert "Invalid or inactive course ID" in response.text
