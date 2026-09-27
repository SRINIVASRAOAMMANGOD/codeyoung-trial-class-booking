// App.jsx — Root coordinator.
// Supports switching between Parent Booking, Admin Dashboard, and Mentor Portal.

import { useState, useEffect } from 'react';
import BookingPage from './pages/BookingPage';
import AdminPage from './pages/AdminPage';
import MentorPage from './pages/MentorPage';

function App() {
  const [currentView, setCurrentView] = useState(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const v = params.get('view');
      if (v === 'admin' || v === 'mentor') return v;
    }
    return 'booking';
  });

  const handleViewChange = (newView) => {
    setCurrentView(newView);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      if (newView === 'booking') {
        url.searchParams.delete('view');
      } else {
        url.searchParams.set('view', newView);
      }
      window.history.pushState({}, '', url.toString());
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      setCurrentView(params.get('view') || 'booking');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  if (currentView === 'admin') {
    return <AdminPage currentView={currentView} onViewChange={handleViewChange} />;
  }

  if (currentView === 'mentor') {
    return <MentorPage currentView={currentView} onViewChange={handleViewChange} />;
  }

  return <BookingPage currentView={currentView} onViewChange={handleViewChange} />;
}

export default App;
