"""
routers/admin.py — Internal operational administration and mentor portal endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.admin import (
    AdminBookingResponse,
    AdminOverviewResponse,
    CourseAdminResponse,
    CourseCreateRequest,
    CourseStatusUpdateRequest,
    CourseUpdateRequest,
    MentorAdminResponse,
    MentorCreateRequest,
    MentorUpdateRequest,
    MentorScheduleItem,
    MentorStatusUpdateRequest,
    ParentAdminResponse,
    ParentAdminResponse,
    ParentBookingDetail,
    ResendEmailRequest,
)
from services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/overview",
    response_model=AdminOverviewResponse,
    summary="Get operational capacity and statistics overview",
)
def get_overview(db: Session = Depends(get_db)) -> AdminOverviewResponse:
    return admin_service.get_admin_overview(db)


@router.get(
    "/mentors",
    response_model=list[MentorAdminResponse],
    summary="List all mentors with real-time today's load",
)
def list_mentors(db: Session = Depends(get_db)) -> list[MentorAdminResponse]:
    return admin_service.get_admin_mentors(db)


@router.get("/courses", response_model=list[CourseAdminResponse], summary="List all courses")
def list_courses(db: Session = Depends(get_db)) -> list[CourseAdminResponse]:
    return admin_service.get_admin_courses(db)


@router.post(
    "/courses",
    response_model=CourseAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course",
)
def add_course(course_in: CourseCreateRequest, db: Session = Depends(get_db)) -> CourseAdminResponse:
    try:
        return admin_service.create_course(db, course_in)
    except ValueError as exc:
        message = str(exc)
        if "already exists" in message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message) from exc


@router.patch("/courses/{id}", response_model=CourseAdminResponse, summary="Update a course")
def edit_course(
    id: int,
    course_in: CourseUpdateRequest,
    db: Session = Depends(get_db),
) -> CourseAdminResponse:
    try:
        return admin_service.update_course(db, id, course_in)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        if "already exists" in message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message) from exc


@router.patch(
    "/courses/{id}/status",
    response_model=CourseAdminResponse,
    summary="Activate or deactivate a course",
)
def set_course_status(
    id: int,
    status_in: CourseStatusUpdateRequest,
    db: Session = Depends(get_db),
) -> CourseAdminResponse:
    course = admin_service.update_course_status(db, id, status_in.is_active)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {id} not found.",
        )
    return course


@router.post(
    "/mentors",
    response_model=MentorAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new mentor",
)
def add_mentor(
    mentor_in: MentorCreateRequest,
    db: Session = Depends(get_db),
) -> MentorAdminResponse:
    try:
        mentor = admin_service.create_mentor(db, mentor_in)
        # Return populated response with 0 classes today
        return MentorAdminResponse(
            id=mentor.id,
            name=mentor.name,
            email=mentor.email,
            timezone=mentor.timezone,
            is_active=mentor.is_active,
            today_classes=0,
            capacity_label="0/2",
            is_full_today=False,
            upcoming_capacity=[],
        )
    except ValueError as exc:
        msg = str(exc)
        if "already exists" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc


@router.patch(
    "/mentors/{id}",
    response_model=MentorAdminResponse,
    summary="Update mentor details",
)
def edit_mentor(
    id: int,
    mentor_in: MentorUpdateRequest,
    db: Session = Depends(get_db),
) -> MentorAdminResponse:
    try:
        mentor = admin_service.update_mentor(db, id, mentor_in)
        # Fetch full populated representation
        mentors = admin_service.get_admin_mentors(db)
        matched = next((m for m in mentors if m.id == id), None)
        if not matched:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found after update.")
        return matched
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        if "already exists" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc


@router.patch(
    "/mentors/{id}/status",
    response_model=MentorAdminResponse,
    summary="Activate or deactivate a mentor",
)
def set_mentor_status(
    id: int,
    status_in: MentorStatusUpdateRequest,
    db: Session = Depends(get_db),
) -> MentorAdminResponse:
    mentor = admin_service.update_mentor_status(db, id, status_in.is_active)
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mentor with ID {id} not found.")

    mentors = admin_service.get_admin_mentors(db)
    matched = next((m for m in mentors if m.id == id), None)
    if not matched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found.")
    return matched


@router.delete(
    "/mentors/{id}",
    summary="Delete a mentor if zero bookings exist",
)
def remove_mentor(
    id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = admin_service.delete_mentor(db, id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mentor with ID {id} not found.")
        return {"message": "Mentor deleted successfully.", "id": id}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/parents",
    response_model=list[ParentAdminResponse],
    summary="List all registered parents with booking counts",
)
def list_parents(db: Session = Depends(get_db)) -> list[ParentAdminResponse]:
    return admin_service.get_admin_parents(db)


@router.get(
    "/parents/{id}/bookings",
    response_model=list[ParentBookingDetail],
    summary="Get all bookings for a specific parent",
)
def get_parent_bookings(
    id: int,
    db: Session = Depends(get_db),
) -> list[ParentBookingDetail]:
    try:
        return admin_service.get_parent_bookings(db, id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/bookings",
    response_model=list[AdminBookingResponse],
    summary="List all confirmed bookings with dual timezone formatting",
)
def list_all_bookings(db: Session = Depends(get_db)) -> list[AdminBookingResponse]:
    return admin_service.get_admin_bookings(db)


@router.get(
    "/mentors/{id}/schedule",
    response_model=list[MentorScheduleItem],
    summary="Get mentor internal schedule in IST",
)
def get_mentor_schedule(
    id: int,
    db: Session = Depends(get_db),
) -> list[MentorScheduleItem]:
    try:
        return admin_service.get_mentor_schedule(db, id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

@router.post(
    "/bookings/{id}/resend-email",
    summary="Resend booking email to parent or mentor",
)
def resend_booking_email(
    id: int,
    req: ResendEmailRequest,
    db: Session = Depends(get_db),
):
    try:
        return admin_service.resend_booking_email(db, id, req)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {exc}") from exc
