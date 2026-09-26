// bookingApi.js — All HTTP calls to the backend API.
//
// Centralising API calls here means:
//   - Base URL is defined once
//   - Error handling can be standardised in one place
//   - Components stay clean (no fetch() calls in components)
//
// Will be implemented in Phase 6 (frontend-backend integration).

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Placeholder — will be replaced in Phase 6
export const getSlots = async ({ date, timezone }) => {
  const res = await fetch(`${BASE_URL}/api/v1/slots?date=${date}&timezone=${encodeURIComponent(timezone)}`)
  if (!res.ok) throw new Error('Failed to fetch slots')
  return res.json()
}

export const createBooking = async (payload) => {
  const res = await fetch(`${BASE_URL}/api/v1/bookings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Booking failed')
  }
  return res.json()
}
