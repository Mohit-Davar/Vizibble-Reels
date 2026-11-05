// Synthesizes the episode's subtle sound effects as 48 kHz mono 16-bit WAVs.
// Deterministic (seeded noise), original material, no licensing concerns.
// Usage: node scripts/generate-sfx.mjs   -> remotion/public/sfx/*.wav
import {existsSync, mkdirSync, writeFileSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'remotion', 'public', 'sfx');
const SR = 48000;

let seed = 0x2bd4ff;
const rand = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 0xffffffff;
};

const buf = (sec) => new Float32Array(Math.round(sec * SR));
const env = (t, a, d) => (t < a ? t / a : Math.exp(-(t - a) / d));
const smooth = (x) => x * x * (3 - 2 * x);

/** One-pole low-pass with a per-sample cutoff function (Hz). */
const lowpass = (input, cutoff) => {
  const out = new Float32Array(input.length);
  let y = 0;
  for (let i = 0; i < input.length; i++) {
    const a = 1 - Math.exp((-2 * Math.PI * cutoff(i / SR)) / SR);
    y += a * (input[i] - y);
    out[i] = y;
  }
  return out;
};

const noise = (sec) => buf(sec).map(() => rand() * 2 - 1);

const tone = (sec, freq, attack, decay, amp = 1, partials = [[1, 1]]) => {
  const b = buf(sec);
  for (let i = 0; i < b.length; i++) {
    const t = i / SR;
    let s = 0;
    for (const [mul, g] of partials) s += g * Math.sin(2 * Math.PI * freq * mul * t);
    b[i] = amp * env(t, attack, decay) * s;
  }
  return b;
};

const mix = (...tracks) => {
  const len = Math.max(...tracks.map(([b, off = 0]) => b.length + Math.round(off * SR)));
  const out = new Float32Array(len);
  for (const [b, off = 0, g = 1] of tracks) {
    const o = Math.round(off * SR);
    for (let i = 0; i < b.length; i++) out[i + o] += b[i] * g;
  }
  return out;
};

const fadeTail = (b, sec = 0.02) => {
  const n = Math.round(sec * SR);
  for (let i = 0; i < n; i++) b[b.length - 1 - i] *= i / n;
  return b;
};

const normalize = (b, peakDb = -3) => {
  const peak = b.reduce((m, v) => Math.max(m, Math.abs(v)), 0) || 1;
  const g = Math.pow(10, peakDb / 20) / peak;
  return b.map((v) => v * g);
};

const writeWav = (name, data) => {
  const pcm = Buffer.alloc(data.length * 2);
  data.forEach((v, i) => pcm.writeInt16LE(Math.round(Math.max(-1, Math.min(1, v)) * 32767), i * 2));
  const h = Buffer.alloc(44);
  h.write('RIFF', 0);
  h.writeUInt32LE(36 + pcm.length, 4);
  h.write('WAVEfmt ', 8);
  h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20);
  h.writeUInt16LE(1, 22);
  h.writeUInt32LE(SR, 24);
  h.writeUInt32LE(SR * 2, 28);
  h.writeUInt16LE(2, 32);
  h.writeUInt16LE(16, 34);
  h.write('data', 36);
  h.writeUInt32LE(pcm.length, 40);
  const target = join(OUT, name);
  try {
    writeFileSync(target, Buffer.concat([h, pcm]));
    console.log(`wrote sfx/${name} (${(data.length / SR).toFixed(2)} s)`);
  } catch (err) {
    if (existsSync(target)) {
      console.log(`sfx/${name} already exists, reusing existing file.`);
    } else {
      throw err;
    }
  }
};

mkdirSync(OUT, {recursive: true});

// Light sweep: filtered noise whose cutoff rises then settles.
{
  const d = 1.4;
  const n = lowpass(noise(d), (t) => 300 + 5200 * Math.sin(Math.PI * Math.min(1, t / d)));
  const shaped = n.map((v, i) => v * Math.sin(Math.PI * smooth(i / n.length)));
  writeWav('sweep.wav', normalize(fadeTail(shaped), -6));
}

// Hardware reveal: soft low body + airy shimmer.
{
  const body = tone(1.2, 70, 0.01, 0.28, 1, [[1, 1], [2, 0.3]]);
  const air = lowpass(noise(1.2), () => 2500).map((v, i) => v * env(i / SR, 0.08, 0.35) * 0.5);
  const glint = tone(1.2, 1318.5, 0.005, 0.4, 0.18, [[1, 1], [2, 0.2]]);
  writeWav('reveal.wav', normalize(fadeTail(mix([body], [air], [glint, 0.05])), -5));
}

// Wire connection: tactile click + short tonal blip.
{
  const click = lowpass(noise(0.03), () => 6000).map((v, i) => v * env(i / SR, 0.0005, 0.004));
  const blip = tone(0.35, 1760, 0.002, 0.07, 0.6, [[1, 1], [1.5, 0.25]]);
  writeWav('connect.wav', normalize(fadeTail(mix([click], [blip, 0.008])), -4));
}

// Transition whoosh.
{
  const d = 0.6;
  const n = lowpass(noise(d), (t) => 400 + 3600 * Math.sin(Math.PI * (t / d)));
  writeWav('whoosh.wav', normalize(fadeTail(n.map((v, i) => v * Math.pow(Math.sin(Math.PI * (i / n.length)), 2))), -6));
}

// Successful output: two-note rising chime (E5 -> B5).
{
  const p = [[1, 1], [2, 0.18], [3, 0.06]];
  writeWav('success.wav', normalize(fadeTail(mix([tone(1.4, 659.25, 0.004, 0.45, 1, p)], [tone(1.2, 987.77, 0.004, 0.55, 1, p), 0.12])), -5));
}

// Outro: soft major chord bloom.
{
  const p = [[1, 1], [2, 0.12]];
  writeWav(
    'outro.wav',
    normalize(fadeTail(mix([tone(2, 523.25, 0.05, 0.7, 1, p)], [tone(2, 659.25, 0.05, 0.7, 0.8, p), 0.04], [tone(2, 783.99, 0.05, 0.7, 0.7, p), 0.08])), -6),
  );
}
