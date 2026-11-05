import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, TYPE} from '../../../config/design';
import {sans} from '../styles/fonts';
import {enter, exit} from '../styles/motion';

type Props = {
  title: string;
  subtitle?: string;
  /** Label position: left edge, or right edge when `align` is 'right'. */
  at: [number, number];
  align?: 'left' | 'right';
  start: number;
  end?: number;
};

/** Plain typographic label placed beside the hardware. No leader lines. */
export const ComponentLabel: React.FC<Props> = ({title, subtitle, at, align = 'left', start, end = 1e9}) => {
  const frame = useCurrentFrame();
  const p = enter(frame, start, 20);
  const out = exit(frame, end);
  const [x, y] = at;
  return (
    <div
      style={{
        position: 'absolute',
        left: align === 'left' ? x : undefined,
        right: align === 'right' ? 1080 - x : undefined,
        top: y,
        textAlign: align,
        opacity: p * out,
        transform: `translateY(${(1 - p) * 16}px)`,
        fontFamily: sans,
      }}
    >
      <div style={{fontSize: TYPE.label + 6, fontWeight: 700, color: COLORS.text, letterSpacing: -0.5}}>{title}</div>
      {subtitle ? <div style={{marginTop: 4, fontSize: TYPE.small + 2, fontWeight: 500, color: COLORS.textMuted}}>{subtitle}</div> : null}
    </div>
  );
};
