import React from 'react';
import {Composition} from 'remotion';
import {VIDEO} from '../../config/episode';
import {Reel} from './Reel';

export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    durationInFrames={VIDEO.durationInFrames}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
