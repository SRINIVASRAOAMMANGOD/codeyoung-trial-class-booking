// BookingPage.jsx — Main coordinator for the trial class booking experience.

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import AlertBanner from '../components/AlertBanner';
import ParentDetailsForm from '../components/ParentDetailsForm';
import TimezoneDatePicker from '../components/TimezoneDatePicker';
import SlotPicker from '../components/SlotPicker';
import BookingConfirmation from '../components/BookingConfirmation';
import CourseSelector from '../components/CourseSelector';
import { getSlots, createBooking, getCourses } from '../api/bookingApi';
import { getBookableDates, isValidEmail } from '../utils/dateUtils';

function BookingPage({ onViewChange, onBackToLanding }) {
  // 1. Initial State
  const initialDates = getBookableDates();
  const defaultDate = initialDates[0]?.isoString || '';

  // Auto-detect browser timezone
  const defaultTimezone =
    typeof Intl !== 'undefined' && Intl.DateTimeFormat
      ? Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/New_York'
      : 'America/New_York';

  const [form, setForm] = useState({
    parentName: '',
    parentEmail: '',
    childName: '',
  });
  const [formErrors, setFormErrors] = useState({});

  const [courses, setCourses] = useState([]);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [selectedCourseId, setSelectedCourseId] = useState(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const c = params.get('course');
      return c ? parseInt(c, 10) : null;
    }
    return null;
  });

  const [selectedTimezone, setSelectedTimezone] = useState(defaultTimezone);
  const [selectedDate, setSelectedDate] = useState(defaultDate);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [slotError, setSlotError] = useState(null);

  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);
  const [confirmedBooking, setConfirmedBooking] = useState(null);

  // Fetch Courses
  useEffect(() => {
    let ignore = false;
    async function fetchAllCourses() {
      try {
        const data = await getCourses();
        if (!ignore) {
          setCourses(data);
          // If no course is selected from URL but we have courses, we don't default it (as per requirements).
        }
      } catch (err) {
        if (!ignore) {
          setAlert({
            type: 'error',
            message: 'Failed to load courses. Please refresh the page.',
          });
        }
      } finally {
        if (!ignore) {
          setLoadingCourses(false);
        }
      }
    }
    fetchAllCourses();
    return () => { ignore = true; };
  }, []);

  // 2. Fetch Slots on Date, Timezone, or Refresh Trigger Change
  useEffect(() => {
    let ignore = false;

    async function fetchSlots() {
      if (!selectedDate || !selectedTimezone) return;
      setLoadingSlots(true);
      setSlotError(null);
      try {
        const data = await getSlots({ date: selectedDate, timezone: selectedTimezone });
        if (!ignore) {
          setSlots(data.slots || []);
        }
      } catch {
        if (!ignore) {
          setSlots([]);
          setSlotError('Unable to load available slots. Please verify your connection or try again.');
        }
      } finally {
        if (!ignore) {
          setLoadingSlots(false);
        }
      }
    }

    fetchSlots();

    return () => {
      ignore = true;
    };
  }, [selectedDate, selectedTimezone, refreshTrigger]);

  // Date and Timezone Handlers
  const handleDateChange = (newDate) => {
    setSelectedDate(newDate);
    setSelectedSlot(null);
    if (formErrors.slot) {
      setFormErrors((prev) => ({ ...prev, slot: null }));
    }
  };

  const handleTimezoneChange = (newTz) => {
    setSelectedTimezone(newTz);
    setSelectedSlot(null);
    if (formErrors.slot) {
      setFormErrors((prev) => ({ ...prev, slot: null }));
    }
  };

  // 3. Form Field Change Handler
  const handleFieldChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  // 4. Form Validation
  const validateForm = () => {
    const errors = {};
    if (!form.parentName.trim() || form.parentName.trim().length < 2) {
      errors.parentName = 'Please enter your full name (minimum 2 characters).';
    }
    if (!form.parentEmail.trim() || !isValidEmail(form.parentEmail)) {
      errors.parentEmail = 'Please enter a valid email address.';
    }
    if (!form.childName.trim() || form.childName.trim().length < 2) {
      errors.childName = "Please enter student's name (minimum 2 characters).";
    }
    if (!selectedCourseId) {
      errors.course = 'Please select a course.';
    }
    if (!selectedSlot) {
      errors.slot = 'Please select a convenient time slot from the list above.';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // 5. Submit Booking
  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlert(null);

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      // Preserve canonical UTC instant exactly as returned by GET /api/v1/slots
      const payload = {
        parent_name: form.parentName.trim(),
        parent_email: form.parentEmail.trim(),
        child_name: form.childName.trim(),
        course_id: selectedCourseId,
        parent_timezone: selectedTimezone,
        slot_utc: selectedSlot.utc_iso,
      };

      const bookingResult = await createBooking(payload);
      setConfirmedBooking(bookingResult);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err.status === 409) {
        setAlert({
          type: 'warning',
          message: 'This slot was just booked by another parent. Please choose an alternate slot.',
        });
        // Trigger slots reload to show live availability
        setRefreshTrigger((prev) => prev + 1);
        setSelectedSlot(null);
      } else if (err.status === 422) {
        setAlert({
          type: 'error',
          message: err.message || 'Please check your input details and selected slot.',
        });
      } else if (err.status === 503) {
        setAlert({
          type: 'warning',
          message: 'Our scheduling service experienced temporary contention. Please try submitting again.',
        });
      } else {
        setAlert({
          type: 'error',
          message: err.message || 'Unable to complete your booking. Please try again.',
        });
      }
    } finally {
      setSubmitting(false);
    }
  };

  // 6. Reset Booking Flow
  const handleReset = () => {
    setConfirmedBooking(null);
    setSelectedSlot(null);
    setAlert(null);
    setForm({
      parentName: '',
      parentEmail: '',
      childName: '',
    });
    setFormErrors({});
    setRefreshTrigger((prev) => prev + 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      <Header
        currentView="booking"
        onViewChange={onViewChange}
        onBackToLanding={onBackToLanding}
      />

      <main className="landing-container" style={{ padding: '3rem 1rem' }}>
        {alert && (
          <AlertBanner
            type={alert.type}
            message={alert.message}
            onDismiss={() => setAlert(null)}
          />
        )}

        {confirmedBooking ? (
          <BookingConfirmation
            booking={confirmedBooking}
            localDisplay={selectedSlot?.local_display}
            onReset={handleReset}
          />
        ) : (
          <form className="booking-form-linear" onSubmit={handleSubmit} noValidate>
            <div className="booking-progress">
              <div className="progress-step active">1. Course</div>
              <div className="progress-separator"></div>
              <div className="progress-step active">2. Date & Timezone</div>
              <div className="progress-separator"></div>
              <div className="progress-step active">3. Time Slot</div>
              <div className="progress-separator"></div>
              <div className="progress-step active">4. Details</div>
            </div>

            <div className="booking-steps-stack">
              <CourseSelector
                courses={courses}
                selectedCourseId={selectedCourseId}
                onSelectCourse={(id) => {
                  setSelectedCourseId(id);
                  if (formErrors.course) {
                    setFormErrors((prev) => ({ ...prev, course: null }));
                  }
                }}
                error={formErrors.course}
                loading={loadingCourses}
              />

              <TimezoneDatePicker
                timezone={selectedTimezone}
                onTimezoneChange={handleTimezoneChange}
                selectedDate={selectedDate}
                onDateChange={handleDateChange}
              />
              
              <SlotPicker
                slots={slots}
                selectedSlot={selectedSlot}
                onSelectSlot={(slot) => {
                  setSelectedSlot(slot);
                  if (formErrors.slot) {
                    setFormErrors((prev) => ({ ...prev, slot: null }));
                  }
                }}
                loading={loadingSlots}
                error={slotError || formErrors.slot}
              />

              <ParentDetailsForm
                form={form}
                errors={formErrors}
                onChange={handleFieldChange}
              >
                <div className="submit-summary" style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                  <h4 style={{ marginBottom: '0.75rem', fontWeight: 600, fontSize: '1rem' }}>Booking Summary</h4>
                  <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}><strong>Course:</strong> {courses.find(c => c.id === selectedCourseId)?.name || 'Not selected'}</p>
                  <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}><strong>Date:</strong> {selectedDate || 'Not selected'}</p>
                  <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}><strong>Time:</strong> {selectedSlot ? selectedSlot.local_display : 'Not selected'}</p>
                  <p style={{ margin: '0.25rem 0', fontSize: '0.9rem' }}><strong>Timezone:</strong> {selectedTimezone}</p>
                </div>

                <button
                  type="submit"
                  className="hero-btn-primary"
                  style={{ width: '100%', marginTop: '1.5rem', display: 'flex', justifyContent: 'center' }}
                  disabled={submitting || loadingSlots}
                >
                  {submitting ? 'Confirming Booking...' : 'Confirm Free Trial Class'}
                </button>
              </ParentDetailsForm>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}

export default BookingPage;
