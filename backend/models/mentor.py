"""
models/mentor.py — Mentor ORM model.

A Mentor is a Codeyoung instructor who conducts trial classes.
Mentors are pre-seeded; they do not log in via this application.

The `is_active` flag allows soft-disabling a mentor (e.g. if they go
on leave) without deleting their historical booking records.
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    # Email is used as the natural unique identifier for mentors.
    # It also makes the seed script idempotent: we check by email
    # before inserting to avoid duplicate rows.
    email = Column(String(150), nullable=False, unique=True)

    # IANA timezone identifier. All current mentors are in Asia/Kolkata.
    # Stored as a field (not hardcoded) so it can vary per mentor in future.
    timezone = Column(String(50), nullable=False, default="Asia/Kolkata")

    # Soft-delete flag. Inactive mentors are excluded from slot availability
    # queries but their past booking records are preserved.
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship: convenient access to a mentor's bookings.
    # `lazy="select"` means bookings are loaded only when accessed.
    # `back_populates` links to Booking.mentor.
    bookings = relationship("Booking", back_populates="mentor", lazy="select")

    def __repr__(self) -> str:
        return f"<Mentor id={self.id} name={self.name!r} email={self.email!r}>"
