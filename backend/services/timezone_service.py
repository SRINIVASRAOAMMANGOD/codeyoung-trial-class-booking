"""
services/timezone_service.py — Timezone conversion utilities.

All timezone operations go through this module.
No manual UTC offset arithmetic is used anywhere.
Python's zoneinfo (stdlib, 3.9+) applies IANA rules including DST automatically.

Key design:
- Slots are anchored in IST (Asia/Kolkata), which has no DST.
- IST anchors are converted to UTC (unambiguous).
- UTC is converted to the parent's display timezone for the UI.
- The backend stores and operates on UTC only.
- Because we always go IST → UTC → parent_tz (never parent_tz → UTC),
  nonexistent or ambiguous parent local times never arise.
"""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Module-level zone singletons — ZoneInfo objects are reusable.
_IST = ZoneInfo("Asia/Kolkata")
_UTC = timezone.utc

# The 7 bookable hour-anchors in IST (15:00 through 21:00 inclusive).
# This is a product decision: covers UK daytime and US East Coast morning
# while keeping mentor hours within a reasonable India evening window.
SLOT_HOURS_IST: list[int] = [15, 16, 17, 18, 19, 20, 21]


def validate_timezone(tz_str: str) -> bool:
    """
    Return True if tz_str is a valid IANA timezone identifier.
    Catches all exceptions raised by zoneinfo for invalid inputs:
      - ZoneInfoNotFoundError: unrecognised timezone name
      - KeyError: some invalid key formats
      - ValueError: empty string or non-normalised path
    """
    try:
        ZoneInfo(tz_str)
        return True
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        return False


def get_ist_date_today() -> date:
    """Return the current calendar date in IST (Asia/Kolkata)."""
    return datetime.now(_IST).date()


def generate_ist_anchors(ist_date: date) -> list[datetime]:
    """
    Generate timezone-aware IST datetimes for the 7 bookable slots
    on the given IST calendar date.

    Returns a list of 7 datetimes, each anchored to Asia/Kolkata.
    Because IST has no DST, these conversions are always unambiguous.
    """
    anchors = []
    for hour in SLOT_HOURS_IST:
        dt = datetime(
            ist_date.year,
            ist_date.month,
            ist_date.day,
            hour,
            0,
            0,
            tzinfo=_IST,
        )
        anchors.append(dt)
    return anchors


def ist_anchor_to_utc(ist_dt: datetime) -> datetime:
    """
    Convert an IST-anchored datetime to UTC.
    IST is always UTC+5:30, so this is a fixed 5h30m subtraction,
    but we use zoneinfo to keep the operation consistent and explicit.
    """
    return ist_dt.astimezone(_UTC)


def utc_to_local_display(utc_dt: datetime, tz_str: str) -> datetime:
    """
    Convert a UTC datetime to the given IANA timezone for display.
    DST offsets are applied automatically by zoneinfo.

    Args:
        utc_dt:  A UTC-aware datetime (from ist_anchor_to_utc).
        tz_str:  IANA timezone identifier, e.g. "America/New_York".

    Returns:
        A timezone-aware datetime in the target zone.
    """
    return utc_dt.astimezone(ZoneInfo(tz_str))
