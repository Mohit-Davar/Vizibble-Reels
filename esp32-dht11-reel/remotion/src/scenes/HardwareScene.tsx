import React from 'react';
import {AbsoluteFill} from 'remotion';
import {LAYOUT} from '../../../config/design';
import {COPY, HARDWARE, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {ComponentLabel} from '../components/ComponentLabel';
import {Title} from '../components/Title';

const S = scene('hardware');

// Hardware is framed into the band above; both labels share one row beneath
// it, each on its own part's side (sensor left, board right).
export const HardwareScene: React.FC = () => (
  <AbsoluteFill>
    <Backdrop scene={S} />
    <Title kicker={COPY.hardware.kicker} lines={[COPY.hardware.title]} start={4} end={S.duration} />
    <ComponentLabel title={HARDWARE.board.name} subtitle="Development Board" at={[LAYOUT.x + LAYOUT.width, LAYOUT.labelTop]} align="right" start={30} end={S.duration} />
    <ComponentLabel title={`${HARDWARE.sensor.name} Sensor`} subtitle="Temperature & Humidity" at={[LAYOUT.x, LAYOUT.labelTop]} start={62} end={S.duration} />
  </AbsoluteFill>
);
