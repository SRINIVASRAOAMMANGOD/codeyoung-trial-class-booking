"""
routers/slots.py — GET /api/v1/slots endpoint.

Returns available trial class slots for a given date and parent timezone.
This router only handles HTTP concerns: parsing query params, validation,
calling the slot service, and returning the response.
All business logic lives in services/slot_service.py.
"""

from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.slots import SlotItem, SlotsResponse
from services.slot_service import get_available_slots
from services.timezone_service import get_ist_date_today, validate_timezone

router = APIRouter(tags=["Slots"])


@router.get(
    "/slots",
    response_model=SlotsResponse,
    summary="Get available trial class slots",
    description=(
        "Returns available 1-hour slots for the given IST date. "
        "Each slot includes a UTC ISO string (to use when booking) "
        "and a localised display string in the parent's timezone."
    ),
)
def list_available_slots(
    date: str = Query(
        ...,
        description="Date in YYYY-MM-DD format (interpreted as an IST calendar date).",
        examples=["2024-12-10"],
    ),
    timezone: str = Query(
        ...,
        description="IANA timezone identifier for the parent's local display.",
        examples=["America/New_York"],
    ),
    db: Session = Depends(get_db),
) -> SlotsResponse:
    # --- Validate timezone ---
    if not validate_timezone(timezone):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid timezone: '{timezone}'. Use an IANA identifier such as 'America/New_York'.",
        )

    # --- Parse and validate date ---
    # 'date' shadows the built-in; we use date_type imported as an alias.
    try:
        requested_date: date_type = date_type.fromisoformat(date)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format: '{date}'. Use YYYY-MM-DD.",
        )

    # --- Enforce booking window: tomorrow through tomorrow+6 (IST) ---
    # Product decision: same-day booking is excluded to avoid past-slot issues.
    today_ist: date_type = get_ist_date_today()
    min_date: date_type = today_ist + timedelta(days=1)
    max_date: date_type = today_ist + timedelta(days=7)

    if requested_date < min_date:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Date must be tomorrow or later (IST). "
                f"Earliest bookable date: {min_date.isoformat()}."
            ),
        )
    if requested_date > max_date:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Date is too far in the future. "
                f"Latest bookable date: {max_date.isoformat()}."
            ),
        )

    # --- Fetch available slots from the service layer ---
    slot_dicts = get_available_slots(
        ist_date=requested_date,
        parent_tz=timezone,
        db=db,
    )

    return SlotsResponse(
        date=str(requested_date),
        timezone=timezone,
        slots=[SlotItem(**s) for s in slot_dicts],
    )
