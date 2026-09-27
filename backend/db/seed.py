"""
db/seed.py — Seeds 10 mentor records into the database.

Run after init_db.py:
    python -m db.seed           (from backend/ directory)

Idempotency guarantee:
    Before inserting each mentor, we check if a mentor with that email
    already exists. If so, the record is skipped. This makes the seed
    safe to run multiple times without creating duplicate rows.

Mentor data:
    10 mentors based in India (Asia/Kolkata timezone).
    Names and emails are realistic but fictional — for demonstration only.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.mentor import Mentor

MENTORS = [
    {"name": "Priya Sharma",    "email": "priya.sharma@democodeyoung.com"},
    {"name": "Arjun Mehta",     "email": "arjun.mehta@democodeyoung.com"},
    {"name": "Divya Nair",      "email": "divya.nair@democodeyoung.com"},
    {"name": "Rohan Gupta",     "email": "rohan.gupta@democodeyoung.com"},
    {"name": "Sneha Iyer",      "email": "sneha.iyer@democodeyoung.com"},
    {"name": "Vikram Pillai",   "email": "vikram.pillai@democodeyoung.com"},
    {"name": "Anjali Desai",    "email": "anjali.desai@democodeyoung.com"},
    {"name": "Karan Joshi",     "email": "karan.joshi@democodeyoung.com"},
    {"name": "Meera Reddy",     "email": "meera.reddy@democodeyoung.com"},
    {"name": "Aditya Verma",    "email": "aditya.verma@democodeyoung.com"},
]


def seed_mentors() -> None:
    db = SessionLocal()
    try:
        inserted = 0
        skipped = 0

        for mentor_data in MENTORS:
            # Check by email (the unique natural key) to ensure idempotency.
            existing = (
                db.query(Mentor)
                .filter(Mentor.email == mentor_data["email"])
                .first()
            )
            if existing:
                print(f"  [skip]   {mentor_data['name']} already exists")
                skipped += 1
            else:
                mentor = Mentor(
                    name=mentor_data["name"],
                    email=mentor_data["email"],
                    timezone="Asia/Kolkata",
                    is_active=True,
                )
                db.add(mentor)
                print(f"  [insert] {mentor_data['name']}")
                inserted += 1

        db.commit()
        print(f"\nSeed complete: {inserted} inserted, {skipped} skipped.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding mentors...")
    seed_mentors()
