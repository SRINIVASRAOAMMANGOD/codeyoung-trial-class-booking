"""
schemas/admin.py — Pydantic models for admin operational management and mentor view.
"""

from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AdminOverviewResponse(BaseModel):
    total_mentors: int
    active_mentors: int
    total_parents: int
    total_bookings: int
    today_classes: int
    theoretical_capacity: int
    remaining_capacity: int


class MentorAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    timezone: str
    is_active: bool
    today_classes: int
    capacity_label: str
    is_full_today: bool


class MentorCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    timezone: str = "Asia/Kolkata"

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        # Standard email regex pattern
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError(f"Invalid email format: '{v}'")
        return clean


class MentorStatusUpdateRequest(BaseModel):
    is_active: bool


class ParentAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime
    bookings_count: int


class ParentBookingDetail(BaseModel):
    id: int
    child_name: str
    course_name: str
    mentor_id: int
    mentor_name: str
    slot_utc: datetime
    local_display: str
    status: str
    class_link: str
    created_at: datetime


class AdminBookingResponse(BaseModel):
    id: int
    parent_id: int
    parent_name: str
    parent_email: str
    child_name: str
    course_name: str
    mentor_id: int
    mentor_name: str
    slot_utc: datetime
    parent_timezone: str
    parent_local_time: str
    mentor_ist_time: str
    status: str
    class_link: str
    created_at: datetime


class MentorScheduleItem(BaseModel):
    id: int
    student_name: str
    course_name: str
    parent_name: str
    parent_email: str
    slot_utc: datetime
    class_date_ist: str
    class_time_ist: str
    class_link: str
    status: str

class ResendEmailRequest(BaseModel):
    recipient_email: str
    recipient_type: str = Field(..., description="Either 'parent' or 'mentor'")
    custom_subject: str | None = None
