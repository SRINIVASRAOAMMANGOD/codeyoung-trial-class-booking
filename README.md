# Codeyoung Trial Class Booking System

> Full-stack trial class booking platform designed for Codeyoung's recruitment assessment.  
> Enables parents across the US and UK to book 1-on-1 coding trial classes with mentors based in India with full timezone awareness, automated mentor scheduling, and concurrency-safe bookings.

---

## 1. Project Overview

Codeyoung connects students in international markets (such as the US and UK) with expert coding mentors located in India. Scheduling trial classes across these global timezones requires precise handling of local time conversions, daylight saving time (DST) shifts, mentor availability, and strict daily class caps.

This system provides:
- A frictionless, single-page booking experience for parents.
- Timezone auto-detection with real-time conversion between US/UK timezones and India Standard Time (IST).
- Automated mentor allocation enforcing a maximum of 2 demo classes per mentor per day.
- Concurrency protection preventing double-booking of any mentor.
- Dummy virtual classroom link generation with instant access for parents and mentors.

---

## 2. Features

- **Global Timezone Support:** Automatically detects the parent's browser timezone (e.g., `America/New_York`, `America/Chicago`, `Europe/London`) and converts slots with active daylight saving time (DST) offsets.
- **Dynamic Slot Availability:** Generates available slots across 7 upcoming bookable calendar days based on real-time mentor eligibility.
- **Smart Mentor Allocation:** Automatically assigns available mentors while strictly enforcing the 2-classes-per-day cap per mentor.
- **Race Condition Prevention:** Database-level unique constraints and PostgreSQL `SERIALIZABLE` transactions prevent simultaneous double-booking.
- **Virtual Classroom Link:** Instantly generates a unique dummy classroom link displayed on confirmation with one-click copying.
- **Clean Responsive UI:** Built with pure React and lightweight CSS without external component or state-management bloat.

---

## 3. Tech Stack

| Layer | Technology | Key Libraries / Details |
|---|---|---|
| **Frontend** | React 19 + Vite | Vanilla CSS (responsive design tokens), native fetch API |
| **Backend** | Python 3.13 + FastAPI | Pydantic v2, SQLAlchemy ORM, `zoneinfo` + `tzdata` |
| **Database** | PostgreSQL 18 | `TIMESTAMPTZ` UTC storage, composite unique constraints |
| **Testing & Quality** | Pytest + Oxlint | Unit tests for timezone/DST math, linting, production builds |

---

## 4. Architecture

The system uses a **canonical UTC-first scheduling architecture**:

```
[ Parent Browser (US/UK) ]
         │
         │ 1. Request slots with date & parent timezone
         ▼
[ FastAPI Backend ] ── 2. Anchor 15:00–21:00 IST slots ──► [ ZoneInfo Engine ]
         │                                                      │
         │ 3. Check mentor availability & daily caps            │
         ▼                                                      ▼
[ PostgreSQL DB ] ◄── 4. Query bookings by UTC & IST date ── [ Canonical UTC ]
         │
         │ 5. Return utc_iso + localized display string
         ▼
[ Parent Selects Slot ] ── 6. Submit booking with canonical utc_iso (verbatim)
         │
         ▼
[ SERIALIZABLE Transaction ] ── 7. Verify mentor eligibility & allocate
         │
         ▼
[ Booking Confirmed ] ── 8. Return dummy classroom link
```

---

## 5. Project Structure

