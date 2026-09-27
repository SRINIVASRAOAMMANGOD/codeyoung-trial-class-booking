# Project Status

## Current Implementation

The repository contains a highly functional recruitment-assessment demonstration. It features public landing/booking views, course selection from a dynamic catalogue, timezone-aware slot rendering, automatic and deterministic mentor allocation, email notification dispatching, staff/admin views, comprehensive mentor management, parent history tracking, dynamic course management (CRUD), and email resend functionality.

## Architecture and Files

The frontend leverages React and Vite, communicating via REST to a FastAPI backend. Backend routers delegate purely to service modules, which orchestrate business rules using SQLAlchemy models and a PostgreSQL database. Scheduling uses IST anchors, UTC canonical timestamps, and IANA timezone conversions. Important structural areas include `backend/main.py`, `backend/routers/`, `backend/services/`, `backend/models/`, `backend/db/`, `frontend/src/App.jsx`, and `frontend/src/pages/`. Refer to [ARCHITECTURE.md](ARCHITECTURE.md) for deeper details.

## Database and API

SQLAlchemy Models define `parents`, `mentors`, `courses`, and `bookings`. The schema enforces normalized parent identities, restrictive foreign keys, and a strict unique mentor-slot constraint. Schema creation utilizes `create_all()` plus explicit scripts for seeding courses and mentors. The API encompasses health, active course listings, available slot calculations, booking orchestration, mentor assignment, comprehensive admin views, and operational metrics. Refer to [DATABASE.md](DATABASE.md) and [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Testing Status

On the latest verified execution:
- **Backend**: `pytest` reported 71 passed, 0 failed, 0 skipped, and 11 warnings (primarily deprecation and SQLAlchemy isolation configuration warnings).
- **Frontend**: The Vite production build succeeded. The linter exited successfully with only one documented warning (an unused catch parameter in `BookingPage.jsx`).

No coverage percentage or automated browser/puppeteer integration is claimed for this assessment baseline.

## Known Limitations

Explicitly omitted for this demonstration: production authentication and RBAC, real video integration, payment processing, calendar sync integrations, Alembic schema migrations, and production deployment configuration. Classroom links are generated dummy UUID URLs. Email relies on console simulation unless SMTP is actively configured in the environment.

## Assumptions and Remaining Work

Product/Engineering assumptions: Slots are one hour long, anchored between 15:00-21:00 IST, and bookable strictly from tomorrow through seven days ahead in IST. Daily mentor capacity is tightly capped at two confirmed classes per IST calendar date; total theoretical admin capacity is active mentors multiplied by two. 
