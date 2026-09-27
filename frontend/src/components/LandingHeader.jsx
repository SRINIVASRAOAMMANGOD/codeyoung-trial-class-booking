// LandingHeader.jsx — Sticky public navigation for the Codeyoung landing page.
// Admin/Mentor internal access is hidden from public nav.

import { useState } from 'react';

function LandingHeader({ onBookTrial, onViewChange }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  const scrollTo = (id) => {
    setMenuOpen(false);
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const navLinks = [
    { label: 'Home', id: 'hero' },
    { label: 'Courses', id: 'courses' },
    { label: 'How It Works', id: 'how-it-works' },
    { label: 'Testimonials', id: 'testimonials' },
    { label: 'FAQ', id: 'faq' },
  ];

  return (
    <header className="landing-header" role="banner">
      <div className="landing-header-inner">
        {/* Logo / Brand */}
        <button
          type="button"
          className="landing-logo"
          onClick={() => scrollTo('hero')}
          aria-label="Codeyoung home"
        >
          
          <span className="logo-text">Codeyoung</span>
        </button>

        {/* Desktop Navigation */}
        <nav className="landing-nav" aria-label="Main navigation">
          {navLinks.map((link) => (
            <button
              key={link.id}
              type="button"
              className="landing-nav-link"
              onClick={() => scrollTo(link.id)}
            >
              {link.label}
            </button>
          ))}
        </nav>

        {/* Desktop CTA */}
        <div className="landing-header-actions">
          <button
            type="button"
            className="landing-nav-link"
            onClick={() => setLoginModalOpen(true)}
            style={{ fontWeight: 600 }}
          >
            Login
          </button>
          <button
            type="button"
            className="landing-btn-cta"
            onClick={() => onBookTrial()}
            id="header-book-trial-btn"
          >
            Book a Free Trial
          </button>
        </div>

        {/* Mobile hamburger */}
        <button
          type="button"
          className="hamburger-btn"
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((o) => !o)}
        >
          <span className={`hamburger-bar ${menuOpen ? 'bar-top-open' : ''}`} />
          <span className={`hamburger-bar ${menuOpen ? 'bar-mid-open' : ''}`} />
          <span className={`hamburger-bar ${menuOpen ? 'bar-bot-open' : ''}`} />
        </button>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="mobile-menu" role="navigation" aria-label="Mobile navigation">
          {navLinks.map((link) => (
            <button
              key={link.id}
              type="button"
              className="mobile-nav-link"
              onClick={() => scrollTo(link.id)}
            >
              {link.label}
            </button>
          ))}
          <button
            type="button"
            className="mobile-nav-link"
            onClick={() => { setMenuOpen(false); setLoginModalOpen(true); }}
            style={{ fontWeight: 600 }}
          >
            Login
          </button>
          <button
            type="button"
            className="mobile-nav-cta"
            onClick={() => { setMenuOpen(false); onBookTrial(); }}
          >
            Book a Free Trial
          </button>
        </div>
      )}

      {/* Login Modal */}
      {loginModalOpen && (
        <div className="modal-backdrop" onClick={() => setLoginModalOpen(false)} style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 10000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ backgroundColor: '#fff', padding: '2rem', borderRadius: '12px', width: '90%', maxWidth: '400px', position: 'relative' }}>
            <button className="modal-close" onClick={() => setLoginModalOpen(false)} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
            <h2 style={{ marginBottom: '0.5rem' }}>Login</h2>
            <p style={{ marginBottom: '1.5rem', color: 'var(--color-text-muted)' }}>Choose your portal</p>
            
            <div className="login-options" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <button className="login-option" disabled style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '8px', textAlign: 'left', opacity: 0.5, cursor: 'not-allowed', backgroundColor: '#f8fafc' }}>
                <strong style={{ display: 'block', fontSize: '1.1rem' }}>Student</strong>
                <span style={{ fontSize: '0.85rem' }}>Not available for this assessment</span>
              </button>
              <button className="login-option" onClick={() => onViewChange('mentor')} style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '8px', textAlign: 'left', cursor: 'pointer', backgroundColor: '#fff', transition: 'all 0.2s' }}>
                <strong style={{ display: 'block', fontSize: '1.1rem' }}>Mentor</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Open Mentor Portal</span>
              </button>
              <button className="login-option" onClick={() => onViewChange('admin')} style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: '8px', textAlign: 'left', cursor: 'pointer', backgroundColor: '#fff', transition: 'all 0.2s' }}>
                <strong style={{ display: 'block', fontSize: '1.1rem' }}>Admin</strong>
                <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Open Admin Portal</span>
              </button>
            </div>
            
            <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
              Demo login — authentication/RBAC is not implemented.
            </p>
          </div>
        </div>
      )}
    </header>
  );
}

export default LandingHeader;
