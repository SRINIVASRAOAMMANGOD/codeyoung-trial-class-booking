# PROJECT_STATUS.md — Codeyoung Trial Class Booking System

## Current Phase
**Phase C.1 — Staff Portal Finalization** ✅ DONE  

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
| **Phase 10** | Admin Management & Parent Entity | ✅ DONE |
| **Phase A** | Course Selection Backend | ✅ DONE |
| **Phase B** | Public Booking UX | ✅ DONE |
| **Phase B.1** | Public Booking UI Correction | ✅ DONE |
| **Phase B.2** | Final Booking UX Redesign + Home Login | ✅ DONE |
| **Phase C** | Staff Portal Separation | ✅ DONE |
| **Phase C.1** | Staff Portal Finalization | ✅ DONE |
| **Phase D** | Email Delivery and Resend | ✅ DONE |
| **Phase E** | Final Public Site Polish | ✅ DONE |

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

### Phase 9 — Documentation & Project Finalization
- Project documentation finalized in `PROJECT_STATUS.md` and `README.md`.
- Full 18-section recruiter-friendly documentation covering architecture, setup, testing, and explicit out-of-scope items.

### Phase 10 — Step 1: Database Model & Parent Relationship (DONE)
- `backend/models/parent.py`: `Parent` model with `id`, `name`, `email UNIQUE`, and `bookings` relationship.
- `backend/models/booking.py`: Normalized with `parent_id` foreign key (`ON DELETE RESTRICT`) and `@property` getters for backward-compatible serialization.
- `backend/db/migrate_phase10.py`: Lossless forward migration preserving existing bookings.
- `backend/services/parent_service.py`: `get_or_create_parent()` with concurrent savepoint collision handling.

### Phase 10 — Step 2: Email Notification Service (DONE)
- `backend/services/email_service.py`: Dual-mode notification system (`console` for dev simulation, `smtp` for real delivery).
- Parent notification formatted in parent local timezone with active DST offset.
- Mentor notification formatted in India Standard Time (`Asia/Kolkata`).
- Commit-before-email guarantee: Booking transaction commits to database before notifications are sent; notification errors are caught and logged without rolling back confirmed bookings.
- 38/38 unit tests passing across timezone math, parent models, and email dispatching.

### Phase 10 — Step 3: Admin & Mentor Management (DONE)
- **Admin Backend Architecture:** Clean Layered Service Pattern (`Router` → `AdminService` → `SQLAlchemy Models` → PostgreSQL).
- **Dynamic Capacity Tracking:** Daily capacity is computed dynamically as $\text{Active Mentors} \times 2$ (e.g. 10 active = 20 classes/day; 8 active = 16 classes/day). No hardcoded 20 bookings/day ceiling.
- **Mentor Lifecycle Management:**
  - View all mentors with their current IST day class count and availability.
  - Add mentor with IANA timezone validation, email regex validation, and duplicate email prevention.
  - Activate and deactivate mentors. Inactive mentors cannot receive new bookings while all historical bookings remain untouched.
  - Safe delete rule: Hard deletion allowed ONLY if mentor has zero bookings. If $\ge 1$ booking exists, deletion is rejected with 400 Bad Request instructing deactivation.
- **Parent & Booking Operational Visibility:**
  - Parent directory with booking counts, first booking date, and modal drill-down into parent booking history.
  - Booking list showing parent local time and mentor IST time derived on-the-fly from canonical `slot_utc` without redundant database columns.
- **Internal Demo Mentor View:** Mentor selector allowing instructors to view their assigned trial classes formatted in IST with classroom links.
- **Frontend Integration:**
  - Single-page application with top navbar view switcher (`📅 Parent Booking`, `🛡️ Admin Dashboard`, `👩‍🏫 Mentor View`).
  - Clear "Internal Demo / Operational Management" banners noting that production authorization (JWT/RBAC) is required for production.

### Phase A — Course Selection Backend (DONE)
- **Database Model:** `Course` model (`id`, `name`, `description`, `is_active`). Added `course_id` foreign key to `Booking`.
- **Idempotent Migration:** Created `backend/db/migrate_phase_a.py` to add tables, seed default courses (Coding Fundamentals, Python Programming, Web Development, AI & Robotics), and dynamically backfill legacy bookings without dropping tables.
- **API Updates:** Added `GET /api/v1/courses`. Updated `POST /api/v1/bookings` to require and validate `course_id`. Added `course_name` dynamically to booking schemas and admin operational endpoints.
- **Email Notification:** Updated email service templates to dynamically embed `Course` name for both parent and mentor notifications.
- **Testing:** Implemented `test_courses.py` and updated all existing booking API calls to comply with the new required field. Suite maintains 50/50 pass rate.

