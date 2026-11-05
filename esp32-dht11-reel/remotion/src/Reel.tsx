import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {AUDIO_FILES} from './generated/scenes';
import {COLORS} from '../../config/design';
import {AUDIO, COPY, SCENES, SFX, TRANSITION, type SceneId} from '../../config/episode';
import {NARRATION} from '../../config/narration';
import {BrandBar} from './components/BrandBar';
import {Captions} from './components/Captions';
import {SceneTransition} from './components/Transition';
import {CodeScene} from './scenes/CodeScene';
import {FinalScene} from './scenes/FinalScene';
import {HardwareScene} from './scenes/HardwareScene';
import {HookScene} from './scenes/HookScene';
import {SerialScene} from './scenes/SerialScene';
import {WiringScene} from './scenes/WiringScene';

const SCENE_COMPONENTS: Record<SceneId, React.FC> = {
  hook: HookScene,
  hardware: HardwareScene,
  wiring: WiringScene,
  code: CodeScene,
  serial: SerialScene,
  final: FinalScene,
};

const hasFile = (name: string) => AUDIO_FILES.includes(name);

export const Reel: React.FC = () => {
  const fps = 30;
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      {SCENES.map((s, i) => {
        const Comp = SCENE_COMPONENTS[s.id];
        const last = i === SCENES.length - 1;
        // Each scene runs TRANSITION frames past its slot so the next scene
        // dissolves over it instead of cutting.
        return (
          <Sequence key={s.id} name={s.id} from={s.start} durationInFrames={s.duration + (last ? 0 : TRANSITION)}>
            <SceneTransition inFrames={i === 0 ? 0 : TRANSITION} outFrames={last ? 15 : TRANSITION}>
              <Comp />
            </SceneTransition>
          </Sequence>
        );
      })}

      <BrandBar brand={COPY.brand} />
      <Captions />

      {/* Audio */}
      {hasFile(AUDIO.narration) ? <Audio src={staticFile(AUDIO.narration)} volume={1.4} /> : null}
      {hasFile(AUDIO.music) ? (
        <Audio
          src={staticFile(AUDIO.music)}
          volume={(f) => {
            const t = f / fps;
            const speaking = NARRATION.some((l) => t >= l.start - 0.2 && t <= l.end + 0.2);
            return speaking ? AUDIO.musicDucked : AUDIO.musicVolume;
          }}
        />
      ) : null}
      {SFX.filter((s) => hasFile(s.file)).map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={90} name={`sfx ${s.file}`}>
          <Audio src={staticFile(s.file)} volume={s.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
