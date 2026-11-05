import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT, TYPE} from '../../../config/design';
import {COPY, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {Title} from '../components/Title';
import {sans} from '../styles/fonts';
import {enter, rise} from '../styles/motion';

const S = scene('final');

// Title, then the finished circuit (framed by blender/scenes/final_scene.py
// into 480-1070 px), then the call to action.
export const FinalScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Backdrop scene={S} />
      <Title lines={[COPY.final.title]} start={6} size={TYPE.display} />
      <div style={{position: 'absolute', left: LAYOUT.x, width: LAYOUT.width, top: LAYOUT.noteTop, display: 'flex', justifyContent: 'center', ...rise(enter(frame, 40, 24))}}>
        <div style={{fontFamily: sans, fontSize: TYPE.small + 2, fontWeight: 600, color: COLORS.bg, background: COLORS.text, padding: '16px 32px', borderRadius: 999}}>
          {COPY.final.cta}
        </div>
      </div>
    </AbsoluteFill>
  );
};
