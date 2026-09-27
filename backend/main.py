"""
main.py — FastAPI application entry point.

Registers routers, configures CORS, and exposes the health check endpoint.
Business logic lives in services/, not here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

settings = get_settings()

app = FastAPI(
    title="Codeyoung Trial Class Booking API",
    description="API for booking trial coding classes. Handles mentor assignment and timezone-aware scheduling.",
    version="1.0.0",
)

# CORS: allow the React frontend (running on localhost:5173 in dev) to call the API.
# In production this would be restricted to the deployed frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server default port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Returns a simple OK response to confirm the API is running."""
    return {"status": "ok", "env": settings.app_env}


from routers import admin, bookings, slots, courses

app.include_router(slots.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
