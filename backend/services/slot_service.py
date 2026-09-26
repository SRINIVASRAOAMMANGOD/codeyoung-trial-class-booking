"""
services/slot_service.py — Slot availability business logic.

Determines which of the 7 daily IST slots are bookable on a given date,
based on live mentor availability in the database.

A slot is available if at least one active mentor is eligible, meaning:
  1. The mentor is not already assigned to that exact UTC slot.
  2. The mentor has fewer than 2 bookings on the same IST calendar date.

This module only reads from the database. Booking writes happen in
booking_service.py (Phase 5), which uses SERIALIZABLE transactions.
"""

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.booking import Booking
from models.mentor import Mentor
from services.timezone_service import (
    generate_ist_anchors,
    ist_anchor_to_utc,
    utc_to_local_display,
)


def get_available_slots(
    ist_date: date,
    parent_tz: str,
    db: Session,
) -> list[dict]:
    """
    Return a list of available slot dicts for the given IST date.

    Each dict contains:
      - utc_iso:       ISO 8601 UTC string (sent back to POST /bookings)
      - local_display: ISO 8601 string in the parent's timezone (UI only)

    Slots with no eligible mentors are excluded from the result.
    An empty list means no slots are available on this date.
    """
    anchors = generate_ist_anchors(ist_date)
    available_slots = []

    for ist_dt in anchors:
        utc_dt = ist_anchor_to_utc(ist_dt)

        if _has_eligible_mentor(db, utc_dt, ist_date):
            local_dt = utc_to_local_display(utc_dt, parent_tz)
            available_slots.append(
                {
                    "utc_iso": utc_dt.isoformat(),
                    "local_display": local_dt.isoformat(),
                }
            )

    return available_slots


def _has_eligible_mentor(
    db: Session,
    utc_slot: datetime,
    ist_date: date,
) -> bool:
    """
    Check whether at least one active mentor is eligible for this slot.

    Eligibility rules (applied per mentor):
      R1. Mentor is active (is_active = True).
      R2. Mentor is not already assigned to this exact UTC slot.
      R3. Mentor has fewer than 2 confirmed bookings on this IST date.

    Returns True if any mentor satisfies all three rules.

    Implementation note on empty-set safety:
      SQLAlchemy's notin_([]) generates "NOT IN (NULL)" which can behave
      unexpectedly. We explicitly skip the notin_ filter when the exclusion
      set is empty to avoid this edge case.
    """
    # --- R2: mentors already assigned to this exact UTC slot ---
    occupied_at_slot: set[int] = {
        row.mentor_id
        for row in db.query(Booking.mentor_id)
        .filter(
            Booking.slot_utc == utc_slot,
            Booking.status == "confirmed",
        )
        .all()
    }

    # --- R3: mentors who have reached the 2-class IST-day cap ---
    # func.timezone('Asia/Kolkata', slot_utc) converts TIMESTAMPTZ → IST timestamp.
    # func.date(...) extracts the calendar date in IST.
    # This is the PostgreSQL-native way to enforce the IST-day boundary.
    at_daily_cap: set[int] = {
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

    # Combined set of mentor IDs ineligible for this slot
    ineligible_ids: set[int] = occupied_at_slot | at_daily_cap

    # --- R1 + eligibility: find any active mentor not in ineligible_ids ---
    query = db.query(Mentor).filter(Mentor.is_active == True)  # noqa: E712

    if ineligible_ids:
        query = query.filter(Mentor.id.notin_(list(ineligible_ids)))

    return query.first() is not None