```
codeyoung-trial-class-booking/
├── backend/
│   ├── main.py                  FastAPI app initialization, CORS, health check
│   ├── config.py                Pydantic settings and database configuration
│   ├── database.py              SQLAlchemy engine, SessionLocal, get_db()
│   ├── models/
│   │   ├── mentor.py            Mentor ORM model
│   │   └── booking.py           Booking ORM model with TIMESTAMPTZ
│   ├── schemas/
│   │   ├── slots.py             SlotItem and SlotsResponse Pydantic models
│   │   └── booking.py           BookingCreate and BookingResponse models
│   ├── routers/
│   │   ├── slots.py             GET /api/v1/slots
│   │   └── bookings.py          POST /bookings, GET /bookings/{id}, GET /mentor/bookings
│   ├── services/
│   │   ├── timezone_service.py  IST anchors, UTC conversions, DST offsets, validation
│   │   ├── slot_service.py      Calculates slot availability against mentor daily caps
│   │   └── booking_service.py   SERIALIZABLE transactions, mentor allocation & retry
│   ├── db/
│   │   ├── init_db.py           Idempotent table creation via create_all()
│   │   └── seed.py              Idempotent seed script for 10 Indian mentors
│   └── tests/
│       └── test_timezone.py     Pytest suite for timezone conversion and DST
│
└── frontend/
    ├── src/
    │   ├── main.jsx             React DOM entry point
    │   ├── App.jsx              Root component
    │   ├── index.css            Design tokens and responsive styling
    │   ├── api/
    │   │   └── bookingApi.js    Centralized API client for slots and bookings
    │   ├── components/
    │   │   ├── Header.jsx              Top navigation and branding
    │   │   ├── ParentDetailsForm.jsx   Parent/student inputs and live validation
    │   │   ├── TimezoneDatePicker.jsx  Timezone select and 7-day date strip
    │   │   ├── SlotPicker.jsx          Slot selection grid and empty states
    │   │   ├── BookingConfirmation.jsx Success screen with meeting link
    │   │   └── AlertBanner.jsx         Dismissible notifications
    │   ├── pages/
    │   │   └── BookingPage.jsx  Main state coordinator
    │   └── utils/
    │       └── dateUtils.js     Date calculations and display formatting
    └── package.json             Vite and React dependencies
```

---

## 6. Booking Flow

1. **Enter Details:** Parent enters their name, email, and child's name.
2. **Select Date & Timezone:** The parent's timezone is auto-detected. The parent selects a convenient date from a 7-day strip (tomorrow through tomorrow + 6 days).
3. **Choose Slot:** Available slots are fetched dynamically from `/api/v1/slots` and displayed in the parent's local time (e.g., `5:30 AM – 6:30 AM EDT`).
4. **Confirm Booking:** The frontend submits the booking with the canonical UTC ISO string.
5. **Confirmation & Class Link:** The parent immediately receives a confirmation screen with their booking reference, session time, assigned instructor label, and a one-click copyable classroom meeting link.

---

## 7. Mentor Assignment Logic

When a parent books a slot:
1. **Active Mentors:** The system checks all active mentors (`is_active = true`).
2. **Slot Conflict Check:** Mentors already booked at that exact `slot_utc` are excluded.
3. **Daily Cap Check:** Mentors who have already reached **2 confirmed bookings** on that **IST calendar date** (`DATE(slot_utc AT TIME ZONE 'Asia/Kolkata')`) are excluded.
4. **Allocation:** An eligible mentor is deterministically selected (`ORDER BY id ASC`).
5. **Exhaustion (409):** If all 10 mentors are booked or capped for that slot, the API returns `409 Conflict`.
6. **Concurrency Safety:** Transactions execute at PostgreSQL `SERIALIZABLE` isolation level. If a conflict occurs, the system automatically retries once before failing gracefully.

---

## 8. Timezone and DST Handling

- **Anchored in India:** All mentor availability is anchored between **15:00 and 21:00 IST** (7 one-hour slots per day), balancing India working hours with US/UK waking hours.
- **Canonical Storage:** All bookings are stored in PostgreSQL as `TIMESTAMPTZ` in UTC.
- **Standard Library Precision:** Conversions use Python's built-in `zoneinfo` and `tzdata==2025.2`, accurately reflecting US Daylight Saving Time (e.g., EDT UTC-4 vs EST UTC-5) and UK Daylight Saving Time (BST UTC+1 vs GMT UTC+0).
- **Zero Frontend Skew:** The frontend submits the server's `utc_iso` string verbatim, eliminating differences caused by client-side clock drift.

---

## 9. Database Design

