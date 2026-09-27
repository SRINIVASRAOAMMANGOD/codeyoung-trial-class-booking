// SlotPicker.jsx — Displays available slots grid with loading and empty states.

import { formatLocalSlotTime } from '../utils/dateUtils';

function SlotPicker({ slots, selectedSlot, onSelectSlot, loading, error }) {
  return (
    <section className="card slot-section" aria-labelledby="slots-heading">
      <h2 id="slots-heading" className="section-title">
        <span className="step-number">3</span> Select a Time Slot
      </h2>
      <p className="section-description">
        Choose a convenient 1-hour session. Real-time availability is updated for your selected date.
      </p>

      {error && !loading && (
        <div className="slot-error-hint" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="slots-loading" aria-live="polite">
          <div className="spinner" />
          <p>Checking mentor availability...</p>
        </div>
      ) : slots && slots.length > 0 ? (
        <div className="slots-grid" role="radiogroup" aria-label="Available slots">
          {slots.map((slot) => {
            const isSelected = selectedSlot && selectedSlot.utc_iso === slot.utc_iso;
            const timeLabel = formatLocalSlotTime(slot.local_display);

            return (
              <button
                key={slot.utc_iso}
                type="button"
                className={`slot-card ${isSelected ? 'slot-card-active' : ''}`}
                onClick={() => onSelectSlot(slot)}
                role="radio"
                aria-checked={isSelected}
              >
                <span className="slot-time">{timeLabel}</span>
                <span className="slot-badge">{isSelected ? 'Selected' : 'Available'}</span>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="slots-empty" role="status">
          
          <p className="empty-message">
            No trial-class slots are currently available for this date. Please choose another date.
          </p>
        </div>
      )}
    </section>
  );
}

export default SlotPicker;
