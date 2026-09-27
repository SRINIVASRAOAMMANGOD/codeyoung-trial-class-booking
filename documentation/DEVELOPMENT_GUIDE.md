# Development Guide

## Prerequisites

Install Python 3.13 or compatible Python, Node.js/npm, and PostgreSQL. Python versions are pinned in `backend/requirements.txt`. A PostgreSQL connection is strictly required by the current backend application and its test suite.

## Backend Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Ensure you set `DATABASE_URL` appropriately in `.env`. 
By default, `EMAIL_BACKEND=console` is set, which is suitable for local demonstration as it logs emails to the terminal instead of sending them. If you wish to test real delivery, switch to `EMAIL_BACKEND=smtp` and configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, and `SMTP_USE_TLS`.

### Database Initialization

To create the tables and apply initial seed data/migrations:

```powershell
python -m db.init_db
python -m db.seed
python -m db.migrate_phase_a
```

### Running the Server

```powershell
uvicorn main:app --reload --port 8000
```
FastAPI documentation will be accessible at `http://localhost:8000/docs`.

## Frontend Setup

In a new terminal, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

The frontend API calls default to `http://localhost:8000`; set `VITE_API_BASE_URL` if your backend is hosted elsewhere. Vite normally serves the UI at `http://localhost:5173`.

## Verification

```powershell
cd backend
python -m pytest -v
cd ..\frontend
npm run lint
npm run build
```

*Expected latest baseline: 71 backend tests pass (with 11 warnings). Frontend lint exits successfully with one expected warning. Frontend build succeeds.*

## Troubleshooting

- **Database Errors**: Confirm PostgreSQL is running, the target database exists, and `DATABASE_URL` is perfectly formed.
- **Missing Courses or Constraints**: Run `python -m db.init_db` followed by `db.seed` and `db.migrate_phase_a`.
- **Frontend API Errors**: Confirm the backend is actually running on port 8000, and CORS is not blocking your Vite domain.
- **SMTP/Email Errors**: If console output works but emails aren't arriving, verify your SMTP credentials and TLS settings.
- **No Available Slots**: Confirm the selected date falls within the "tomorrow through seven days ahead" window in IST, and that the seeded mentors haven't already hit their 2-class daily capacity limit for that date.
- **Admin Authentication**: The current demo internal routes are intentionally unauthenticated.
