# Development Guide

## Prerequisites

Install Python 3.13 or compatible Python, Node.js/npm, and PostgreSQL. Python versions are pinned in `backend/requirements.txt`. A PostgreSQL connection is required by the current backend tests and application.

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env`. `EMAIL_BACKEND=console` is suitable for local simulation. SMTP mode additionally uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, and `SMTP_USE_TLS`.

```powershell
python -m db.init_db
python -m db.seed
uvicorn main:app --reload --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:8000`; set `VITE_API_BASE_URL` when needed. Vite normally serves `http://localhost:5173`.

## Verification

```powershell
cd backend
python -m pytest
cd ..\frontend
npm run lint
npm run build
```

On 2026-09-27, 53 backend tests passed, the frontend build passed, and lint exited successfully with one unused catch-parameter warning.

## Troubleshooting

- Database errors: confirm PostgreSQL is running, the database exists, and `DATABASE_URL` is correct.
- Missing tables/courses: run `python -m db.init_db` and the applicable migration/seed scripts.
- Frontend API errors: confirm port 8000 and `VITE_API_BASE_URL`.
- SMTP errors: use console mode locally or configure `SMTP_HOST` and related settings.
- No slots: confirm the date is tomorrow through seven days ahead in IST and capacity remains.
- Admin access: current demo routes are intentionally unauthenticated.
