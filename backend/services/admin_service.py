"""
services/admin_service.py — Operational management and visibility business logic.

Handles:
  - Dynamic capacity and metrics calculation
  - Mentor administration (view, add, activate/deactivate, delete with booking guard)
  - Parent directory and booking drill-down
  - Complete booking registry with dual-timezone formatting
  - Mentor internal schedule viewing
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from models.booking import Booking
from models.mentor import Mentor
from models.parent import Parent
from schemas.admin import (
    AdminBookingResponse,
    AdminOverviewResponse,
    MentorAdminResponse,
    MentorCreateRequest,
    MentorScheduleItem,
    ParentAdminResponse,
    ParentBookingDetail,
)
from services.timezone_service import get_ist_date_today, validate_timezone

_IST = ZoneInfo("Asia/Kolkata")


def get_admin_overview(db: Session) -> AdminOverviewResponse:
    """
    Compute operational metrics dynamically.
    Capacity = active_mentors * 2 classes/day.
    """
    today_ist = get_ist_date_today()

    total_mentors = db.query(Mentor).count()
    active_mentors = db.query(Mentor).filter(Mentor.is_active == True).count()  # noqa: E712
    total_parents = db.query(Parent).count()
    total_bookings = db.query(Booking).filter(Booking.status == "confirmed").count()

    today_classes = (
        db.query(Booking)
        .filter(
            Booking.status == "confirmed",
            func.date(func.timezone("Asia/Kolkata", Booking.slot_utc)) == today_ist,
        )
        .count()
    )

    theoretical_capacity = active_mentors * 2
    remaining_capacity = max(0, theoretical_capacity - today_classes)

    return AdminOverviewResponse(
        total_mentors=total_mentors,
        active_mentors=active_mentors,
        total_parents=total_parents,
        total_bookings=total_bookings,
        today_classes=today_classes,
        theoretical_capacity=theoretical_capacity,
        remaining_capacity=remaining_capacity,
    )


def get_admin_mentors(db: Session) -> list[MentorAdminResponse]:
    """
    List all mentors with real-time today's load (0/2, 1/2, 2/2) on the current IST date.
    """
    today_ist = get_ist_date_today()
    mentors = db.query(Mentor).order_by(Mentor.id.asc()).all()

    # Query counts for today grouped by mentor
    today_counts_query = (
        db.query(Booking.mentor_id, func.count(Booking.id))
        .filter(
            Booking.status == "confirmed",
            func.date(func.timezone("Asia/Kolkata", Booking.slot_utc)) == today_ist,
        )
        .group_by(Booking.mentor_id)
        .all()
    )
    counts_map = dict(today_counts_query)

    result = []
    for m in mentors:
        classes_today = counts_map.get(m.id, 0)
        result.append(
            MentorAdminResponse(
                id=m.id,
                name=m.name,
                email=m.email,
                timezone=m.timezone,
                is_active=m.is_active,
                today_classes=classes_today,
                capacity_label=f"{classes_today}/2",
                is_full_today=classes_today >= 2,
            )
        )
    return result


def create_mentor(db: Session, mentor_in: MentorCreateRequest) -> Mentor:
    """
    Create a new mentor with email uniqueness and timezone validation.
    """
    clean_email = mentor_in.email.strip().lower()
    clean_name = mentor_in.name.strip()
    clean_tz = mentor_in.timezone.strip()

    if not validate_timezone(clean_tz):
        raise ValueError(f"Invalid IANA timezone: '{clean_tz}'.")

    existing = (
        db.query(Mentor)
        .filter(func.lower(Mentor.email) == clean_email)
        .first()
    )
    if existing:
        raise ValueError("A mentor with this email already exists.")

    mentor = Mentor(
        name=clean_name,
        email=clean_email,
        timezone=clean_tz,
        is_active=True,
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    return mentor


def update_mentor_status(db: Session, mentor_id: int, is_active: bool) -> Mentor | None:
    """Toggle a mentor's active status."""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        return None
    mentor.is_active = is_active
    db.commit()
    db.refresh(mentor)
    return mentor


def delete_mentor(db: Session, mentor_id: int) -> bool:
    """
    Delete a mentor ONLY if zero bookings are associated.
    If historical bookings exist, raises ValueError instructing deactivation.
    """
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        return False

    bookings_count = db.query(Booking).filter(Booking.mentor_id == mentor_id).count()
    if bookings_count > 0:
        raise ValueError(
            f"Cannot delete mentor '{mentor.name}' because {bookings_count} historical "
            f"booking(s) exist. Deactivate the mentor instead."
        )

    db.delete(mentor)
    db.commit()
    return True


