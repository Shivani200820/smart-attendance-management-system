import React from 'react';
import {
  LayoutDashboard,
  Users,
  Building2,
  Calendar,
  AlertTriangle,
  FileCheck2,
  BookOpen,
  QrCode,
  CheckSquare,
  BarChart3,
  Clock,
  History,
  Calculator,
  Layers,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ role, activeTab, onSelectTab, isOpen, isMobile, onCloseMobile }) {
  const getNavItems = () => {
    switch (role) {
      case 'ADMIN':
        return [
          { id: 'overview', label: 'Dashboard Overview', icon: LayoutDashboard },
          { id: 'users', label: 'User Management', icon: Users },
          { id: 'academic', label: 'Academic Structure', icon: Building2 },
          { id: 'timetable', label: 'Timetable Schedules', icon: Calendar },
          { id: 'defaulters', label: 'Defaulters & Analytics', icon: AlertTriangle },
          { id: 'audit', label: 'Audit Trail & Corrections', icon: FileCheck2 },
        ];
      case 'TEACHER':
        return [
          { id: 'overview', label: 'Teacher Dashboard', icon: LayoutDashboard },
          { id: 'my-classes', label: 'My Assigned Classes', icon: Layers },
          { id: 'timetable', label: 'My Timetable', icon: Calendar },
          { id: 'start-session', label: 'Start Attendance Session', icon: QrCode, highlight: true },
          { id: 'live-monitor', label: 'Live Session Monitor', icon: Clock },
          { id: 'records', label: 'Session Records', icon: CheckSquare },
          { id: 'corrections', label: 'Corrections & Audit', icon: FileCheck2 },
          { id: 'reports', label: 'Class Defaulter Reports', icon: BarChart3 },
        ];
      case 'STUDENT':
        return [
          { id: 'overview', label: 'Student Dashboard', icon: LayoutDashboard },
          { id: 'mark-attendance', label: 'Mark Attendance', icon: QrCode, highlight: true },
          { id: 'subject-breakdown', label: 'Subject Attendance', icon: BookOpen },
          { id: 'risk-calculator', label: 'Smart Margin & Risk Calc', icon: Calculator, badge: 'Smart' },
          { id: 'timetable', label: 'My Timetable', icon: Calendar },
          { id: 'history', label: 'Attendance Log History', icon: History },
        ];
      default:
        return [];
    }
  };

  const navItems = getNavItems();

  const sidebarStyles = {
    width: '260px',
    flexShrink: 0,
    background: 'rgba(15, 23, 42, 0.75)',
    backdropFilter: 'blur(16px)',
    borderRight: '1px solid var(--border-glass)',
    display: 'flex',
    flexDirection: 'column',
    padding: '1.5rem 1rem',
    transition: 'transform 0.3s ease, left 0.3s ease',
    ...(isMobile ? {
      position: 'fixed',
      top: 0,
      bottom: 0,
      left: isOpen ? 0 : '-280px',
      zIndex: 200,
      boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
    } : {}),
  };

  return (
    <>
      {isMobile && isOpen && (
        <div
          onClick={onCloseMobile}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(4px)',
            zIndex: 199,
          }}
        />
      )}

      <aside style={sidebarStyles}>
        <div style={{ marginBottom: '1.5rem', padding: '0 0.5rem' }}>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', fontWeight: 700 }}>
            {role} PORTAL MENU
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  if (isMobile) onCloseMobile();
                }}
                className={`btn-sidebar ${isActive ? 'active' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 0.9rem',
                  borderRadius: '12px',
                  border: 'none',
                  fontSize: '0.88rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(67, 56, 202, 0.25))'
                    : item.highlight
                    ? 'rgba(99, 102, 241, 0.1)'
                    : 'transparent',
                  color: isActive
                    ? '#ffffff'
                    : item.highlight
                    ? '#a5b4fc'
                    : 'var(--text-secondary)',
                  borderLeft: isActive ? '3px solid var(--accent-primary)' : '3px solid transparent',
                  boxShadow: isActive ? '0 4px 12px rgba(99, 102, 241, 0.2)' : 'none',
                }}
              >
                <Icon size={18} color={isActive ? '#818cf8' : item.highlight ? '#a5b4fc' : 'currentColor'} />
                <span style={{ flex: 1 }}>{item.label}</span>

                {item.badge && (
                  <span style={{
                    fontSize: '0.65rem',
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    color: '#ffffff',
                    padding: '0.15rem 0.45rem',
                    borderRadius: '9999px',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.15rem',
                  }}>
                    <Sparkles size={9} /> {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer info box */}
        <div className="glass-card" style={{ padding: '0.85rem', borderRadius: '12px', marginTop: 'auto', background: 'rgba(255,255,255,0.02)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            JSPM's B. S. Polytechnic
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Computer Engineering • Pune
          </div>
        </div>
      </aside>
    </>
  );
}
