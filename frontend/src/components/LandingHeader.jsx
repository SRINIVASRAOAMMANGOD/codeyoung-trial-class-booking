// LandingHeader.jsx — Sticky public navigation for the Codeyoung landing page.
// Admin/Mentor internal access is hidden from public nav.

import { useState } from 'react';

function LandingHeader({ onBookTrial }) {
  const [menuOpen, setMenuOpen] = useState(false);

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
            className="mobile-nav-cta"
            onClick={() => { setMenuOpen(false); onBookTrial(); }}
          >
            Book a Free Trial
          </button>
        </div>
      )}
    </header>
  );
}

export default LandingHeader;
