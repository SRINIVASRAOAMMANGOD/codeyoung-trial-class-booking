# Codeyoung Trial Class Booking System

> Recruitment assessment submission for Codeyoung.
> Full-stack web application for booking trial coding classes.

---

## Overview

A web application that allows parents to book a free trial coding class with a Codeyoung mentor. The system handles timezone-aware scheduling (parents in US/UK, mentors in India), automatic mentor assignment, DST-safe time display, and dummy class link generation.

*Full documentation will be completed in Phase 10.*

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite (JavaScript) |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Testing | pytest |

---

## Quick Start (Development)


> Prerequisites: Python 3.9+, Node.js 18+, PostgreSQL 12+

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Edit DATABASE_URL in .env
python -m db.init_db          # Create database tables
python -m db.seed             # Seed 10 mentor records
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env.local    # Edit VITE_API_BASE_URL if needed
npm install
npm run dev
```

---

## Assumptions and Limitations

- **Database migrations:** Tables are created using `SQLAlchemy Base.metadata.create_all()`
  via `db/init_db.py` rather than Alembic. This is an intentional scope decision for this
  assessment — the schema is defined once and does not require incremental migration support.
  In a production system, Alembic would be the appropriate tool.

- **Booking window:** 15:00–22:00 IST, 1-hour slots (product decision, not an assignment
  requirement). Chosen to balance India mentor hours with US/UK parent availability.

- **Booking dates:** Parents may book from tomorrow through 6 days after tomorrow (7
  calendar dates). Same-day booking is excluded to avoid past-slot complexity.

- **Authentication:** None. Not required by the assignment.

- **Email delivery:** Not implemented. The dummy class link is shown on the confirmation
  screen only. In production, it would be emailed to both parent and mentor.

---

*README will be expanded with full architecture, API reference, and design decisions in Phase 10.*
