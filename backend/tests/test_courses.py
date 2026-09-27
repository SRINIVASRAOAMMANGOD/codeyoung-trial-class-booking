"""
test_courses.py — Tests for the course API and booking integration.
"""

from fastapi.testclient import TestClient
from datetime import datetime, timezone

from database import Base, engine, SessionLocal
from main import app
from models.course import Course

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
    assert "Coding Fundamentals" in [c["name"] for c in data]

def test_book_with_valid_course(db):
    course = db.query(Course).filter(Course.name == "Coding Fundamentals").first()
    course_id = course.id

    payload = {
        "parent_name": "Course Test Parent",
        "parent_email": "coursetest@example.com",
        "child_name": "Course Child",
        "course_id": course_id,
        "parent_timezone": "America/New_York",
        "slot_utc": "2026-10-01T09:30:00Z"
    }

    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == course_id
    assert data["course_name"] == "Coding Fundamentals"

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
