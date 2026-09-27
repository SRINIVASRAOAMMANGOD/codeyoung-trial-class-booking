# Project Status

## Current Implementation

The repository contains a functional recruitment-assessment demonstration with public landing/booking views, course selection, timezone-aware slots, automatic mentor allocation, email notification, staff/admin views, mentor management, parent history, and email resend.

## Architecture and Files

React/Vite calls FastAPI. Routers delegate to services, which use SQLAlchemy models and PostgreSQL. Scheduling uses IST anchors, UTC timestamps, and IANA conversion. Important areas are `backend/main.py`, `backend/routers/`, `backend/services/`, `backend/models/`, `backend/db/`, `frontend/src/App.jsx`, and `frontend/src/pages/`. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Database and API

Models define `parents`, `mentors`, `courses`, and `bookings`, with foreign keys, indexes, normalized parent identity, and a unique mentor-slot constraint. Schema creation uses `create_all()` plus explicit scripts rather than Alembic. The API includes health, course, slot, booking, mentor, admin, parent, and resend-email routes. See [DATABASE.md](DATABASE.md) and [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Testing Status

Verified on 2026-09-27: backend pytest reported 53 passed and 5 warnings; frontend build succeeded; frontend lint exited successfully with one warning. No coverage percentage or browser automation result is claimed. A dedicated concurrent multi-request test and visual/browser verification are To be verified.

## Known Limitations

No authentication/RBAC, real video integration, payment, calendar sync, Alembic, or production deployment configuration. Classroom links are dummy URLs. Email is console simulation unless SMTP is configured. The actual AI session transcript is not present in this repository.

## Assumptions and Remaining Work

Slots are one hour, anchored at 15:00-21:00 IST, and bookable from tomorrow through seven days ahead in IST. Daily mentor capacity is two confirmed classes; admin capacity is active mentors times two. Before submission, import the real transcript, add only available screenshots/video, and confirm deployment/remote repository details if required. Optional further verification is dedicated concurrent integration coverage and browser testing.
