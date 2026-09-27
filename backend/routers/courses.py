"""
routers/courses.py — API endpoints for courses.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.course import CourseResponse
from services import course_service

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    """
    Fetch all active courses available for trial booking.
    """
    return course_service.get_active_courses(db)
