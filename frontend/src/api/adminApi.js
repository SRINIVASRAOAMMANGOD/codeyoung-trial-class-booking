// adminApi.js — Centralized client for internal operational admin and mentor portal.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(res) {
  if (res.ok) {
    return res.json();
  }
  let errorDetail = 'An unexpected error occurred.';
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

export async function getOverview() {
  const res = await fetch(`${BASE_URL}/api/v1/admin/overview`);
  return handleResponse(res);
}

export async function getMentors() {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors`);
  return handleResponse(res);
}

export async function getCourses() {
  const res = await fetch(`${BASE_URL}/api/v1/admin/courses`);
  return handleResponse(res);
}

export async function createCourse(payload) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/courses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function updateCourse(courseId, payload) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/courses/${courseId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function setCourseStatus(courseId, isActive) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/courses/${courseId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  });
  return handleResponse(res);
}

export async function createMentor(payload) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function updateMentor(mentorId, payload) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors/${mentorId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function setMentorStatus(mentorId, isActive) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors/${mentorId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  });
  return handleResponse(res);
}

export async function deleteMentor(mentorId) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors/${mentorId}`, {
    method: 'DELETE',
  });
  return handleResponse(res);
}

export async function getParents() {
  const res = await fetch(`${BASE_URL}/api/v1/admin/parents`);
  return handleResponse(res);
}

export async function getParentBookings(parentId) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/parents/${parentId}/bookings`);
  return handleResponse(res);
}

export async function getBookings() {
  const res = await fetch(`${BASE_URL}/api/v1/admin/bookings`);
  return handleResponse(res);
}

export async function getMentorSchedule(mentorId) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/mentors/${mentorId}/schedule`);
  return handleResponse(res);
}

export async function resendEmail(bookingId, payload) {
  const res = await fetch(`${BASE_URL}/api/v1/admin/bookings/${bookingId}/resend-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
