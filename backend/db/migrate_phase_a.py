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
                        age_range VARCHAR(50) NOT NULL DEFAULT 'All Ages',
                        level VARCHAR(50) NOT NULL DEFAULT 'All Levels',
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )
            )
        else:
            print("  -> 'courses' table already exists.")

        course_cols = [c["name"] for c in inspector.get_columns("courses")]
        if "age_range" not in course_cols:
            conn.execute(text("ALTER TABLE courses ADD COLUMN age_range VARCHAR(50) NOT NULL DEFAULT 'All Ages';"))
        if "level" not in course_cols:
            conn.execute(text("ALTER TABLE courses ADD COLUMN level VARCHAR(50) NOT NULL DEFAULT 'All Levels';"))

        print("Seeding default courses...")
        seed_courses = [
            ("Coding Fundamentals", "Build a strong foundation in programming and computational thinking through guided exercises.", "Ages 6–10", "Beginner"),
            ("Python Programming", "Learn Python through practical, beginner-friendly projects and problem-solving challenges.", "Ages 10–16", "Beginner – Intermediate"),
            ("Web Development", "Create websites and understand the fundamentals of modern web development with HTML, CSS, and JavaScript.", "Ages 12–18", "Intermediate"),
            ("AI & Robotics", "Explore AI concepts, automation and beginner-friendly robotics in hands-on interactive projects.", "Ages 10–16", "Intermediate"),
            ("Game Development", "Design and code your own interactive 2D and 3D games from scratch.", "Ages 10–16", "Intermediate"),
            ("App Development", "Learn to build functional mobile applications for iOS and Android.", "Ages 12–18", "Advanced"),
            ("Data & Analytics", "Discover how to collect, visualize, and understand data through code.", "Ages 14–18", "Advanced"),
        ]
        
        for name, desc, age_range, level in seed_courses:
            conn.execute(
                text(
                    """
                    INSERT INTO courses (name, description, age_range, level, is_active)
                    VALUES (:name, :desc, :age_range, :level, TRUE)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        age_range = EXCLUDED.age_range,
                        level = EXCLUDED.level;
                    """
                ),
                {"name": name, "desc": desc, "age_range": age_range, "level": level}
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
