# PROJECT_STATUS.md — Codeyoung Trial Class Booking System

## Current Phase
**Phase 9 — Documentation & Project Finalization** ✅ Complete  
*(All 9 project phases completed, fully tested, documented, and verified for submission.)*

---

## Phase Execution Summary

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Planning & Requirements Breakdown | ✅ DONE |
| **Phase 2** | Project Scaffolding (FastAPI + React Vite) | ✅ DONE |
| **Phase 3** | Database Models & Mentor Seed (PostgreSQL) | ✅ DONE |
| **Phase 4** | Slot Availability API & Timezone Service | ✅ DONE |
| **Phase 5** | Booking Creation & Mentor Allocation | ✅ DONE |
| **Phase 6** | React Booking Flow UI | ✅ DONE |
| **Phase 7** | Integration & Edge-Case Testing | ✅ DONE |
| **Phase 8** | Architecture & Code Quality Audit | ✅ DONE |
| **Phase 9** | Documentation & Project Finalization | ✅ DONE |

---

## Current Project State

The application is a fully functional, production-ready recruitment assessment submission implementing the 1-on-1 trial class booking system for Codeyoung.
- **Backend:** FastAPI with SQLAlchemy ORM running on Python 3.13 / PostgreSQL 18.
- **Frontend:** Pure React 19 + Vite with custom responsive CSS (zero external UI/state libraries).
- **Database:** PostgreSQL schema with TIMESTAMPTZ columns, foreign keys, and unique composite constraints preventing double-booking.
- **Seeded Data:** 10 active mentors based in India (`Asia/Kolkata`).
- **Tests:** 23 passing pytest tests covering timezone calculations, DST transitions, and slot math; comprehensive end-to-end browser and edge-case testing completed.
- **Active Working Tree:** Clean git status on `main`, synchronised with `origin/main`. Database contains 10 seeded mentors and 0 bookings (reset after verification).

---

## Completed Work

### Phase 1 — Planning & Requirements
- Requirement taxonomy established: Explicit assignment requirements, Engineering inferences, and Product decisions.
- Addressed cross-timezone complexities between US/UK parents and India mentors.
- Established canonical UTC-first persistence architecture.
- Identified PostgreSQL `SERIALIZABLE` transaction isolation and unique constraints for race condition protection.

### Phase 2 — Scaffolding
- Backend structure initialized: `config.py`, `database.py`, `main.py`, routers, services, models, schemas.
- Frontend structure initialized: Vite + React 19, vanilla CSS tokens, base component layouts.
- Environment templates: `backend/.env.example` and `frontend/.env.example`.

### Phase 3 — Database & Mentor Seed
- SQLAlchemy ORM models: `Mentor` (`backend/models/mentor.py`) and `Booking` (`backend/models/booking.py`).
- Table creation via `backend/db/init_db.py` (idempotent `Base.metadata.create_all()`).
- Database seed script `backend/db/seed.py`: Idempotently seeds 10 verified mentors with timezone `Asia/Kolkata`.
- Database constraint: `uq_mentor_slot_utc` (`UNIQUE (mentor_id, slot_utc)`) preventing any mentor from having overlapping bookings.

### Phase 4 — Slot Availability & Timezones
- `backend/services/timezone_service.py`: Slot generation (15:00 to 21:00 IST), conversion to canonical UTC, local formatting with DST offset calculation.
- `backend/services/slot_service.py`: Database queries evaluating slot availability against mentor active status and daily cap.
- `backend/routers/slots.py`: `GET /api/v1/slots?date=YYYY-MM-DD&timezone=<IANA>`.
- `backend/tests/test_timezone.py`: 23 unit tests verifying IST anchor generation, UTC conversion, US EDT/EST, UK BST/GMT, and date boundary integrity.

### Phase 5 — Booking & Mentor Allocation
- `backend/services/booking_service.py`: Mentor allocation algorithm, `SERIALIZABLE` transaction isolation, automatic single-retry logic for serialization collisions, and dummy classroom link generation (`https://class.codeyoung.com/room/{uuid4()}`).
- `backend/routers/bookings.py`:
  - `POST /api/v1/bookings`: Creates confirmed booking with automatic mentor assignment.
  - `GET /api/v1/bookings/{id}`: Retrieves confirmed booking by ID.
  - `GET /api/v1/mentor/bookings`: Retrieves confirmed bookings for mentors (optional `mentor_id` query param).

### Phase 6 — React Booking Flow
- Clean two-column responsive UI built with pure React hooks and semantic HTML.
- Components implemented:
  - `Header.jsx`: Branding and value proposition.
  - `ParentDetailsForm.jsx`: Parent name, email, and student name with live client-side validation.
  - `TimezoneDatePicker.jsx`: Browser timezone auto-detection, curated timezone dropdown, and 7-day IST date strip.
  - `SlotPicker.jsx`: Interactive slot selection grid, loading skeletons, and empty state messaging.
  - `BookingConfirmation.jsx`: Success screen with reference ID, local scheduled time, assigned instructor label, classroom link with one-click copy, and "Book Another Class" reset button.
  - `AlertBanner.jsx`: Banner for conflict, validation, and connectivity messages.
