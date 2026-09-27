# API Documentation

Base prefix: `/api/v1`. FastAPI generated OpenAPI documentation is available at `/docs` when running.

## Public Routes

| Method | Path | Request | Response / errors |
|---|---|---|---|
| GET | `/health` | None | `{status, env}`. |
| GET | `/courses` | None | Active courses with `id`, `name`, `description`, `is_active`, `created_at`. |
| GET | `/slots` | Query `date=YYYY-MM-DD`, `timezone=<IANA>` | `{date, timezone, slots[]}`; each slot has `utc_iso` and `local_display`. 422 for invalid values or dates outside tomorrow through tomorrow+7 IST. |
| POST | `/bookings` | JSON: `parent_name`, `parent_email`, `child_name`, `course_id`, `parent_timezone`, `slot_utc` | 201 booking with parent, course, mentor, UTC slot, status, link, and creation time. 422 invalid input/course/slot; 409 no mentor; 503 repeated concurrency failure. |
| GET | `/bookings/{id}` | Integer path ID | Booking response, or 404. |
| GET | `/mentor/bookings` | Optional `mentor_id` query | Confirmed bookings, optionally filtered by mentor. |

Booking slots must be timezone-aware UTC timestamps, on `:00:00`, within 15:00-21:00 IST, and within the seven-day future window. `course_id` must identify an active course.

## Admin and Mentor Routes

| Method | Path | Request | Response / errors |
|---|---|---|---|
| GET | `/admin/overview` | None | Counts, today's IST classes, theoretical capacity, remaining capacity. |
| GET | `/admin/mentors` | None | All mentors with status and today's `0/2`-style load. |
| POST | `/admin/mentors` | JSON `name`, `email`, optional `timezone` | 201 mentor; 409 duplicate email; 422 validation. |
| PATCH | `/admin/mentors/{id}` | Any of `name`, `email`, `timezone`, `is_active` | Updated mentor; 404, 409, or 422 as applicable. |
| PATCH | `/admin/mentors/{id}/status` | `{is_active: boolean}` | Updated mentor or 404. |
| DELETE | `/admin/mentors/{id}` | None | Delete result; 404 missing; 400 if bookings exist. |
| GET | `/admin/parents` | None | Parent directory with confirmed booking counts. |
| GET | `/admin/parents/{id}/bookings` | Integer parent ID | Parent booking history or 404. |
| GET | `/admin/bookings` | None | Confirmed registry with parent-local and mentor-IST times. |
| GET | `/admin/mentors/{id}/schedule` | Integer mentor ID | Confirmed schedule in IST or 404. |
| POST | `/admin/bookings/{id}/resend-email` | `recipient_email`, `recipient_type` (`parent`/`mentor`), optional `custom_subject` | Success message and recipient; delivery failure is 500. |

Internal routes have no authentication or RBAC in the current implementation.
