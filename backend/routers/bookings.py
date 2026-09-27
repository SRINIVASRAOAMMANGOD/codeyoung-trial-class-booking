"""
routers/bookings.py — Booking API endpoints.

Exposes:
  - POST /api/v1/bookings — create a new trial class booking.
  - GET /api/v1/bookings/{id} — retrieve a confirmed booking by ID.
  - GET /api/v1/mentor/bookings — retrieve mentor bookings (optional mentor_id filter).

Thin HTTP layer:
  - Validates request payloads and slot constraints (in-memory, before DB access).
  - Delegates business logic and transaction management to services/booking_service.py.
  - Translates domain exceptions to HTTP status codes (201, 404, 409, 422, 503).
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.booking import BookingCreate, BookingResponse
from services.booking_service import (
    BookingConflictError,
    BookingValidationError,
    ConcurrencyError,
    create_booking,
    get_booking_by_id,
    get_mentor_bookings,
)
from services.timezone_service import (
    SLOT_HOURS_IST,
    get_ist_date_today,
    validate_timezone,
)

_IST = ZoneInfo("Asia/Kolkata")

router = APIRouter(tags=["Bookings"])


def _validate_slot_rules(slot_utc: datetime) -> None:
    """
    Validate that slot_utc aligns with the canonical 1-hour trial class slots:
      1. Must be timezone-aware and in UTC (offset 0).
      2. Must be on the exact hour (:00:00).
      3. Hour in IST must fall within the 15:00–21:00 IST daily window.
      4. Date in IST must fall within the bookable window (tomorrow through tomorrow+6).
    """
    if slot_utc.tzinfo is None or slot_utc.utcoffset() is None or slot_utc.utcoffset().total_seconds() != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="slot_utc must be a timezone-aware UTC datetime (offset +00:00).",
        )

    ist_dt = slot_utc.astimezone(_IST)
    if ist_dt.minute != 0 or ist_dt.second != 0 or ist_dt.microsecond != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="slot_utc must be on the top of an hour (e.g. :00:00).",
        )

    if ist_dt.hour not in SLOT_HOURS_IST:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"slot_utc hour in IST ({ist_dt.hour:02d}:00) is outside the daily "
                f"booking window (15:00–21:00 IST)."
            ),
        )

    today_ist = get_ist_date_today()
    min_date = today_ist + timedelta(days=1)
    max_date = today_ist + timedelta(days=7)
    slot_date = ist_dt.date()

    if slot_date < min_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"slot_utc date ({slot_date}) must be tomorrow or later (IST). "
                f"Earliest bookable date: {min_date.isoformat()}."
            ),
        )
    if slot_date > max_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"slot_utc date ({slot_date}) is too far in the future. "
                f"Latest bookable date: {max_date.isoformat()}."
            ),
        )


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trial class booking",
    description="Validates slot selection, automatically assigns an available mentor, and confirms the booking.",
)
def create_new_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
) -> BookingResponse:
    # 1. Validate parent timezone (in-memory)
    if not validate_timezone(booking_in.parent_timezone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid timezone: '{booking_in.parent_timezone}'. Use a valid IANA timezone identifier.",
        )

    # 2. Validate slot rules (in-memory, NO database queries before SERIALIZABLE transaction)
    _validate_slot_rules(booking_in.slot_utc)

    # 3. Delegate to booking service
    try:
        booking = create_booking(db=db, booking_in=booking_in)
        return booking
    except BookingValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except BookingConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ConcurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/bookings/{id}",
    response_model=BookingResponse,
    summary="Get booking by ID",
    description="Retrieve a confirmed booking by its primary key ID.",
)
def get_booking(
    id: int,
    db: Session = Depends(get_db),
) -> BookingResponse:
    booking = get_booking_by_id(db=db, booking_id=id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {id} not found.",
        )
    return booking


@router.get(
    "/mentor/bookings",
    response_model=list[BookingResponse],
    summary="Get mentor bookings",
    description="Retrieve confirmed trial class bookings for mentors, optionally filtered by mentor ID.",
)
def list_mentor_bookings(
    mentor_id: int | None = Query(
        None,
        description="Optional mentor ID to filter bookings.",
    ),
    db: Session = Depends(get_db),
) -> list[BookingResponse]:
    return get_mentor_bookings(db=db, mentor_id=mentor_id)
