import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function RiskBadge({ percentage, showText = true, size = 'md' }) {
  let tier = 'SAFE';
  let color = '#34d399';
  let bg = 'rgba(16, 185, 129, 0.15)';
  let border = 'rgba(16, 185, 129, 0.3)';
  let icon = ShieldCheck;
  let label = 'SAFE';

  if (percentage < 60) {
    tier = 'CRITICAL';
    color = '#f87171';
    bg = 'rgba(239, 68, 68, 0.15)';
    border = 'rgba(239, 68, 68, 0.3)';
    icon = ShieldAlert;
    label = 'CRITICAL DEFAULTER';
  } else if (percentage < 75) {
    tier = 'AT_RISK';
    color = '#fbbf24';
    bg = 'rgba(245, 158, 11, 0.15)';
    border = 'rgba(245, 158, 11, 0.3)';
    icon = AlertTriangle;
    label = 'AT RISK (<75%)';
  }

  const IconComp = icon;
  const iconSize = size === 'sm' ? 12 : size === 'lg' ? 18 : 14;
  const fontSize = size === 'sm' ? '0.7rem' : size === 'lg' ? '0.9rem' : '0.78rem';
  const padding = size === 'sm' ? '0.15rem 0.45rem' : size === 'lg' ? '0.45rem 0.9rem' : '0.25rem 0.65rem';

  return (
    <span
      className="badge"
      style={{
        background: bg,
        color: color,
        border: `1px solid ${border}`,
        fontSize: fontSize,
        padding: padding,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        borderRadius: '9999px',
        fontWeight: 700,
      }}
    >
      <IconComp size={iconSize} color={color} />
      {showText && <span>{label}</span>}
    </span>
  );
}
