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

*README will be expanded with full setup, architecture, API reference, design decisions, and assumptions in Phase 10.*
