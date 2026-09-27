// CourseSection.jsx — Public course cards.

const COURSE_METADATA = {
  'Coding Fundamentals': {
    icon: '</>',
    age: 'Ages 6–10',
    level: 'Beginner',
    tag: 'Most Popular',
    tagColor: 'tag-gold',
  },
  'Python Programming': {
    icon: 'Py',
    age: 'Ages 10–16',
    level: 'Beginner – Intermediate',
    tag: 'High Demand',
    tagColor: 'tag-teal',
  },
  'Web Development': {
    icon: 'Web',
    age: 'Ages 12–18',
    level: 'Intermediate',
    tag: 'New',
    tagColor: 'tag-green',
  },
  'AI & Robotics': {
    icon: 'AI',
    age: 'Ages 10–16',
    level: 'Intermediate',
    tag: 'Trending',
    tagColor: 'tag-purple',
  },
  'Game Development': {
    icon: 'Game',
    age: 'Ages 10–16',
    level: 'Intermediate',
    tag: 'Course',
    tagColor: 'tag-purple',
  },
  'App Development': {
    icon: 'App',
    age: 'Ages 12–18',
    level: 'Advanced',
    tag: 'Course',
    tagColor: 'tag-teal',
  },
  'Data & Analytics': {
    icon: 'Data',
    age: 'Ages 14–18',
    level: 'Advanced',
    tag: 'Course',
    tagColor: 'tag-green',
  },
};

function CourseCard({ course, onBookTrial }) {
  return (
    <article className="course-card" aria-label={`Course: ${course.name}`}>
      <div className={`course-tag ${course.tagColor}`}>{course.tag}</div>
      <div className="course-icon-wrap">
        <span className="course-icon" aria-hidden="true">{course.icon}</span>
      </div>
      <h3 className="course-name">{course.name}</h3>
      <p className="course-description">{course.description}</p>
      <div className="course-meta">
        <span className="meta-pill">{course.age}</span>
        <span className="meta-pill">{course.level}</span>
      </div>
      <button
        type="button"
        className="course-cta-btn"
        onClick={() => {
          if (!course.fake) {
            onBookTrial(course.id);
          }
        }}
        id={`course-cta-${course.id}`}
        aria-label={`Book a free trial for ${course.name}`}
        disabled={course.fake}
        style={course.fake ? { opacity: 0.6, cursor: 'not-allowed', backgroundColor: '#e2e8f0', color: '#64748b' } : {}}
      >
        {course.fake ? 'Coming Soon' : 'Book Free Trial ↗'}
      </button>
    </article>
  );
}

import { useState, useEffect } from 'react';
import { getCourses } from '../api/bookingApi';

function CourseSection({ onBookTrial }) {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCourses() {
      try {
        const data = await getCourses();
        // Merge API data with local metadata
        const merged = data.map((c) => {
          const meta = COURSE_METADATA[c.name] || {
            icon: '🎓',
            age: 'All Ages',
            level: 'All Levels',
            tag: 'Course',
            tagColor: 'tag-gold',
          };
          return { ...c, ...meta, fake: false };
        });

        setCourses(merged);
      } catch (err) {
        console.error('Failed to load courses', err);
      } finally {
        setLoading(false);
      }
    }
    fetchCourses();
  }, []);

  return (
    <section className="landing-section course-section" id="courses" aria-labelledby="courses-heading">
      <div className="landing-container">
        <div className="section-label-row">
          <span className="section-label-pill">Our Curriculum</span>
        </div>
        <h2 className="landing-section-heading" id="courses-heading">
          Explore Our Courses
        </h2>
        <p className="landing-section-subheading">
          Sample courses available for children across different age groups and skill levels.
          All content below is illustrative of our course offering.
        </p>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>Loading courses...</div>
        ) : (
          <div className="courses-grid">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} onBookTrial={onBookTrial} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default CourseSection;
