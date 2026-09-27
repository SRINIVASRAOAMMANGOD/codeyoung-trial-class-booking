// Header.jsx — Brand header, title, and view switcher navigation.

function Header({ currentView = 'booking', onViewChange, onBackToLanding }) {
  return (
    <>
      <header className={currentView === 'booking' ? "landing-header" : "internal-app-header"} role="banner">
        <div className={currentView === 'booking' ? "landing-header-inner" : "internal-header-left"}>
          {currentView === 'booking' ? (
            <button 
              type="button"
              className="landing-logo" 
              onClick={onBackToLanding}
              aria-label="Back to Codeyoung Home"
            >
              <span className="logo-text">Codeyoung</span>
            </button>
          ) : (
            <button 
              type="button"
              className="internal-brand" 
              onClick={() => onViewChange('staff')}
              style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
              aria-label="Back to Staff Portal"
            >
              CODEYOUNG STAFF
            </button>
          )}
        </div>

        {onViewChange && currentView !== 'booking' && (
          <nav className="internal-app-nav" aria-label="Portal Navigation">
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
          </nav>
        )}
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
