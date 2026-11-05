import React from 'react';
import {AbsoluteFill} from 'remotion';
import {TYPE} from '../../../config/design';
import {COPY, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {Title} from '../components/Title';

const S = scene('hook');

export const HookScene: React.FC = () => (
  <AbsoluteFill>
    <Backdrop scene={S} />
    <Title kicker={COPY.hook.kicker} lines={COPY.hook.title} start={12} end={S.duration} size={TYPE.display - 6} />
  </AbsoluteFill>
);
