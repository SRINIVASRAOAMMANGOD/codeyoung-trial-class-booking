import React from 'react';

function CourseSelector({ courses, selectedCourseId, onSelectCourse, error, loading }) {
  if (loading) {
    return (
      <div className="card form-card">
      <h2 className="card-title">
        <span className="step-number">1</span> Select a Course
      </h2>
      <div style={{ padding: '1rem', textAlign: 'center' }}>Loading courses...</div>
      </div>
    );
  }

  return (
    <div className="card form-card">
      <h2 className="card-title">
        <span className="step-number">1</span> Select a Course
      </h2>
      {error && <p className="error-text" style={{ color: 'var(--color-error)', marginBottom: '1rem' }}>{error}</p>}
      <div className="courses-grid" style={{ marginTop: '1.5rem' }}>
        {courses.map((course) => (
          <label 
            key={course.id} 
            className={`course-card ${selectedCourseId === course.id ? 'selected' : ''}`}
            style={{
              cursor: 'pointer',
              border: selectedCourseId === course.id ? '2px solid var(--cy-teal)' : '1px solid var(--color-border)',
              backgroundColor: selectedCourseId === course.id ? '#f0fdff' : '#ffffff',
              boxShadow: selectedCourseId === course.id ? '0 10px 25px -5px rgba(26, 107, 114, 0.15)' : '',
              position: 'relative',
              display: 'block'
            }}
          >
            <input
              type="radio"
              name="courseSelection"
              value={course.id}
              checked={selectedCourseId === course.id}
              onChange={() => onSelectCourse(course.id)}
              style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
            />
            <h3 className="course-name">{course.name}</h3>
            <p className="course-description">{course.description}</p>
            <div className="course-meta">
              <span className="meta-pill">Select</span>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}

export default CourseSelector;
