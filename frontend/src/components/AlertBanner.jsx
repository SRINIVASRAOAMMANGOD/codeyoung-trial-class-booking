// AlertBanner.jsx — Reusable banner for errors, conflicts, and warnings.

function AlertBanner({ type = 'error', message, onDismiss }) {
  if (!message) return null;

  return (
    <div className={`alert-banner alert-${type}`} role="alert">
      <div className="alert-content">
        <span className="alert-icon">
          {type === 'error' && '[!]'}
          {type === 'warning' && '[!]'}
          {type === 'info' && '[i]'}
        </span>
        <span className="alert-message">{message}</span>
      </div>
      {onDismiss && (
        <button
          type="button"
          className="alert-dismiss"
          onClick={onDismiss}
          aria-label="Dismiss notification"
        >
          ✕
        </button>
      )}
    </div>
  );
}

export default AlertBanner;