### Phase B — Public Booking UX (DONE)
- **Booking Flow Reorganization:** Refactored `BookingPage.jsx` to enforce a strict logical sequence: (1) Select Course, (2) Choose Date & Timezone, (3) Select Time Slot, (4) Parent & Student Details.
- **Course Selection Integration:** 
  - Created `CourseSelector.jsx` component that fetches active courses from `GET /api/v1/courses`.
  - Added URL parameter routing (`?course=ID`) allowing deep linking directly from the `LandingPage` into the `BookingPage` with preselected courses.
  - Implemented form validation blocking submission without a valid course.
- **Header & Navigation UX:**
  - Modified `Header.jsx` to remove internal App navigation (`Admin Dashboard`, `Mentor View`) when the parent booking form is visible, preventing public exposure of internal tools.
  - Re-mapped the 'CODEYOUNG' logo to act as a navigation button back to the public `LandingPage`.
- **Visual Consistency:** Ensure new UI elements map perfectly to predefined CSS tokens from `index.css`.
- **Testing:** Verified clean linting and successful Vite production build.

### Phase B.2 — Final Booking UX Redesign + Home Login (DONE)
- **Deep-Link Bug Fixed:** Corrected logic in `App.jsx` to pass `courseId` strictly as a primitive value, preventing `[object Object]` parsing failures.
- **Login Portal Modal:** Implemented a new modal UI in `LandingHeader` allowing navigation to Mentor or Admin portals, and explicitly disabling Student access per requirements.
- **Hero Redesign:** Removed the generic "CY" circle and replaced it with a multi-course "learning paths" illustrative floating-card layout in `HeroSection.jsx`.
- **Sample Domains:** Added new fictional/informational domain placeholders directly into the Course Grid, safely handling their "Coming Soon" states.
- **Booking Progress Flow Redesign:** 
  - Restyled course cards into a clean 4-column compact Grid (`.compact-courses-grid`).
  - Adjusted the layout of the Date/Timezone block.
  - Placed time slots in a symmetrical 4-column (desktop) / 2-column (mobile) layout grid (`.slots-grid`).
  - Restructured Parent Details into logical sub-headers.
  - Re-positioned the final checkout summary and "Confirm Booking" CTA directly within the final card frame.
- **Legal Placeholders:** Upgraded Footer Privacy and Terms placeholders to interactive modest modals displaying the site's primary disclaimer.

### Phase C — Staff Portal Separation (DONE)
- **Dedicated Routing:** Created a new route (`/staff`) resolving to the `StaffPage.jsx` component, completely isolating internal tools from the public booking experience.
- **Header Decoupling:** Re-architected `Header.jsx` so that the `Admin` and `Mentor` navigation options are exclusively injected when viewing the Staff Portal or its sub-pages.
- **Clear Demo Disclaimers:** Explicitly marked the Staff Portal UI with non-dismissible warning banners highlighting the intentional absence of Authentication and RBAC to meet Phase C assessment constraints.
- **Quality Verified:** Validated through `npm run build` and zero failing tests in `pytest`.

### Phase C.1 — Staff Portal Finalization (DONE)
- **Header Standardization:** Left-aligned the Codeyoung brand logo inside the Staff Portal (`Header.jsx`) to exactly match the public Home page positioning.
- **Logo Navigation Context:** Ensured that clicking the Codeyoung logo universally routes the user back to the public Home page (`/`), breaking out of the internal `/staff` view.
- **Staff Demo Notice:** Standardized the `/staff` entry page with a professional alert: "Authentication and role-based access control (RBAC) are not implemented. The data shown here is sample/demo data for the recruitment assessment."
- **Internal Routing Menu:** Consolidated staff navigation to dynamically present "Staff Home | Admin Dashboard | Mentor View" only when actively inside internal portals, supplemented by a clear "Back to Website" exit route.
- **Mentor Editing (Admin Dashboard):**
  - **Backend API:** Extended `schemas/admin.py` and `routers/admin.py` with `PATCH /api/v1/admin/mentors/{id}` supporting targeted mutation of name, email, timezone, and active status. Guaranteed email uniqueness and IANA validations.
  - **Admin UI:** Surfaced an "Edit" action button inside the Mentors Management table (`AdminPage.jsx`). Implemented a polished React state-driven modal for seamless editing without reloading the table.
