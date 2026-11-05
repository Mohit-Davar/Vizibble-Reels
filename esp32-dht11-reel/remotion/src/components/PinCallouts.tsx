import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT, TYPE} from '../../../config/design';
import {WIRE_COLORS, WIRING} from '../../../config/episode';
import anchors from '../generated/wiring-anchors.json';
import {label as labelFont} from '../styles/fonts';
import {enter, exit} from '../styles/motion';

/**
 * Pin callouts for the wiring scene: a ring on the real pin and a small tag
 * naming it, drawn from the per-frame pin positions Blender exports
 * (blender/scenes/wiring.py -> generated/wiring-anchors.json). One connection
 * at a time: the sensor pin first, then the board pin it goes to, a flash when
 * the wire seats, then both fade and the chip row keeps the summary.
 */
const RING = 13;
const TAG_DX = 104; // sensor tags sit left of the pin, board tags right
const TAG_DY = 52;
const TAG_FONT = TYPE.small;

const NAMES: string[] = anchors.names;
const FRAMES: number[][] = anchors.frames;

const at = (locator: string, frame: number) => {
  const i = NAMES.indexOf(locator);
  if (i < 0) throw new Error(`No anchor for ${locator}; re-run blender/scenes/wiring.py`);
  const row = (f: number) => FRAMES[Math.max(0, Math.min(FRAMES.length - 1, f))];
  const r = row(frame);
  // Smooth the ray-cast visibility over +-3 frames so occlusion fades, not pops.
  let seen = 0;
  for (let d = -3; d <= 3; d++) seen += row(frame + d)[i * 3 + 2];
  return {x: r[i * 3], y: r[i * 3 + 1], visible: seen / 7};
};

const Callout: React.FC<{
  locator: string;
  label: string;
  color: string;
  side: -1 | 1;
  presence: number;
  flash: number;
}> = ({locator, label, color, side, presence, flash}) => {
  const frame = useCurrentFrame();
  const p = at(locator, frame);
  const opacity = presence * p.visible;
  if (opacity <= 0.01) return null;
  const tagW = label.length * TAG_FONT * 0.6 + 40;
  const tagH = TAG_FONT + 24;
  const half = tagW / 2;
  const cx = Math.max(LAYOUT.x + half, Math.min(LAYOUT.x + LAYOUT.width - half, p.x + side * TAG_DX));
  const cy = p.y + TAG_DY;
  // Leader runs from the ring edge to the near side of the tag.
  const ang = Math.atan2(cy - p.y, cx - side * half - p.x);
  const x0 = p.x + Math.cos(ang) * (RING + 2);
  const y0 = p.y + Math.sin(ang) * (RING + 2);
  const draw = Math.min(1, presence * 1.4);
  return (
    <>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, opacity}}>
        <circle cx={p.x} cy={p.y} r={RING} fill="none" stroke={color} strokeWidth={3} />
        {flash > 0 ? (
          <circle cx={p.x} cy={p.y} r={RING * (1 + flash * 1.3)} fill="none" stroke={color} strokeWidth={3} opacity={1 - flash} />
        ) : null}
        <line
          x1={x0}
          y1={y0}
          x2={x0 + (cx - side * half - x0) * draw}
          y2={y0 + (cy - y0) * draw}
          stroke={color}
          strokeWidth={2}
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          left: cx - half,
          top: cy - tagH / 2,
          width: tagW,
          height: tagH,
          opacity,
          transform: `scale(${0.9 + 0.1 * presence})`,
          borderRadius: 8,
          background: COLORS.surface,
          border: `2px solid ${color}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: labelFont,
          fontSize: TAG_FONT,
          fontWeight: 700,
          color: COLORS.text,
        }}
      >
        {label}
      </div>
    </>
  );
};

export const PinCallouts: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {WIRING.map((w) => {
        const color = WIRE_COLORS[w.color].ui;
        const out = exit(frame, w.drawEnd + 30, 12);
        const sensor = Math.min(enter(frame, w.drawStart - 14, 12), out);
        const board = Math.min(enter(frame, w.drawStart + 4, 12), out);
        // One ring pulse at each end as the wire seats.
        const flash = frame >= w.drawEnd && frame < w.drawEnd + 18 ? (frame - w.drawEnd) / 18 : 0;
        return (
          <React.Fragment key={w.id}>
            <Callout locator={w.from.locator} label={w.from.pin} color={color} side={-1} presence={sensor} flash={flash} />
            <Callout locator={w.to.locator} label={w.to.pin} color={color} side={1} presence={board} flash={flash} />
          </React.Fragment>
        );
      })}
    </>
  );
};
