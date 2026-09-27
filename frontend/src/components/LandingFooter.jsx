// LandingFooter.jsx — Professional footer for the Codeyoung landing page.

import { useState } from 'react';

function LandingFooter({ onBookTrial }) {
  const [legalModalOpen, setLegalModalOpen] = useState(false);
  const [legalTitle, setLegalTitle] = useState('');

  const handleNav = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const openLegalModal = (title) => {
    setLegalTitle(title);
    setLegalModalOpen(true);
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
                <button type="button" className="footer-link" onClick={() => openLegalModal('Privacy Policy')}>Privacy Policy</button>
              </li>
              <li>
                <button type="button" className="footer-link" onClick={() => openLegalModal('Terms of Use')}>Terms of Use</button>
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

      {/* Legal Modal */}
      {legalModalOpen && (
        <div className="modal-backdrop" onClick={() => setLegalModalOpen(false)} style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 10000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ backgroundColor: '#fff', padding: '2rem', borderRadius: '12px', width: '90%', maxWidth: '400px', position: 'relative' }}>
            <button className="modal-close" onClick={() => setLegalModalOpen(false)} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
            <h2 style={{ marginBottom: '1rem' }}>{legalTitle}</h2>
            
            <div style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '8px', backgroundColor: '#f8fafc', color: 'var(--color-text)' }}>
              <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Disclaimer</p>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>
                Independent demonstration project created for a Codeyoung recruitment assessment. Not the official Codeyoung website. All displayed data is sample/fictional.
              </p>
            </div>
            
            <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
              These are demo placeholders and do not represent actual legal documents.
            </p>
          </div>
        </div>
      )}
    </footer>
  );
}

export default LandingFooter;
