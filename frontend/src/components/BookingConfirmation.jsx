// BookingConfirmation.jsx — Celebratory success card after a confirmed booking.

import { useState } from 'react';
import { formatLocalSlotTime } from '../utils/dateUtils';

function BookingConfirmation({ booking, localDisplay, onReset }) {
  const [copied, setCopied] = useState(false);

  if (!booking) return null;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(booking.class_link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback if clipboard API is unavailable
      setCopied(false);
    }
  };

  const formattedTime = formatLocalSlotTime(localDisplay || booking.slot_utc);

  return (
    <div className="confirmation-container" aria-live="polite">
      <div className="card confirmation-card">
        {/* Success Header */}
        <div className="success-badge" aria-hidden="true">✓</div>
        <h2 className="confirmation-title">Trial Class Confirmed!</h2>
        <p className="confirmation-subtitle">
          Your 1-on-1 coding trial has been scheduled. Details have been confirmed below.
        </p>

        {/* Booking Details Summary */}
        <div className="confirmation-details">
          <div className="detail-row">
            <span className="detail-label">Booking Reference:</span>
            <span className="detail-value reference-id">#{booking.id}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Student:</span>
            <span className="detail-value">{booking.child_name}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Parent:</span>
            <span className="detail-value">{booking.parent_name} ({booking.parent_email})</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Scheduled Time:</span>
            <span className="detail-value time-highlight">
              {formattedTime} ({booking.parent_timezone})
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Assigned Instructor:</span>
            <span className="detail-value">
              {/* User-friendly label shown to parent; internal mentor_id retained on booking object */}
              Dedicated Codeyoung Mentor
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Status:</span>
            <span className="detail-value status-badge">{booking.status}</span>
          </div>
        </div>

        {/* Trial Class Room Link */}
        <div className="class-link-box">
          <label htmlFor="class-url-display" className="class-link-label">
            Classroom Meeting Link
          </label>
          <div className="class-link-controls">
            <input
              id="class-url-display"
              type="text"
              readOnly
              value={booking.class_link}
              className="class-url-input"
            />
            <button
              type="button"
              className="btn btn-secondary btn-copy"
              onClick={handleCopyLink}
            >
              {copied ? '✓ Copied!' : 'Copy Link'}
            </button>
          </div>
          <p className="class-link-hint">
            Please save this link. You can join the classroom directly when your session starts.
          </p>
        </div>

        {/* Actions */}
        <div className="confirmation-actions">
          <a
            href={booking.class_link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary btn-join"
          >
            Enter Classroom
          </a>
          <button
            type="button"
            className="btn btn-outline"
            onClick={onReset}
          >
            Book Another Class
          </button>
        </div>
      </div>
    </div>
  );
}

export default BookingConfirmation;
