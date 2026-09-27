// MentorPage.jsx — Internal Demo Mentor View.

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import AlertBanner from '../components/AlertBanner';
import ResendEmailModal from '../components/ResendEmailModal';
import { getMentors, getMentorSchedule } from '../api/adminApi';

function MentorPage({ currentView, onViewChange }) {
  const [mentors, setMentors] = useState([]);
  const [selectedMentorId, setSelectedMentorId] = useState('');
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [resendEmailBooking, setResendEmailBooking] = useState(null);

  // Load mentors list on mount
  useEffect(() => {
    async function fetchMentors() {
      try {
        const data = await getMentors();
        setMentors(data);
        if (data.length > 0) {
          setSelectedMentorId(String(data[0].id));
        }
      } catch (err) {
        setAlert({
          type: 'error',
          message: err.message || 'Could not load mentors list.',
        });
      }
    }
    fetchMentors();
  }, []);

  // Fetch schedule whenever selected mentor changes
  useEffect(() => {
    if (!selectedMentorId) return;

    async function fetchSchedule() {
      setLoading(true);
      setAlert(null);
      try {
        const items = await getMentorSchedule(selectedMentorId);
        setSchedule(items);
      } catch (err) {
        setAlert({
          type: 'error',
          message: err.message || 'Could not load mentor schedule.',
        });
        setSchedule([]);
      } finally {
        setLoading(false);
      }
    }
    fetchSchedule();
  }, [selectedMentorId]);

  const currentMentor = mentors.find((m) => String(m.id) === String(selectedMentorId));

  return (
    <div className="booking-page-layout">
      <Header currentView={currentView} onViewChange={onViewChange} />

      <main className="booking-container mentor-view-container">
        {/* Notice Banner */}
        <div className="internal-notice-badge">
          Notice: This is a demo internal portal. Authentication and Role-Based Access Control (RBAC) are not implemented.
        </div>

        {alert && (
          <AlertBanner
            type={alert.type}
            message={alert.message}
            onDismiss={() => setAlert(null)}
          />
        )}

        {/* Mentor Selector Card */}
        <div className="card mentor-selector-card">
          <div className="mentor-select-row">
            <div className="form-group select-group">
              <label htmlFor="mentor-picker" className="form-label">
                Select Mentor Identity:
              </label>
              <select
                id="mentor-picker"
                className="form-select"
                value={selectedMentorId}
                onChange={(e) => setSelectedMentorId(e.target.value)}
              >
                {mentors.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.email}) — {m.is_active ? 'Active' : 'Inactive'} ({m.upcoming_capacity?.length || 0} upcoming dates)
                  </option>
                ))}
              </select>
            </div>

            {currentMentor && (
              <div className="mentor-quick-stats">
                <div className="stat-pill">
                  <span className="stat-label">Status:</span>
                  <span className={`status-pill ${currentMentor.is_active ? 'pill-active' : 'pill-inactive'}`}>
                    {currentMentor.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="stat-pill">
                  <span className="stat-label">Timezone:</span>
                  <span className="stat-val">{currentMentor.timezone}</span>
                </div>
                <div className="stat-pill" style={{ alignItems: 'flex-start' }}>
                  <span className="stat-label">Upcoming Capacity:</span>
                  <div className="upcoming-capacity-list">
                    {currentMentor.upcoming_capacity?.length ? currentMentor.upcoming_capacity.map((item) => (
                      <span key={item.ist_date} className="stat-val">
                        {item.ist_date} — {item.classes_booked}/{item.capacity}
                      </span>
                    )) : <span className="stat-val">No upcoming classes</span>}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Assigned Classes Schedule */}
        <div className="card mentor-schedule-card">
          <div className="section-header-row">
            <div>
              <h3 className="section-heading">Assigned Trial Classes (IST)</h3>
              <p className="section-subheading">
                All class times are rendered in India Standard Time (Asia/Kolkata, UTC+5:30).
              </p>
            </div>
            <span className="schedule-count-badge">
              {schedule.length} Total Class{schedule.length === 1 ? '' : 'es'}
            </span>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
              <p>Loading mentor schedule...</p>
            </div>
          ) : schedule.length === 0 ? (
            <div className="empty-schedule-box">
              <p className="empty-title">No demo classes currently scheduled</p>
              <p className="empty-hint">
                New trial classes booked by parents will appear here automatically when allocated to {currentMentor?.name}.
              </p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Ref</th>
                    <th>Student Name</th>
                    <th>Parent Contact</th>
                    <th>Class Date (IST)</th>
                    <th>Time Window (IST)</th>
                    <th>Status</th>
                    <th>Classroom Meeting Link</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {schedule.map((item) => (
                    <tr key={item.id}>
                      <td><strong>#{item.id}</strong></td>
                      <td><strong>{item.student_name}</strong></td>
                      <td>
                        <div>{item.parent_name}</div>
                        <small className="sub-text">{item.parent_email}</small>
                      </td>
                      <td>{item.class_date_ist}</td>
                      <td><span className="ist-badge">{item.class_time_ist}</span></td>
                      <td>
                        <span className="status-badge">{item.status}</span>
                      </td>
                      <td>
                        <a
                          href={item.class_link}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary btn-xs"
                        >
                          Join Class Room ↗
                        </a>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-secondary btn-xs"
                          onClick={() => setResendEmailBooking(item)}
                        >
                          Resend Email
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {resendEmailBooking && (
          <ResendEmailModal
            booking={resendEmailBooking}
            onClose={() => setResendEmailBooking(null)}
          />
        )}
      </main>
    </div>
  );
}

export default MentorPage;
