"""
services/email_service.py — Notification service for trial class bookings.

Supports two backends:
  - 'console' (default): Formats full email content and outputs to console log.
    Simulates delivery safely for local development and assessment evaluation.
  - 'smtp': Delivers real emails via standard library `smtplib`.

Generates two notifications per confirmed booking:
  1. Parent notification: Formatted in the parent's requested timezone.
  2. Mentor notification: Formatted in India Standard Time (Asia/Kolkata).
"""

import logging
import smtplib
from collections import deque
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from config import get_settings
from models.booking import Booking

logger = logging.getLogger(__name__)

# Thread-safe in-memory log of recent notifications for testing and verification
_recent_emails: deque[dict] = deque(maxlen=50)


class EmailConfigurationError(ValueError):
    """Raised when email settings are incomplete or invalid (e.g. SMTP_HOST missing in smtp mode)."""
    pass


def get_recent_emails() -> list[dict]:
    """Retrieve in-memory copy of recently dispatched emails (for tests and verification)."""
    return list(_recent_emails)


def clear_recent_emails() -> None:
    """Clear in-memory email log."""
    _recent_emails.clear()


def format_slot_datetime(slot_utc, tz_identifier: str) -> tuple[str, str, str]:
    """
    Convert canonical slot_utc to local date, time window, and timezone label.
    Returns: (date_str, time_str, tz_label)
    Example: ('Monday, September 28, 2026', '05:30 AM – 06:30 AM', 'America/New_York (UTC-04:00)')
    """
    tz = ZoneInfo(tz_identifier)
    local_dt = slot_utc.astimezone(tz)
    end_dt = local_dt + timedelta(hours=1)

    date_str = local_dt.strftime("%A, %B %d, %Y")
    start_time = local_dt.strftime("%I:%M %p")
    end_time = end_dt.strftime("%I:%M %p")
    time_window = f"{start_time} – {end_time}"

    offset = local_dt.strftime("%z")
    offset_formatted = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC"
    tz_label = f"{tz_identifier} ({offset_formatted})"

    return date_str, time_window, tz_label


def build_parent_email_content(booking: Booking) -> dict:
    """
    Build parent-specific notification payload formatted in parent's timezone.
    """
    parent_name = booking.parent.name if booking.parent else booking.parent_name
    parent_email = booking.parent.email if booking.parent else booking.parent_email
    mentor_name = booking.mentor.name if booking.mentor else "Assigned Codeyoung Mentor"

    date_str, time_str, tz_label = format_slot_datetime(
        booking.slot_utc,
        booking.parent_timezone,
    )

    subject = f"Confirmed: 1-on-1 Coding Trial Class for {booking.child_name}"

    body_text = f"""Hello {parent_name},

Great news! Your 1-on-1 trial coding class for {booking.child_name} has been successfully scheduled with Codeyoung.

SESSION DETAILS:
--------------------------------------------------
Student:          {booking.child_name}
Course:           {booking.course.name if booking.course else "Unknown Course"}
Assigned Mentor:  {mentor_name}
Date:             {date_str}
Scheduled Time:   {time_str}
Timezone:         {tz_label}
Booking Ref:      {booking.id}

CLASSROOM MEETING LINK:
--------------------------------------------------
{booking.class_link}

Please save this link. You and {booking.child_name} can join the classroom directly at the scheduled start time.

Happy Learning,
The Codeyoung Team

ADMIN
Srinivas
"""

    return {
        "recipient": parent_email,
        "recipient_type": "Parent",
        "recipient_name": parent_name,
        "subject": subject,
        "body_text": body_text,
        "class_date": date_str,
        "class_time": time_str,
        "timezone": tz_label,
        "class_link": booking.class_link,
        "child_name": booking.child_name,
        "mentor_name": mentor_name,
    }


