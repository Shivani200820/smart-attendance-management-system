import React from 'react';
import { Radio, Shield, UserCheck, GraduationCap, LogOut, Menu, Activity, Sun, Moon, Bell } from 'lucide-react';

export default function Header({ currentUser, onLogout, toggleSidebar, isMobile, theme = 'dark', onToggleTheme }) {
  const renderRoleBadge = () => {
    switch (currentUser.role) {
      case 'ADMIN':
        return (
          <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Shield size={13} /> Admin / HOD
          </span>
        );
      case 'TEACHER':
        return (
          <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <UserCheck size={13} /> Faculty
          </span>
        );
      case 'STUDENT':
        return (
          <span className="badge" style={{ background: 'rgba(244, 63, 94, 0.2)', color: '#fb7185', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <GraduationCap size={13} /> Student
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <header className="glass-card" style={{
        borderRadius: 0,
        borderLeft: 0,
        borderRight: 0,
        borderTop: 0,
        padding: '0.85rem 1.5rem',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        background: theme === 'light' ? 'rgba(255, 255, 255, 0.95)' : 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(16px)',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1440px',
          margin: '0 auto',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {isMobile && (
              <button
                onClick={toggleSidebar}
                className="btn-secondary"
                style={{ padding: '0.4rem 0.6rem' }}
                aria-label="Toggle Sidebar"
              >
                <Menu size={20} />
              </button>
            )}

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{
                width: '38px',
                height: '38px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, var(--accent-primary), #4338ca)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-glow)',
              }}>
                <Radio size={20} color="#ffffff" />
              </div>
              <div>
                <div style={{ fontSize: '1.05rem', fontWeight: 800, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  JSPM's Bhivrabai Sawant Polytechnic
                  <span style={{ fontSize: '0.65rem', background: 'rgba(52, 211, 153, 0.15)', color: '#34d399', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid rgba(52, 211, 153, 0.3)' }}>
                    Pune
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Activity size={10} color="#10b981" /> Computer Engineering Dept • {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                </div>
              </div>
            </div>
          </div>

          {/* User Info & Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Theme Toggle Button */}
            <button
              onClick={onToggleTheme}
              className="btn-secondary"
              style={{
                padding: '0.45rem 0.75rem',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                borderRadius: '9999px',
                background: theme === 'light' ? '#e2e8f0' : 'rgba(255,255,255,0.08)'
              }}
              title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            >
              {theme === 'light' ? (
                <Moon size={16} color="#475569" />
              ) : (
                <Sun size={16} color="#fbbf24" />
              )}
              <span style={{ display: isMobile ? 'none' : 'inline', fontWeight: 600 }}>
                {theme === 'light' ? 'Dark' : 'Light'}
              </span>
            </button>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              padding: '0.35rem 0.85rem',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-glass)',
              borderRadius: '9999px',
            }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                {currentUser.full_name || currentUser.username}
              </span>
              {renderRoleBadge()}
            </div>

            <button
              onClick={onLogout}
              className="btn-secondary"
              style={{ padding: '0.4rem 0.85rem', fontSize: '0.82rem' }}
              title="Sign Out"
            >
              <LogOut size={15} /> <span style={{ display: isMobile ? 'none' : 'inline' }}>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Notice Board Ticker */}
      <div style={{
        background: theme === 'light' ? 'rgba(37, 99, 235, 0.08)' : 'linear-gradient(90deg, rgba(37, 99, 235, 0.15), rgba(16, 185, 129, 0.15))',
        borderBottom: '1px solid var(--border-glass)',
        padding: '0.35rem 1.5rem',
        fontSize: '0.78rem',
        color: 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        fontWeight: 500,
      }}>
        <Bell size={13} color="#3b82f6" />
        <span><strong>JSPM Campus Notice:</strong> Mid-Term Attendance Assessment Deadline is 25th August • Minimum 75% attendance mandatory.</span>
      </div>
    </>
  );
}
