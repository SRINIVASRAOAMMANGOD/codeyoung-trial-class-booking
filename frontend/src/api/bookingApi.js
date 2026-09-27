// bookingApi.js — Centralised API client for the Codeyoung trial class booking API.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Handle API responses and extract meaningful error details.
 */
async function handleResponse(res) {
  if (res.ok) {
    return res.json();
  }

  let errorDetail = 'An unexpected error occurred. Please try again.';
  try {
    const errorData = await res.json();
    if (typeof errorData.detail === 'string') {
      errorDetail = errorData.detail;
    } else if (Array.isArray(errorData.detail)) {
      errorDetail = errorData.detail.map((err) => err.msg || err.detail).join(', ');
    }
  } catch {
    errorDetail = res.statusText || errorDetail;
  }

  const error = new Error(errorDetail);
  error.status = res.status;
  throw error;
}

/**
 * Fetch available trial class slots for a specific date and parent timezone.
 * @param {Object} params
 * @param {string} params.date - Date in YYYY-MM-DD format (IST anchor)
 * @param {string} params.timezone - IANA timezone identifier
 * @returns {Promise<{ date: string, timezone: string, slots: Array<{ utc_iso: string, local_display: string }> }>}
 */
export async function getSlots({ date, timezone }) {
  const url = `${BASE_URL}/api/v1/slots?date=${encodeURIComponent(date)}&timezone=${encodeURIComponent(timezone)}`;
  const res = await fetch(url);
  return handleResponse(res);
}

/**
 * Create a new trial class booking.
 * Submits the canonical UTC ISO string chosen by the parent.
 * @param {Object} payload
 * @param {string} payload.parent_name
 * @param {string} payload.parent_email
 * @param {string} payload.child_name
 * @param {string} payload.parent_timezone
 * @param {string} payload.slot_utc - Canonical UTC instant (utc_iso)
 * @returns {Promise<Object>} Confirmed booking record
 */
export async function createBooking(payload) {
  const res = await fetch(`${BASE_URL}/api/v1/bookings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

/**
 * Fetch available courses.
 * @returns {Promise<Array<{ id: number, name: string, description: string }>>}
 */
export async function getCourses() {
  const res = await fetch(`${BASE_URL}/api/v1/courses`);
  return handleResponse(res);
}
