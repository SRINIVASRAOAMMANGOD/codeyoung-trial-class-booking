"""
schemas/slots.py — Pydantic models for the slots API.

SlotItem represents one available 1-hour slot.
SlotsResponse is the full response from GET /api/v1/slots.
"""

from pydantic import BaseModel


class SlotItem(BaseModel):
    # ISO 8601 UTC string, e.g. "2024-12-10T09:30:00+00:00"
    # This is what the frontend sends back to POST /bookings.
    utc_iso: str

    # ISO 8601 string in the parent's local timezone, e.g. "2024-12-10T04:30:00-05:00"
    # Used only for display. Never re-parsed by the backend.
    local_display: str


class SlotsResponse(BaseModel):
    date: str       # The IST date requested, e.g. "2024-12-10"
    timezone: str   # The parent timezone used for local_display, e.g. "America/New_York"
    slots: list[SlotItem]  # Empty list means no mentors available for this date
