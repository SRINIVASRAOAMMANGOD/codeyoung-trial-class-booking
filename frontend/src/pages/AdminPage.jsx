// AdminPage.jsx — Internal Operational Demo Admin Dashboard.

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import AlertBanner from '../components/AlertBanner';
import ResendEmailModal from '../components/ResendEmailModal';
import {
  getOverview,
  getMentors,
  getCourses,
  createCourse,
  updateCourse,
  setCourseStatus,
  createMentor,
  setMentorStatus,
  deleteMentor,
  getParents,
  getParentBookings,
  getBookings,
  updateMentor,
} from '../api/adminApi';

function AdminPage({ currentView, onViewChange }) {
  const [activeTab, setActiveTab] = useState('mentors'); // 'mentors' | 'courses' | 'parents' | 'bookings'
  const [overview, setOverview] = useState(null);
  const [mentors, setMentors] = useState([]);
  const [courses, setCourses] = useState([]);
  const [parents, setParents] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [resendEmailBooking, setResendEmailBooking] = useState(null);

  // Add Mentor Modal State
  const [showAddMentor, setShowAddMentor] = useState(false);
  const [newMentor, setNewMentor] = useState({ name: '', email: '', timezone: 'Asia/Kolkata' });
  const [addingMentor, setAddingMentor] = useState(false);

  // Edit Mentor Modal State
  const [editingMentor, setEditingMentor] = useState(null);
  const [isUpdatingMentor, setIsUpdatingMentor] = useState(false);

  // Parent Bookings Modal State
  const [selectedParent, setSelectedParent] = useState(null);
  const [parentBookings, setParentBookings] = useState([]);
  const [loadingParentBookings, setLoadingParentBookings] = useState(false);

  const [showAddCourse, setShowAddCourse] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [courseForm, setCourseForm] = useState({
    name: '',
    description: '',
    age_range: '',
    level: '',
  });
  const [savingCourse, setSavingCourse] = useState(false);



  useEffect(() => {
    let ignore = false;
    async function loadInitial() {
      try {
        const [ovData, mData, cData, pData, bData] = await Promise.all([
          getOverview(),
          getMentors(),
          getCourses(),
          getParents(),
          getBookings(),
        ]);
        if (!ignore) {
          setOverview(ovData);
          setMentors(mData);
          setCourses(cData);
          setParents(pData);
          setBookings(bData);
        }
      } catch (err) {
        if (!ignore) {
          setAlert({
            type: 'error',
            message: err.message || 'Failed to load admin dashboard data.',
          });
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadInitial();
    return () => {
      ignore = true;
    };
  }, []);

  // Handle Mentor Status Toggle
  const handleToggleMentor = async (mentor) => {
    try {
      const updated = await setMentorStatus(mentor.id, !mentor.is_active);
      setMentors((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      // Refresh overview capacity
      const ovData = await getOverview();
      setOverview(ovData);
      setAlert({
        type: 'info',
        message: `Mentor '${mentor.name}' is now ${updated.is_active ? 'Active' : 'Inactive'}.`,
      });
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to update mentor status.' });
    }
  };

  // Handle Delete Mentor
  const handleDeleteMentor = async (mentor) => {
    if (!window.confirm(`Are you sure you want to delete mentor '${mentor.name}'?`)) {
      return;
    }
    try {
      await deleteMentor(mentor.id);
      setMentors((prev) => prev.filter((m) => m.id !== mentor.id));
      const ovData = await getOverview();
      setOverview(ovData);
      setAlert({
        type: 'info',
        message: `Mentor '${mentor.name}' was successfully deleted.`,
      });
    } catch (err) {
      setAlert({
        type: 'error',
        message: err.message || 'Cannot delete mentor.',
      });
    }
  };

  // Handle Add Mentor Form Submission
  const handleAddMentorSubmit = async (e) => {
    e.preventDefault();
    if (!newMentor.name.trim() || !newMentor.email.trim()) {
      setAlert({ type: 'warning', message: 'Please provide both mentor name and email.' });
      return;
    }
    setAddingMentor(true);
    try {
      const created = await createMentor(newMentor);
      setMentors((prev) => [...prev, created]);
      const ovData = await getOverview();
      setOverview(ovData);
      setShowAddMentor(false);
      setNewMentor({ name: '', email: '', timezone: 'Asia/Kolkata' });
      setAlert({
        type: 'info',
        message: `Mentor '${created.name}' added successfully.`,
      });
    } catch (err) {
      setAlert({
        type: 'error',
        message: err.message || 'Failed to create mentor.',
      });
    } finally {
      setAddingMentor(false);
    }
  };

  // Handle Edit Mentor Form Submission
  const handleEditMentorSubmit = async (e) => {
    e.preventDefault();
    if (!editingMentor.name.trim() || !editingMentor.email.trim()) {
      setAlert({ type: 'warning', message: 'Please provide both mentor name and email.' });
      return;
    }
    setIsUpdatingMentor(true);
    try {
      const payload = {
        name: editingMentor.name,
        email: editingMentor.email,
        timezone: editingMentor.timezone,
        is_active: editingMentor.is_active,
      };
      const updated = await updateMentor(editingMentor.id, payload);
      setMentors((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      const ovData = await getOverview();
      setOverview(ovData);
      setEditingMentor(null);
      setAlert({
        type: 'info',
        message: `Mentor '${updated.name}' updated successfully.`,
      });
    } catch (err) {
      setAlert({
        type: 'error',
        message: err.message || 'Failed to update mentor.',
      });
    } finally {
      setIsUpdatingMentor(false);
    }
  };

  const openAddCourse = () => {
    setCourseForm({ name: '', description: '', age_range: '', level: '' });
    setShowAddCourse(true);
  };

  const openEditCourse = (course) => {
    setCourseForm({
      name: course.name,
      description: course.description,
      age_range: course.age_range,
      level: course.level,
    });
    setEditingCourse(course);
  };

  const handleCourseSubmit = async (e) => {
    e.preventDefault();
    setSavingCourse(true);
    try {
      const updated = editingCourse
        ? await updateCourse(editingCourse.id, courseForm)
        : await createCourse(courseForm);
      setCourses((prev) => {
        if (!editingCourse) return [...prev, updated];
        return prev.map((course) => (course.id === updated.id ? updated : course));
      });
      setShowAddCourse(false);
      setEditingCourse(null);
      setAlert({ type: 'info', message: `Course '${updated.name}' saved successfully.` });
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to save course.' });
    } finally {
      setSavingCourse(false);
    }
  };

  const handleToggleCourse = async (course) => {
    try {
      const updated = await setCourseStatus(course.id, !course.is_active);
      setCourses((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setAlert({
        type: 'info',
        message: `Course '${updated.name}' is now ${updated.is_active ? 'active' : 'inactive'}.`,
      });
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to update course status.' });
    }
  };

  // Handle View Parent Bookings
  const handleViewParentBookings = async (parent) => {
    setSelectedParent(parent);
    setLoadingParentBookings(true);
    try {
      const pBookings = await getParentBookings(parent.id);
      setParentBookings(pBookings);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Could not load bookings for parent.' });
    } finally {
      setLoadingParentBookings(false);
    }
  };

  return (
    <div className="booking-page-layout">
      <Header currentView={currentView} onViewChange={onViewChange} />

      <main className="booking-container admin-container">
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

        {/* Overview Metric Cards */}
        {overview && (
          <div className="admin-metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Active Mentors</span>
              <span className="metric-value">{overview.active_mentors} <small>/ {overview.total_mentors}</small></span>
              <span className="metric-hint">Available for new allocations</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Upcoming Bookings</span>
              <span className="metric-value">{overview.upcoming_bookings}</span>
              <span className="metric-hint">Confirmed classes across future IST dates</span>
            </div>

            <div className="metric-card highlight-metric">
              <span className="metric-label">Daily Capacity</span>
              <span className="metric-value">{overview.theoretical_capacity}</span>
              <span className="metric-hint">Dynamic: {overview.active_mentors} active mentors × 2 classes/day</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Registered Parents</span>
              <span className="metric-value">{overview.total_parents}</span>
              <span className="metric-hint">Unique parent accounts</span>
            </div>

            <div className="metric-card">
              <span className="metric-label">Total Bookings</span>
              <span className="metric-value">{overview.total_bookings}</span>
              <span className="metric-hint">All-time confirmed demo classes</span>
            </div>
          </div>
        )}

        {/* Tab Controls */}
        <div className="admin-nav-tabs">
          <button
            type="button"
            className={`admin-tab-btn ${activeTab === 'mentors' ? 'active' : ''}`}
            onClick={() => setActiveTab('mentors')}
          >
            Mentors Management ({mentors.length})
          </button>
          <button
            type="button"
            className={`admin-tab-btn ${activeTab === 'courses' ? 'active' : ''}`}
            onClick={() => setActiveTab('courses')}
          >
            Courses Management ({courses.length})
          </button>
          <button
            type="button"
            className={`admin-tab-btn ${activeTab === 'parents' ? 'active' : ''}`}
            onClick={() => setActiveTab('parents')}
          >
            Parents Directory ({parents.length})
          </button>
          <button
            type="button"
            className={`admin-tab-btn ${activeTab === 'bookings' ? 'active' : ''}`}
            onClick={() => setActiveTab('bookings')}
          >
            Confirmed Bookings ({bookings.length})
          </button>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="spinner" />
            <p>Loading operational records...</p>
          </div>
        ) : (
          <div className="admin-content-pane">
            {/* TAB 1: MENTORS */}
            {activeTab === 'mentors' && (
              <div className="admin-section">
                <div className="section-header-row">
                  <div>
                    <h3 className="section-heading">Mentor Roster & Capacity</h3>
                    <p className="section-subheading">
                      Dynamic capacity = Active Mentors × 2 demo classes/IST day. Inactive mentors cannot be assigned.
                    </p>
                  </div>
                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    onClick={() => setShowAddMentor(true)}
                  >
                    + Add Mentor
                  </button>
                </div>

                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Timezone</th>
                        <th>Status</th>
                        <th>Upcoming Capacity (IST)</th>
                        <th>Daily Capacity</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mentors.map((m) => (
                        <tr key={m.id} className={!m.is_active ? 'row-inactive' : ''}>
                          <td><strong>#{m.id}</strong></td>
                          <td>{m.name}</td>
                          <td><code>{m.email}</code></td>
                          <td>{m.timezone}</td>
                          <td>
                            <span className={`status-pill ${m.is_active ? 'pill-active' : 'pill-inactive'}`}>
                              {m.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td>
                            {m.upcoming_capacity?.length ? (
                              <div className="upcoming-capacity-list">
                                {m.upcoming_capacity.map((item) => (
                                  <span key={item.ist_date} className="capacity-indicator">
                                    {item.ist_date} — {item.classes_booked}/{item.capacity}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <span className="sub-text">No upcoming classes</span>
                            )}
                          </td>
                          <td>
                            <span className="capacity-indicator cap-avail">2 classes/day</span>
                          </td>
                          <td>
                            <div className="table-action-btns">
                              <button
                                type="button"
                                className={`btn-action ${m.is_active ? 'btn-deactivate' : 'btn-activate'}`}
                                onClick={() => handleToggleMentor(m)}
                              >
                                {m.is_active ? 'Deactivate' : 'Reactivate'}
                              </button>
                              <button
                                type="button"
                                className="btn-action"
                                onClick={() => setEditingMentor(m)}
                              >
                                Edit
                              </button>
                              <button
                                type="button"
                                className="btn-action btn-delete"
                                onClick={() => handleDeleteMentor(m)}
                                title="Allowed only if 0 bookings exist"
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB 2: COURSES */}
            {activeTab === 'courses' && (
              <div className="admin-section">
                <div className="section-header-row">
                  <div>
                    <h3 className="section-heading">Courses Management</h3>
                    <p className="section-subheading">
                      Manage the course catalogue used by new bookings. Existing bookings keep their course relationship.
                    </p>
                  </div>
                  <button type="button" className="btn btn-primary btn-sm" onClick={openAddCourse}>
                    + Add Course
                  </button>
                </div>

                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Age Range</th>
                        <th>Level</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {courses.map((course) => (
                        <tr key={course.id} className={!course.is_active ? 'row-inactive' : ''}>
                          <td><strong>{course.name}</strong></td>
                          <td>{course.description}</td>
                          <td>{course.age_range}</td>
                          <td>{course.level}</td>
                          <td>
                            <span className={`status-pill ${course.is_active ? 'pill-active' : 'pill-inactive'}`}>
                              {course.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td>
                            <div className="table-action-btns">
                              <button type="button" className="btn-action" onClick={() => openEditCourse(course)}>
                                Edit
                              </button>
                              <button
                                type="button"
                                className={`btn-action ${course.is_active ? 'btn-deactivate' : 'btn-activate'}`}
                                onClick={() => handleToggleCourse(course)}
                              >
                                {course.is_active ? 'Deactivate' : 'Activate'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB 3: PARENTS */}
            {activeTab === 'parents' && (
              <div className="admin-section">
                <div className="section-header-row">
                  <div>
                    <h3 className="section-heading">Parent Directory</h3>
                    <p className="section-subheading">
                      Normalized parent records. Click "View Bookings" to inspect family history.
                    </p>
                  </div>
                </div>

                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Parent Name</th>
                        <th>Email</th>
                        <th>Registered Date</th>
                        <th>Total Bookings</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parents.map((p) => (
                        <tr key={p.id}>
                          <td><strong>#{p.id}</strong></td>
                          <td>{p.name}</td>
                          <td><code>{p.email}</code></td>
                          <td>{new Date(p.created_at).toLocaleDateString()}</td>
                          <td>
                            <span className="count-badge">{p.bookings_count}</span>
                          </td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-secondary btn-xs"
                              onClick={() => handleViewParentBookings(p)}
                            >
                              View Bookings ({p.bookings_count})
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB 4: BOOKINGS */}
            {activeTab === 'bookings' && (
              <div className="admin-section">
                <div className="section-header-row">
                  <div>
                    <h3 className="section-heading">All Confirmed Bookings</h3>
                    <p className="section-subheading">
                      Dual timezone presentation: Local parent time & Indian mentor time.
                    </p>
                  </div>
                </div>

                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Ref</th>
                        <th>Student</th>
                        <th>Parent</th>
                        <th>Assigned Mentor</th>
                        <th>Parent Local Time</th>
                        <th>Mentor Time (IST)</th>
                        <th>Status</th>
                        <th>Meeting Link</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bookings.length === 0 ? (
                        <tr>
                          <td colSpan="8" className="empty-table-cell">No bookings found.</td>
                        </tr>
                      ) : (
                        bookings.map((b) => (
                          <tr key={b.id}>
                            <td><strong>#{b.id}</strong></td>
                            <td><strong>{b.child_name}</strong></td>
                            <td>
                              <div>{b.parent_name}</div>
                              <small className="sub-text">{b.parent_email}</small>
                            </td>
                            <td>{b.mentor_name}</td>
                            <td><span className="time-badge">{b.parent_local_time}</span></td>
                            <td><span className="ist-badge">{b.mentor_ist_time}</span></td>
                            <td>
                              <span className="status-badge">{b.status}</span>
                            </td>
                            <td>
                              <a
                                href={b.class_link}
                                target="_blank"
                                rel="noreferrer"
                                className="class-link-btn"
                              >
                                Join Room ↗
                              </a>
                            </td>
                            <td>
                              <button
                                type="button"
                                className="btn btn-secondary btn-xs"
                                onClick={() => setResendEmailBooking(b)}
                              >
                                Resend Email
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MODAL: ADD/EDIT COURSE */}
        {(showAddCourse || editingCourse) && (
          <div className="modal-backdrop">
            <div className="modal-dialog">
              <div className="modal-header">
                <h3>{editingCourse ? `Edit Course: ${editingCourse.name}` : 'Add New Course'}</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => { setShowAddCourse(false); setEditingCourse(null); }}
                >
                  ✕
                </button>
              </div>
              <form onSubmit={handleCourseSubmit}>
                <div className="modal-body">
                  <div className="form-group">
                    <label htmlFor="course-name">Course Name</label>
                    <input
                      id="course-name"
                      type="text"
                      className="form-input"
                      value={courseForm.name}
                      onChange={(e) => setCourseForm({ ...courseForm, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="course-description">Description</label>
                    <textarea
                      id="course-description"
                      className="form-input"
                      value={courseForm.description}
                      onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })}
                      rows="3"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="course-age-range">Age Range</label>
                    <input
                      id="course-age-range"
                      type="text"
                      className="form-input"
                      value={courseForm.age_range}
                      onChange={(e) => setCourseForm({ ...courseForm, age_range: e.target.value })}
                      placeholder="e.g. Ages 10–16"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="course-level">Level</label>
                    <input
                      id="course-level"
                      type="text"
                      className="form-input"
                      value={courseForm.level}
                      onChange={(e) => setCourseForm({ ...courseForm, level: e.target.value })}
                      placeholder="e.g. Intermediate"
                      required
                    />
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => { setShowAddCourse(false); setEditingCourse(null); }}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={savingCourse}>
                    {savingCourse ? 'Saving...' : editingCourse ? 'Save Changes' : 'Add Course'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: ADD MENTOR */}
        {showAddMentor && (
          <div className="modal-backdrop">
            <div className="modal-dialog">
              <div className="modal-header">
                <h3>Add New Codeyoung Mentor</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => setShowAddMentor(false)}
                >
                  ✕
                </button>
              </div>
              <form onSubmit={handleAddMentorSubmit}>
                <div className="modal-body">
                  <div className="form-group">
                    <label htmlFor="mentor-name">Mentor Full Name</label>
                    <input
                      id="mentor-name"
                      type="text"
                      className="form-input"
                      value={newMentor.name}
                      onChange={(e) => setNewMentor({ ...newMentor, name: e.target.value })}
                      placeholder="e.g. Ananya Rao"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="mentor-email">Email Address</label>
                    <input
                      id="mentor-email"
                      type="email"
                      className="form-input"
                      value={newMentor.email}
                      onChange={(e) => setNewMentor({ ...newMentor, email: e.target.value })}
                      placeholder="e.g. ananya@codeyoung.com"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="mentor-tz">Timezone (IANA)</label>
                    <input
                      id="mentor-tz"
                      type="text"
                      className="form-input"
                      value={newMentor.timezone}
                      onChange={(e) => setNewMentor({ ...newMentor, timezone: e.target.value })}
                      required
                    />
                  </div>
                </div>

                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowAddMentor(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={addingMentor}
                  >
                    {addingMentor ? 'Saving...' : 'Add Mentor'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: EDIT MENTOR */}
        {editingMentor && (
          <div className="modal-backdrop">
            <div className="modal-dialog">
              <div className="modal-header">
                <h3>Edit Mentor: {editingMentor.name}</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => setEditingMentor(null)}
                >
                  ✕
                </button>
              </div>
              <form onSubmit={handleEditMentorSubmit}>
                <div className="modal-body">
                  <div className="form-group">
                    <label htmlFor="edit-mentor-name">Mentor Full Name</label>
                    <input
                      id="edit-mentor-name"
                      type="text"
                      className="form-input"
                      value={editingMentor.name}
                      onChange={(e) => setEditingMentor({ ...editingMentor, name: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="edit-mentor-email">Email Address</label>
                    <input
                      id="edit-mentor-email"
                      type="email"
                      className="form-input"
                      value={editingMentor.email}
                      onChange={(e) => setEditingMentor({ ...editingMentor, email: e.target.value })}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="edit-mentor-tz">Timezone (IANA)</label>
                    <input
                      id="edit-mentor-tz"
                      type="text"
                      className="form-input"
                      value={editingMentor.timezone}
                      onChange={(e) => setEditingMentor({ ...editingMentor, timezone: e.target.value })}
                      required
                    />
                  </div>
                  
                  <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem' }}>
                    <input
                      id="edit-mentor-active"
                      type="checkbox"
                      checked={editingMentor.is_active}
                      onChange={(e) => setEditingMentor({ ...editingMentor, is_active: e.target.checked })}
                      style={{ width: 'auto' }}
                    />
                    <label htmlFor="edit-mentor-active" style={{ marginBottom: 0 }}>Active for assignments</label>
                  </div>
                </div>

                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setEditingMentor(null)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isUpdatingMentor}
                  >
                    {isUpdatingMentor ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: PARENT BOOKINGS */}
        {selectedParent && (
          <div className="modal-backdrop">
            <div className="modal-dialog modal-lg">
              <div className="modal-header">
                <h3>Bookings for {selectedParent.name} ({selectedParent.email})</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => setSelectedParent(null)}
                >
                  ✕
                </button>
              </div>
              <div className="modal-body">
                {loadingParentBookings ? (
                  <p>Loading bookings...</p>
                ) : parentBookings.length === 0 ? (
                  <p>No bookings found for this parent.</p>
                ) : (
                  <div className="table-responsive">
                    <table className="admin-table">
                      <thead>
                        <tr>
                          <th>Ref</th>
                          <th>Student</th>
                          <th>Mentor</th>
                          <th>Local Scheduled Time</th>
                          <th>Status</th>
                          <th>Meeting Link</th>
                        </tr>
                      </thead>
                      <tbody>
                        {parentBookings.map((pb) => (
                          <tr key={pb.id}>
                            <td>#{pb.id}</td>
                            <td>{pb.child_name}</td>
                            <td>{pb.mentor_name}</td>
                            <td>{pb.local_display}</td>
                            <td><span className="status-badge">{pb.status}</span></td>
                            <td>
                              <a
                                href={pb.class_link}
                                target="_blank"
                                rel="noreferrer"
                                className="class-link-btn"
                              >
                                Room ↗
                              </a>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setSelectedParent(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

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

export default AdminPage;
