// FeaturesSection.jsx — "Why Learn with Us" feature highlights.

const FEATURES = [
  {
    id: 'one-on-one',
    icon: '1',
    title: 'Personalised 1:1 Learning',
    description:
      'Every session is dedicated entirely to your child. One mentor, one student — complete focus and individual attention throughout.',
  },
  {
    id: 'expert-mentors',
    icon: '2',
    title: 'Expert Mentors',
    description:
      'Sessions are conducted by qualified, experienced coding educators who make learning engaging, practical, and fun.',
  },
  {
    id: 'flexible-scheduling',
    icon: '3',
    title: 'Flexible Scheduling',
    description:
      'Available slots are shown in your local timezone. Choose times that genuinely fit your family\'s routine.',
  },
  {
    id: 'hands-on',
    icon: '4',
    title: 'Hands-on Learning',
    description:
      'Children learn by building real things — games, websites, and programs — reinforcing concepts through practical creation.',
  },
];

function FeaturesSection() {
  return (
    <section
      className="landing-section features-section"
      id="features"
      aria-labelledby="features-heading"
    >
      <div className="landing-container">
        <div className="section-label-row">
          <span className="section-label-pill">Our Approach</span>
        </div>
        <h2 className="landing-section-heading" id="features-heading">
          Why Learn with Us
        </h2>
        <p className="landing-section-subheading">
          A learning environment designed to help children genuinely enjoy and understand coding.
        </p>

        <div className="features-grid">
          {FEATURES.map((f) => (
            <div className="feature-card" key={f.id}>
              <div className="feature-icon-wrap" aria-hidden="true">
                <span className="feature-icon">{f.icon}</span>
              </div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;
