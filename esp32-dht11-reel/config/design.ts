// Design system shared by every scene. Change brand here, not in components.

// Palette: pure black stage, near-black cards, white type and one signature
// violet accent, chosen so it can never be mistaken for a wire colour
// (red / yellow / black). No gradients, glows or neon.
export const COLORS = {
  bg: '#000000',
  surface: '#111113',
  surface2: '#1C1C1F',
  stroke: 'rgba(255,255,255,0.08)',
  strokeStrong: 'rgba(255,255,255,0.16)',
  text: '#FAFAFA',
  textMuted: '#A1A1AA',
  textDim: '#52525B',
  accent: '#8B7CFF',
  success: '#30D158',
  warm: '#FF9F0A',
  syntax: {
    keyword: '#FF7AB2',
    type: '#6BDFFF',
    preproc: '#FFA14F',
    string: '#FF8170',
    number: '#D9C97C',
    func: '#F5F5F7',
    comment: '#7F8C98',
    plain: '#F5F5F7',
  },
} as const;

export const FONTS = {
  // Loaded in remotion/src/styles/fonts.ts
  sans: 'Inter',
  mono: 'JetBrains Mono',
};

/** Type scale in px at 1080 wide. Nothing below 26px reaches the screen. */
export const TYPE = {
  display: 92,
  title: 76,
  kicker: 32,
  body: 40,
  label: 34,
  caption: 40,
  code: 30,
  small: 26,
};

/**
 * Instagram Reels safe zones (px at 1080x1920). The top ~14% holds the
 * header, the bottom ~25-35% the caption/username/audio row, and the right
 * edge of the lower half the like/comment/share rail. Important content stays
 * inside; the captions sit just above the bottom overlay.
 */
export const SAFE = {top: 250, bottom: 480, side: 90, right: 130};

/**
 * One vertical grid for every scene, so text and hardware never collide:
 *   brand bar → title → content band (hardware / cards / code) → captions.
 */
export const LAYOUT = {
  brandTop: 236,
  titleTop: 300,
  contentTop: 560,
  /** Nothing but captions below this line: keeps >= 130px of air above them. */
  contentBottom: 1180,
  /** Row under the 3D hardware (wire chips, part names). Blender bands end at 1000. */
  labelTop: 1060,
  /** Secondary line under the labels (notes, call to action). */
  noteTop: 1150,
  captionBottom: 480, // distance from the bottom edge
  width: 900, // content column, centred: x 90..990
  x: 90,
};

export const RADIUS = {sm: 10, md: 18, lg: 28};

/** Animation durations in frames @30fps. */
export const MOTION = {
  enter: 26,
  exit: 14,
  stagger: 4,
  // Cubic-bezier control points for Easing.bezier
  easeOut: [0.16, 1, 0.3, 1] as const,
  easeInOut: [0.65, 0, 0.35, 1] as const,
};
