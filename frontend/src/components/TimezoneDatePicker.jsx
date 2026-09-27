// TimezoneDatePicker.jsx — Timezone selection and 7-day date selector.

import { useMemo } from 'react';
import { getBookableDates } from '../utils/dateUtils';

// Common IANA timezones covering key global regions
const COMMON_TIMEZONES = [
  { value: 'America/New_York', label: 'US Eastern Time (New York)' },
  { value: 'America/Chicago', label: 'US Central Time (Chicago)' },
  { value: 'America/Denver', label: 'US Mountain Time (Denver)' },
  { value: 'America/Los_Angeles', label: 'US Pacific Time (Los Angeles)' },
  { value: 'Europe/London', label: 'UK Time (London)' },
  { value: 'Europe/Paris', label: 'Central European Time (Paris)' },
  { value: 'Asia/Dubai', label: 'Gulf Standard Time (Dubai)' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
  { value: 'Asia/Singapore', label: 'Singapore Time (SGT)' },
  { value: 'Australia/Sydney', label: 'Australian Eastern (Sydney)' },
];

function TimezoneDatePicker({ timezone, onTimezoneChange, selectedDate, onDateChange }) {
  const bookableDates = useMemo(() => getBookableDates(), []);

  // Ensure detected browser timezone is in the select options
  const timezoneOptions = useMemo(() => {
    const exists = COMMON_TIMEZONES.some((tz) => tz.value === timezone);
    if (!exists && timezone) {
      return [{ value: timezone, label: `${timezone} (Detected)` }, ...COMMON_TIMEZONES];
    }
    return COMMON_TIMEZONES;
  }, [timezone]);

  return (
    <section className="card date-tz-section" aria-labelledby="datetime-heading">
      <h2 id="datetime-heading" className="section-title">
        <span className="step-number">2</span> Choose Date & Timezone
      </h2>
      <p className="section-description">
        All class times below will automatically display in your selected timezone.
      </p>

      {/* Timezone Selector */}
      <div className="form-group tz-group">
        <label htmlFor="timezone-select" className="form-label">
          Your Local Timezone
        </label>
        <div className="select-wrapper">
          <select
            id="timezone-select"
            className="form-select"
            value={timezone}
            onChange={(e) => onTimezoneChange(e.target.value)}
          >
            {timezoneOptions.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 7-Day Date Selector Strip */}
      <div className="dates-container">
        <label className="form-label">Select Date (7-day window)</label>
        <div className="date-strip" role="radiogroup" aria-label="Bookable dates">
          {bookableDates.map((item) => {
            const isSelected = item.isoString === selectedDate;
            return (
              <button
                key={item.isoString}
                type="button"
                className={`date-pill ${isSelected ? 'date-pill-active' : ''}`}
                onClick={() => onDateChange(item.isoString)}
                role="radio"
                aria-checked={isSelected}
              >
                <span className="date-pill-weekday">{item.weekday}</span>
                <span className="date-pill-day">{item.monthDay}</span>
                {item.isTomorrow && <span className="date-pill-tag">Tomorrow</span>}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default TimezoneDatePicker;