- Submits canonical `utc_iso` verbatim to ensure zero clock skew.

### Phase 7 — Integration & Edge-Case Testing
- End-to-end testing across all user workflows:
  - Normal booking creation flow.
  - Daily mentor limit enforcement (maximum 2 bookings per IST calendar day).
  - Same-slot multi-booking (allocates distinct mentors).
  - Slot exhaustion (returns 409 Conflict when all 10 mentors are capped or booked).
  - Concurrency collision verification with PostgreSQL SERIALIZABLE isolation.
  - Timezone switching with dynamic slot refresh and correct DST offset display.
  - Validation handling (invalid emails, short names, past dates, invalid IANA timezones).
- Test data cleared post-verification (`bookings = 0`, `mentors = 10`).

### Phase 8 — Architecture & Code Quality Audit
- Comprehensive read-only audit verifying adherence to assignment specifications.
- Verification of class link lifecycle: stored in database, returned on booking response/confirmation, and accessible to mentors via `GET /api/v1/mentor/bookings`.
- Codebase verified free of dead code, test artifacts, or temporary scripts.

---

## Current Architecture

```
codeyoung-trial-class-booking/
├── backend/
│   ├── main.py                  FastAPI entry point, CORS, routers, health check
│   ├── config.py                Pydantic settings and database configuration
│   ├── database.py              SQLAlchemy engine, SessionLocal, get_db() dependency
│   ├── models/
│   │   ├── mentor.py            Mentor ORM model (id, name, email, timezone, is_active)
│   │   └── booking.py           Booking ORM model (TIMESTAMPTZ slot_utc, FK mentor_id)
│   ├── schemas/
│   │   ├── slots.py             SlotItem (utc_iso, local_display), SlotsResponse
│   │   └── booking.py           BookingCreate, BookingResponse
│   ├── routers/
│   │   ├── slots.py             GET /api/v1/slots
│   │   └── bookings.py          POST /api/v1/bookings, GET /bookings/{id}, GET /mentor/bookings
│   ├── services/
│   │   ├── timezone_service.py  IST anchors, UTC conversions, IANA validation, DST offsets
│   │   ├── slot_service.py      Slot generation & mentor eligibility filtering
│   │   └── booking_service.py   SERIALIZABLE transactions, mentor allocation, retry logic
│   ├── db/
│   │   ├── init_db.py           Idempotent table creation (Base.metadata.create_all)
│   │   └── seed.py              Idempotent seed script for 10 Indian mentors
│   ├── tests/
│   │   └── test_timezone.py     23 pytest unit tests for timezone conversions & DST
│   ├── requirements.txt         Pinned backend dependencies
│   └── pytest.ini               Pytest configuration with strict asyncio mode
│
└── frontend/
    ├── src/
    │   ├── main.jsx             React entry point
    │   ├── App.jsx              Root application component
    │   ├── index.css            Vanilla CSS design system (tokens, responsive grid)
    │   ├── api/
    │   │   └── bookingApi.js    Centralized API client for slots and bookings
    │   ├── components/
    │   │   ├── Header.jsx              Top navbar and branding
    │   │   ├── ParentDetailsForm.jsx   Parent and child input fields
    │   │   ├── TimezoneDatePicker.jsx  Timezone select & 7-day date selector
    │   │   ├── SlotPicker.jsx          Slot list & state handling
    │   │   ├── BookingConfirmation.jsx Success screen with meeting link
    │   │   └── AlertBanner.jsx         Dismissible feedback alerts
    │   ├── pages/
    │   │   └── BookingPage.jsx  Main state coordinator for 2-step booking flow
    │   └── utils/
    │       └── dateUtils.js     Date calculations and display formatting
    ├── package.json             Vite + React 19 dependencies & scripts
    └── vite.config.js           Vite bundler configuration
```

---

## Database Schema

```sql
CREATE TABLE mentors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Kolkata',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    parent_name VARCHAR(100) NOT NULL,
    parent_email VARCHAR(150) NOT NULL,
    child_name VARCHAR(100) NOT NULL,
    parent_timezone VARCHAR(50) NOT NULL,
    slot_utc TIMESTAMPTZ NOT NULL,
    mentor_id INTEGER NOT NULL REFERENCES mentors(id),
    class_link VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_mentor_slot_utc UNIQUE (mentor_id, slot_utc)
);
```

---

## API Endpoints

| Method | Path | Summary | Description | Status Codes |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | Health Check | Verifies service availability | 200 |
| `GET` | `/api/v1/slots` | Available Slots | Lists available slots for a date & parent timezone | 200, 422 |
| `POST` | `/api/v1/bookings` | Create Booking | Validates slot, assigns mentor, confirms booking | 201, 409, 422, 503 |
| `GET` | `/api/v1/bookings/{id}` | Get Booking | Retrieves confirmed booking record by ID | 200, 404 |
| `GET` | `/api/v1/mentor/bookings` | Mentor Bookings | Retrieves mentor schedule (filter by `mentor_id`) | 200 |

