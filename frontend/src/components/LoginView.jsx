import React, { useState } from 'react';
import { LogIn, Shield, UserCheck, GraduationCap, AlertCircle } from 'lucide-react';
import { api, setAuthToken, setStoredUser } from '../api';

export default function LoginView({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please fill in both username and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await api.login(username, password);
      setAuthToken(res.access_token);
      setStoredUser(res.user);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCreds = (u, p) => {
    setUsername(u);
    setPassword(p);
    setError('');
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '1.5rem',
    }}>
      <div className="glass-card" style={{
        width: '100%',
        maxWidth: '460px',
        padding: '2.5rem',
        borderRadius: '24px',
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, var(--accent-primary), #4338ca)',
            boxShadow: 'var(--shadow-glow)',
            marginBottom: '1rem',
          }}>
            <UserCheck size={32} color="#ffffff" />
          </div>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent-primary)', fontWeight: 700, marginBottom: '0.2rem' }}>
            JSPM's Bhivrabai Sawant Polytechnic, Pune
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
            Attendance MS
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.35rem' }}>
            Sign in to access your portal
          </p>
        </div>

        {error && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.85rem 1rem',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: '#fca5a5',
            fontSize: '0.88rem',
            marginBottom: '1.5rem',
          }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Username / Identification
            </label>
            <input
              type="text"
              className="glass-input"
              placeholder="e.g. admin, teacher1, student1"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Password
            </label>
            <input
              type="password"
              className="glass-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem', height: '48px', fontSize: '1rem' }}
          >
            {loading ? 'Authenticating...' : <><LogIn size={18} /> Sign In</>}
          </button>
        </form>

        {/* Demo Login Shortcuts */}
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-glass)' }}>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', textAlign: 'center', marginBottom: '0.85rem' }}>
            Quick Development Login
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
            <button
              onClick={() => fillDemoCreds('admin', 'AdminPass@123')}
              className="btn-secondary"
              style={{ padding: '0.5rem', fontSize: '0.78rem', flexDirection: 'column', gap: '0.25rem' }}
            >
              <Shield size={16} color="#818cf8" />
              Admin
            </button>

            <button
              onClick={() => fillDemoCreds('teacher1', 'JSPM#Faculty2026!')}
              className="btn-secondary"
              style={{ padding: '0.5rem', fontSize: '0.78rem', flexDirection: 'column', gap: '0.25rem' }}
            >
              <UserCheck size={16} color="#34d399" />
              Teacher
            </button>

            <button
              onClick={() => fillDemoCreds('student1', 'StudentPass123!')}
              className="btn-secondary"
              style={{ padding: '0.5rem', fontSize: '0.78rem', flexDirection: 'column', gap: '0.25rem' }}
            >
              <GraduationCap size={16} color="#f43f5e" />
              Student
            </button>
          </div>
        </div>

        {/* Small College Footer */}
        <div style={{ marginTop: '1.75rem', textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          © 2026 JSPM's Bhivrabai Sawant Polytechnic<br />
          Computer Engineering Department
        </div>
      </div>
    </div>
  );
}
