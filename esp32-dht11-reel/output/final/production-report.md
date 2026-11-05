# Production Report: How to Connect a DHT11 to an ESP32-S3

**Deliverable:** `output/final/esp32-s3-dht11-reel.mp4`. 1080x1920, 30 fps, 45.1 s, H.264 High (yuv420p, BT.709) + AAC 192 kbps, 4.5 MB. Loudness -13.0 LUFS, true peak -1.0 dBFS.

## Structure
| Time | Scene | Content |
|---|---|---|
| 0-4 s | Hook | DHT11 close-up under a soft light sweep; ESP32-S3 glides in. "Measure temperature & humidity." |
| 4-9 s | What you need | Both parts on black, slow orbit, labels underneath |
| 9-18 s | Wiring | Red VCC → 3V3, yellow DATA → GPIO4, black GND → GND. Each wire draws in 1.2 s as it is named, then its Dupont connector slides onto the real pin |
| 18-33 s | The code | Library card, then three segments typed from the real sketch. Pointer callouts underline the exact tokens (`4`, `DHT11`, `115200`, `begin`, `readTemperature`, `readHumidity`) |
| 33-40 s | Serial Monitor | Three lines at 115200 baud, marked "Illustrative output"; reading cards appear after the last line prints |
| 40-45 s | That's it. | Finished circuit and "Follow for more electronics projects" |

## Pipeline
Blender 5.2.3 (EEVEE, 96 samples, motion blur) → Remotion 4.0.540 (React/TypeScript) → FFmpeg 9.0.2 (delivery encode + loudness). Rebuild with `.\scripts\render-final.ps1`; see `docs/RENDERING.md`.

## Known limitations
- No narration voice yet. Captions and sound effects only. Recording `remotion/public/audio/narration.wav` to `config/narration.ts`, then running `render-final.ps1 -SkipBlender`, adds it without re-rendering the 3D.
- Serial values are illustrative. Replace `SERIAL.readings` in `config/episode.ts` with real ones and set `illustrative: false`.
- The sketch has not been compile-checked (no arduino-cli).
- DHT11 module dimensions are nominal (`dimensions_verified: False` in `dht11.py`).
