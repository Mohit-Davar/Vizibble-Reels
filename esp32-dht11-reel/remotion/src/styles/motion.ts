import {Easing, interpolate} from 'remotion';
import {MOTION} from '../../../config/design';

export const easeOut = Easing.bezier(...MOTION.easeOut);
export const easeInOut = Easing.bezier(...MOTION.easeInOut);

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** 0 -> 1 over [start, start + duration] with ease-out. */
export const enter = (frame: number, start: number, duration: number = MOTION.enter) =>
  interpolate(frame, [start, start + duration], [0, 1], {...clamp, easing: easeOut});

/** 1 -> 0 over [end - duration, end] with ease-in-out. */
export const exit = (frame: number, end: number, duration: number = MOTION.exit) =>
  interpolate(frame, [end - duration, end], [1, 0], {...clamp, easing: easeInOut});

/** Visibility for an element that enters at `start` and leaves at `end`. */
export const presence = (frame: number, start: number, end: number, inDur?: number, outDur?: number) =>
  Math.min(enter(frame, start, inDur), exit(frame, end, outDur));

export const lerp = (frame: number, range: [number, number], out: [number, number], ease = easeInOut) =>
  interpolate(frame, range, out, {...clamp, easing: ease});

/** Standard "rise and fade" for UI entering. Deliberately no blur. */
export const rise = (p: number, distance = 20) => ({
  opacity: p,
  transform: `translateY(${(1 - p) * distance}px)`,
});
