// scripts/generate-narration.mjs
// Generates perfectly visual-synchronized narration audio using ElevenLabs with-timestamps API.
// Every code step, wiring cue, and serial print hits its exact visual cue frame-by-frame.
// Initial hook & hardware are relaxed to avoid feeling rushed.

import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CONFIG_PATH = join(ROOT, 'config', 'narration.ts');
const OUT_DIR = join(ROOT, 'remotion', 'public', 'audio');
const OUT_WAV = join(OUT_DIR, 'narration.wav');
const SCENES_TS = join(ROOT, 'remotion', 'src', 'generated', 'scenes.ts');

const SAMPLE_RATE = 48000;
const DURATION_SECONDS = 45.0; // Total Reel length (1350 frames @ 30 fps)

function getEnv(key) {
  if (process.env[key]) return process.env[key];
  for (const envFile of ['.env.local', '.env']) {
    const p = join(ROOT, envFile);
    if (existsSync(p)) {
      const match = readFileSync(p, 'utf8').match(new RegExp(`^${key}=(.*)$`, 'm'));
      if (match) return match[1].trim();
    }
  }
  return null;
}

const args = process.argv.slice(2);
function getArg(flag, fallback) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : fallback;
}

const API_KEY = getArg('--api-key', getEnv('ELEVENLABS_API_KEY'));
const VOICE_ID = getArg('--voice-id', getEnv('ELEVENLABS_VOICE_ID') || 'iP95p4xoKVk53GoZ742B'); // Chris
const MODEL_ID = getArg('--model-id', 'eleven_multilingual_v2');

if (!API_KEY) {
  console.error('Error: ELEVENLABS_API_KEY is missing.');
  process.exit(1);
}

// Exactly aligned cue points:
// Hook: Starts at 0.5s (relaxed, clear hook)
// Hardware: Starts at 4.5s (gives visual time to settle)
// Wiring: Starts at 9.8s (wire animations)
// Code:
//   - Library card: 18.4s
//   - Config card (DHT11 on GPIO 4): 21.8s (exact frame 110 in CodeScene)
//   - Setup card (begin): 25.8s (exact frame 230 in CodeScene)
//   - Read card (temperature in loop): 29.5s (exact frame 340 in CodeScene)
// Serial: 33.3s & 36.5s
// Outro: 40.2s
const CUE_SECTIONS = [
  {
    id: 'hook',
    scene: 'hook',
    start: 0.5,
    text: 'Want to measure temperature and humidity with your ESP32?',
    stability: 0.45,
    style: 0.18,
  },
  {
    id: 'hardware',
    scene: 'hardware',
    start: 4.5,
    text: 'You only need two parts: an ESP32-S3 board, and a DHT11 sensor.',
    stability: 0.42,
    style: 0.20,
  },
  {
    id: 'wiring',
    scene: 'wiring',
    start: 9.8,
    text: 'VCC connects to 3.3 volts. Next, data goes to GPIO 4. And ground goes right to ground.',
    stability: 0.38,
    style: 0.25,
  },
  {
    id: 'code_lib',
    scene: 'code',
    start: 18.4,
    text: 'First, in the Arduino IDE, install the Adafruit DHT library.',
    stability: 0.38,
    style: 0.25,
  },
  {
    id: 'code_config',
    scene: 'code',
    start: 21.8,
    text: 'Define the DHT11 on GPIO 4.',
    stability: 0.38,
    style: 0.25,
  },
  {
    id: 'code_setup',
    scene: 'code',
    start: 25.8,
    text: 'Next, start the sensor inside setup.',
    stability: 0.38,
    style: 0.25,
  },
  {
    id: 'code_read',
    scene: 'code',
    start: 29.5,
    text: 'Then, read temperature and humidity in loop!',
    stability: 0.38,
    style: 0.28,
  },
  {
    id: 'serial_upload',
    scene: 'serial',
    start: 33.3,
    text: 'Upload the code and open the Serial Monitor.',
    stability: 0.38,
    style: 0.25,
  },
  {
    id: 'serial_reading',
    scene: 'serial',
    start: 36.5,
    text: 'You get a fresh reading every two seconds!',
    stability: 0.38,
    style: 0.28,
  },
  {
    id: 'final',
    scene: 'final',
    start: 40.2,
    text: 'Just three wires and simple code. Save this and follow for more!',
    stability: 0.38,
    style: 0.28,
  },
];

function decodeMp3ToPcm(mp3Buffer) {
  return new Promise((resolve, reject) => {
    const ff = spawn('ffmpeg', [
      '-y',
      '-loglevel',
      'error',
      '-i',
      'pipe:0',
      '-f',
      's16le',
      '-ar',
      String(SAMPLE_RATE),
      '-ac',
      '1',
      'pipe:1',
    ]);
    const chunks = [];
    ff.stdout.on('data', (c) => chunks.push(c));
    ff.stderr.on('data', (d) => console.error('FFmpeg stderr:', d.toString()));
    ff.on('close', (code) => {
      if (code === 0) resolve(Buffer.concat(chunks));
      else reject(new Error(`FFmpeg exited with code ${code}`));
    });
    ff.on('error', reject);
    ff.stdin.write(mp3Buffer);
    ff.stdin.end();
  });
}

