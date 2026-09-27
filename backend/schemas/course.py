"""
schemas/course.py — Pydantic models for courses.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    age_range: str
    level: str
    is_active: bool
    created_at: datetime
