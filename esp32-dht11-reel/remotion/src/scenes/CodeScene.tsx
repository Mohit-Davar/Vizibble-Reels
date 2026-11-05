import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT, RADIUS, TYPE} from '../../../config/design';
import {CODE_SEGMENTS, COPY, LIBRARIES, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {CodeEditor} from '../components/CodeEditor';
import {Title} from '../components/Title';
import {sans} from '../styles/fonts';
import {enter, exit, rise} from '../styles/motion';

const S = scene('code');

// One idea at a time: the library card owns the content band first, then
// each code segment replaces the previous one in the same place.
export const CodeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const libraryEnd = CODE_SEGMENTS[0].at;
  return (
    <AbsoluteFill>
      <Backdrop />
      <Title kicker={COPY.code.kicker} lines={[COPY.code.title]} start={4} end={S.duration} size={TYPE.title - 8} />
      <LibraryCard start={10} end={libraryEnd} />

      {CODE_SEGMENTS.map((seg, i) => {
        const next = CODE_SEGMENTS[i + 1]?.at ?? S.duration + 20;
        const p = Math.min(enter(frame, seg.at + 4, 16), exit(frame, next + 4, 10));
        if (p <= 0) return null;
        return (
          <div key={seg.id} style={{position: 'absolute', left: LAYOUT.x, top: LAYOUT.contentTop, ...rise(p)}}>
            <div style={{marginBottom: 20, fontFamily: sans, fontSize: TYPE.small + 4, fontWeight: 600, color: COLORS.textMuted}}>{seg.heading}</div>
            <CodeEditor filename="dht11_esp32s3.ino" segment={seg} start={seg.at + 14} width={LAYOUT.width} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Names the exact libraries to install. Text only, not a fake screenshot. */
const LibraryCard: React.FC<{start: number; end: number}> = ({start, end}) => {
  const frame = useCurrentFrame();
  const p = Math.min(enter(frame, start, 18), exit(frame, end + 4, 10));
  const dep = enter(frame, start + 24, 16);
  if (p <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: LAYOUT.x,
        width: LAYOUT.width,
        top: LAYOUT.contentTop + 130,
        ...rise(p),
        padding: '44px 48px',
        borderRadius: RADIUS.lg,
        background: COLORS.surface,
        border: `1px solid ${COLORS.stroke}`,
        fontFamily: sans,
      }}
    >
      <div style={{fontSize: TYPE.small, fontWeight: 600, letterSpacing: 2, color: COLORS.textMuted}}>ARDUINO IDE → LIBRARY MANAGER</div>
      <div style={{marginTop: 18, fontSize: TYPE.title - 24, fontWeight: 700, lineHeight: 1.15, color: COLORS.text}}>{LIBRARIES.main}</div>
      <div style={{marginTop: 28, paddingTop: 28, borderTop: `1px solid ${COLORS.stroke}`, fontSize: TYPE.small + 4, lineHeight: 1.45, color: COLORS.textMuted, opacity: dep}}>
        It also asks for <span style={{color: COLORS.text, fontWeight: 600}}>{LIBRARIES.dependency}</span>. Click Install All.
      </div>
    </div>
  );
};
