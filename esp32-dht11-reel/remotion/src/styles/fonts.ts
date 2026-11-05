import {loadFont as loadGeist} from '@remotion/google-fonts/Geist';
import {loadFont as loadGeistMono} from '@remotion/google-fonts/GeistMono';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';

/** Interface type: headlines, captions, cards. */
export const sans = loadGeist('normal', {
  weights: ['400', '500', '600', '700', '800'],
  subsets: ['latin'],
}).fontFamily;

/** Labels, tags, step counters. */
export const label = loadGeistMono('normal', {
  weights: ['500', '600', '700'],
  subsets: ['latin'],
}).fontFamily;

/** Source code only. CodeEditor's token layout relies on its exact 0.6em advance. */
export const mono = loadMono('normal', {
  weights: ['400', '500', '700'],
  subsets: ['latin'],
}).fontFamily;
