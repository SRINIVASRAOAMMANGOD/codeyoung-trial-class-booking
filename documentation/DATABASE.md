# Database

The ORM defines four application tables. PostgreSQL is the configured target; deployed contents are To be verified.

## `parents`

Normalized parent identity. `id` is the indexed primary key; `name`, `email`, and `created_at` are required. Email is unique and indexed. One parent has many bookings. The Phase 10 migration backfills this table and makes `bookings.parent_id` required.

## `mentors`

`id` is an indexed primary key; `name`, unique `email`, `timezone`, and `is_active` are required. `bookings.mentor_id` references it with `ON DELETE RESTRICT`. The seed script inserts ten fictional active `Asia/Kolkata` mentors idempotently.

## `courses`

`id` is an indexed primary key; unique `name`, `description`, `is_active`, and timezone-aware `created_at` are required. Bookings reference courses with `ON DELETE RESTRICT`. Booking creation rejects missing or inactive courses.

## `bookings`

`id` is an indexed primary key; `parent_id`, `mentor_id`, and `course_id` are required foreign keys. Other required fields are `child_name`, `parent_timezone`, `slot_utc`, `class_link`, `status`, and `created_at`. Timezone-aware `slot_utc` is intended to map to PostgreSQL `TIMESTAMPTZ` and is the canonical UTC instant.

Named constraint `uq_mentor_slot_utc` prevents one mentor being assigned twice to the same UTC slot. Indexes exist on parent, mentor, and course foreign keys. Parent, mentor, and course relationships are bidirectional in SQLAlchemy.

## Capacity and Schema Management

Booking and slot services convert `slot_utc` to `Asia/Kolkata`, group confirmed bookings by IST date, and exclude mentors with two or more. Admin theoretical capacity is active mentors multiplied by two; there is no separate 20-booking limit. `db/init_db.py` uses `Base.metadata.create_all()`, while explicit scripts handle seed and parent normalization. Alembic is not present. Credentials are not documented.
