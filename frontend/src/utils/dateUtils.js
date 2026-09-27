// dateUtils.js — Helper utilities for date formatting and calculation.

/**
 * Generate 7 bookable calendar dates (tomorrow through tomorrow + 6 days in IST).
 */
export function getBookableDates() {
  const now = new Date();
  const utcMillis = now.getTime() + now.getTimezoneOffset() * 60000;
  const istMillis = utcMillis + 5.5 * 3600000; // IST is UTC+5:30
  const istDate = new Date(istMillis);

  const dates = [];
  for (let i = 1; i <= 7; i++) {
    const d = new Date(istDate);
    d.setDate(d.getDate() + i);

    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const isoString = `${yyyy}-${mm}-${dd}`;

    const weekday = d.toLocaleDateString('en-US', { weekday: 'short' });
    const monthDay = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    dates.push({
      isoString,
      weekday,
      monthDay,
      isTomorrow: i === 1,
    });
  }
  return dates;
}

/**
 * Format the local display ISO string (e.g. "2026-09-28T05:30:00-04:00")
 * into a friendly 12-hour time range (e.g. "5:30 AM – 6:30 AM").
 * Reads the time directly from the backend-calculated local_display string
 * rather than relying on browser OS timezone conversions.
 */
export function formatLocalSlotTime(localIso) {
  if (!localIso) return '';
  try {
    const timePart = localIso.includes('T') ? localIso.split('T')[1] : localIso;
    const [hhStr, mmStr] = timePart.split(':');
    const startHour = parseInt(hhStr, 10);
    const minute = mmStr ? mmStr.substring(0, 2) : '00';

    if (isNaN(startHour)) return localIso;

    // Start time in 12-hour format
    const startAmPm = startHour >= 12 ? 'PM' : 'AM';
    const startH12 = startHour % 12 === 0 ? 12 : startHour % 12;
    const startFormatted = `${startH12}:${minute} ${startAmPm}`;

    // End time (1-hour duration product assumption)
    const endHour = (startHour + 1) % 24;
    const endAmPm = endHour >= 12 ? 'PM' : 'AM';
    const endH12 = endHour % 12 === 0 ? 12 : endHour % 12;
    const endFormatted = `${endH12}:${minute} ${endAmPm}`;

    return `${startFormatted} – ${endFormatted}`;
  } catch {
    return localIso;
  }
}

/**
 * Validate standard email format.
 */
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}
