// LandingFooter.jsx — Professional footer for the Codeyoung landing page.

function LandingFooter({ onBookTrial }) {
  const handleNav = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <footer className="landing-footer" role="contentinfo">
      <div className="landing-container">
        <div className="footer-grid">
          {/* Brand Column */}
          <div className="footer-brand-col">
            <div className="footer-logo">
              
              <span className="footer-logo-text">Codeyoung Trial Class</span>
            </div>
            <p className="footer-tagline">
              Live 1:1 coding classes for children — personalised, flexible, and hands-on.
            </p>
          </div>

          {/* Platform Links */}
          <div className="footer-links-col">
            <h3 className="footer-col-heading">Platform</h3>
            <ul className="footer-link-list">
              <li>
                <button type="button" className="footer-link" onClick={() => handleNav('courses')}>
                  Courses
                </button>
              </li>
              <li>
                <button type="button" className="footer-link" onClick={() => handleNav('how-it-works')}>
                  How It Works
                </button>
              </li>
              <li>
                <button type="button" className="footer-link" onClick={() => handleNav('features')}>
                  Why Learn with Us
                </button>
              </li>
              <li>
                <button type="button" className="footer-link" onClick={() => handleNav('testimonials')}>
                  Testimonials
                </button>
              </li>
              <li>
                <button type="button" className="footer-link" onClick={() => handleNav('faq')}>
                  FAQ
                </button>
              </li>
            </ul>
          </div>

          {/* Quick Actions */}
          <div className="footer-links-col">
            <h3 className="footer-col-heading">Quick Actions</h3>
            <ul className="footer-link-list">
              <li>
                <button type="button" className="footer-link footer-link-cta" onClick={() => onBookTrial()}>
                  Book a Free Trial
                </button>
              </li>
              <li>
                <a href="/staff" className="footer-link">Staff Portal (Demo)</a>
              </li>
              <li>
                <span className="footer-link footer-link-disabled">Privacy Policy (placeholder)</span>
              </li>
              <li>
                <span className="footer-link footer-link-disabled">Terms of Use (placeholder)</span>
              </li>
            </ul>
          </div>

          {/* Contact / Tech Info */}
          <div className="footer-links-col">
            <h3 className="footer-col-heading">Connect with the developer</h3>
            <ul className="footer-link-list footer-info-list">
              <li className="footer-info-item">
                <span className="footer-info-label">Developer:</span>
                <span>Srinivas Rao</span>
              </li>
              <li className="footer-info-item">
                <a href="https://linkedin.com/in/srinivasraoammangod" target="_blank" rel="noopener noreferrer" className="footer-link">LinkedIn</a>
              </li>
              <li className="footer-info-item">
                <a href="https://github.com/SRINIVASRAOAMMANGOD" target="_blank" rel="noopener noreferrer" className="footer-link">GitHub</a>
              </li>
              <li className="footer-info-item">
                <a href="https://ammangodsrinivasrao.netlify.app" target="_blank" rel="noopener noreferrer" className="footer-link">Personal Website</a>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright" style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
            Independent demonstration project created for a Codeyoung recruitment assessment. Not the official Codeyoung website. All displayed data is sample/fictional.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default LandingFooter;