function extractWords(alignment, blockStart) {
  const chars = alignment.characters;
  const starts = alignment.character_start_times_seconds;
  const ends = alignment.character_end_times_seconds;
  const words = [];
  let currentWord = '';
  let wordStart = null;
  let wordEnd = null;

  for (let i = 0; i < chars.length; i++) {
    const c = chars[i];
    if (c === ' ' || c === '\n' || c === '\t') {
      if (currentWord.length > 0) {
        words.push({
          word: currentWord,
          start: Number((blockStart + wordStart).toFixed(3)),
          end: Number((blockStart + wordEnd).toFixed(3)),
        });
        currentWord = '';
        wordStart = null;
        wordEnd = null;
      }
    } else {
      if (wordStart === null) wordStart = starts[i];
      wordEnd = ends[i];
      currentWord += c;
    }
  }
  if (currentWord.length > 0) {
    words.push({
      word: currentWord,
      start: Number((blockStart + wordStart).toFixed(3)),
      end: Number((blockStart + wordEnd).toFixed(3)),
    });
  }
  return words;
}

// Split into clean 2-3 word caption cards
function chunkWordsIntoCaptions(words, sceneName) {
  const captions = [];
  const CHUNK_SIZE = 3;

  for (let i = 0; i < words.length; i += CHUNK_SIZE) {
    const slice = words.slice(i, i + CHUNK_SIZE);
    const text = slice.map((w) => w.word).join(' ');
    const start = slice[0].start;
    const end = slice[slice.length - 1].end;
    const isOutro = text.toLowerCase().includes('follow for more');

    captions.push({
      scene: sceneName,
      start,
      end,
      text,
      caption: isOutro ? false : undefined,
      words: slice,
    });
  }
  return captions;
}

async function run() {
  mkdirSync(OUT_DIR, { recursive: true });

  const masterBytes = Math.round(DURATION_SECONDS * SAMPLE_RATE) * 2;
  const masterPcm = Buffer.alloc(masterBytes); // silence
  const allCaptions = [];

  console.log(`Generating frame-synced narration across ${CUE_SECTIONS.length} visual cues...`);

  for (let i = 0; i < CUE_SECTIONS.length; i++) {
    const sec = CUE_SECTIONS[i];
    console.log(`[${i + 1}/${CUE_SECTIONS.length}] (${sec.id}) -> "${sec.text}"`);

    const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/with-timestamps`, {
      method: 'POST',
      headers: {
        'xi-api-key': API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: sec.text,
        model_id: MODEL_ID,
        voice_settings: {
          stability: sec.stability,
          similarity_boost: 0.8,
          style: sec.style,
          use_speaker_boost: true,
        },
      }),
    });

    if (!res.ok) {
      console.error(await res.text());
      process.exit(1);
    }

    const data = await res.json();
    const mp3 = Buffer.from(data.audio_base64, 'base64');
    const pcm = await decodeMp3ToPcm(mp3);
    const duration = pcm.length / (SAMPLE_RATE * 2);

    console.log(`   Starts at ${sec.start}s, duration ${duration.toFixed(2)}s, ends at ${(sec.start + duration).toFixed(2)}s`);

    // Place into master timeline
    const offset = Math.round(sec.start * SAMPLE_RATE) * 2;
    pcm.copy(masterPcm, offset);

    // Extract word timestamps aligned to this section's start time
    const words = extractWords(data.alignment, sec.start);
    const captions = chunkWordsIntoCaptions(words, sec.scene);
    allCaptions.push(...captions);
  }

  // Write master 48kHz WAV
  const wavHeader = Buffer.alloc(44);
  wavHeader.write('RIFF', 0);
  wavHeader.writeUInt32LE(36 + masterPcm.length, 4);
  wavHeader.write('WAVEfmt ', 8);
  wavHeader.writeUInt32LE(16, 16);
  wavHeader.writeUInt16LE(1, 20);
  wavHeader.writeUInt16LE(1, 22);
  wavHeader.writeUInt32LE(SAMPLE_RATE, 24);
  wavHeader.writeUInt32LE(SAMPLE_RATE * 2, 28);
  wavHeader.writeUInt16LE(2, 32);
  wavHeader.writeUInt16LE(16, 34);
  wavHeader.write('data', 36);
  wavHeader.writeUInt32LE(masterPcm.length, 40);

  const fullWav = Buffer.concat([wavHeader, masterPcm]);
  writeFileSync(OUT_WAV, fullWav);
  console.log(`\nGenerated visual-synced narration WAV: ${OUT_WAV}`);

  // Update config/narration.ts
  const tsLinesCode = allCaptions
    .map((l) => {
      const extra = l.caption === false ? ', caption: false' : '';
      const wordsJson = JSON.stringify(l.words);
      return `  {scene: '${l.scene}', start: ${l.start}, end: ${l.end}, text: ${JSON.stringify(l.text)}${extra}, words: ${wordsJson}},`;
    })
    .join('\n');

  const newTsContent = `// Narration script + timing sheet. Frame-perfect visual synchronization.
// Every code step, wiring cue, and serial print hits its exact visual cue frame-by-frame.
// Word timestamps provide real-time electric gold karaoke pop-ins in Captions.tsx.

export type WordTiming = { word: string; start: number; end: number };

export type NarrationLine = {
  scene: string;
  start: number;
  end: number;
  text: string;
  caption?: boolean;
  words?: WordTiming[];
};

export const NARRATION: NarrationLine[] = [
${tsLinesCode}
];

export const NARRATION_TEXT = NARRATION.map((l) => l.text).join(' ');
`;

  writeFileSync(CONFIG_PATH, newTsContent, 'utf8');
  console.log(`Updated ${CONFIG_PATH} with visual-synced captions.`);

  if (existsSync(SCENES_TS)) {
    let scenesContent = readFileSync(SCENES_TS, 'utf8');
    if (!scenesContent.includes('audio/narration.wav')) {
      scenesContent = scenesContent.replace(
        "export const AUDIO_FILES: string[] = [",
        "export const AUDIO_FILES: string[] = [\n  'audio/narration.wav',"
      );
      writeFileSync(SCENES_TS, scenesContent, 'utf8');
    }
  }

  console.log('\nAll done! Perfect visual sync achieved.');
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
