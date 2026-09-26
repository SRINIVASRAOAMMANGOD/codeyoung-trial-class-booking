"""
models/booking.py — Booking ORM model.

A Booking represents a confirmed trial class appointment between a parent
and a mentor. It is created when a parent selects a slot and the system
successfully assigns an available mentor.

Key design decisions:
- slot_utc (TIMESTAMPTZ) is the canonical appointment time. All timezone
  conversions happen at the application layer; the DB stores only UTC.
- class_link is a dummy URL generated at booking time and is the same
  link available to both parent (via confirmation screen) and mentor
  (via the mentor bookings endpoint).
- status defaults to 'confirmed'; reserved for future cancellation support.
"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Parent information
    parent_name = Column(String(100), nullable=False)
    parent_email = Column(String(150), nullable=False)
    child_name = Column(String(100), nullable=False)

    # IANA timezone string for the parent (e.g. "America/New_York").
    # Used to display slot_utc back in the parent's local time.
    parent_timezone = Column(String(50), nullable=False)

    # Canonical UTC appointment time.
    # DateTime(timezone=True) maps to TIMESTAMPTZ in PostgreSQL.
    # This is the single source of truth for when the class occurs.
    slot_utc = Column(DateTime(timezone=True), nullable=False)

    # Assigned mentor
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)

    # Dummy class link shown to both parent and mentor.
    # Format: https://class.codeyoung.com/room/<uuid4>
    class_link = Column(String(255), nullable=False)

    # 'confirmed' by default; supports future 'cancelled' state.
    status = Column(String(20), nullable=False, default="confirmed")

    # Audit timestamp — when the booking was created.
    # server_default=func.now() lets PostgreSQL set this, not Python.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ORM relationship: access booking.mentor to get the Mentor object.
    mentor = relationship("Mentor", back_populates="bookings")

    __table_args__ = (
        # PRIMARY constraint: one mentor cannot be assigned to the same
        # UTC slot twice. This is the database-level double-booking guard.
        # The application layer (SERIALIZABLE transactions) handles the
        # daily cap; this constraint is the final hard guarantee.
        UniqueConstraint("mentor_id", "slot_utc", name="uq_mentor_slot_utc"),
    )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} mentor_id={self.mentor_id} "
            f"slot_utc={self.slot_utc!r} status={self.status!r}>"
        )
