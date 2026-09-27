"""
models/booking.py — Booking ORM model.

A Booking represents a confirmed trial class appointment between a parent
and a mentor. It is created when a parent selects a slot and the system
successfully assigns an available mentor.

Key design decisions:
- parent_id links to the Parent entity (Foreign Key -> parents.id ON DELETE RESTRICT).
- mentor_id links to the Mentor entity (Foreign Key -> mentors.id ON DELETE RESTRICT).
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

    # Associated parent (normalized)
    parent_id = Column(
        Integer,
        ForeignKey("parents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    child_name = Column(String(100), nullable=False)

    # IANA timezone string for the parent (e.g. "America/New_York").
    # Used to display slot_utc back in the parent's local time.
    parent_timezone = Column(String(50), nullable=False)

    # Canonical UTC appointment time.
    # DateTime(timezone=True) maps to TIMESTAMPTZ in PostgreSQL.
    # This is the single source of truth for when the class occurs.
    slot_utc = Column(DateTime(timezone=True), nullable=False)

    # Assigned mentor
    mentor_id = Column(
        Integer,
        ForeignKey("mentors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Selected course
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

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

    # ORM relationships
    parent = relationship("Parent", back_populates="bookings")
    mentor = relationship("Mentor", back_populates="bookings")
    course = relationship("Course", back_populates="bookings")

    # Backward-compatibility accessors for Pydantic serialization
    @property
    def parent_name(self) -> str:
        return self.parent.name if self.parent else ""

    @property
    def parent_email(self) -> str:
        return self.parent.email if self.parent else ""

    @property
    def course_name(self) -> str:
        return self.course.name if self.course else ""

    __table_args__ = (
        # Double-booking guard
        UniqueConstraint("mentor_id", "slot_utc", name="uq_mentor_slot_utc"),
    )

    def __repr__(self) -> str:
        return (
            f"<Booking id={self.id} parent_id={self.parent_id} mentor_id={self.mentor_id} course_id={self.course_id} "
            f"slot_utc={self.slot_utc!r} status={self.status!r}>"
        )
