"""
tests/test_email_service.py — Unit and integration tests for email notification service.
"""

from datetime import datetime, timezone
from unittest.mock import patch
import pytest

from database import SessionLocal
from models.booking import Booking
from models.mentor import Mentor
from models.parent import Parent
from schemas.booking import BookingCreate
from services.booking_service import BookingConflictError, create_booking
from services.email_service import (
    EmailConfigurationError,
    build_mentor_email_content,
    build_parent_email_content,
    clear_recent_emails,
    dispatch_email,
    format_slot_datetime,
    get_recent_emails,
    send_booking_notifications,
)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_email_queue():
    clear_recent_emails()
    yield
    clear_recent_emails()


class TestEmailFormattingAndContent:
    """Verifies content, local timezone conversions, and recipient formatting."""

    def test_format_slot_datetime_us_eastern_edt(self):
        # 2026-09-28 09:30:00 UTC = 05:30:00 EDT (UTC-4)
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)
        date_str, time_str, tz_label = format_slot_datetime(slot_utc, "America/New_York")

        assert "Monday, September 28, 2026" in date_str
        assert "05:30 AM – 06:30 AM" in time_str
        assert "America/New_York" in tz_label
        assert "UTC-04:00" in tz_label

    def test_format_slot_datetime_uk_london_bst(self):
        # 2026-09-28 09:30:00 UTC = 10:30:00 BST (UTC+1)
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)
        date_str, time_str, tz_label = format_slot_datetime(slot_utc, "Europe/London")

        assert "Monday, September 28, 2026" in date_str
        assert "10:30 AM – 11:30 AM" in time_str
        assert "Europe/London" in tz_label
        assert "UTC+01:00" in tz_label

    def test_format_slot_datetime_india_ist(self):
        # 2026-09-28 09:30:00 UTC = 15:00:00 IST (UTC+5:30)
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)
        date_str, time_str, tz_label = format_slot_datetime(slot_utc, "Asia/Kolkata")

        assert "Monday, September 28, 2026" in date_str
        assert "03:00 PM – 04:00 PM" in time_str
        assert "Asia/Kolkata" in tz_label
        assert "UTC+05:30" in tz_label

    def test_parent_and_mentor_email_content_alignment(self):
        parent = Parent(name="Bruce Wayne", email="bruce@wayne.com")
        mentor = Mentor(name="Aarav Sharma", email="aarav@democodeyoung.com", timezone="Asia/Kolkata")
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)

        booking = Booking(
            id=101,
            parent=parent,
            mentor=mentor,
            child_name="Damian Wayne",
            parent_timezone="America/New_York",
            slot_utc=slot_utc,
            class_link="https://class.codeyoung.com/room/test-link-xyz",
            status="confirmed",
            course_id=1,
        )

        parent_email = build_parent_email_content(booking)
        mentor_email = build_mentor_email_content(booking)

        # 1. Recipient check
        assert parent_email["recipient"] == "bruce@wayne.com"
        assert mentor_email["recipient"] == "aarav@democodeyoung.com"

        # 2. Timezone-specific display times
        assert "05:30 AM – 06:30 AM" in parent_email["class_time"]
        assert "America/New_York" in parent_email["timezone"]

        assert "03:00 PM – 04:00 PM" in mentor_email["class_time"]
        assert "Asia/Kolkata" in mentor_email["timezone"]

        # 3. Both receive the identical class link
        assert parent_email["class_link"] == "https://class.codeyoung.com/room/test-link-xyz"
        assert mentor_email["class_link"] == "https://class.codeyoung.com/room/test-link-xyz"

        # 4. Correct names cross-referenced
        assert parent_email["mentor_name"] == "Aarav Sharma"
        assert mentor_email["parent_name"] == "Bruce Wayne"
        assert parent_email["child_name"] == "Damian Wayne"
        assert mentor_email["child_name"] == "Damian Wayne"


class TestConsoleDispatchAndQueue:
    """Verifies that console backend records both emails in the in-memory queue."""

    def test_send_booking_notifications_dispatches_two_emails(self):
        parent = Parent(name="Diana Prince", email="diana@themyscira.gov")
        mentor = Mentor(name="Priya Patel", email="priya@democodeyoung.com", timezone="Asia/Kolkata")
        slot_utc = datetime(2026, 9, 28, 10, 30, tzinfo=timezone.utc)

        booking = Booking(
            id=102,
            parent=parent,
            mentor=mentor,
            child_name="Cassie Sandsmark",
            parent_timezone="Europe/London",
            slot_utc=slot_utc,
            class_link="https://class.codeyoung.com/room/diana-cassie",
            status="confirmed",
            course_id=1,
        )

        results = send_booking_notifications(booking)
        assert results["parent"] is True
        assert results["mentor"] is True

        recent = get_recent_emails()
        assert len(recent) == 2

        parent_entry = next(e for e in recent if e["recipient_type"] == "Parent")
        mentor_entry = next(e for e in recent if e["recipient_type"] == "Mentor")

        assert parent_entry["recipient"] == "diana@themyscira.gov"
        assert mentor_entry["recipient"] == "priya@democodeyoung.com"
        assert "11:30 AM – 12:30 PM" in parent_entry["class_time"]  # London BST
        assert "04:00 PM – 05:00 PM" in mentor_entry["class_time"]  # India IST


