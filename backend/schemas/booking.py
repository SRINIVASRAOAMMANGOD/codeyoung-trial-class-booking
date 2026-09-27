"""
schemas/booking.py — Pydantic models for the booking API.

BookingCreate represents the incoming payload from a parent to book a slot.
BookingResponse represents the full booking record returned by the API.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    # Parent & child details
    parent_name: str
    parent_email: str
    child_name: str
    course_id: int

    # IANA timezone string for the parent (e.g. "America/New_York").
    # Business validation against valid IANA timezones is handled at the
    # service/router layer to avoid duplicating logic in the schema.
    parent_timezone: str

    # Canonical UTC booking time (ISO 8601 UTC string submitted from slot picker).
    slot_utc: datetime


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_name: str
    parent_email: str
    child_name: str
    course_id: int
    course_name: str
    parent_timezone: str
    slot_utc: datetime
    mentor_id: int
    class_link: str
    status: str
    created_at: datetime
