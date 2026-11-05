import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {easeInOut} from '../styles/motion';

/**
 * Wraps a scene: fades + slightly scales in over `inFrames` and out over
 * `outFrames`. Adjacent scenes overlap by the transition length in Reel.tsx,
 * giving a soft cross-dissolve with a touch of depth, never a hard cut.
 */
export const SceneTransition: React.FC<{
  inFrames: number;
  outFrames: number;
  children: React.ReactNode;
}> = ({inFrames, outFrames, children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opt = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: easeInOut} as const;
  const fadeIn = inFrames > 0 ? interpolate(frame, [0, inFrames], [0, 1], opt) : 1;
  const fadeOut = outFrames > 0 ? interpolate(frame, [durationInFrames - outFrames, durationInFrames], [1, 0], opt) : 1;
  const scaleIn = inFrames > 0 ? interpolate(frame, [0, inFrames], [1.025, 1], opt) : 1;
  return (
    <AbsoluteFill style={{opacity: Math.min(fadeIn, fadeOut), transform: `scale(${scaleIn})`}}>
      {children}
    </AbsoluteFill>
  );
};