```sql
-- Mentors Table (10 Seeded Mentors based in India)
CREATE TABLE mentors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Kolkata',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Bookings Table
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

## 10. API Endpoints

### `GET /api/v1/health`
Health check endpoint returning system status.

### `GET /api/v1/slots`
Returns available slots for an IST date formatted in the parent's timezone.
- **Query Params:**
  - `date`: `YYYY-MM-DD` (must be within tomorrow through tomorrow + 6 days in IST)
  - `timezone`: Valid IANA identifier (e.g., `America/New_York`)
- **Response:**
  ```json
  {
    "date": "2026-09-28",
    "timezone": "America/New_York",
    "slots": [
      {
        "utc_iso": "2026-09-28T09:30:00+00:00",
        "local_display": "2026-09-28T05:30:00-04:00"
      }
    ]
  }
  ```

### `POST /api/v1/bookings`
Creates a confirmed booking and automatically assigns an eligible mentor.
- **Request Body:**
  ```json
  {
    "parent_name": "Sarah Connor",
    "parent_email": "sarah@example.com",
    "child_name": "John Connor",
    "parent_timezone": "America/New_York",
    "slot_utc": "2026-09-28T09:30:00+00:00"
  }
  ```
- **Responses:**
  - `201 Created`: Booking confirmed with assigned mentor and dummy class link.
  - `409 Conflict`: No mentors available for the requested slot.
  - `422 Unprocessable Entity`: Validation failure (bad timezone, slot not on hour, out of booking window).
  - `503 Service Unavailable`: Concurrent transaction conflict after retry.

### `GET /api/v1/bookings/{id}`
Retrieves a booking record by ID. Returns `404 Not Found` if the record does not exist.

### `GET /api/v1/mentor/bookings`
Retrieves confirmed bookings for mentors. Accepts an optional `?mentor_id=<id>` query parameter to filter by mentor.

---

## 11. Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/codeyoung_booking
CORS_ORIGINS=["http://localhost:5173"]
ENVIRONMENT=development
```

### Frontend (`frontend/.env` or `frontend/.env.local`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 12. Local Setup

### Prerequisites
- **Python:** 3.10+ (tested on Python 3.13)
- **Node.js:** 18+ (tested on Node.js 20+)
- **PostgreSQL:** 12+ (tested on PostgreSQL 18)

### Database Initialization
1. Create a local PostgreSQL database:
   ```sql
   CREATE DATABASE codeyoung_booking;
   ```

---

## 13. Running Backend

1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Update DATABASE_URL with your PostgreSQL credentials
   ```

4. Initialize database schema and seed mentors:
   ```bash
   python -m db.init_db
   python -m db.seed
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   API interactive docs available at: `http://localhost:8000/docs`

---

## 14. Running Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Vite development server:
   ```bash
   npm run dev
   ```
   Access the web application at: `http://localhost:5173`

---

## 15. Running Tests

### Backend Unit Tests
```bash
cd backend
pytest -v
```
Runs 23 unit tests verifying IST anchor generation, UTC conversions, US and UK DST transitions, date boundary integrity, and IANA timezone validation.

### Frontend Quality Checks
```bash
cd frontend
npm run lint     # Oxlint static check (0 errors, 0 warnings)
npm run build    # Production build verification
```

---

## 16. Design Decisions / Assumptions

- **Class Duration (Product Assumption):** Classes are assumed to be 1 hour long (15:00–16:00, 16:00–17:00, ..., 21:00–22:00 IST).
- **Booking Window (Product Assumption):** Parents can book from tomorrow through tomorrow + 6 days (7 calendar days). Same-day bookings are omitted to prevent past-slot booking issues.
- **Mentor Day Boundary (Engineering Inference):** The daily 2-class limit is measured according to the mentor's local calendar date in `Asia/Kolkata`.
- **Classroom Link Delivery (Specification Wording):**
  > *The system generates and stores a dummy class link for each confirmed booking. The link is available to the parent through the booking confirmation flow and to the mentor through the mentor booking endpoint. Actual email/notification delivery is intentionally outside the scope of this assignment.*
- **Database Migrations:** Schema creation uses `SQLAlchemy Base.metadata.create_all()` via `db/init_db.py`. Alembic was deliberately omitted to keep the assessment submission self-contained and reproducible.
- **Parent-Facing Instructor Label:** The parent confirmation screen shows "Dedicated Codeyoung Mentor" rather than internal mentor IDs or emails, while retaining internal IDs on the backend.

---

## 17. Deliberately Out-of-Scope Features

To keep the application focused on the core scheduling challenge, the following features were intentionally not built:
- No user authentication or session management (passwords, JWT, OAuth).
- No actual email or SMS notifications (SendGrid, SES, Twilio).
- No external calendar synchronization (Google Calendar, Outlook iCal).
- No live video streaming infrastructure (WebRTC, Zoom).
- No payment processing or billing integration.
- No administrative CRM portal.

---

## 18. Known Limitations

- **Fixed Daily Window:** Slots are strictly locked to 15:00–21:00 IST anchors.
- **Single Mentor Timezone:** All seeded mentors operate in `Asia/Kolkata`.
- **Single-Node Serializability:** Concurrency protection relies on PostgreSQL `SERIALIZABLE` isolation. In a multi-region distributed database, a distributed lock or reservation queue would be recommended.
