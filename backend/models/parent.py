"""
models/parent.py — Parent ORM model.

A Parent represents the customer who books trial classes for their children.
Each Parent is uniquely identified by email and can have multiple Bookings.
"""

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)

    # Parent's full name
    name = Column(String(100), nullable=False)

    # Natural unique identifier for a parent account.
    email = Column(String(150), nullable=False, unique=True, index=True)

    # When the parent record was first created
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # 1-to-many relationship: one parent can have multiple bookings
    bookings = relationship(
        "Booking",
        back_populates="parent",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Parent id={self.id} name={self.name!r} email={self.email!r}>"
