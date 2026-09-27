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
      <div className="compact-courses-grid">
        {courses.map((course) => (
          <label 
            key={course.id} 
            className={`compact-course-card ${selectedCourseId === course.id ? 'selected' : ''}`}
          >
            <input
              type="radio"
              name="courseSelection"
              value={course.id}
              checked={selectedCourseId === course.id}
              onChange={() => onSelectCourse(course.id)}
              className="sr-only"
            />
            <h3 className="compact-course-name">{course.name}</h3>
            <p className="compact-course-desc">{course.description.substring(0, 50)}...</p>
            <div className="compact-course-indicator">
              {selectedCourseId === course.id ? '✓ Selected' : 'Select'}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}

export default CourseSelector;
