import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, RADIUS, TYPE} from '../../../config/design';
import {sans} from '../styles/fonts';
import {enter, rise} from '../styles/motion';

type Props = {
  label: string;
  value: number;
  unit: string;
  decimals?: number;
  accent: string;
  start: number;
  width: number;
  /** Smaller variant for the closing shot. */
  compact?: boolean;
};

/**
 * Reading card. The value appears as-is (no count-up), so the video never
 * shows intermediate numbers that were never "measured".
 */
export const MeasureCard: React.FC<Props> = ({label, value, unit, decimals = 1, accent, start, width, compact = false}) => {
  const frame = useCurrentFrame();
  const reveal = enter(frame, start + 8, 22);
  const s = compact ? {pad: '22px 28px 24px', num: 72, unit: 34} : {pad: '30px 34px 34px', num: 108, unit: 46};
  return (
    <div
      style={{
        ...rise(enter(frame, start, 20)),
        width,
        padding: s.pad,
        borderRadius: RADIUS.lg,
        background: COLORS.surface,
        border: `1px solid ${COLORS.stroke}`,
        fontFamily: sans,
      }}
    >
      <div style={{fontSize: TYPE.small, fontWeight: 600, color: COLORS.textMuted}}>{label}</div>
      {/* Masked slide-up: the final value rises into place; nothing else is ever shown. */}
      <div style={{marginTop: compact ? 4 : 10, overflow: 'hidden', paddingBottom: 6}}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 8, transform: `translateY(${(1 - reveal) * 105}%)`}}>
          <span style={{fontSize: s.num, fontWeight: 700, color: COLORS.text, letterSpacing: compact ? -2 : -4, fontVariantNumeric: 'tabular-nums'}}>
            {value.toFixed(decimals)}
          </span>
          <span style={{fontSize: s.unit, fontWeight: 600, color: accent}}>{unit}</span>
        </div>
      </div>
    </div>
  );
};
