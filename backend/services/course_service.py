"""
services/course_service.py — Business logic for courses.
"""

from sqlalchemy.orm import Session
from typing import List

from models.course import Course


def get_active_courses(db: Session) -> List[Course]:
    """
    Returns all active courses ordered by ID.
    """
    return db.query(Course).filter(Course.is_active == True).order_by(Course.id).all()