---

## Timezone & DST Handling

1. **Canonical Anchors:** All available classes are anchored in India Standard Time (`Asia/Kolkata`) from **15:00 to 21:00 IST** (7 one-hour slots daily).
2. **UTC-First Conversion:** Each IST slot is converted to an exact UTC `datetime` instant (e.g., 15:00 IST $\rightarrow$ 09:30 UTC).
3. **Local Display:** The backend converts the UTC instant to the parent's requested IANA timezone using standard Python `zoneinfo` and `tzdata==2025.2`, computing local time with the correct daylight saving time (DST) offset (e.g., EDT vs EST, BST vs GMT).
4. **Zero Frontend Drift:** The frontend receives both `utc_iso` and `local_display`. When booking, the frontend returns `utc_iso` verbatim to the backend, completely eliminating browser clock skews.

---

## Mentor Allocation Logic

When a parent books a slot:
1. **Active Filter:** Mentor must have `is_active = TRUE`.
2. **Slot Availability:** Mentor must not already be booked at `slot_utc` with `status = 'confirmed'`.
3. **Daily Cap:** Mentor must have fewer than **2 confirmed bookings** on that **IST calendar date** (`DATE(slot_utc AT TIME ZONE 'Asia/Kolkata') == ist_date`).
4. **Assignment Strategy:** If multiple mentors qualify, assignment picks the lowest mentor ID deterministically (`ORDER BY Mentor.id ASC`).
5. **Capacity Exhaustion:** If all 10 mentors are booked at that slot or have hit their 2-class daily cap, the API returns `409 Conflict`.

---

## Concurrency Protection

- **Database-Level Protection:** A composite unique constraint `uq_mentor_slot_utc` (`UNIQUE (mentor_id, slot_utc)`) guarantees at the storage engine level that two transactions can never assign the same mentor to the same UTC slot.
- **Transaction Isolation:** Booking creation executes inside PostgreSQL `SERIALIZABLE` isolation level, which monitors read/write dependencies and aborts concurrent overlapping transactions via Serializable Snapshot Isolation (SSI).
- **Automatic Retry:** The backend catches serialization failures (`40001`) and unique constraint collisions (`23505`) and retries once automatically. If contention persists, it returns `503 Service Unavailable` with a prompt to retry.

---

## Testing Status

- **Unit Tests:** 23 passing pytest tests in `backend/tests/test_timezone.py` (0.10s execution time).
- **Frontend Quality:**
  - `oxlint`: 0 warnings, 0 errors across 12 files.
  - `vite build`: Production build passes in ~530ms with zero errors.
- **End-to-End Verification:** Passed across normal booking, 2-class daily limit, distinct mentor allocation, slot conflict handling (409), invalid inputs (422), and cross-timezone DST transitions.

---

## Important Assumptions & Design Decisions

1. **Class Duration (Product Assumption):** Classes are assumed to be 1 hour in duration (15:00–16:00, 16:00–17:00, ..., 21:00–22:00 IST).
2. **Booking Window (Product Assumption):** Parents can book slots starting from tomorrow through tomorrow + 6 days (7 calendar days). Same-day bookings are excluded to avoid booking past hours or mentor short-notice issues.
3. **Mentor "Day" Boundary (Engineering Inference):** Because mentors reside in India, the daily 2-class limit is measured by the mentor's local calendar date in `Asia/Kolkata`.
4. **Class Meeting Link (Specification Requirement):**
   > *The system generates and stores a dummy class link for each confirmed booking. The link is available to the parent through the booking confirmation flow and to the mentor through the mentor booking endpoint. Actual email/notification delivery is intentionally outside the scope of this assignment.*
5. **Database Initialization:** Database tables are initialized using `SQLAlchemy Base.metadata.create_all()` via `backend/db/init_db.py`. Alembic is deliberately omitted for this standalone assessment.
6. **Parent-Facing Mentor Display:** The parent confirmation screen displays "Dedicated Codeyoung Mentor" rather than internal mentor IDs or emails, while preserving the internal `mentor_id` in API payloads.

---

## Deliberately Unbuilt Features

As specified by project constraints:
- ❌ No user authentication or login sessions (JWT, OAuth, passwords).
- ❌ No transactional email delivery (SendGrid, SES, SMTP).
- ❌ No calendar integrations (Google Calendar, Outlook iCal).
- ❌ No live video conferencing infrastructure (WebRTC, Zoom API).
- ❌ No payment gateway or checkout processing.
- ❌ No internal administrative CRM or mentor management dashboard.

---

## Next Steps / Project Status

1. **Project Finalized:** All core requirements, edge cases, integration flows, and documentation are complete.
2. **Repository Ready:** Working tree clean, all 23 unit tests pass, frontend linter and production build pass with 0 errors.
3. **Assessment Ready for Review.**
