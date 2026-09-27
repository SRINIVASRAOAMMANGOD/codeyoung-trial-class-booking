"""
db/migrate_phase10.py — Lossless migration to normalize parents table and link bookings.

Performs:
  1. Creates the `parents` table if it does not exist.
  2. Populates `parents` using distinct parent records from existing `bookings`.
  3. Adds `parent_id` foreign key column to `bookings` if missing.
  4. Backfills `parent_id` by matching parent email.
  5. Verifies that zero NULL `parent_id` rows exist (aborts before dropping if invalid).
  6. Enforces NOT NULL constraint on `bookings.parent_id`.
  7. Creates index on `bookings.parent_id`.
  8. Safely drops legacy `parent_name` and `parent_email` columns from `bookings`.

This migration is 100% idempotent and preserves all existing booking data.
"""

import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from database import engine


def migrate_phase10() -> None:
    print("=" * 60)
    print("PHASE 10 MIGRATION: Normalizing Parent Entity")
    print("=" * 60)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Current tables in database: {tables}")

    with engine.begin() as conn:
        # Step 1: Create parents table if not present
        if "parents" not in tables:
            print("Creating 'parents' table...")
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS parents (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(150) NOT NULL UNIQUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS ix_parents_email ON parents(email);
                    """
                )
            )
            print("  -> 'parents' table created successfully.")
        else:
            print("  -> 'parents' table already exists.")

        # Re-inspect columns on bookings
        booking_cols = [c["name"] for c in inspector.get_columns("bookings")]
        print(f"Current columns in 'bookings': {booking_cols}")

        # Step 2: Populate parents table from existing bookings if legacy columns exist
        if "parent_email" in booking_cols:
            print("Populating 'parents' from existing bookings...")
            result = conn.execute(
                text(
                    """
                    INSERT INTO parents (name, email, created_at)
                    SELECT parent_name, LOWER(TRIM(parent_email)), MIN(created_at)
                    FROM bookings
                    WHERE parent_email IS NOT NULL AND TRIM(parent_email) != ''
                    GROUP BY parent_name, LOWER(TRIM(parent_email))
                    ON CONFLICT (email) DO NOTHING;
                    """
                )
            )
            print(f"  -> Inserted/ensured parents from existing bookings.")

        # Step 3: Add parent_id column to bookings if not present
        if "parent_id" not in booking_cols:
            print("Adding 'parent_id' column to 'bookings'...")
            conn.execute(
                text(
                    """
                    ALTER TABLE bookings
                    ADD COLUMN parent_id INTEGER REFERENCES parents(id) ON DELETE RESTRICT;
                    """
                )
            )
            print("  -> 'parent_id' column added.")

        # Step 4: Backfill parent_id if legacy parent_email exists
        if "parent_email" in booking_cols:
            print("Backfilling 'parent_id' in 'bookings'...")
            conn.execute(
                text(
                    """
                    UPDATE bookings b
                    SET parent_id = p.id
                    FROM parents p
                    WHERE LOWER(TRIM(b.parent_email)) = p.email
                      AND b.parent_id IS NULL;
                    """
                )
            )
            print("  -> 'parent_id' backfilled.")

        # Step 5: Verify all bookings have a valid parent_id
        null_count = conn.execute(
            text("SELECT COUNT(*) FROM bookings WHERE parent_id IS NULL;")
        ).scalar()

        if null_count > 0:
            raise RuntimeError(
                f"MIGRATION ERROR: {null_count} bookings have NULL parent_id! Aborting."
            )
        print("  -> Integrity check passed: 0 NULL parent_id values.")

        # Step 6: Enforce NOT NULL on parent_id
        print("Enforcing NOT NULL on 'bookings.parent_id'...")
        conn.execute(
            text("ALTER TABLE bookings ALTER COLUMN parent_id SET NOT NULL;")
        )

        # Step 7: Create index on bookings(parent_id)
        print("Ensuring index on 'bookings.parent_id'...")
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_bookings_parent_id ON bookings(parent_id);")
        )

        # Step 8: Safely drop legacy columns if present
        if "parent_name" in booking_cols:
            print("Dropping legacy 'parent_name' column from 'bookings'...")
            conn.execute(text("ALTER TABLE bookings DROP COLUMN parent_name;"))

        if "parent_email" in booking_cols:
            print("Dropping legacy 'parent_email' column from 'bookings'...")
            conn.execute(text("ALTER TABLE bookings DROP COLUMN parent_email;"))

        print("=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)


def verify_migration() -> None:
    print("\n--- Post-Migration Database Verification ---")
    with engine.connect() as conn:
        mentor_count = conn.execute(text("SELECT COUNT(*) FROM mentors;")).scalar()
        booking_count = conn.execute(text("SELECT COUNT(*) FROM bookings;")).scalar()
        parent_count = conn.execute(text("SELECT COUNT(*) FROM parents;")).scalar()

        print(f"Mentors in DB:  {mentor_count}")
        print(f"Parents in DB:  {parent_count}")
        print(f"Bookings in DB: {booking_count}")

        # Check sample parent and booking linkage
        if booking_count > 0:
            sample = conn.execute(
                text(
                    """
                    SELECT b.id, b.child_name, b.slot_utc, b.mentor_id,
                           p.id as parent_id, p.name as parent_name, p.email as parent_email
                    FROM bookings b
                    JOIN parents p ON b.parent_id = p.id
                    LIMIT 5;
                    """
                )
            ).fetchall()
            print("\nSample linked bookings:")
            for row in sample:
                print(f"  Booking #{row.id}: Child={row.child_name!r}, Parent={row.parent_name!r} ({row.parent_email}), Mentor={row.mentor_id}, Slot={row.slot_utc}")


if __name__ == "__main__":
    migrate_phase10()
    verify_migration()