class TestBookingCommitBeforeNotification:
    """Verifies transaction commit order and failure resilience."""

    def test_booking_persists_even_if_email_dispatch_fails(self, db):
        # Even if dispatch_email raises an error, the booking is already committed to DB
        with patch("services.booking_service.send_booking_notifications", side_effect=RuntimeError("SMTP crash")):
            booking_in = BookingCreate(
                parent_name="Clark Kent",
                parent_email="clark@dailyplanet.com",
                child_name="Jon Kent",
                course_id=1,
                parent_timezone="America/New_York",
                slot_utc=datetime(2026, 9, 30, 9, 30, tzinfo=timezone.utc),
            )

            booking = create_booking(db=db, booking_in=booking_in)

            try:
                assert booking.id is not None
                # Verify booking is present in database
                fetched = db.query(Booking).filter(Booking.id == booking.id).one_or_none()
                assert fetched is not None
                assert fetched.status == "confirmed"
            finally:
                # Cleanup
                parent_id = booking.parent_id
                db.delete(booking)
                db.commit()
                parent = db.query(Parent).filter(Parent.id == parent_id).first()
                if parent:
                    db.delete(parent)
                    db.commit()

    def test_no_email_attempted_if_booking_fails(self, db):
        # Trigger an intentional conflict where mentor cannot be allocated
        with patch("services.booking_service._find_eligible_mentor", return_value=None):
            booking_in = BookingCreate(
                parent_name="Barry Allen",
                parent_email="barry@centralcity.gov",
                child_name="Bart Allen",
                course_id=1,
                parent_timezone="America/New_York",
                slot_utc=datetime(2026, 9, 29, 9, 30, tzinfo=timezone.utc),
            )

            with pytest.raises(BookingConflictError):
                create_booking(db=db, booking_in=booking_in)

            # No notifications should be dispatched
            assert len(get_recent_emails()) == 0


class TestSmtpConfigurationValidation:
    """Verifies SMTP validation when host is missing."""

    def test_smtp_missing_host_raises_configuration_error(self):
        with patch("services.email_service.get_settings") as mock_settings:
            mock_settings.return_value.email_backend = "smtp"
            mock_settings.return_value.smtp_host = ""

            with pytest.raises(EmailConfigurationError, match="SMTP_HOST must be configured"):
                dispatch_email({"recipient": "test@example.com", "body_text": "hello", "subject": "test"})

class TestResendEmail:
    """Verifies resend email functionality with default and custom overrides."""

    def test_resend_to_default_recipient(self, db):
        from services.admin_service import resend_booking_email
        from schemas.admin import ResendEmailRequest

        # Seed data
        parent = Parent(name="Tony Stark", email="tony@stark.com")
        mentor = Mentor(name="Peter Parker", email="peter@democodeyoung.com", timezone="Asia/Kolkata")
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)
        booking = Booking(
            parent=parent,
            mentor=mentor,
            child_name="Morgan Stark",
            parent_timezone="America/New_York",
            slot_utc=slot_utc,
            class_link="https://class.codeyoung.com/room/test-1",
            status="confirmed",
            course_id=1,
        )
        db.add(booking)
        db.commit()

        try:
            req = ResendEmailRequest(recipient_type="parent", recipient_email="")
            result = resend_booking_email(db, booking.id, req)
            
            assert result["message"] == "Email resent successfully"
            assert result["recipient"] == "tony@stark.com"
            
            emails = get_recent_emails()
            assert len(emails) == 1
            assert emails[0]["recipient"] == "tony@stark.com"
        finally:
            db.delete(booking)
            db.delete(parent)
            db.delete(mentor)
            db.commit()

    def test_resend_to_edited_recipient_with_custom_subject(self, db):
        from services.admin_service import resend_booking_email
        from schemas.admin import ResendEmailRequest

        # Seed data
        parent = Parent(name="Steve Rogers", email="steve@avengers.com")
        mentor = Mentor(name="Sam Wilson", email="sam@democodeyoung.com", timezone="Asia/Kolkata")
        slot_utc = datetime(2026, 9, 28, 9, 30, tzinfo=timezone.utc)
        booking = Booking(
            parent=parent,
            mentor=mentor,
            child_name="Trainee",
            parent_timezone="America/New_York",
            slot_utc=slot_utc,
            class_link="https://class.codeyoung.com/room/test-2",
            status="confirmed",
            course_id=1,
        )
        db.add(booking)
        db.commit()

        try:
            req = ResendEmailRequest(
                recipient_type="parent", 
                recipient_email="bucky@avengers.com",
                custom_subject="Your Rescheduled Class"
            )
            result = resend_booking_email(db, booking.id, req)
            
            assert result["recipient"] == "bucky@avengers.com"
            
            emails = get_recent_emails()
            assert len(emails) == 1
            assert emails[0]["recipient"] == "bucky@avengers.com"
            assert emails[0]["subject"] == "Your Rescheduled Class"
        finally:
            db.delete(booking)
            db.delete(parent)
            db.delete(mentor)
            db.commit()
