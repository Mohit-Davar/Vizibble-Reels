import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, RADIUS, TYPE} from '../../../config/design';
import {mono, sans} from '../styles/fonts';
import {enter} from '../styles/motion';

type Props = {
  lines: string[];
  /** Local frame first line prints. */
  start: number;
  interval: number;
  baud: number;
  illustrative: boolean;
  width?: number;
};

/** Serial console that prints one line every `interval` frames. */
export const SerialMonitor: React.FC<Props> = ({lines, start, interval, baud, illustrative, width = 900}) => {
  const frame = useCurrentFrame();
  const printed = lines.filter((_, i) => frame >= start + i * interval);
  return (
    <div
      style={{
        width,
        borderRadius: RADIUS.lg,
        background: COLORS.surface,
        border: `1px solid ${COLORS.stroke}`,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '22px 34px',
          borderBottom: `1px solid ${COLORS.stroke}`,
          fontFamily: sans,
          fontSize: TYPE.small,
          color: COLORS.textMuted,
        }}
      >
        <span style={{color: COLORS.text, fontWeight: 600}}>Serial Monitor</span>
        <span style={{fontFamily: mono}}>{baud} baud</span>
      </div>
      <div style={{padding: '26px 34px 30px', minHeight: lines.length * 46 + 10}}>
        {printed.map((l, i) => {
          const p = enter(frame, start + i * interval, 8);
          const latest = i === printed.length - 1;
          return (
            <div
              key={i}
              style={{
                fontFamily: mono,
                fontSize: 29,
                lineHeight: '46px',
                whiteSpace: 'pre',
                color: latest ? COLORS.text : COLORS.textMuted,
                opacity: p,
                transform: `translateY(${(1 - p) * 10}px)`,
              }}
            >
              {l}
            </div>
          );
        })}
      </div>
      {illustrative ? (
        <div
          style={{
            padding: '12px 26px',
            borderTop: `1px solid ${COLORS.stroke}`,
            fontFamily: sans,
            fontSize: TYPE.small,
            fontWeight: 600,
            letterSpacing: 2,
            color: COLORS.textMuted,
            textTransform: 'uppercase',
          }}
        >
          Illustrative output
        </div>
      ) : null}
    </div>
  );
};
