import React from 'react';
import Header from '../components/Header';

function StaffPage({ onViewChange, onBackToLanding }) {
  return (
    <div className="staff-page-layout" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        currentView="staff"
        onViewChange={onViewChange}
        onBackToLanding={onBackToLanding}
      />
      
      <main className="staff-container" style={{ maxWidth: '800px', margin: '0 auto', padding: '3rem 1.5rem', flex: 1, width: '100%' }}>
        <div className="card" style={{ padding: '2rem', textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', color: 'var(--cy-teal)', marginBottom: '1rem' }}>Demo Staff Portal</h2>
          
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-warning-light)', color: 'var(--color-warning)', borderRadius: 'var(--radius-md)', marginBottom: '2rem', border: '1px solid var(--color-warning)' }}>
            <strong>Notice:</strong> This is a demo internal portal. Authentication and Role-Based Access Control (RBAC) are not implemented.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <button 
              className="btn btn-primary" 
              onClick={() => onViewChange('admin')}
              style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}
            >
              <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Admin Login</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 'normal', opacity: 0.9 }}>Manage mentors & view capacity</span>
            </button>
            
            <button 
              className="btn btn-secondary" 
              onClick={() => onViewChange('mentor')}
              style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}
            >
              <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Mentor Login</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 'normal', opacity: 0.9 }}>View assigned classes</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default StaffPage;
