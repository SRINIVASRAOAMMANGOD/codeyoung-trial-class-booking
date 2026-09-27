"""
services/booking_service.py — Booking business logic and mentor allocation.

Handles booking creation, validation, mentor assignment, and concurrency control.
Key architectural guarantees:
  1. slot_utc must be timezone-aware and in UTC.
  2. Parent timezone must be a valid IANA identifier.
  3. Mentors are allocated automatically from active mentors who:
     - Are not already booked at the requested slot_utc.
     - Have fewer than 2 confirmed bookings on that IST calendar day.
  4. Transactions run at SERIALIZABLE isolation level in PostgreSQL.
  5. Concurrency / serialization failures are retried once before raising ConcurrencyError (503).
  6. Genuine lack of available mentors raises BookingConflictError (409).
"""

import logging
import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session, joinedload

from models.booking import Booking
from models.mentor import Mentor
from models.course import Course
from schemas.booking import BookingCreate
from services.email_service import send_booking_notifications
from services.parent_service import get_or_create_parent
from services.timezone_service import validate_timezone

_IST = ZoneInfo("Asia/Kolkata")
logger = logging.getLogger(__name__)


# --- Custom Domain Exceptions ---

class BookingError(Exception):
    """Base exception for booking service errors."""
    pass


class BookingValidationError(ValueError, BookingError):
    """Raised when request parameters fail domain validation (HTTP 422 / 400)."""
    pass


class BookingConflictError(BookingError):
    """Raised when no active mentor is available for the slot (HTTP 409)."""
    pass


class ConcurrencyError(BookingError):
    """Raised when serialization failure persists after retry (HTTP 503)."""
    pass


# --- Helper Functions ---

def generate_class_link() -> str:
    """Generate a dummy trial class room URL with a unique UUID."""
    return f"https://class.codeyoung.com/room/{uuid.uuid4()}"


def validate_booking_input(slot_utc: datetime, parent_timezone: str) -> None:
    """
    Validate slot_utc and parent_timezone.
    - parent_timezone must be a recognised IANA identifier.
    - slot_utc must be timezone-aware.
    - slot_utc must have a UTC offset of zero.
    """
    if not validate_timezone(parent_timezone):
        raise BookingValidationError(f"Invalid IANA timezone: '{parent_timezone}'")

    if slot_utc.tzinfo is None or slot_utc.utcoffset() is None:
        raise BookingValidationError("slot_utc must be a timezone-aware datetime")

    if slot_utc.utcoffset().total_seconds() != 0:
        raise BookingValidationError("slot_utc must be in UTC (offset +00:00)")


def _is_retryable_concurrency_error(exc: Exception) -> bool:
    """
    Detect PostgreSQL serialization failures (40001) or unique constraint race
    collisions (23505 on uq_mentor_slot_utc) that qualify for a retry.
    """
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)
    if pgcode in ("40001", "40P01", "23505"):
        return True

    if isinstance(exc, (OperationalError, IntegrityError, DBAPIError)):
        msg = str(exc).lower()
        if (
            "could not serialize access" in msg
            or "serializationfailure" in msg
            or "deadlock detected" in msg
            or "uq_mentor_slot_utc" in msg
        ):
            return True

    return False


def _find_eligible_mentor(
    db: Session,
    slot_utc: datetime,
    ist_date: date,
) -> Mentor | None:
    """
    Find and return the next eligible active mentor.

    Eligibility rules:
      1. Mentor is active (is_active == True).
      2. Mentor is not already booked at this exact slot_utc.
      3. Mentor has fewer than 2 confirmed bookings on the same IST calendar date.

    Picks deterministically by lowest mentor ID if multiple mentors are available.
    """
    # Mentors already booked at this exact UTC slot
    occupied_mentor_ids: set[int] = {
        row.mentor_id
        for row in db.query(Booking.mentor_id)
        .filter(
            Booking.slot_utc == slot_utc,
            Booking.status == "confirmed",
        )
        .all()
    }

    # Mentors who have reached the 2-class IST-day cap
    capped_mentor_ids: set[int] = {
        row.mentor_id
        for row in db.query(Booking.mentor_id)
        .filter(
            func.date(
                func.timezone("Asia/Kolkata", Booking.slot_utc)
            ) == ist_date,
            Booking.status == "confirmed",
        )
        .group_by(Booking.mentor_id)
        .having(func.count(Booking.id) >= 2)
        .all()
    }

    ineligible_ids: set[int] = occupied_mentor_ids | capped_mentor_ids

    query = db.query(Mentor).filter(Mentor.is_active == True)  # noqa: E712
    if ineligible_ids:
        query = query.filter(Mentor.id.notin_(list(ineligible_ids)))

    return query.order_by(Mentor.id.asc()).first()