- **Verification:** Maintained test integrity with 53 passing tests in Pytest and zero linting/build errors in the Vite frontend.

### Phase D — Email Delivery and Resend (DONE)
- **Email Delivery Integration:** Verified that parent and mentor emails correctly reflect dual timezones and send out canonical timezone formats with correct SMTP settings.
- **Resend Email Endpoints:** Added `POST /api/v1/admin/bookings/{id}/resend-email` in `admin` router mapping to the backend service.
- **Admin UI Updates:** Added a `ResendEmailModal.jsx` shared component, allowing admins and mentors to override default recipient email addresses or insert a custom subject line.
- **Quality Verified:** Added `TestResendEmail` testing suite to explicitly guarantee the backend correctly supports customizable recipient payloads without leaking states between tests. Passed all 52/52 tests.

### Phase E — Final Public Site Polish (DONE)
- **Footer Updates:** Overhauled the footer to remove "Phase 10" development artifacts. Added the required "Connect with the developer" section linking accurately to the developer's provided LinkedIn, GitHub, and Personal Website. Implemented a clear non-commercial recruitment project disclaimer.
- **Fake Content Handling:** Re-checked course and testimonial sample data for explicit disclaimers confirming their demonstrative nature.
- **Accessibility & Polish:** Ensured focus states, semantic buttons, responsive headers, and spacing are well aligned without introducing disruptive dependencies. Verified linting (`0 errors`) and build steps are passing successfully alongside `pytest`.

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
│   │   ├── parent.py            Parent ORM model (id, name, email UNIQUE)
│   │   └── booking.py           Booking ORM model (TIMESTAMPTZ slot_utc, FK mentor_id, FK parent_id)
│   ├── schemas/
│   │   ├── slots.py             SlotItem (utc_iso, local_display), SlotsResponse
│   │   ├── booking.py           BookingCreate, BookingResponse
│   │   └── admin.py             AdminOverviewResponse, MentorAdminResponse, MentorCreateRequest, ParentAdminResponse, AdminBookingResponse
│   ├── routers/
│   │   ├── slots.py             GET /api/v1/slots
│   │   ├── bookings.py          POST /api/v1/bookings, GET /bookings/{id}, GET /mentor/bookings
│   │   └── admin.py             Admin overview, mentor management, parent & booking visibility
│   ├── services/
│   │   ├── timezone_service.py  IST anchors, UTC conversions, IANA validation, DST offsets
│   │   ├── slot_service.py      Slot generation & mentor eligibility filtering
│   │   ├── booking_service.py   SERIALIZABLE transactions, mentor allocation, retry logic
│   │   ├── parent_service.py    Parent lookup and atomic creation
│   │   ├── email_service.py     Dual-mode notification service (console & SMTP)
│   │   └── admin_service.py     Dynamic capacity, mentor lifecycle, parent/booking reporting
│   ├── db/
│   │   ├── init_db.py           Idempotent table creation (Base.metadata.create_all)
│   │   ├── seed.py              Idempotent seed script for 10 Indian mentors
│   │   └── migrate_phase10.py   Lossless migration for parents table and FK
│   ├── tests/
│   │   ├── test_timezone.py     23 pytest unit tests for timezone conversions & DST
│   │   ├── test_phase10_step1.py 7 pytest tests for parent entity & booking FK
│   │   ├── test_email_service.py 8 pytest tests for email service formatting & modes
│   │   └── test_admin.py        9 pytest tests for admin metrics, mentor lifecycle, delete rules
│   ├── requirements.txt         Pinned backend dependencies
│   └── pytest.ini               Pytest configuration with strict asyncio mode
│
└── frontend/
    ├── src/
    │   ├── main.jsx             React entry point
    │   ├── App.jsx              Root view coordinator (Booking, Admin, Mentor)
    │   ├── index.css            Vanilla CSS design system (tokens, responsive grid, admin UI)
    │   ├── api/
    │   │   ├── bookingApi.js    Centralized API client for slots and bookings
    │   │   └── adminApi.js      Centralized API client for admin & mentor views
    │   ├── components/
    │   │   ├── Header.jsx              Top navbar, branding & view switcher
    │   │   ├── ParentDetailsForm.jsx   Parent and child input fields
    │   │   ├── TimezoneDatePicker.jsx  Timezone select & 7-day date selector
    │   │   ├── SlotPicker.jsx          Slot list & state handling
    │   │   ├── BookingConfirmation.jsx Success screen with meeting link
    │   │   └── AlertBanner.jsx         Dismissible feedback alerts
    │   ├── pages/
    │   │   ├── BookingPage.jsx  Main state coordinator for 2-step booking flow
    │   │   ├── AdminPage.jsx    Operational admin dashboard (metrics, mentors, parents, bookings)
    │   │   └── MentorPage.jsx   Internal demo mentor portal for assigned classes
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

