// Header.jsx — Brand header, title, and view switcher navigation.

function Header({ currentView = 'booking', onViewChange }) {
  return (
    <header className="app-header">
      {/* View Switcher Bar */}
      {onViewChange && (
        <nav className="view-switcher-nav" aria-label="Portal Navigation">
          <button
            type="button"
            className={`view-nav-btn ${currentView === 'booking' ? 'active' : ''}`}
            onClick={() => onViewChange('booking')}
          >
            📅 Parent Booking
          </button>
          <button
            type="button"
            className={`view-nav-btn ${currentView === 'admin' ? 'active' : ''}`}
            onClick={() => onViewChange('admin')}
          >
            🛡️ Admin Dashboard
          </button>
          <button
            type="button"
            className={`view-nav-btn ${currentView === 'mentor' ? 'active' : ''}`}
            onClick={() => onViewChange('mentor')}
          >
            👩‍🏫 Mentor View
          </button>
        </nav>
      )}

      <div className="brand-badge">Codeyoung</div>
      <h1 className="header-title">
        {currentView === 'admin'
          ? 'Operational Admin Dashboard'
          : currentView === 'mentor'
          ? 'Mentor Assignment Portal'
          : 'Book a Free Trial Coding Class'}
      </h1>
      <p className="header-subtitle">
        {currentView === 'admin'
          ? 'Monitor dynamic mentor capacity, manage roster, inspect parent accounts, and review confirmed bookings.'
          : currentView === 'mentor'
          ? 'View your assigned trial demo classes, student contacts, and classroom room links in India Standard Time.'
          : '1-on-1 interactive session with an expert mentor. Select your convenient date and local time.'}
      </p>
    </header>
  );
}

export default Header;
