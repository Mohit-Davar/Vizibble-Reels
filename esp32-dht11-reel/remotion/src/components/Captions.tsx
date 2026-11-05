import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, LAYOUT, TYPE} from '../../../config/design';
import {NARRATION} from '../../../config/narration';
import {sans} from '../styles/fonts';
import {enter} from '../styles/motion';

/** Lines closer than this (seconds) share one caption box with no fade between. */
const JOIN_GAP = 0.6;
const FADE = 5; // frames

const CAPTIONED = NARRATION.filter((l) => l.caption !== false);

/** Consecutive narration lines grouped into runs that keep the box on screen. */
const RUNS = CAPTIONED.reduce<{start: number; end: number}[]>((runs, l) => {
  const last = runs[runs.length - 1];
  if (last && l.start - last.end <= JOIN_GAP) last.end = l.end;
  else runs.push({start: l.start, end: l.end});
  return runs;
}, []);

/**
 * Modern fast-paced Reel captions:
 * - Wide 920px horizontal width with clean margins
 * - Only 2-4 words shown at a time
 * - Words pop in dynamically only as the AI speaks them (never shown beforehand)
 * - Spoken active word highlighted in electric gold (#FFD13B)
 */
export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const run = RUNS.find((r) => t >= r.start - FADE / fps && t < r.end + FADE / fps);
  if (!run) return null;

  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const box = interpolate(frame, [run.start * fps - FADE, run.start * fps, run.end * fps, run.end * fps + FADE], [0, 1, 1, 0], clamp);
  const lines = CAPTIONED.filter((l) => l.start >= run.start - 1e-6 && l.end <= run.end + 1e-6);

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: LAYOUT.captionBottom,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        pointerEvents: 'none',
        opacity: box,
        zIndex: 50,
      }}
    >
      <div
        style={{
          position: 'relative',
          width: 920,
          maxWidth: 920,
          minHeight: 88,
          padding: '16px 40px',
          borderRadius: 24,
          background: 'rgba(12, 12, 15, 0.84)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          boxShadow: '0 12px 36px rgba(0, 0, 0, 0.65), 0 2px 8px rgba(0, 0, 0, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {lines.map((l, i) => {
          // Each line holds until the next one starts, then crossfades.
          const next = lines[i + 1];
          const s = l.start * fps;
          const e = Math.max(s + 6, (next ? next.start : l.end) * fps);
          const o = interpolate(frame, [s, s + 2, e - 2, e], [0, 1, 1, next ? 0 : 1], clamp);
          if (o <= 0) return null;

          const words = l.words ? l.words.map((w) => w.word) : l.text.split(' ');
          const total = l.text.length;
          const span = (l.end - l.start) * fps;
          let chars = 0;
          const starts = l.words
            ? l.words.map((w) => w.start * fps)
            : words.map((w) => {
                const at = s + (chars / total) * span;
                chars += w.length + 1;
                return at;
              });

          // Do not show the line container before speech begins
          if (frame < starts[0]) return null;

          return (
            <div
              key={i}
              style={{
                position: lines.length > 1 ? 'absolute' : 'relative',
                inset: lines.length > 1 ? 0 : undefined,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                fontFamily: sans,
                fontSize: TYPE.caption + 4,
                fontWeight: 800,
                letterSpacing: -0.3,
                wordSpacing: 6,
                lineHeight: 1.3,
                color: COLORS.text,
                opacity: o,
                whiteSpace: 'nowrap',
                textShadow: '0 2px 6px rgba(0, 0, 0, 0.8)',
              }}
            >
              <div>
                {words.map((w, k) => {
                  const said = frame >= starts[k];
                  // ONLY show words as the AI speaks them (never show upcoming words)
                  if (!said) return null;

                  const p = enter(frame, starts[k], 4);
                  const wordEnd = l.words ? l.words[k].end * fps : (k === words.length - 1 ? l.end * fps : starts[k + 1]);
                  const active = frame < wordEnd;
                  const scale = interpolate(p, [0, 0.5, 1], [0.8, 1.15, 1]);

                  return (
                    <React.Fragment key={k}>
                      <span
                        style={{
                          display: 'inline-block',
                          transform: `scale(${scale})`,
                          transformOrigin: 'center bottom',
                          color: active ? '#FFD13B' : COLORS.text,
                          textShadow: active
                            ? '0 0 18px rgba(255, 209, 59, 0.6), 0 2px 6px rgba(0, 0, 0, 0.95)'
                            : '0 2px 6px rgba(0, 0, 0, 0.8)',
                          transition: 'color 0.1s ease',
                        }}
                      >
                        {w}
                      </span>
                      {k < words.length - 1 ? ' ' : null}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