CREATE TABLE parents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES parents(id) ON DELETE RESTRICT,
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
| `POST` | `/api/v1/bookings` | Create Booking | Validates slot, assigns mentor, creates parent, sends emails | 201, 409, 422, 503 |
| `GET` | `/api/v1/bookings/{id}` | Get Booking | Retrieves confirmed booking record by ID | 200, 404 |
| `GET` | `/api/v1/mentor/bookings` | Mentor Bookings | Retrieves mentor schedule (filter by `mentor_id`) | 200 |
| `GET` | `/api/v1/admin/overview` | Admin Overview | Returns metrics, active mentors, parents, bookings, capacity | 200 |
| `GET` | `/api/v1/admin/mentors` | Admin Mentors | Lists all mentors with today's class count and active status | 200 |
| `POST` | `/api/v1/admin/mentors` | Create Mentor | Adds mentor with email, name, and IANA timezone validation | 201, 400, 409 |
| `PATCH` | `/api/v1/admin/mentors/{id}/status` | Update Mentor Status | Activates or deactivates mentor | 200, 404 |
| `DELETE` | `/api/v1/admin/mentors/{id}` | Delete Mentor | Safe delete: allowed only if 0 bookings exist | 200, 400, 404 |
| `GET` | `/api/v1/admin/parents` | Admin Parents | Lists registered parents with booking counts and first date | 200 |
| `GET` | `/api/v1/admin/parents/{id}/bookings` | Parent Bookings | Retrieves all bookings for a specific parent | 200, 404 |
| `GET` | `/api/v1/admin/bookings` | Admin Bookings | Lists bookings with parent local and mentor IST times | 200 |

---

## Dynamic Mentor Capacity & Safe Delete Rules

1. **Dynamic Capacity Calculation:**
   - Theoretical Daily Capacity = $\text{Active Mentors} \times 2$.
   - Remaining Today Capacity = $\max(0, \text{Theoretical Daily Capacity} - \text{Today's Confirmed Classes})$.
   - Never hardcoded to 20 bookings/day; updates dynamically when mentors are added, deactivated, or reactivated.
2. **Delete vs Deactivate Rule:**
   - **Zero Bookings:** Hard `DELETE` from database is permitted.
   - **$\ge 1$ Bookings:** Hard `DELETE` is blocked with HTTP 400 (`"Cannot delete mentor because X historical booking(s) exist. Deactivate the mentor instead."`).
   - **Deactivation (`is_active = FALSE`):** Immediately excludes the mentor from receiving new booking slots, but preserves all historical booking records, parent relationships, and class schedules.

---

## Testing & Code Quality Status

- **Pytest Suite:** 47 passing unit and integration tests across 4 test modules:
  - `test_timezone.py` (23 tests): Slot generation, DST conversions (US EDT/EST, UK BST/GMT).
  - `test_phase10_step1.py` (7 tests): Parent normalization, foreign key preservation, duplicate parent reuse.
  - `test_email_service.py` (8 tests): Dual-mode console/SMTP dispatching, template formatting, non-blocking guarantee.
  - `test_admin.py` (9 tests): Metrics calculation, mentor creation & validation, deactivation, safe delete rule, parent drill-downs, dual timezone presentation.
- **Frontend Quality:**
  - `oxlint`: 0 warnings, 0 errors across 15 files.
  - `vite build`: Production build passes in ~950ms with 0 errors.

---

## Security & Operational Scope Limitations

- ⚠️ **Internal Demo Scope:** The Admin Dashboard and Mentor Portal are designed as internal demonstration and operational management interfaces for recruitment evaluation.
- ⚠️ **No Authentication:** In accordance with explicit Phase 10 Step 3 instructions, user authentication (JWT/OAuth) and role-based access control (RBAC) are deliberately omitted.
- ⚠️ **Production Readiness:** Before exposing admin and mentor management endpoints to public networks, production authentication (e.g. Auth0, OAuth2 password grant, session cookies), CSRF tokens, and rate-limiting middleware must be introduced.
