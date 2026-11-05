import React from 'react';
import {COLORS, RADIUS, TYPE} from '../../../config/design';
import {label as labelFont, sans} from '../styles/fonts';

/** Tag used for wire labels ("VCC → 3V3"), library names and status tags. */
export const Chip: React.FC<{
  label: string;
  color?: string;
  mono?: boolean;
  size?: number;
  glow?: number;
  style?: React.CSSProperties;
}> = ({label, color = COLORS.accent, mono: isMono = false, size = TYPE.label, glow = 0, style}) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 14,
      padding: '12px 20px 12px 14px',
      borderRadius: RADIUS.sm,
      background: COLORS.surface,
      border: `1.5px solid ${glow > 0 ? color : COLORS.strokeStrong}`,
      fontFamily: isMono ? labelFont : sans,
      fontSize: size,
      fontWeight: 600,
      color: COLORS.text,
      whiteSpace: 'nowrap',
      ...style,
    }}
  >
    <span style={{width: 5, height: size * 0.95, borderRadius: 2, background: color, flexShrink: 0}} />
    {label}
  </div>
);
