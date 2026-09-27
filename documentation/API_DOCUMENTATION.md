# API Documentation

Base prefix for application routes: `/api/v1` (with the exception of the root health check). FastAPI's interactive OpenAPI documentation is automatically generated and available at `/docs` when the backend is running.

## Health

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| GET | `/health` | None | `{status: "ok", environment: "development"}` |

## Courses

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| GET | `/api/v1/courses` | None | Returns a list of active courses containing `id`, `name`, `description`, `age_range`, `level`, `is_active`, and `created_at`. |

## Slots

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| GET | `/api/v1/slots` | Query: `date=YYYY-MM-DD`, `timezone=<IANA>` | Returns `{date, timezone, slots[]}` where each slot object contains `utc_iso` and `local_display`. Returns 422 if parameters are invalid or if the date falls outside the tomorrow through tomorrow+7 IST window. |

## Bookings

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| POST | `/api/v1/bookings` | JSON Body: `parent_name`, `parent_email`, `child_name`, `course_id`, `parent_timezone`, `slot_utc` | 201 Created. Returns the generated booking including the generated dummy `class_link`. <br> **Errors**: 422 for invalid inputs, timezones, or out-of-schedule slots; 409 if no mentor is available or the course is inactive; 503 if a persistent retryable concurrency error occurs. |
| GET | `/api/v1/bookings/{id}` | Path: `id` (integer) | Returns the detailed booking response. Returns 404 if not found. |

*Note on Bookings*: `slot_utc` must be a timezone-aware UTC timestamp corresponding to a top-of-hour (`:00:00`) anchor between 15:00-21:00 IST within the valid future booking window. `course_id` must match a currently active course.

## Mentor operations

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| GET | `/api/v1/mentor/bookings` | Query (Optional): `mentor_id=<integer>` | Returns a list of confirmed bookings, optionally filtered by the provided mentor ID. |

## Admin (Staff Portal)

Internal operational endpoints. Authentication/RBAC is intentionally excluded for this demonstration.

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| GET | `/api/v1/admin/overview` | None | Returns operational metrics: total mentors, active mentors, total bookings, today's IST classes, and theoretical/remaining daily capacity. |
| GET | `/api/v1/admin/mentors` | None | Returns a list of all mentors, complete with their current status and an upcoming class load grouped by IST date. |
| GET | `/api/v1/admin/courses` | None | Returns the full list of courses (both active and inactive) for administrative management. |
| POST | `/api/v1/admin/courses` | JSON Body: `name`, `description`, `age_range`, `level`, optional `is_active` | 201 Created. Returns the new course. <br> **Errors**: 409 if the course name is a duplicate, 422 for validation errors. |
| PATCH | `/api/v1/admin/courses/{id}` | JSON Body (Partial): `name`, `description`, `age_range`, `level`, `is_active` | Returns the updated course. <br> **Errors**: 404 Not Found, 409 Conflict (duplicate name), 422 Unprocessable Entity. |
| PATCH | `/api/v1/admin/courses/{id}/status` | JSON Body: `{is_active: boolean}` | Returns the updated course status. Returns 404 if not found. |
| POST | `/api/v1/admin/mentors` | JSON Body: `name`, `email`, optional `timezone` | 201 Created. Returns the new mentor. <br> **Errors**: 409 if the email already exists, 422 for validation errors. |
| PATCH | `/api/v1/admin/mentors/{id}` | JSON Body (Partial): `name`, `email`, `timezone`, `is_active` | Returns the updated mentor. <br> **Errors**: 404 Not Found, 409 Conflict (duplicate email), 422 Unprocessable Entity. |
| PATCH | `/api/v1/admin/mentors/{id}/status` | JSON Body: `{is_active: boolean}` | Returns the updated mentor. Returns 404 if not found. |
| DELETE | `/api/v1/admin/mentors/{id}` | None | 200 Success. <br> **Errors**: 404 Not Found, 400 Bad Request if the mentor has historical bookings (must deactivate instead). |
| GET | `/api/v1/admin/parents` | None | Returns the parent directory, including counts of confirmed bookings per parent. |
| GET | `/api/v1/admin/parents/{id}/bookings` | Path: `id` (integer) | Returns the detailed booking history for a specific parent, or 404 if the parent is not found. |
| GET | `/api/v1/admin/bookings` | None | Returns the full registry of confirmed bookings containing both parent-local and mentor-IST formatted time strings. |
| GET | `/api/v1/admin/mentors/{id}/schedule` | Path: `id` (integer) | Returns the mentor's confirmed schedule formatted strictly in IST, or 404 if the mentor is not found. |

## Email Resend

| Method | Path | Request | Response / Errors |
|---|---|---|---|
| POST | `/api/v1/admin/bookings/{id}/resend-email` | JSON Body: `recipient_email`, `recipient_type` (`parent` or `mentor`), optional `custom_subject` | 200 Success indicating the notification was queued/sent. <br> **Errors**: 404 if the booking is missing, 500 if the notification delivery mechanism fundamentally fails. |
