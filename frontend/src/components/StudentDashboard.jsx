import React, { useState, useEffect } from 'react';
import {
  QrCode,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Award,
  CheckSquare,
  Calculator,
  History,
  Calendar,
  Sparkles,
  ShieldCheck,
  Clock,
  ArrowRight,
  Camera,
  IdCard,
  FileText,
  X,
  UserCheck
} from 'lucide-react';
import { api } from '../api';
import RiskBadge from './common/RiskBadge';
import Toast from './common/Toast';

export default function StudentDashboard({ user, activeTab = 'overview', onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  // Modals & Toast State
  const [showIdCard, setShowIdCard] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [showCorrectionModal, setShowCorrectionModal] = useState(false);
  const [correctionSubject, setCorrectionSubject] = useState('');
  const [correctionReason, setCorrectionReason] = useState('');
  const [toast, setToast] = useState({ message: '', type: 'success' });

  // Mark attendance state
  const [tokenInput, setTokenInput] = useState('');
  const [markLoading, setMarkLoading] = useState(false);
  const [markResult, setMarkResult] = useState(null);
  const [markError, setMarkError] = useState('');
  const [activeStep, setActiveStep] = useState('IDLE'); // IDLE, VALIDATING, SUCCESS, ERROR

  // Active sessions available for student's division
  const [activeSessions, setActiveSessions] = useState([]);

  // Timetable
  const [timetables, setTimetables] = useState([]);

  // History log
  const [historyLogs, setHistoryLogs] = useState([]);

  // Smart Margin Calculator Interactive State
  const [projectedMisses, setProjectedMisses] = useState(0);

  useEffect(() => {
    fetchStudentData();
  }, [activeTab]);

  const fetchStudentData = async () => {
    setLoading(true);
    try {
      const [sumData, activeSess, ttData, histData] = await Promise.all([
        api.getMySummary().catch(() => null),
        api.getSessions({ status: 'ACTIVE' }).catch(() => []),
        api.getTimetables().catch(() => []),
        api.getMyHistory().catch(() => []),
      ]);

      setSummary(sumData);
      setActiveSessions(activeSess);
      setTimetables(ttData);
      setHistoryLogs(histData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAttendance = async (e) => {
    if (e) e.preventDefault();
    if (!tokenInput.trim()) {
      setMarkError('Please enter a valid session token');
      return;
    }

    setMarkLoading(true);
    setMarkError('');
    setMarkResult(null);
    setActiveStep('VALIDATING');

    try {
      const result = await api.studentMarkAttendance(tokenInput.trim());
      setMarkResult(result);
      setTokenInput('');
      setActiveStep('SUCCESS');
      fetchStudentData();
    } catch (err) {
      setMarkError(err.message);
      setActiveStep('ERROR');
    } finally {
      setMarkLoading(false);
    }
  };

  // Smart Risk Margin Calculation Logic
  const total = summary ? summary.total_sessions : 0;
  const attended = summary ? summary.attended_sessions : 0;
  const currentPct = summary ? summary.overall_percentage : 100;

  // Needed sessions to reach >= 75%:
  // (attended + N) / (total + N) >= 0.75  =>  N >= 3 * total - 4 * attended
  const neededClasses = Math.max(0, Math.ceil(3 * total - 4 * attended));

  // Classes student can safely miss without dropping below 75%:
  // (attended) / (total + M) >= 0.75  =>  M <= (attended / 0.75) - total
  const skippableClasses = Math.max(0, Math.floor((attended / 0.75) - total));

  // Projected percentage with projectedMisses
  const projectedTotal = total + parseInt(projectedMisses || 0);
  const projectedPct = projectedTotal > 0 ? ((attended / projectedTotal) * 100).toFixed(2) : 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Overview View */}
      {activeTab === 'overview' && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>
                Good morning, {user.full_name ? user.full_name.split(' ')[0] : user.username} 👋
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginTop: '0.2rem' }}>
                Here's your attendance overview for today at JSPM's Bhivrabai Sawant Polytechnic.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => setShowIdCard(true)}
                className="btn-secondary"
                style={{ padding: '0.55rem 1rem', fontSize: '0.85rem', gap: '0.5rem', background: 'rgba(37, 99, 235, 0.1)', color: '#3b82f6', border: '1px solid rgba(37, 99, 235, 0.3)' }}
              >
                <IdCard size={17} /> Digital ID Card
              </button>

              <button
                onClick={() => setShowScanner(true)}
                className="btn-primary"
                style={{ padding: '0.55rem 1rem', fontSize: '0.85rem', gap: '0.5rem' }}
              >
                <Camera size={17} /> Scan Camera QR
              </button>

              <button
                onClick={() => setShowCorrectionModal(true)}
                className="btn-secondary"
                style={{ padding: '0.55rem 1rem', fontSize: '0.85rem', gap: '0.5rem' }}
              >
                <FileText size={17} /> Request Correction
              </button>
            </div>
          </div>

          {/* Quick Stats Grid with Attendance Health */}
          {summary && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              {/* Attendance Health Widget */}
              <div className="glass-card" style={{
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '1.25rem',
                border: summary.overall_percentage >= 75 ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(239, 68, 68, 0.4)',
                background: summary.overall_percentage >= 75 ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)'
              }}>
                <div style={{ padding: '1rem', background: summary.overall_percentage >= 75 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', borderRadius: '16px', color: summary.overall_percentage >= 75 ? '#34d399' : '#f87171' }}>
                  <Award size={32} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', fontWeight: 700 }}>
                    Attendance Health
                  </div>
                  <div style={{
                    fontSize: '1.8rem',
                    fontWeight: 900,
                    marginTop: '0.1rem',
                    color: summary.overall_percentage >= 75 ? '#34d399' : '#f87171'
                  }}>
                    {summary.overall_percentage}%
                  </div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: summary.overall_percentage >= 75 ? '#34d399' : '#f87171', marginTop: '0.2rem' }}>
                    {summary.overall_percentage >= 75 ? '● GOOD' : '● AT RISK'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                    {summary.overall_percentage >= 75 ? 'You are currently above the 75% requirement.' : 'You need to attend upcoming classes consistently.'}
                  </div>
                </div>
              </div>

              <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                <div style={{ padding: '1rem', background: 'rgba(99, 102, 241, 0.15)', borderRadius: '16px', color: '#818cf8' }}>
                  <BookOpen size={32} />
                </div>
                <div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Attended / Total Sessions</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.2rem' }}>
                    {summary.attended_sessions} / {summary.total_sessions}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                    Semester V • Computer Engineering
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Smart Risk & Margin Indicator Banner */}
          <div className="glass-card" style={{
            padding: '1.75rem',
            background: currentPct >= 75
              ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.05))'
              : 'linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.05))',
            border: `1px solid ${currentPct >= 75 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
              <div style={{
                padding: '0.75rem',
                borderRadius: '14px',
                background: currentPct >= 75 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: currentPct >= 75 ? '#34d399' : '#f87171',
              }}>
                <Sparkles size={24} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Smart Attendance Risk & Margin Indicator</h3>
                  <button className="btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }} onClick={() => onNavigate('risk-calculator')}>
                    Interactive Calculator <ArrowRight size={14} />
                  </button>
                </div>

                <div style={{ marginTop: '0.6rem', fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {currentPct >= 75 ? (
                    <span>
                      🎉 Safe Status: You have a margin to safely miss up to <strong style={{ color: '#34d399', fontSize: '1.1rem' }}>{skippableClasses}</strong> upcoming class(es) while maintaining &ge;75% attendance.
                    </span>
                  ) : (
                    <span>
                      ⚠️ Attendance Warning: You are currently below 75%. You MUST attend the next <strong style={{ color: '#f87171', fontSize: '1.1rem' }}>{neededClasses}</strong> consecutive class(es) to get back into the safe zone.
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Active Sessions Available Banner */}
          {activeSessions.length > 0 && (
            <div className="glass-card" style={{ padding: '1.5rem', background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <Clock size={24} color="#818cf8" />
                  <div>
                    <div style={{ fontWeight: 800, fontSize: '1.05rem' }}>Active Attendance Session Available</div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      Teacher launched an active session! Click below to enter token and mark present.
                    </div>
                  </div>
                </div>
                <button className="btn-primary" onClick={() => onNavigate('mark-attendance')}>
                  <QrCode size={16} /> Go to Mark Attendance
                </button>
              </div>
            </div>
          )}

          {/* Quick Mark Input Card */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.6rem', background: 'rgba(99, 102, 241, 0.2)', borderRadius: '12px', color: '#818cf8' }}>
                <QrCode size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Quick Mark Attendance</h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Scan teacher's QR code or type token below</p>
              </div>
            </div>

            {markResult && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '1rem',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: 'var(--radius-md)',
                color: '#34d399',
                marginBottom: '1.25rem',
              }}>
                <CheckCircle2 size={24} />
                <div>
                  <div style={{ fontWeight: 700 }}>Attendance Marked Successfully!</div>
                  <div style={{ fontSize: '0.82rem' }}>Status: PRESENT • Recorded via {markResult.source}</div>
                </div>
              </div>
            )}

            {markError && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '1rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 'var(--radius-md)',
                color: '#f87171',
                marginBottom: '1.25rem',
              }}>
                <AlertCircle size={24} />
                <span>{markError}</span>
              </div>
            )}

            <form onSubmit={handleMarkAttendance} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <input
                type="text"
                className="glass-input"
                placeholder="Paste or type session token (e.g. sIKHZrE2xs...)"
                style={{ flex: 1, minWidth: '260px' }}
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
              />
              <button type="submit" className="btn-primary" disabled={markLoading} style={{ minWidth: '160px' }}>
                {markLoading ? 'Validating...' : <><CheckSquare size={18} /> Submit Attendance</>}
              </button>
            </form>
          </div>
        </>
      )}

      {/* Mark Attendance Dedicated View */}
      {activeTab === 'mark-attendance' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Mark Session Attendance</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              Scan QR code or enter session token to mark yourself present for your class.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '2.5rem', maxWidth: '640px', margin: '0 auto', width: '100%' }}>
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
                <QrCode size={32} color="#ffffff" />
              </div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Session Token Submission</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
                Tokens expire automatically based on teacher settings.
              </p>
            </div>

            {/* Validation Pipeline Stepper */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem', padding: '0 1rem', position: 'relative' }}>
              <div style={{ textAlign: 'center', flex: 1 }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: activeStep !== 'IDLE' ? '#34d399' : 'var(--accent-primary)', color: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>1</div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.4rem', color: 'var(--text-secondary)' }}>Enter Token</div>
              </div>
              <div style={{ textAlign: 'center', flex: 1 }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: activeStep === 'VALIDATING' ? '#fbbf24' : activeStep === 'SUCCESS' || activeStep === 'ERROR' ? '#34d399' : 'rgba(255,255,255,0.1)', color: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>2</div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.4rem', color: 'var(--text-secondary)' }}>Validating</div>
              </div>
              <div style={{ textAlign: 'center', flex: 1 }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: activeStep === 'SUCCESS' ? '#34d399' : activeStep === 'ERROR' ? '#ef4444' : 'rgba(255,255,255,0.1)', color: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>3</div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.4rem', color: 'var(--text-secondary)' }}>Marked Present</div>
              </div>
            </div>

            {markResult && (
              <div style={{
                padding: '1.25rem',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '16px',
                color: '#34d399',
                textAlign: 'center',
                marginBottom: '1.5rem',
              }}>
                <CheckCircle2 size={36} style={{ margin: '0 auto 0.5rem auto' }} />
                <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>ATTENDANCE MARKED PRESENT!</div>
                <div style={{ fontSize: '0.85rem', marginTop: '0.2rem' }}>
                  Recorded via {markResult.source} • Marked At: {new Date().toLocaleTimeString()}
                </div>
              </div>
            )}

            {markError && (
              <div style={{
                padding: '1.25rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '16px',
                color: '#f87171',
                textAlign: 'center',
                marginBottom: '1.5rem',
              }}>
                <AlertCircle size={36} style={{ margin: '0 auto 0.5rem auto' }} />
                <div style={{ fontWeight: 800, fontSize: '1.05rem' }}>Validation Failed</div>
                <div style={{ fontSize: '0.85rem', marginTop: '0.2rem' }}>{markError}</div>
              </div>
            )}

            <form onSubmit={handleMarkAttendance} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                  Attendance Session Token
                </label>
                <input
                  type="text"
                  className="glass-input"
                  placeholder="Paste or type session token here..."
                  style={{ height: '48px', fontSize: '1rem', fontFamily: 'monospace' }}
                  value={tokenInput}
                  onChange={(e) => {
                    setTokenInput(e.target.value);
                    if (activeStep !== 'IDLE') setActiveStep('IDLE');
                  }}
                />
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={markLoading}
                style={{ height: '50px', fontSize: '1.05rem' }}
              >
                {markLoading ? 'Validating Token & Division...' : <><CheckSquare size={20} /> Mark Attendance Now</>}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Subject Attendance Breakdown View */}
      {activeTab === 'subject-breakdown' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Subject-wise Attendance Breakdown</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              Detailed subject performance, attended sessions, and individual subject risk status.
            </p>
          </div>

          {loading ? (
            <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading subject breakdown data...
            </div>
          ) : !summary || !summary.subject_breakdown || summary.subject_breakdown.length === 0 ? (
            <div className="glass-card" style={{ padding: '3.5rem 2rem', textAlign: 'center', borderRadius: '20px' }}>
              <div style={{
                width: '64px', height: '64px', borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.25)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 1.25rem auto', color: '#818cf8'
              }}>
                <BookOpen size={30} />
              </div>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem' }}>No Subject Attendance Records Yet</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '500px', margin: '0 auto 1.5rem auto', lineHeight: '1.5' }}>
                Your subject-wise attendance stats will populate here automatically as soon as your teachers create active class sessions and mark your attendance.
              </p>
              <button
                className="btn-primary"
                onClick={() => onNavigate && onNavigate('mark-attendance')}
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', borderRadius: '12px', fontWeight: 700 }}
              >
                <CheckSquare size={18} /> Mark Active Session Attendance
              </button>
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '1.75rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
                {summary.subject_breakdown.map((sub) => {
                  const targetAttendedNeeded = Math.max(0, Math.ceil(0.75 * sub.total_sessions - sub.attended_sessions));
                  return (
                    <div key={sub.subject_id} style={{
                      padding: '1.4rem',
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid var(--border-glass)',
                      borderRadius: '18px',
                      display: 'flex',
                      flexDirection: 'column',
                      justify: 'space-between',
                      gap: '1rem',
                      transition: 'all 0.2s ease',
                    }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.85rem' }}>
                          <div>
                            <div style={{ fontWeight: 800, fontSize: '1.15rem', color: 'var(--text-primary)' }}>{sub.subject_name}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginTop: '0.15rem' }}>{sub.subject_code}</div>
                          </div>
                          <RiskBadge percentage={sub.percentage} />
                        </div>

                        <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                          Attended <strong style={{ color: 'var(--text-primary)', fontWeight: 700 }}>{sub.attended_sessions}</strong> of {sub.total_sessions} sessions ({sub.percentage}%)
                        </div>

                        {/* Progress Bar */}
                        <div style={{ width: '100%', height: '9px', background: 'rgba(255,255,255,0.08)', borderRadius: '6px', overflow: 'hidden' }}>
                          <div style={{
                            width: `${Math.min(sub.percentage, 100)}%`,
                            height: '100%',
                            background: sub.percentage >= 75 ? 'linear-gradient(90deg, #10b981, #34d399)' : 'linear-gradient(90deg, #ef4444, #f87171)',
                            borderRadius: '6px',
                            transition: 'width 0.6s ease',
                          }} />
                        </div>
                      </div>

                      {/* Footer Insight */}
                      <div style={{
                        paddingTop: '0.75rem',
                        borderTop: '1px solid rgba(255,255,255,0.06)',
                        display: 'flex',
                        justify: 'space-between',
                        alignItems: 'center',
                        fontSize: '0.8rem',
                      }}>
                        <span style={{ color: 'var(--text-muted)' }}>Target: 75%</span>
                        {sub.percentage >= 75 ? (
                          <span style={{ color: '#34d399', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            ✓ On Track
                          </span>
                        ) : (
                          <span style={{ color: '#f87171', fontWeight: 700 }}>
                            Attend next {targetAttendedNeeded > 0 ? targetAttendedNeeded : 1} classes
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Smart Margin & Risk Calculator View */}
      {activeTab === 'risk-calculator' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Smart Attendance Risk & Margin Calculator</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              Project future attendance scenarios, calculate safe leave limits, or calculate required attendance.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="glass-card" style={{ padding: '2rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Calculator size={22} color="#818cf8" /> Interactive Scenario Projection
              </h3>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  Select Projected Upcoming Missed Classes: <strong>{projectedMisses}</strong>
                </label>
                <input
                  type="range"
                  min="0"
                  max="15"
                  value={projectedMisses}
                  onChange={(e) => setProjectedMisses(e.target.value)}
                  style={{ width: '100%', accentColor: 'var(--accent-primary)' }}
                />
              </div>

              <div style={{ padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>PROJECTED OVERALL PERCENTAGE</div>
                <div style={{ fontSize: '2.2rem', fontWeight: 800, color: projectedPct >= 75 ? '#34d399' : '#f87171', marginTop: '0.2rem' }}>
                  {projectedPct}%
                </div>
                <div style={{ marginTop: '0.5rem' }}>
                  <RiskBadge percentage={parseFloat(projectedPct)} />
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ padding: '2rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '1.25rem' }}>Target 75% Formula Insights</h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.12)', borderRadius: '14px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                  <div style={{ fontSize: '0.78rem', color: '#34d399', fontWeight: 700 }}>SAFE MARGIN CAPACITY</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', marginTop: '0.2rem' }}>
                    {skippableClasses} Classes
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    Number of upcoming classes you can miss while keeping attendance &ge; 75%.
                  </div>
                </div>

                <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.12)', borderRadius: '14px', border: '1px solid rgba(239, 68, 68, 0.25)' }}>
                  <div style={{ fontSize: '0.78rem', color: '#f87171', fontWeight: 700 }}>RECOVERY REQUIREMENT</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', marginTop: '0.2rem' }}>
                    {neededClasses} Consecutive Classes
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    Consecutive future classes you must attend to achieve 75% threshold if currently below.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timetable View */}
      {activeTab === 'timetable' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Student Class Timetable</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              Your division schedule and lecture time slots.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '1.75rem' }}>
            {timetables.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No timetable assigned for your division.</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.85rem 1rem' }}>Day</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Time Slot</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Subject ID</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Teacher ID</th>
                  </tr>
                </thead>
                <tbody>
                  {timetables.map((t) => (
                    <tr key={t.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '0.85rem 1rem', fontWeight: 700, color: '#818cf8' }}>{t.day_of_week}</td>
                      <td style={{ padding: '0.85rem 1rem' }}>{t.start_time} - {t.end_time}</td>
                      <td style={{ padding: '0.85rem 1rem' }}>Subject #{t.subject_id}</td>
                      <td style={{ padding: '0.85rem 1rem' }}>Faculty #{t.teacher_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* History Log View */}
      {activeTab === 'history' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Attendance History Log</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem' }}>
              Chronological audit log of all sessions marked for your student account.
            </p>
          </div>

          <div className="glass-card" style={{ padding: '1.75rem' }}>
            {historyLogs.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No attendance records marked yet.
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.85rem 1rem' }}>Record ID</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Session Date</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Subject Name</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Source</th>
                    <th style={{ padding: '0.85rem 1rem' }}>Marked At</th>
                  </tr>
                </thead>
                <tbody>
                  {historyLogs.map((log) => (
                    <tr key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>#{log.id}</td>
                      <td style={{ padding: '0.85rem 1rem' }}>{log.session_date}</td>
                      <td style={{ padding: '0.85rem 1rem', fontWeight: 700 }}>
                        {log.subject_name} {log.subject_code ? `(${log.subject_code})` : ''}
                      </td>
                      <td style={{ padding: '0.85rem 1rem' }}>
                        <span className={`badge badge-${log.status.toLowerCase()}`}>{log.status}</span>
                      </td>
                      <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)' }}>{log.source}</td>
                      <td style={{ padding: '0.85rem 1rem', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                        {log.marked_at ? new Date(log.marked_at).toLocaleString() : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Digital Student ID Card Modal */}
      {showIdCard && (
        <div className="modal-overlay" onClick={() => setShowIdCard(false)}>
          <div className="glass-card" onClick={(e) => e.stopPropagation()} style={{ width: '360px', padding: '1.5rem', borderRadius: '20px', background: 'linear-gradient(145deg, #1e1b4b, #0f172a)', border: '2px solid #818cf8', boxShadow: '0 20px 40px rgba(0,0,0,0.6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldCheck size={20} color="#818cf8" />
                <div style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#818cf8' }}>
                  JSPM'S B. S. POLYTECHNIC, PUNE
                </div>
              </div>
              <button onClick={() => setShowIdCard(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}><X size={18} /></button>
            </div>

            <div style={{ textAlign: 'center', margin: '1rem 0' }}>
              <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #10b981)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', border: '3px solid #ffffff', boxShadow: '0 4px 15px rgba(0,0,0,0.3)', marginBottom: '0.75rem' }}>
                <UserCheck size={40} color="#ffffff" />
              </div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>{user.full_name || 'Aarohi Patil'}</h2>
              <div style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 700, marginTop: '0.2rem' }}>ROLL NO: CE23A001</div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.04)', padding: '1rem', borderRadius: '12px', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Branch:</span><span style={{ fontWeight: 700 }}>Computer Engineering</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Year / Class:</span><span style={{ fontWeight: 700 }}>Third Year (TY - Div A)</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Batch:</span><span style={{ fontWeight: 700 }}>Batch A1</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Enrollment No:</span><span style={{ fontWeight: 700 }}>2304891204</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Blood Group:</span><span style={{ fontWeight: 700, color: '#f87171' }}>O+</span></div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#94a3b8' }}>Validity:</span><span style={{ fontWeight: 700, color: '#fbbf24' }}>2024 - 2026</span></div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px dashed rgba(255,255,255,0.15)', paddingTop: '0.75rem', fontSize: '0.7rem', color: '#64748b' }}>
              <div>Campus ID: #JSPM-CE-8902</div>
              <div style={{ fontWeight: 700, color: '#818cf8' }}>VERIFIED STUDENT</div>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Camera QR Scanner Simulator Modal */}
      {showScanner && (
        <div className="modal-overlay" onClick={() => setShowScanner(false)}>
          <div className="glass-card" onClick={(e) => e.stopPropagation()} style={{ width: '400px', padding: '1.75rem', textAlign: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Camera size={20} color="#3b82f6" /> Live Camera QR Scanner
              </h3>
              <button onClick={() => setShowScanner(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={18} /></button>
            </div>

            <div style={{ position: 'relative', width: '240px', height: '240px', margin: '0 auto 1.5rem auto', borderRadius: '16px', background: '#000000', border: '2px solid #3b82f6', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <QrCode size={160} color="rgba(255,255,255,0.15)" />
              <div style={{ position: 'absolute', bottom: '1rem', background: 'rgba(0,0,0,0.7)', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.72rem', color: '#60a5fa' }}>
                Align Classroom QR inside frame
              </div>
            </div>

            <button
              onClick={() => {
                if (activeSessions && activeSessions.length > 0) {
                  setTokenInput(activeSessions[0].session_token);
                  setToast({ message: `QR Code Scanned! Token: ${activeSessions[0].session_token}`, type: 'success' });
                  setShowScanner(false);
                } else {
                  setToast({ message: 'No active classroom QR session right now. Token manual entry available below.', type: 'error' });
                  setShowScanner(false);
                }
              }}
              className="btn-primary"
              style={{ width: '100%', gap: '0.5rem' }}
            >
              <Sparkles size={18} /> Auto-Detect Classroom QR Token
            </button>
          </div>
        </div>
      )}

      {/* Attendance Correction Request Modal */}
      {showCorrectionModal && (
        <div className="modal-overlay" onClick={() => setShowCorrectionModal(false)}>
          <div className="glass-card" onClick={(e) => e.stopPropagation()} style={{ width: '420px', padding: '1.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={20} color="#34d399" /> Submit Attendance Correction
              </h3>
              <button onClick={() => setShowCorrectionModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={18} /></button>
            </div>

            <form onSubmit={(e) => {
              e.preventDefault();
              setToast({ message: `Correction request for ${correctionSubject || 'Subject'} submitted to Faculty & HOD!`, type: 'success' });
              setShowCorrectionModal(false);
              setCorrectionReason('');
            }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Select Subject</label>
                <select
                  className="glass-input"
                  value={correctionSubject}
                  onChange={(e) => setCorrectionSubject(e.target.value)}
                  required
                >
                  <option value="" style={{ background: '#0f172a' }}>-- Select Subject --</option>
                  <option value="Operating Systems" style={{ background: '#0f172a' }}>Operating Systems (OS)</option>
                  <option value="Software Engineering" style={{ background: '#0f172a' }}>Software Engineering (SE)</option>
                  <option value="Database Management Systems" style={{ background: '#0f172a' }}>Database Management Systems (DBMS)</option>
                  <option value="Computer Networks" style={{ background: '#0f172a' }}>Computer Networks (CN)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Reason for Correction</label>
                <textarea
                  className="glass-input"
                  rows={3}
                  placeholder="e.g. Present in class but token expired / Medical leave approved by HOD..."
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn-success" style={{ padding: '0.75rem', gap: '0.5rem', width: '100%', borderRadius: '12px' }}>
                <CheckCircle2 size={18} /> Submit Correction Request
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Floating Notification Toast */}
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '', type: 'success' })} />
    </div>
  );
}
