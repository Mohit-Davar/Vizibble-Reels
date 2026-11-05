import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT, TYPE} from '../../../config/design';
import {COPY, WIRE_COLORS, WIRING, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {Chip} from '../components/Chip';
import {PinCallouts} from '../components/PinCallouts';
import {Title} from '../components/Title';
import {sans} from '../styles/fonts';
import {enter, rise} from '../styles/motion';

const S = scene('wiring');

export const WiringScene: React.FC = () => {
  const frame = useCurrentFrame();
  const complete = WIRING[WIRING.length - 1].drawEnd;

  return (
    <AbsoluteFill>
      <Backdrop scene={S} />
      <Title kicker={COPY.wiring.kicker} lines={[COPY.wiring.title]} start={4} end={S.duration} size={TYPE.title - 8} />
      <PinCallouts />

      {/* One row of chips names each connection as its wire lands in 3D. */}
        <div
          style={{
            position: 'absolute',
            left: LAYOUT.x,
            width: LAYOUT.width,
            top: LAYOUT.labelTop,
            display: 'flex',
            justifyContent: 'center',
            gap: 18,
          }}
        >
          {WIRING.map((w) => {
            const p = enter(frame, w.drawStart, 16);
            const glow = frame >= w.drawEnd ? Math.max(0.35, 1 - (frame - w.drawEnd) / 25) : 0;
            return (
              <div key={w.id} style={rise(p, 18)}>
                <Chip label={w.label} color={WIRE_COLORS[w.color].ui} mono size={27} glow={glow} />
              </div>
            );
          })}
        </div>

      <div
        style={{
          position: 'absolute',
          left: LAYOUT.x,
          width: LAYOUT.width,
          top: LAYOUT.noteTop,
          textAlign: 'center',
          ...rise(enter(frame, complete + 8, 18), 12),
          fontFamily: sans,
          fontSize: TYPE.small,
          fontWeight: 500,
          color: COLORS.textMuted,
        }}
      >
        <span style={{color: COLORS.success, fontWeight: 700}}>All wired.</span> {COPY.wiring.note}
      </div>
    </AbsoluteFill>
  );
};
