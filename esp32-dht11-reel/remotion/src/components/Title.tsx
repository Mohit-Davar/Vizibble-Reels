import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT, SAFE, TYPE} from '../../../config/design';
import {label, sans} from '../styles/fonts';
import {enter, exit, rise} from '../styles/motion';

type Props = {
  kicker?: string;
  lines: string[];
  start?: number;
  end?: number;
  top?: number;
  size?: number;
};

/**
 * Left-aligned editorial headline. The kicker is a mono tag with an accent
 * mark; each headline line rises out of its own mask, staggered.
 */
export const Title: React.FC<Props> = ({kicker, lines, start = 0, end = 1e9, top = LAYOUT.titleTop, size = TYPE.title}) => {
  const frame = useCurrentFrame();
  const mark = enter(frame, start, 16);
  return (
    <div style={{position: 'absolute', top, left: SAFE.side, right: SAFE.side, fontFamily: sans, opacity: exit(frame, end)}}>
      {kicker ? (
        <div
          style={{
            ...rise(enter(frame, start + 2, 22), 10),
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            marginBottom: 22,
            fontFamily: label,
            fontSize: TYPE.small,
            fontWeight: 600,
            letterSpacing: 2,
            textTransform: 'uppercase',
            color: COLORS.textMuted,
          }}
        >
          <span style={{width: 12, height: 12, background: COLORS.accent, transform: `scale(${mark})`}} />
          {kicker}
        </div>
      ) : null}
      {lines.map((line, i) => (
        <div key={i} style={{overflow: 'hidden', paddingBottom: size * 0.08}}>
          <div
            style={{
              ...rise(enter(frame, start + 6 + i * 6, 30), size * 0.9),
              color: COLORS.text,
              fontSize: size,
              fontWeight: 700,
              letterSpacing: size * -0.045,
              lineHeight: 1.06,
            }}
          >
            {line}
          </div>
        </div>
      ))}
    </div>
  );
};