# --- Core Booking Functions ---

def create_booking(db: Session, booking_in: BookingCreate) -> Booking:
    """
    Create a new confirmed trial class booking with automatic mentor assignment.

    Workflow:
      1. Validate input parameters (timezone & UTC awareness).
      2. Derive IST calendar date for daily cap enforcement.
      3. Execute inside a SERIALIZABLE transaction.
      4. If serialization error occurs, retry once. If it fails again, raise ConcurrencyError (503).
      5. If no mentor is available, raise BookingConflictError (409).
    """
    # 1. Validation
    validate_booking_input(booking_in.slot_utc, booking_in.parent_timezone)
    course = db.query(Course).filter(Course.id == booking_in.course_id).first()
    if not course or not course.is_active:
        raise BookingValidationError(f"Invalid or inactive course ID: {booking_in.course_id}")

    # 2. Derive IST calendar date
    ist_dt = booking_in.slot_utc.astimezone(_IST)
    ist_date = ist_dt.date()

    # 3. Transaction with retry on concurrency conflicts
    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            # Set PostgreSQL isolation level to SERIALIZABLE
            db.connection(execution_options={"isolation_level": "SERIALIZABLE"})

            mentor = _find_eligible_mentor(db, booking_in.slot_utc, ist_date)
            if mentor is None:
                raise BookingConflictError(
                    "No mentors are available for the requested slot."
                )

            parent = get_or_create_parent(
                db=db,
                name=booking_in.parent_name,
                email=booking_in.parent_email,
            )

            booking = Booking(
                parent_id=parent.id,
                child_name=booking_in.child_name.strip(),
                parent_timezone=booking_in.parent_timezone.strip(),
                slot_utc=booking_in.slot_utc,
                mentor_id=mentor.id,
                course_id=course.id,
                class_link=generate_class_link(),
                status="confirmed",
            )
            booking.parent = parent
            booking.mentor = mentor
            booking.course = course
            db.add(booking)
            db.commit()
            db.refresh(booking)

            # Dispatch email notifications post-commit (never rolls back confirmed booking on delivery error)
            try:
                send_booking_notifications(booking)
            except Exception as notify_err:
                logger.error(
                    "Email notification failed for confirmed booking #%s: %s",
                    getattr(booking, "id", None),
                    notify_err,
                    exc_info=True,
                )

            return booking

        except BookingConflictError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            if _is_retryable_concurrency_error(exc) and attempt < max_attempts - 1:
                continue
            if _is_retryable_concurrency_error(exc):
                raise ConcurrencyError(
                    "Could not complete booking due to concurrent requests. Please retry."
                ) from exc
            raise

    # Fallback (should not be reached)
    raise ConcurrencyError("Booking could not be completed.")


# --- Read Functions ---

def get_booking_by_id(db: Session, booking_id: int) -> Booking | None:
    """Retrieve a booking by its primary key ID."""
    return (
        db.query(Booking)
        .options(joinedload(Booking.parent), joinedload(Booking.course))
        .filter(Booking.id == booking_id)
        .first()
    )


def get_mentor_bookings(
    db: Session,
    mentor_id: int | None = None,
    status: str = "confirmed",
) -> list[Booking]:
    """
    Retrieve confirmed bookings.
    If mentor_id is specified, filter to only that mentor's bookings.
    Ordered chronologically by slot_utc ascending.
    """
    query = (
        db.query(Booking)
        .options(joinedload(Booking.parent), joinedload(Booking.course))
        .filter(Booking.status == status)
    )
    if mentor_id is not None:
        query = query.filter(Booking.mentor_id == mentor_id)
    return query.order_by(Booking.slot_utc.asc()).all()