def get_admin_parents(db: Session) -> list[ParentAdminResponse]:
    """List registered parents with their total booking count."""
    parents = db.query(Parent).order_by(Parent.id.asc()).all()

    counts = dict(
        db.query(Booking.parent_id, func.count(Booking.id))
        .filter(Booking.status == "confirmed")
        .group_by(Booking.parent_id)
        .all()
    )

    return [
        ParentAdminResponse(
            id=p.id,
            name=p.name,
            email=p.email,
            created_at=p.created_at,
            bookings_count=counts.get(p.id, 0),
        )
        for p in parents
    ]


def get_parent_bookings(db: Session, parent_id: int) -> list[ParentBookingDetail]:
    """Retrieve bookings for a parent."""
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise ValueError(f"Parent with ID {parent_id} not found.")

    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.mentor))
        .filter(Booking.parent_id == parent_id)
        .order_by(Booking.slot_utc.desc())
        .all()
    )

    result = []
    for b in bookings:
        tz = ZoneInfo(b.parent_timezone)
        local_dt = b.slot_utc.astimezone(tz)
        local_end = local_dt + timedelta(hours=1)
        local_str = f"{local_dt.strftime('%b %d, %Y')} at {local_dt.strftime('%I:%M %p')} – {local_end.strftime('%I:%M %p')} ({b.parent_timezone})"

        result.append(
            ParentBookingDetail(
                id=b.id,
                child_name=b.child_name,
                mentor_id=b.mentor_id,
                mentor_name=b.mentor.name if b.mentor else "Assigned Mentor",
                slot_utc=b.slot_utc,
                local_display=local_str,
                status=b.status,
                class_link=b.class_link,
                created_at=b.created_at,
            )
        )
    return result


def get_admin_bookings(db: Session) -> list[AdminBookingResponse]:
    """
    List all confirmed bookings with dual timezone conversion (Parent local and Mentor IST).
    """
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.parent), joinedload(Booking.mentor))
        .order_by(Booking.slot_utc.desc())
        .all()
    )

    items = []
    for b in bookings:
        # Parent local time
        try:
            p_tz = ZoneInfo(b.parent_timezone)
            p_dt = b.slot_utc.astimezone(p_tz)
            p_end = p_dt + timedelta(hours=1)
            p_str = f"{p_dt.strftime('%a, %b %d, %Y')} at {p_dt.strftime('%I:%M %p')} – {p_end.strftime('%I:%M %p')} ({b.parent_timezone})"
        except Exception:
            p_str = b.slot_utc.isoformat()

        # Mentor IST time
        m_dt = b.slot_utc.astimezone(_IST)
        m_end = m_dt + timedelta(hours=1)
        m_str = f"{m_dt.strftime('%a, %b %d, %Y')} at {m_dt.strftime('%I:%M %p')} – {m_end.strftime('%I:%M %p')} IST"

        items.append(
            AdminBookingResponse(
                id=b.id,
                parent_id=b.parent_id,
                parent_name=b.parent.name if b.parent else b.parent_name,
                parent_email=b.parent.email if b.parent else b.parent_email,
                child_name=b.child_name,
                mentor_id=b.mentor_id,
                mentor_name=b.mentor.name if b.mentor else "Assigned Mentor",
                slot_utc=b.slot_utc,
                parent_timezone=b.parent_timezone,
                parent_local_time=p_str,
                mentor_ist_time=m_str,
                status=b.status,
                class_link=b.class_link,
                created_at=b.created_at,
            )
        )
    return items


def get_mentor_schedule(db: Session, mentor_id: int) -> list[MentorScheduleItem]:
    """
    Retrieve assigned classes for a mentor formatted in India Standard Time.
    """
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise ValueError(f"Mentor with ID {mentor_id} not found.")

    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.parent))
        .filter(Booking.mentor_id == mentor_id, Booking.status == "confirmed")
        .order_by(Booking.slot_utc.asc())
        .all()
    )

    items = []
    for b in bookings:
        m_dt = b.slot_utc.astimezone(_IST)
        m_end = m_dt + timedelta(hours=1)
        date_str = m_dt.strftime("%a, %b %d, %Y")
        time_str = f"{m_dt.strftime('%I:%M %p')} – {m_end.strftime('%I:%M %p')} IST"

        items.append(
            MentorScheduleItem(
                id=b.id,
                student_name=b.child_name,
                parent_name=b.parent.name if b.parent else b.parent_name,
                parent_email=b.parent.email if b.parent else b.parent_email,
                slot_utc=b.slot_utc,
                class_date_ist=date_str,
                class_time_ist=time_str,
                class_link=b.class_link,
                status=b.status,
            )
        )
    return items
