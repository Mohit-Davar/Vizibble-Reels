import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {COLORS} from '../../../config/design';
import type {Scene} from '../../../config/episode';
import {RENDERED} from '../generated/scenes';

/**
 * Pure black stage. For 3D scenes, plays the Blender PNG sequence from
 * public/scenes/<folder>/NNNN.png (rendered on black, so no seams).
 */
export const Backdrop: React.FC<{scene?: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const count = scene?.blender ? RENDERED[scene.folder] ?? 0 : 0;
  const name = scene ? `scenes/${scene.folder}/${String(Math.min(frame, count - 1) + 1).padStart(4, '0')}.png` : '';
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      {count > 0 ? <Img src={staticFile(name)} style={{width: '100%', height: '100%'}} /> : null}
    </AbsoluteFill>
  );
};
