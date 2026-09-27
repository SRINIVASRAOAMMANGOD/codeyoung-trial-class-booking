"""
models/course.py — Course ORM model.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    age_range = Column(String(50), nullable=False, default="All Ages")
    level = Column(String(50), nullable=False, default="All Levels")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    bookings = relationship("Booking", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course id={self.id} name={self.name!r} active={self.is_active}>"
