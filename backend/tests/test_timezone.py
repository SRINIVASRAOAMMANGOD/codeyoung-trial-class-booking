"""
tests/test_timezone.py — Pytest tests for the timezone service.

These tests verify the core timezone conversion logic that underpins
all slot generation and display throughout the system.

No database access is required — these are pure unit tests.
"""

from datetime import date, timedelta

import pytest
from zoneinfo import ZoneInfo

from services.timezone_service import (
    SLOT_HOURS_IST,
    generate_ist_anchors,
    get_ist_date_today,
    ist_anchor_to_utc,
    utc_to_local_display,
    validate_timezone,
)

IST = ZoneInfo("Asia/Kolkata")


# ─── Slot anchor generation ───────────────────────────────────────────────────

class TestGenerateIstAnchors:
    def test_returns_seven_slots(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        assert len(anchors) == 7

    def test_starts_at_1500_ist(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        assert anchors[0].hour == 15
        assert anchors[0].minute == 0

    def test_ends_at_2100_ist(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        assert anchors[-1].hour == 21
        assert anchors[-1].minute == 0

    def test_all_anchors_are_ist_aware(self):
        anchors = generate_ist_anchors(date(2025, 6, 15))
        assert all(str(a.tzinfo) == "Asia/Kolkata" for a in anchors)

    def test_consecutive_slots_are_one_hour_apart(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        for i in range(1, len(anchors)):
            delta = anchors[i] - anchors[i - 1]
            assert delta.total_seconds() == 3600

    def test_slot_hours_match_constant(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        assert [a.hour for a in anchors] == SLOT_HOURS_IST


# ─── IST → UTC conversion ─────────────────────────────────────────────────────

class TestIstAnchorToUtc:
    """IST is UTC+5:30. Subtracting 5h30m gives UTC."""

    def test_1500_ist_to_0930_utc(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        utc = ist_anchor_to_utc(anchors[0])
        assert utc.hour == 9
        assert utc.minute == 30

    def test_2100_ist_to_1530_utc(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        utc = ist_anchor_to_utc(anchors[-1])
        assert utc.hour == 15
        assert utc.minute == 30

    def test_result_is_utc(self):
        anchors = generate_ist_anchors(date(2025, 1, 15))
        utc = ist_anchor_to_utc(anchors[0])
        assert utc.utcoffset().total_seconds() == 0


# ─── UTC → parent local display ───────────────────────────────────────────────

class TestUtcToLocalDisplay:
    """
    All tests use a fixed UTC datetime (2025-01-15 09:30:00 UTC)
    which corresponds to 15:00 IST (first slot).
    """

    def _first_slot_utc(self, d=date(2025, 1, 15)):
        return ist_anchor_to_utc(generate_ist_anchors(d)[0])

    def test_new_york_winter_est(self):
        """January: EST (UTC-5). 09:30 UTC = 04:30 EST."""
        local = utc_to_local_display(self._first_slot_utc(), "America/New_York")
        assert local.hour == 4
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == -5 * 3600

    def test_new_york_summer_edt(self):
        """July: EDT (UTC-4). 09:30 UTC = 05:30 EDT."""
        local = utc_to_local_display(self._first_slot_utc(date(2025, 7, 15)), "America/New_York")
        assert local.hour == 5
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == -4 * 3600

    def test_london_winter_gmt(self):
        """January: GMT (UTC+0). 09:30 UTC = 09:30 GMT."""
        local = utc_to_local_display(self._first_slot_utc(), "Europe/London")
        assert local.hour == 9
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == 0

    def test_london_summer_bst(self):
        """July: BST (UTC+1). 09:30 UTC = 10:30 BST."""
        local = utc_to_local_display(self._first_slot_utc(date(2025, 7, 15)), "Europe/London")
        assert local.hour == 10
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == 3600

    def test_us_dst_spring_forward_2025(self):
        """
        2025-03-09: US clocks spring forward at 2 AM (EST -> EDT).
        09:30 UTC on this date is after the transition, so EDT applies.
        09:30 UTC = 05:30 EDT.
        """
        utc = ist_anchor_to_utc(generate_ist_anchors(date(2025, 3, 9))[0])
        local = utc_to_local_display(utc, "America/New_York")
        assert local.hour == 5
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == -4 * 3600  # EDT

    def test_uk_dst_spring_forward_2025(self):
        """
        2025-03-30: UK clocks spring forward at 1 AM (GMT -> BST).
        09:30 UTC on this date is after the transition, so BST applies.
        09:30 UTC = 10:30 BST.
        """
        utc = ist_anchor_to_utc(generate_ist_anchors(date(2025, 3, 30))[0])
        local = utc_to_local_display(utc, "Europe/London")
        assert local.hour == 10
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == 3600  # BST

    def test_last_slot_stays_same_date_for_ny(self):
        """21:00 IST = 15:30 UTC. In any US/UK timezone this stays same calendar date."""
        utc = ist_anchor_to_utc(generate_ist_anchors(date(2025, 6, 15))[-1])
        local = utc_to_local_display(utc, "America/New_York")
        assert local.date() == date(2025, 6, 15)

    def test_last_slot_stays_same_date_for_london(self):
        utc = ist_anchor_to_utc(generate_ist_anchors(date(2025, 6, 15))[-1])
        local = utc_to_local_display(utc, "Europe/London")
        assert local.date() == date(2025, 6, 15)


# ─── Timezone validation ──────────────────────────────────────────────────────

class TestValidateTimezone:
    def test_valid_iana_zones(self):
        assert validate_timezone("America/New_York") is True
        assert validate_timezone("Europe/London") is True
        assert validate_timezone("Asia/Kolkata") is True
        assert validate_timezone("America/Los_Angeles") is True
        assert validate_timezone("America/Chicago") is True
        assert validate_timezone("Europe/Paris") is True

    def test_empty_string_is_invalid(self):
        assert validate_timezone("") is False

    def test_nonsense_string_is_invalid(self):
        assert validate_timezone("NotAZone") is False
        assert validate_timezone("not/a/timezone") is False

    def test_est_is_valid_iana_fixed_offset(self):
        """
        'EST' is a valid IANA fixed-offset zone (always UTC-5, no DST).
        It is accepted by zoneinfo. We prefer 'America/New_York' for DST
        correctness, but we do not explicitly reject 'EST'.
        """
        assert validate_timezone("EST") is True


# ─── Booking window helper ────────────────────────────────────────────────────

class TestGetIstDateToday:
    def test_returns_a_date(self):
        result = get_ist_date_today()
        assert isinstance(result, date)

    def test_tomorrow_is_one_day_ahead(self):
        today = get_ist_date_today()
        tomorrow = today + timedelta(days=1)
        assert (tomorrow - today).days == 1
