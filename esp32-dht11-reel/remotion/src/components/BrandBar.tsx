import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, LAYOUT, SAFE} from '../../../config/design';
import {SCENES, type SceneId} from '../../../config/episode';
import {label} from '../styles/fonts';

/** The four teaching steps, in order. The hook and outro sit outside them. */
const STEPS: SceneId[] = ['hardware', 'wiring', 'code', 'serial'];
const BAR_H = 4;
const GAP = 8;

/**
 * Wordmark on the left, step counter on the right, and a story-style
 * progress bar beneath: one segment per step, filling as that step plays.
 */
export const BrandBar: React.FC<{brand: string}> = ({brand}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opacity = Math.min(1, frame / 20, (durationInFrames - frame) / 15);
  const steps = STEPS.map((id) => SCENES.find((s) => s.id === id)!);
  const fills = steps.map((s) =>
    interpolate(frame, [s.start, s.start + s.duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
  );
  const current = steps.findIndex((s) => frame >= s.start && frame < s.start + s.duration);
  const width = 1080 - SAFE.side * 2;
  const seg = (width - GAP * (STEPS.length - 1)) / STEPS.length;
  // The bar appears with step 1 and stays to the end.
  const barIn = interpolate(frame, [steps[0].start - 10, steps[0].start + 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <div style={{position: 'absolute', left: SAFE.side, top: LAYOUT.brandTop - 34, width, opacity, fontFamily: label}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 22, fontWeight: 600, letterSpacing: 3}}>
        <span style={{color: COLORS.textMuted}}>{brand}</span>
        <span style={{color: COLORS.textMuted, opacity: current >= 0 ? 1 : 0}}>
          <span style={{color: COLORS.text}}>{String(Math.max(0, current) + 1).padStart(2, '0')}</span>
          {` / ${String(STEPS.length).padStart(2, '0')}`}
        </span>
      </div>
      <div style={{display: 'flex', gap: GAP, marginTop: 14, opacity: barIn}}>
        {fills.map((f, i) => (
          <div key={i} style={{width: seg, height: BAR_H, borderRadius: BAR_H, background: 'rgba(255,255,255,0.14)', overflow: 'hidden'}}>
            <div style={{width: `${f * 100}%`, height: '100%', background: f >= 1 ? COLORS.text : COLORS.accent}} />
          </div>
        ))}
      </div>
    </div>
  );
};
