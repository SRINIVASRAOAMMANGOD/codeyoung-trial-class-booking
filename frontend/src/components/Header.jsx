// Header.jsx — Brand header, title, and view switcher navigation.

function Header({ currentView = 'booking', onViewChange, onBackToLanding }) {
  return (
    <>
      <header className="landing-header" role="banner">
        <div className="landing-header-inner">
          <button 
            type="button"
            className="landing-logo" 
            onClick={onBackToLanding || (() => onViewChange('landing'))}
            aria-label="Codeyoung home"
          >
            <span className="logo-text">Codeyoung</span>
          </button>

          {onViewChange && currentView !== 'booking' && (
            <nav className="internal-app-nav" aria-label="Portal Navigation" style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', marginLeft: 'auto' }}>
              <button
                type="button"
                className={`internal-nav-link ${currentView === 'staff' ? 'active' : ''}`}
                onClick={() => onViewChange('staff')}
              >
                Staff Home
              </button>
              <button
                type="button"
                className={`internal-nav-link ${currentView === 'admin' ? 'active' : ''}`}
                onClick={() => onViewChange('admin')}
              >
                Admin Dashboard
              </button>
              <button
                type="button"
                className={`internal-nav-link ${currentView === 'mentor' ? 'active' : ''}`}
                onClick={() => onViewChange('mentor')}
              >
                Mentor View
              </button>
              <button
                type="button"
                className="internal-nav-link"
                onClick={() => onViewChange('landing')}
                style={{ fontWeight: 600, color: 'var(--color-text)', borderLeft: '1px solid var(--color-border)', paddingLeft: '1.5rem' }}
              >
                Back to Website
              </button>
            </nav>
          )}
        </div>
      </header>

      {/* Page Title Banner - only for admin/mentor/staff as booking form is self-contained */}
      {currentView !== 'booking' && currentView !== 'staff' && (
        <div className="internal-page-banner">
          <h1 className="header-title">
            {currentView === 'admin'
              ? 'Operational Admin Dashboard'
              : 'Mentor Assignment Portal'}
          </h1>
          <p className="header-subtitle">
            {currentView === 'admin'
              ? 'Monitor dynamic mentor capacity, manage roster, inspect parent accounts, and review confirmed bookings.'
              : 'View your assigned trial demo classes, student contacts, and classroom room links in India Standard Time.'}
          </p>
        </div>
      )}
    </>
  );
}

export default Header;
