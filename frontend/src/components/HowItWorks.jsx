// HowItWorks.jsx — 4-step booking process explanation.

const STEPS = [
  {
    step: 1,
    icon: '1',
    title: 'Choose a Course',
    description:
      'Browse our curriculum and pick the subject area that interests your child — from Coding Basics to AI & Robotics.',
  },
  {
    step: 2,
    icon: '2',
    title: 'Pick a Convenient Time',
    description:
      'Select a date and time that works for you. Available slots are shown in your local timezone, and update in real time.',
  },
  {
    step: 3,
    icon: '3',
    title: 'Get Matched with a Mentor',
    description:
      'Our system automatically assigns an available expert mentor for your chosen slot — no waiting, instant confirmation.',
  },
  {
    step: 4,
    icon: '4',
    title: 'Join Your Live Trial Class',
    description:
      'Receive your classroom link instantly. Join the live 1-on-1 session at the scheduled time from any device.',
  },
];

function HowItWorks() {
  return (
    <section
      className="landing-section how-it-works-section"
      id="how-it-works"
      aria-labelledby="how-heading"
    >
      <div className="landing-container">
        <div className="section-label-row">
          <span className="section-label-pill">Simple Process</span>
        </div>
        <h2 className="landing-section-heading" id="how-heading">
          How It Works
        </h2>
        <p className="landing-section-subheading">
          From choosing a subject to joining a live class — your child can start learning in minutes.
        </p>

        <div className="steps-grid">
          {STEPS.map((s, i) => (
            <div className="step-card" key={s.step}>
              {/* Connector line between cards (not after last) */}
              {i < STEPS.length - 1 && (
                <div className="step-connector" aria-hidden="true" />
              )}
              <div className="step-number-badge" aria-label={`Step ${s.step}`}>
                {s.step}
              </div>
              <div className="step-icon" aria-hidden="true">{s.icon}</div>
              <h3 className="step-title">{s.title}</h3>
              <p className="step-desc">{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;