def build_mentor_email_content(booking: Booking) -> dict:
    """
    Build mentor-specific notification payload formatted in Asia/Kolkata (IST).
    """
    mentor_name = booking.mentor.name if booking.mentor else "Mentor"
    mentor_email = booking.mentor.email if booking.mentor else ""
    parent_name = booking.parent.name if booking.parent else booking.parent_name

    date_str, time_str, tz_label = format_slot_datetime(
        booking.slot_utc,
        "Asia/Kolkata",
    )

    subject = f"New Trial Class Assignment: {booking.child_name} on {date_str}"

    body_text = f"""Hello {mentor_name},

You have been assigned to conduct a 1-on-1 trial coding demo class.

SESSION DETAILS:
--------------------------------------------------
Student:          {booking.child_name}
Course:           {booking.course.name if booking.course else "Unknown Course"}
Parent:           {parent_name}
Date:             {date_str}
Scheduled Time:   {time_str}
Timezone:         {tz_label}
Booking Ref:      {booking.id}

CLASSROOM MEETING LINK:
--------------------------------------------------
{booking.class_link}

Please ensure you join 5 minutes before the session starts to welcome the student.

Codeyoung Mentor Operations

ADMIN
Srinivas
"""

    return {
        "recipient": mentor_email,
        "recipient_type": "Mentor",
        "recipient_name": mentor_name,
        "subject": subject,
        "body_text": body_text,
        "class_date": date_str,
        "class_time": time_str,
        "timezone": tz_label,
        "class_link": booking.class_link,
        "child_name": booking.child_name,
        "parent_name": parent_name,
    }


def _dispatch_console(email_data: dict) -> None:
    """Log formatted email simulation to console and record in in-memory queue."""
    log_output = f"""
================================================================================
[EMAIL NOTIFICATION — CONSOLE DELIVERY SIMULATION]
Recipient:      {email_data['recipient']} ({email_data['recipient_type']}: {email_data['recipient_name']})
Subject:        {email_data['subject']}
Scheduled Date: {email_data['class_date']}
Time Window:    {email_data['class_time']} ({email_data['timezone']})
Classroom Link: {email_data['class_link']}
Delivery Note:  EMAIL_BACKEND=console is active. Simulated delivery (no external email sent).
================================================================================
{email_data['body_text'].strip()}
================================================================================
"""
    print(log_output)
    logger.info("Console email dispatched to %s [%s]", email_data['recipient'], email_data['recipient_type'])
    _recent_emails.append(email_data)


def _dispatch_smtp(email_data: dict) -> None:
    """Send real email via Python smtplib."""
    settings = get_settings()
    if not settings.smtp_host:
        raise EmailConfigurationError("SMTP_HOST must be configured when EMAIL_BACKEND=smtp")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = email_data["subject"]
    msg["From"] = settings.smtp_from
    msg["To"] = email_data["recipient"]

    msg.attach(MIMEText(email_data["body_text"], "plain", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)

    logger.info("SMTP email dispatched to %s", email_data['recipient'])
    _recent_emails.append(email_data)


def dispatch_email(email_data: dict) -> None:
    """Route email to configured backend."""
    settings = get_settings()
    backend = settings.email_backend.lower()

    if backend == "smtp":
        _dispatch_smtp(email_data)
    else:
        # Default: console simulation
        _dispatch_console(email_data)


def send_booking_notifications(booking: Booking) -> dict[str, bool]:
    """
    Send parent and mentor notifications for a confirmed booking.

    Guarantees:
      - Does not re-raise delivery errors to the caller so committed bookings remain confirmed.
      - Returns status dictionary: {"parent": bool, "mentor": bool}
    """
    results = {"parent": False, "mentor": False}

    # 1. Send Parent Notification
    try:
        parent_email_data = build_parent_email_content(booking)
        dispatch_email(parent_email_data)
        results["parent"] = True
    except Exception as exc:
        logger.error(
            "Failed to send parent confirmation email for booking #%s to %s: %s",
            getattr(booking, "id", None),
            getattr(getattr(booking, "parent", None), "email", "unknown"),
            exc,
            exc_info=True,
        )

    # 2. Send Mentor Notification
    try:
        mentor_email_data = build_mentor_email_content(booking)
        dispatch_email(mentor_email_data)
        results["mentor"] = True
    except Exception as exc:
        logger.error(
            "Failed to send mentor notification email for booking #%s to %s: %s",
            getattr(booking, "id", None),
            getattr(getattr(booking, "mentor", None), "email", "unknown"),
            exc,
            exc_info=True,
        )

    return results
