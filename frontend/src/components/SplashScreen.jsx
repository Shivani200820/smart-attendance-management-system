import React, { useState, useEffect } from 'react';
import { UserCheck, Sparkles, GraduationCap, ShieldCheck } from 'lucide-react';

export default function SplashScreen({ onComplete }) {
  const [stage, setStage] = useState(0); // 0: initial, 1: logo, 2: title, 3: tagline, 4: progress, 5: exit

  useEffect(() => {
    // Stage timer sequence
    const t1 = setTimeout(() => setStage(1), 200);   // Logo glow
    const t2 = setTimeout(() => setStage(2), 600);   // College title
    const t3 = setTimeout(() => setStage(3), 1000);  // Tagline
    const t4 = setTimeout(() => setStage(4), 1400);  // Progress loading
    const t5 = setTimeout(() => setStage(5), 2300);  // Exit transition
    const t6 = setTimeout(() => {
      onComplete();
    }, 2700);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(t6);
    };
  }, [onComplete]);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 40%, #1e1b4b 0%, #0f172a 70%, #090d16 100%)',
      color: '#ffffff',
      opacity: stage === 5 ? 0 : 1,
      transition: 'opacity 0.4s ease-out',
      pointerEvents: stage === 5 ? 'none' : 'auto',
      overflow: 'hidden',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Background Decorative Mesh & Glow */}
      <div style={{
        position: 'absolute',
        width: '600px',
        height: '600px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(67, 56, 202, 0.05) 50%, transparent 70%)',
        filter: 'blur(60px)',
        transform: stage >= 1 ? 'scale(1.2)' : 'scale(0.8)',
        transition: 'transform 1.8s ease-out'
      }} />

      <div style={{
        position: 'relative',
        zIndex: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        padding: '2rem',
        maxWidth: '540px'
      }}>
        {/* Animated Glowing Logo */}
        <div style={{
          position: 'relative',
          marginBottom: '1.75rem',
          transform: stage >= 1 ? 'scale(1) translateY(0)' : 'scale(0.7) translateY(20px)',
          opacity: stage >= 1 ? 1 : 0,
          transition: 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.6s ease'
        }}>
          <div style={{
            width: '88px',
            height: '88px',
            borderRadius: '26px',
            background: 'linear-gradient(135deg, #6366f1 0%, #4338ca 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 50px rgba(99, 102, 241, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.4)',
            position: 'relative'
          }}>
            <ShieldCheck size={44} color="#ffffff" strokeWidth={2.2} />
            <div style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: '#10b981',
              borderRadius: '50%',
              padding: '4px',
              boxShadow: '0 0 12px #10b981'
            }}>
              <Sparkles size={14} color="#ffffff" />
            </div>
          </div>
        </div>

        {/* College Name & Location */}
        <div style={{
          transform: stage >= 2 ? 'translateY(0)' : 'translateY(15px)',
          opacity: stage >= 2 ? 1 : 0,
          transition: 'transform 0.5s ease-out, opacity 0.5s ease'
        }}>
          <div style={{
            fontSize: '0.85rem',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#818cf8',
            fontWeight: 700,
            marginBottom: '0.4rem'
          }}>
            Pune, Maharashtra
          </div>
          <h1 style={{
            fontSize: '1.8rem',
            fontWeight: 900,
            letterSpacing: '-0.02em',
            background: 'linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 0.5rem 0',
            lineHeight: 1.25
          }}>
            JSPM's Bhivrabai Sawant Polytechnic
          </h1>
        </div>

        {/* Tagline */}
        <div style={{
          transform: stage >= 3 ? 'translateY(0)' : 'translateY(10px)',
          opacity: stage >= 3 ? 1 : 0,
          transition: 'transform 0.5s ease-out, opacity 0.5s ease',
          marginBottom: '2rem'
        }}>
          <p style={{
            fontSize: '1rem',
            color: '#94a3b8',
            margin: 0,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            justifyContent: 'center'
          }}>
            <GraduationCap size={18} color="#818cf8" />
            <span>Smart Attendance. Smarter Campus.</span>
          </p>
        </div>

        {/* Progress Bar Loader */}
        <div style={{
          width: '180px',
          height: '4px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '4px',
          overflow: 'hidden',
          opacity: stage >= 4 ? 1 : 0,
          transition: 'opacity 0.4s ease',
          position: 'relative'
        }}>
          <div style={{
            width: stage >= 4 ? '100%' : '0%',
            height: '100%',
            background: 'linear-gradient(90deg, #6366f1, #10b981)',
            borderRadius: '4px',
            transition: 'width 0.8s ease-in-out'
          }} />
        </div>

        <div style={{
          marginTop: '0.75rem',
          fontSize: '0.75rem',
          color: '#64748b',
          letterSpacing: '0.05em',
          opacity: stage >= 4 ? 1 : 0,
          transition: 'opacity 0.4s ease'
        }}>
          Loading Campus Portal...
        </div>
      </div>
    </div>
  );
}
