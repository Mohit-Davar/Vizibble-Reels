import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS, LAYOUT, TYPE} from '../../../config/design';
import {COPY, SERIAL, formatSerialLine, scene} from '../../../config/episode';
import {Backdrop} from '../components/Backdrop';
import {MeasureCard} from '../components/MeasureCard';
import {SerialMonitor} from '../components/SerialMonitor';
import {Title} from '../components/Title';

const S = scene('serial');
const CARD_W = (LAYOUT.width - 30) / 2;
const PRINT_START = 24;
// Cards wait until the monitor has printed its last line.
const CARDS_AT = PRINT_START + (SERIAL.readings.length - 1) * SERIAL.lineInterval + 14;

export const SerialScene: React.FC = () => {
  const r = SERIAL.readings[0];
  return (
    <AbsoluteFill>
      <Backdrop />
      <Title kicker={COPY.serial.kicker} lines={[COPY.serial.title]} start={4} end={S.duration} size={TYPE.title - 8} />
      <div style={{position: 'absolute', left: LAYOUT.x, top: LAYOUT.contentTop - 70}}>
        <SerialMonitor
          lines={SERIAL.readings.map(formatSerialLine)}
          start={PRINT_START}
          interval={SERIAL.lineInterval}
          baud={SERIAL.baud}
          illustrative={SERIAL.illustrative}
          width={LAYOUT.width}
        />
      </div>
      <div style={{position: 'absolute', left: LAYOUT.x, width: LAYOUT.width, top: LAYOUT.contentBottom - 230, display: 'flex', justifyContent: 'space-between'}}>
        <MeasureCard label="Temperature" value={r.t} unit="°C" accent={COLORS.warm} start={CARDS_AT} width={CARD_W} />
        <MeasureCard label="Humidity" value={r.h} unit="%" accent={COLORS.accent} start={CARDS_AT + 8} width={CARD_W} />
      </div>
    </AbsoluteFill>
  );
};
