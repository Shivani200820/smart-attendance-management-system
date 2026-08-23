import React, { useState, useEffect } from 'react';
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import LoginView from './components/LoginView';
import AdminDashboard from './components/AdminDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import StudentDashboard from './components/StudentDashboard';
import SplashScreen from './components/SplashScreen';
import { getStoredUser, removeAuthToken, getAuthToken } from './api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpenMobile, setSidebarOpenMobile] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [theme, setTheme] = useState(() => localStorage.getItem('jspm_theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('jspm_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  useEffect(() => {
    // Mobile detection
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    const user = getStoredUser();
    if (token && user) {
      setCurrentUser(user);
    }

    const handleUnauthorized = () => {
      setCurrentUser(null);
    };
    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);

  // Hash-based URL routing sync
  useEffect(() => {
    if (!currentUser) return;

    const handleHashChange = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (hash) {
        setActiveTab(hash);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [currentUser]);

  const handleSelectTab = (tabId) => {
    setActiveTab(tabId);
    window.location.hash = `#/${tabId}`;
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setActiveTab('overview');
    window.location.hash = '#/overview';
  };

  const handleLogout = () => {
    removeAuthToken();
    setCurrentUser(null);
    window.location.hash = '';
  };

  return (
    <>
      {showSplash && (
        <SplashScreen onComplete={() => setShowSplash(false)} />
      )}

      {!currentUser ? (
        <LoginView onLoginSuccess={handleLoginSuccess} />
      ) : (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-main)', color: 'var(--text-primary)' }}>
          {/* Top App Header */}
          <Header
            currentUser={currentUser}
            onLogout={handleLogout}
            toggleSidebar={() => setSidebarOpenMobile(!sidebarOpenMobile)}
            isMobile={isMobile}
            theme={theme}
            onToggleTheme={toggleTheme}
          />

          {/* Main Body with Sidebar + Subviews */}
          <div style={{ flex: 1, display: 'flex', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
            {/* Role-based Sidebar */}
            <Sidebar
              role={currentUser.role}
              activeTab={activeTab}
              onSelectTab={handleSelectTab}
              isOpen={sidebarOpenMobile}
              isMobile={isMobile}
              onCloseMobile={() => setSidebarOpenMobile(false)}
            />

            {/* Dynamic Portal Sub-View */}
            <main style={{ flex: 1, padding: '2rem 1.5rem', minWidth: 0 }}>
              {currentUser.role === 'ADMIN' && (
                <AdminDashboard activeTab={activeTab} onNavigate={handleSelectTab} />
              )}

              {currentUser.role === 'TEACHER' && (
                <TeacherDashboard user={currentUser} activeTab={activeTab} onNavigate={handleSelectTab} />
              )}

              {currentUser.role === 'STUDENT' && (
                <StudentDashboard user={currentUser} activeTab={activeTab} onNavigate={handleSelectTab} />
              )}
            </main>
          </div>

          {/* Footer */}
          <footer style={{
            textAlign: 'center',
            padding: '1.25rem',
            color: 'var(--text-muted)',
            fontSize: '0.82rem',
            borderTop: '1px solid var(--border-glass)',
            background: 'rgba(15, 23, 42, 0.4)',
          }}>
            © 2026 JSPM's Bhivrabai Sawant Polytechnic • Department of Computer Engineering • Pune, Maharashtra
          </footer>
        </div>
      )}
    </>
  );
}
