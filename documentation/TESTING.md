# Testing

## Verified Result

On 2026-09-27, `python -m pytest` from `backend/` collected 53 tests and completed with **53 passed**. The run emitted five warnings: pytest-asyncio configuration deprecation, Starlette multipart deprecation, and four SQLAlchemy isolation-option warnings. `npm run build` succeeded. `npm run lint` exited successfully with one unused catch-parameter warning in `src/pages/BookingPage.jsx`.

## Test Areas

| Area | Evidence |
|---|---|
| Unit/service | Timezone, parent, email, course, admin, and booking-service modules are covered. |
| API | Admin and course tests use FastAPI `TestClient`; service tests cover booking behavior. |
| Booking/allocation | Valid and invalid course, parent creation, active mentor filtering, assignment integrity, and unique mentor-slot constraint are tested. |
| Timezone/DST | IST conversion, IANA validation, US EST/EDT, UK GMT/BST, and date boundaries are tested. |
| Concurrency | Retry handling exists, but a dedicated concurrent multi-request test is not visible: To be verified. |
| Email | Formatting, dual recipients, console dispatch, SMTP configuration, commit-before-notification, failure resilience, and resend overrides are tested. |
| Admin | Metrics, capacity, mentor lifecycle, parent history, booking visibility, and mentor schedule are tested. |
| Frontend | Lint and production build were run; no automated browser suite is present. |

Important edge cases covered by code/tests include invalid timezone, malformed/stale slot, past/date-window boundaries, exact-slot conflict, two-class IST capacity, no mentor available, US/UK conversion and DST, inactive/invalid course, and post-commit email failure. Dedicated concurrency and visual/browser verification are To be verified.
