# CLAUDE.md

Code-driven pipeline for a 45 s, 1080x1920, 30 fps educational Reel: ESP32-S3 + DHT11. The full brief is `PLAN.md`; status is `PROJECT_STATUS.md`.

## Hard rules
- Never modify or recreate `blender/models/esp32_s3.py`. It is approved. Do not delete any existing file.
- Hardware accuracy beats decoration. Do not invent pin locations or markings; check `assets/reference/*.png`.
- Wiring: DHT11 VCC -> 3V3 (red), DATA -> GPIO4 (yellow), GND -> GND (black). Defined once in `config/episode.ts`; everything else reads from it.
- Sensor values in the video are illustrative and must be labelled "Illustrative output".
- Never claim a render, install or compile succeeded unless it ran.
- No emoji, no stock/AI imagery, no unlicensed music, no invented API keys.

## Layout
- `blender/models/` hardware models (bpy, run in Blender's bundled Python). `blender/scenes/` per-scene scripts. `blender/render.py` CLI entry.
- `remotion/` React + TypeScript motion graphics and final composition.
- `config/` single source of truth: `episode.ts`, `narration.ts`, `design.ts`. Arduino source lives in `firmware/dht11_esp32s3/dht11_esp32s3.ino` and is imported by the code scene.
- `scripts/` PowerShell entry points (environment check, preview, final) plus the existing Blender helper scripts.
- `output/` renders (generated, not committed except reports).

## Conventions
- Blender: `blender -b <file.blend> --python <script.py>`; scene unit scale is 0.04 units per mm. Deterministic, explicit keyframes only.
- Remotion: frame-based `interpolate`/`spring` only, no wall-clock timing.
- Shell is Windows PowerShell 5.1: no `&&`.
