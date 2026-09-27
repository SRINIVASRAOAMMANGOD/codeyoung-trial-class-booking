import React, { useState } from 'react';
import { resendEmail } from '../api/adminApi';
import AlertBanner from './AlertBanner';

function ResendEmailModal({ booking, onClose, onSuccess }) {
  const [recipientType, setRecipientType] = useState('parent');
  const [recipientEmail, setRecipientEmail] = useState(booking.parent_email);
  const [customSubject, setCustomSubject] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleTypeChange = (type) => {
    setRecipientType(type);
    if (type === 'parent') {
      setRecipientEmail(booking.parent_email);
    } else {
      // For admin view, we don't have mentor_email in booking list natively unless joined, but we can assume empty if missing, backend will handle it
      setRecipientEmail(''); 
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setAlert(null);

    try {
      await resendEmail(booking.id, {
        recipient_type: recipientType,
        recipient_email: recipientEmail,
        custom_subject: customSubject || null,
      });
      setAlert({ type: 'success', message: 'Email sent successfully!' });
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
      }, 1500);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to send email.' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
      backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', 
      alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div className="modal-content card" style={{ padding: '2rem', maxWidth: '500px', width: '100%', position: 'relative' }}>
        <button 
          onClick={onClose}
          style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: 'var(--color-text-muted)' }}
          aria-label="Close"
        >
          &times;
        </button>
        <h2 style={{ marginBottom: '1.5rem', color: 'var(--cy-teal)' }}>Resend Email (Booking #{booking.id})</h2>
        
        {alert && <AlertBanner type={alert.type} message={alert.message} />}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label className="form-label">Recipient Type</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input type="radio" name="recType" value="parent" checked={recipientType === 'parent'} onChange={() => handleTypeChange('parent')} />
                Parent
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input type="radio" name="recType" value="mentor" checked={recipientType === 'mentor'} onChange={() => handleTypeChange('mentor')} />
                Mentor
              </label>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Recipient Email <span className="required">*</span></label>
            <input 
              type="email" 
              className="form-input" 
              value={recipientEmail} 
              onChange={e => setRecipientEmail(e.target.value)} 
              required
            />
            <small style={{ color: 'var(--color-text-muted)' }}>You can override the default recipient email if needed.</small>
          </div>

          <div className="form-group">
            <label className="form-label">Custom Subject (Optional)</label>
            <input 
              type="text" 
              className="form-input" 
              value={customSubject} 
              onChange={e => setCustomSubject(e.target.value)} 
              placeholder="e.g. Updated Class Details"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting} style={{ marginTop: '1rem' }}>
            {submitting ? 'Sending...' : 'Send Email'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ResendEmailModal;
