// App.jsx — Root coordinator.
// Default view: 'landing' (public landing page).
// 'booking' → trial class booking flow.
// 'admin' → internal operational admin dashboard.
// 'mentor' → internal demo mentor view.

import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import BookingPage from './pages/BookingPage';
import AdminPage from './pages/AdminPage';
import MentorPage from './pages/MentorPage';
import StaffPage from './pages/StaffPage';

function App() {
  const [currentView, setCurrentView] = useState(() => {
    if (typeof window !== 'undefined') {
      const pathname = window.location.pathname;
      if (pathname.startsWith('/staff')) {
        return 'staff';
      }
      const params = new URLSearchParams(window.location.search);
      const v = params.get('view');
      if (v === 'booking' || v === 'admin' || v === 'mentor' || v === 'staff') return v;
    }
    return 'landing';
  });

  const handleViewChange = (newView, options = {}) => {
    setCurrentView(newView);
    if (typeof window !== 'undefined') {
      let url = new URL(window.location.href);
      
      // If we go to landing, reset to /
      if (newView === 'landing') {
        url.pathname = '/';
        url.searchParams.delete('view');
        url.searchParams.delete('course');
      } else if (newView === 'staff') {
        url.pathname = '/staff';
        url.searchParams.delete('view');
        url.searchParams.delete('course');
      } else {
        // If we were on /staff, and now go to admin/mentor, we might want to stay on /staff?view=admin
        // Or revert to /?view=admin. The instructions don't mandate the exact URL for admin/mentor.
        // Let's just use ?view=admin on the current path, or reset to /?view=admin.
        if (newView === 'admin' || newView === 'mentor') {
          url.pathname = '/staff';
          url.searchParams.set('view', newView);
        } else {
          url.pathname = '/';
          url.searchParams.set('view', newView);
        }
        
        if (options.courseId && typeof options.courseId !== 'object') {
          url.searchParams.set('course', options.courseId);
        }
      }
      
      window.history.pushState({}, '', url.toString());
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      const pathname = window.location.pathname;
      const params = new URLSearchParams(window.location.search);
      const v = params.get('view');
      
      if (v === 'booking' || v === 'admin' || v === 'mentor' || v === 'staff') {
        setCurrentView(v);
      } else if (pathname.startsWith('/staff')) {
        setCurrentView('staff');
      } else {
        setCurrentView('landing');
      }
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

  if (currentView === 'staff') {
    return (
      <StaffPage 
        onViewChange={handleViewChange}
        onBackToLanding={() => handleViewChange('landing')}
      />
    );
  }

  if (currentView === 'booking') {
    return (
      <BookingPage
        currentView={currentView}
        onViewChange={handleViewChange}
        onBackToLanding={() => handleViewChange('landing')}
      />
    );
  }

  // Default: landing page
  return <LandingPage onBookTrial={(courseId) => handleViewChange('booking', { courseId })} onViewChange={handleViewChange} />;
}

export default App;
