"""
db/migrate_phase_a.py — Phase A migration for courses.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from database import engine

def migrate_phase_a() -> None:
    print("=" * 60)
    print("PHASE A MIGRATION: Adding Courses")
    print("=" * 60)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.begin() as conn:
        if "courses" not in tables:
            print("Creating 'courses' table...")
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS courses (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(150) NOT NULL UNIQUE,
                        description VARCHAR(500) NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
            )
        else:
            print("  -> 'courses' table already exists.")

        print("Seeding default courses...")
        seed_courses = [
            ("Coding Fundamentals", "Build a strong foundation in programming and computational thinking through guided exercises."),
            ("Python Programming", "Learn Python through practical, beginner-friendly projects and problem-solving challenges."),
            ("Web Development", "Create websites and understand the fundamentals of modern web development with HTML, CSS, and JavaScript."),
            ("AI & Robotics", "Explore AI concepts, automation and beginner-friendly robotics in hands-on interactive projects."),
        ]
        
        for name, desc in seed_courses:
            conn.execute(
                text(
                    """
                    INSERT INTO courses (name, description, is_active)
                    VALUES (:name, :desc, TRUE)
                    ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;
                    """
                ),
                {"name": name, "desc": desc}
            )

        booking_cols = [c["name"] for c in inspector.get_columns("bookings")]
        
        if "course_id" not in booking_cols:
            print("Adding 'course_id' to bookings and backfilling...")
            result = conn.execute(text("SELECT id FROM courses WHERE name = 'Coding Fundamentals' LIMIT 1;"))
            default_course_id = result.scalar()

            conn.execute(
                text(
                    """
                    ALTER TABLE bookings
                    ADD COLUMN course_id INTEGER REFERENCES courses(id) ON DELETE RESTRICT;
                    """
                )
            )
            
            conn.execute(
                text("UPDATE bookings SET course_id = :cid WHERE course_id IS NULL"),
                {"cid": default_course_id}
            )
            
            conn.execute(
                text("ALTER TABLE bookings ALTER COLUMN course_id SET NOT NULL;")
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_bookings_course_id ON bookings(course_id);")
            )
            print("  -> 'course_id' added and backfilled.")
        else:
            print("  -> 'course_id' already on bookings.")

if __name__ == "__main__":
    migrate_phase_a()
