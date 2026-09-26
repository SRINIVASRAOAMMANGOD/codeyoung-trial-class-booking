# PROJECT_STATUS.md

## Current Phase
**Phase 2 — Project Scaffolding** ✅ Complete (Git checkpoint pending)
**Next: Phase 3 — Database Models + Migrations + Mentor Seed**

---

## Completed

### Phase 1 — Requirements & Architecture
- Requirements breakdown with explicit/inferred/product-decision classification
- Ambiguities identified and resolved
- Booking window: 15:00–22:00 IST, 1-hour slots, 7 slots/day (Product decision)
- Mentor "day" = IST calendar date (Engineering inference)
- UTC-first storage strategy confirmed
- Concurrency: SERIALIZABLE isolation + UNIQUE(mentor_id, slot_utc)
- Booking window: tomorrow + 6 days = exactly 7 bookable dates
- Dummy class link: stored in DB, shown on confirmation, accessible via mentor endpoint
- No auth, no real email, no real video

### Phase 2 — Scaffolding
- `backend/requirements.txt` — pinned dependencies
- `backend/.env.example` — environment variable template
- `backend/config.py` — pydantic-settings config with lru_cache
- `backend/database.py` — SQLAlchemy engine + SessionLocal + Base + get_db()
- `backend/main.py` — FastAPI app, CORS, health check endpoint
- `backend/models/`, `schemas/`, `routers/`, `services/`, `db/`, `tests/` — package stubs
- `backend/pytest.ini` — pytest config
- `frontend/` — Vite + React scaffold (npm installed, 0 vulnerabilities)
- `frontend/src/index.css` — global CSS with design tokens
- `frontend/src/App.jsx` — root component (renders BookingPage)
- `frontend/src/pages/BookingPage.jsx` — stub
- `frontend/src/api/bookingApi.js` — API client stub
- `frontend/.env.example`
- `.gitignore`

---

## In Progress
Nothing currently in progress.

---

## Remaining (Required)

### Phase 3 — DB Models + Migrations + Seed
- [ ] `backend/models/mentor.py` — Mentor ORM model
- [ ] `backend/models/booking.py` — Booking ORM model
- [ ] `backend/db/seed.py` — Seed 10 mentors
- [ ] Create DB tables (SQLAlchemy `create_all` for now; Alembic optional)
- [ ] Verify DB connection + seed runs successfully

### Phase 4 — Slots API + Timezone Service
- [ ] `backend/services/timezone_service.py`
- [ ] `backend/services/slot_service.py`
- [ ] `backend/routers/slots.py` — GET /api/v1/slots
- [ ] Register slots router in main.py
- [ ] Manual test: correct UTC + local display times

### Phase 5 — Booking API + Mentor Allocation
- [ ] `backend/services/booking_service.py` — SERIALIZABLE txn, mentor allocation
- [ ] `backend/schemas/booking.py`
- [ ] `backend/routers/bookings.py` — POST /api/v1/bookings, GET /api/v1/bookings/{id}
- [ ] Mentor bookings endpoint — GET /api/v1/mentor/bookings
- [ ] Register booking routers in main.py
- [ ] Manual test: successful booking, no-mentor 409

### Phase 6 — React Frontend
- [ ] BookingForm component (parent details + timezone + date)
- [ ] SlotPicker component (slot grid from API)
- [ ] Confirmation component (booking ID + mentor + link)
- [ ] Loading, error, empty states for all components

### Phase 7 — Frontend-Backend Integration
- [ ] Wire up bookingApi.js to real backend
- [ ] End-to-end manual test: full booking flow
- [ ] Error state: no mentors available
- [ ] Error state: network failure

### Phase 8 — Testing
- [ ] `tests/test_bookings.py` — booking happy path, mentor cap, 409, concurrency
- [ ] `tests/test_slots.py` — slot generation, booked slot exclusion
- [ ] `tests/test_timezone.py` — NY parent, London parent, DST dates, date-boundary
- [ ] Run all tests and confirm passing

### Phase 9 — Optional Features
- [ ] Booking lookup by email/booking ID
- [ ] Mentor dashboard view
(Only after Phase 8 complete)

### Phase 10 — Documentation
- [ ] README.md (full)
- [ ] TRANSCRIPT.md

### Phase 11 — Final Review
- [ ] Code review pass
- [ ] Edge case audit
- [ ] Cleanup

---

## Architecture

```
backend/
├── main.py          FastAPI entry point, CORS, health check
├── config.py        pydantic-settings, lru_cache
├── database.py      SQLAlchemy engine, SessionLocal, Base, get_db()
├── models/          ORM models (Mentor, Booking)
├── schemas/         Pydantic request/response schemas
├── routers/         Route handlers (slots, bookings)
├── services/        Business logic (slot_service, booking_service, timezone_service)
├── db/              Seed scripts
└── tests/           pytest suites

frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── pages/       BookingPage (orchestrates 3-step flow)
│   ├── components/  BookingForm, SlotPicker, Confirmation, shared
│   ├── api/         bookingApi.js
│   └── index.css    Global CSS with design tokens
```

---

## Database Schema (planned, not yet created)

```sql
mentors  (id, name, email, timezone, is_active)
bookings (id, parent_name, parent_email, child_name, parent_timezone,
          slot_utc TIMESTAMPTZ, mentor_id FK, class_link, status, created_at)
UNIQUE (mentor_id, slot_utc)
```

---

## Key Decisions

| Decision | Value | Classification |
|---|---|---|
| Booking window | 15:00–22:00 IST | C — Product decision |
| Slot duration | 1 hour | C — Product decision |
| Mentor "day" | IST calendar date | B — Engineering inference |
| Booking dates | Tomorrow + 6 days | C — Product decision |
| Storage | UTC TIMESTAMPTZ | B — Engineering inference |
| Concurrency | SERIALIZABLE + UNIQUE | B — Engineering inference |
| Dummy link | UUID-based, on-screen only | B — Engineering inference |
| Auth | None | B — Not required |
| Email | None | B — Not required |

---

## Known Issues / Risks
- None at this stage.

---

## Important Notes
- Python 3.9+ required (for `zoneinfo` stdlib)
- PostgreSQL 12+ required (for SERIALIZABLE SSI correctness)
- Backend runs on port 8000; frontend dev server on port 5173
