// HeroSection.jsx — Landing page hero with headline, CTAs, and trust signals.

function HeroSection({ onBookTrial, onExploreCourses }) {
  return (
    <section className="hero-section" id="hero" aria-labelledby="hero-heading">
      <div className="hero-inner">
        {/* Left: Copy */}
        <div className="hero-copy">
          <div className="hero-eyebrow">
            <span className="eyebrow-pill">Live 1:1 Coding Classes</span>
          </div>

          <h1 className="hero-heading" id="hero-heading">
            Live coding classes that help your child{' '}
            <span className="hero-accent">build real skills.</span>
          </h1>

          <p className="hero-subheading">
            Personalised 1-on-1 learning with expert mentors, flexible scheduling,
            and hands-on projects — all from home.
          </p>

          {/* Trust Badges */}
          <div className="hero-trust-badges">
            <div className="trust-badge">
              
              <span>1:1 Live Learning</span>
            </div>
            <div className="trust-badge">
              
              <span>Flexible Scheduling</span>
            </div>
            <div className="trust-badge">
              
              <span>Expert Mentors</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="hero-cta-group">
            <button
              type="button"
              className="hero-btn-primary"
              onClick={() => onBookTrial()}
              id="hero-book-trial-btn"
            >
              Book a Free Trial →
            </button>
            <button
              type="button"
              className="hero-btn-secondary"
              onClick={onExploreCourses}
            >
              Explore Courses
            </button>
          </div>

          <p className="hero-footnote">
            No credit card required &bull; Instant classroom link confirmation
          </p>
        </div>

        {/* Right: Visual Illustration */}
        <div className="hero-visual" aria-hidden="true">
          <div className="learning-paths-visual">
            <div className="path-card" style={{ transform: 'rotate(-5deg) translateY(10px)' }}>
              <div className="path-icon">{'</>'}</div>
              <div className="path-text">Coding</div>
            </div>
            <div className="path-card" style={{ transform: 'rotate(5deg) translateY(-10px)' }}>
              <div className="path-icon">Py</div>
              <div className="path-text">Python</div>
            </div>
            <div className="path-card" style={{ transform: 'rotate(-2deg)' }}>
              <div className="path-icon">W3</div>
              <div className="path-text">Web Dev</div>
            </div>
            <div className="path-card" style={{ transform: 'rotate(4deg) translateY(10px)' }}>
              <div className="path-icon">AI</div>
              <div className="path-text">Robotics</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
