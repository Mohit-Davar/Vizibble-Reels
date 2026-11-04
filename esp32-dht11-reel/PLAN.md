# PROJECT: ESP32-S3 + DHT11

## Production-Ready 3D Electronics Explainer Reel

You are the lead technical artist, 3D motion designer, creative developer, and video production engineer for this project.

Your job is to build a complete, reusable, code-driven production pipeline and produce a polished educational Instagram Reel explaining how to connect a DHT11 temperature and humidity sensor to an ESP32-S3 development board.

This is not a basic slideshow, a collection of static images, or a simple screen recording. The final result should look like a professionally produced technology explainer from a high-quality electronics, engineering, or hardware brand.

Work autonomously wherever possible. Inspect the existing project, make technical decisions, implement the pipeline, generate the assets, render previews, validate the results, and produce the final video.

Do not stop after creating a plan. Implement the project.

However, work in clearly defined milestones. Validate each milestone before moving forward. If an important technical detail is unknown, inspect the available assets or ask me instead of inventing it.

---

# 1. PROJECT OBJECTIVE

Create a 45-second vertical educational Reel.

**Topic:** How to Connect a DHT11 Sensor to an ESP32-S3.

**Audience:**

- Electronics beginners
- ESP32 developers
- Students
- Makers and hobbyists
- People learning embedded systems and IoT

**Primary learning objective:**

By the end of the video, viewers should understand:

1. Which components are required.
2. How to connect the DHT11 to the ESP32-S3.
3. Which GPIO pin is being used.
4. Which Arduino library is required.
5. How to read temperature and humidity.
6. How to verify the readings using the Serial Monitor.

**Final output:**

- Vertical 9:16 video.
- Resolution: 1080 × 1920.
- Frame rate: 30 FPS.
- Duration: approximately 45 seconds.
- Format: MP4.
- Video codec: H.264.
- Audio codec: AAC.
- High-quality typography, animation, lighting, rendering, and sound design.

Create a clean, premium, modern engineering aesthetic.

---

# 2. FIRST: INSPECT THE EXISTING PROJECT

Before changing anything, inspect the complete project directory.

Identify:

- Existing Blender Python scripts.
- Existing `.blend` files.
- Existing ESP32-S3 3D model.
- Existing DHT11 model, if any.
- Existing connection-point objects.
- Existing materials, cameras, lights, and scenes.
- Blender installation and executable path.
- Node.js and package manager availability.
- FFmpeg availability.
- Existing Remotion installation, if any.
- Existing assets and reference images.

The ESP32-S3 model has already been created and visually reviewed.

**IMPORTANT: Preserve the existing ESP32-S3 model.**

Do not recreate it, replace it, simplify it, or overwrite its source script unless absolutely necessary and explicitly approved.

Inspect its geometry and determine whether it contains identifiable connection points for:

- 3V3
- GND
- GPIO4

If actual electrical connection points are missing, add separate connection-point objects without damaging the existing model.

Use the actual board reference images supplied in the project to maintain hardware accuracy.

Create:

- `PROJECT_STATUS.md`
- `CLAUDE.md`
- `docs/HARDWARE_REFERENCE.md`
- `docs/PRODUCTION_PLAN.md`

Document existing work, missing work, important assumptions, and exact file locations.

Do not delete any existing files.

---

# 3. CREATIVE DIRECTION

The video should feel like a premium engineering explainer.

## Visual identity

Use:

- Deep charcoal backgrounds.
- Dark graphite surfaces.
- Cyan and electric blue accents.
- White typography.
- Subtle gradients.
- Soft studio lighting.
- Controlled reflections.
- Realistic materials.
- Clean technical overlays.
- Smooth camera movement.

Avoid:

- Generic AI-generated-looking visuals.
- Excessive glowing effects.
- Random floating particles.
- Unnecessary transitions.
- Cartoon-style hardware.
- Cluttered layouts.
- Oversized text.
- Excessive gradients.
- Emoji.
- Fake UI elements that do not help explain the topic.

Hardware should be the visual focus.

## Design language

Think of a combination of:

- Premium consumer electronics advertising.
- High-quality engineering animation.
- Modern developer education content.
- Professional technical product visualization.

Use a consistent design system across the complete video.

Create reusable typography, colors, spacing, animation, and transition configurations.

---

# 4. TECHNICAL ARCHITECTURE

Use a code-first workflow.

The production system should be reusable for future electronics videos.

## Blender: 3D production

Use Blender's Python API (`bpy`) for:

- ESP32-S3 model placement.
- DHT11 model placement.
- Hardware geometry.
- Materials.
- Lighting.
- Cameras.
- Product shots.
- Wire geometry.
- Wire animations.
- Camera animation.
- Scene composition.
- Technical close-ups.
- 3D scene rendering.

Use Blender's bundled Python environment for Blender scripts.

Do not assume that an ordinary system Python installation has `bpy`.

Use deterministic scripts so that the same inputs produce the same scenes.

## Remotion: motion graphics and video composition

Use Remotion with React and TypeScript for:

- Animated titles.
- Captions.
- Code presentation.
- Pin labels.
- Wiring diagrams.
- Serial Monitor interface.
- Temperature and humidity cards.
- Transitions.
- Branding.
- Final composition.

Use reusable components rather than hardcoding every scene independently.

## FFmpeg: final video processing

Use FFmpeg for:

- Audio processing.
- Final encoding.
- Combining rendered video and audio.
- Format validation.
- Final export.

## Claude Code

Claude Code should orchestrate the development process.

It should:

- Write Blender scripts.
- Write Remotion components.
- Run available commands.
- Inspect errors.
- Render previews.
- Validate output.
- Improve visual quality.
- Maintain project documentation.

Do not introduce unnecessary frameworks.

Do not use Manim for this first video. Blender and Remotion are sufficient.

Do not make Blender MCP a mandatory dependency. A reliable command-line workflow is preferred.

---

# 5. PROJECT STRUCTURE

Inspect the current project first. Adapt its existing structure rather than blindly replacing it.

Use the following structure as the target:

```text
esp32-dht11-reel/
│
├── CLAUDE.md
├── PROJECT_STATUS.md
├── package.json
├── README.md
│
├── assets/
│   ├── reference/
│   │   ├── esp32-front.png
│   │   ├── esp32-back.png
│   │   └── dht11-reference.png
│   ├── audio/
│   ├── music/
│   └── textures/
│
├── blender/
│   ├── models/
│   │   ├── esp32_s3.py
│   │   ├── dht11.py
│   │   └── breadboard.py
│   │
│   ├── scenes/
│   │   ├── intro.py
│   │   ├── hardware_reveal.py
│   │   ├── wiring.py
│   │   ├── code_scene.py
│   │   ├── output_scene.py
│   │   └── final_scene.py
│   │
│   ├── scripts/
│   └── render.py
│
├── remotion/
│   ├── src/
│   │   ├── components/
│   │   ├── scenes/
│   │   ├── styles/
│   │   ├── Reel.tsx
│   │   └── Root.tsx
│   └── package.json
│
├── config/
│   ├── episode.ts
│   ├── narration.ts
│   └── design.ts
│
├── scripts/
│   ├── check-environment.ps1
│   ├── render-preview.ps1
│   └── render-final.ps1
│
├── docs/
│   ├── HARDWARE_REFERENCE.md
│   ├── PRODUCTION_PLAN.md
│   └── RENDERING.md
│
└── output/
    ├── previews/
    ├── scenes/
    └── final/
```

The structure may be adjusted if the existing project already has a better organization.

Do not create duplicate models or duplicate project configurations.

---

# 6. HARDWARE ACCURACY

This is an engineering education video. Hardware accuracy is more important than visual decoration.

## ESP32-S3

Use the existing ESP32-S3 model.

Preserve:

- PCB dimensions and proportions.
- ESP32-S3 module.
- USB connectors.
- Header pins.
- Existing silkscreen details.
- Existing board appearance.

Use the user's actual reference images to validate the model.

Do not invent board markings or pin locations.

## DHT11

The intended sensor is the commonly available blue DHT11 sensor.

First inspect the supplied reference image.

Determine whether it is:

- A three-pin PCB module, or
- A bare four-pin DHT11 sensor.

Model the correct variant.

For a three-pin module, represent:

- Blue sensor housing.
- Small PCB.
- Three pins.
- Appropriate pin labels if visible in the reference.

For a bare four-pin sensor, model the correct four-pin package and pin layout.

Do not mix the two variants.

Use the actual reference image for geometry and appearance.

## Electrical connections

The intended three-pin module wiring is:

| DHT11          | ESP32-S3 |
| -------------- | -------- |
| VCC / +        | 3V3      |
| DATA / OUT / S | GPIO4    |
| GND / -        | GND      |

Use:

- Red wire for VCC.
- Yellow wire for DATA.
- Black wire for GND.

Use 3.3V power.

The wiring must terminate at the correct physical header pins, not merely near the printed labels.

Use actual connection-point coordinates from the existing ESP32 model.

If the board orientation makes GPIO4 or another connection point unclear, inspect the reference image before proceeding.

For a typical three-pin DHT11 module, assume its PCB includes the required pull-up circuitry only if the actual module supports that assumption.

If using a bare four-pin sensor, account for the external pull-up resistor between DATA and VCC.

Do not display an external resistor for a module that already includes one unless it is clearly presented as an optional technical note.

---

# 7. THE VIDEO STORYBOARD

Produce six connected scenes.

All scene timings are approximate. Adjust them to maintain pacing and narration clarity.

## SCENE 1: HOOK

### 0–4 seconds

Visual:

- Begin with a dark, minimal environment.
- Reveal the blue DHT11 sensor using a dramatic macro camera shot.
- Bring the ESP32-S3 into the frame.
- Use controlled studio lighting.
- Add a subtle cyan light sweep.

Text:

"MEASURE TEMPERATURE & HUMIDITY"

Secondary text:

"ESP32-S3 + DHT11"

Narration:

"Want to measure temperature and humidity using an ESP32? Let's do it!"

The opening must immediately communicate what the video teaches.

## SCENE 2: HARDWARE REVEAL

### 4–9 seconds

Visual:

- Show both components in a clean product arrangement.
- ESP32-S3 on one side.
- DHT11 on the other.
- Slight camera orbit.
- Clean component labels.
- Soft shadows and realistic materials.

Text:

"WHAT YOU NEED"

Component labels:

- ESP32-S3 Development Board
- DHT11 Temperature & Humidity Sensor

Narration:

"We need just two things: an ESP32-S3 development board and a DHT11 sensor."

## SCENE 3: WIRING

### 9–21 seconds

This is the most important scene.

Create a clear, beautiful, technically accurate wiring animation.

Show the ESP32-S3 and DHT11 in a composition where the connection pins are visible.

Animate the wires individually.

First connection:

Red wire:
DHT11 VCC → ESP32-S3 3V3

Show a clear label:

"VCC → 3V3"

Second connection:

Yellow wire:
DHT11 DATA → ESP32-S3 GPIO4

Show:

"DATA → GPIO4"

Third connection:

Black wire:
DHT11 GND → ESP32-S3 GND

Show:

"GND → GND"

Each wire should:

- Start at the correct physical pin.
- Follow a clean, visually understandable path.
- End at the correct physical pin.
- Animate smoothly.
- Have a brief visual highlight when connected.

Use elegant curves and realistic wire thickness.

Do not use straight lines passing through hardware.

Do not let wires intersect unnecessarily.

Do not allow labels to overlap the hardware.

Use a camera angle that makes the connections understandable.

When the wiring is complete, briefly show the complete circuit.

Narration:

"Connect VCC to 3.3 volts, data to GPIO four, and ground to ground."

## SCENE 4: CODE

### 21–33 seconds

Transition from the 3D hardware to a modern code-editor presentation.

The code should be readable on a mobile screen.

Do not display the complete program in tiny text.

Show the important code in three readable segments.

Segment 1: Library and sensor configuration.

```cpp
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
```

Segment 2: Initialization.

```cpp
void setup() {
  Serial.begin(115200);
  dht.begin();
}
```

Segment 3: Reading values.

```cpp
float temperature = dht.readTemperature();
float humidity = dht.readHumidity();
```

Explain the purpose of GPIO4 and the DHT11 sensor type through subtle annotations.

Narration:

"Now install the Adafruit DHT library. Select DHT11, initialize the sensor, and read its temperature and humidity."

Show a small installation annotation:

"Adafruit DHT Sensor Library"

Also mention its dependency:

"Adafruit Unified Sensor"

Do not pretend the video has installed or uploaded the code automatically.

## SCENE 5: SERIAL MONITOR OUTPUT

### 33–40 seconds

Show the Serial Monitor in a polished developer-style interface.

Display actual readings obtained from a working sensor if hardware is available.

Example format:

```text
Temperature: 27.0 °C | Humidity: 58.0 %
Temperature: 27.0 °C | Humidity: 58.0 %
```

These numbers are illustrative only.

Never represent illustrative values as measurements from the user's actual sensor.

If no real hardware readings are available:

- Use clearly labeled sample data.
- Mark it as "Illustrative output".
- Make it easy to replace later with actual readings.

Animate the temperature and humidity values into two clear visual cards.

Narration:

"Upload the code, open the Serial Monitor, and now your ESP32 is reading temperature and humidity!"

## SCENE 6: FINAL SHOT

### 40–45 seconds

Visual:

- Show the complete ESP32-S3 and DHT11 circuit.
- All three wires connected.
- Camera slowly moves into a final product shot.
- Show the two output cards.
- Display a clean closing title.

Text:

"THAT'S IT!"

Secondary:

"ESP32-S3 + DHT11"

Closing CTA:

"FOLLOW FOR MORE ELECTRONICS PROJECTS"

Narration:

"And that's how you connect a DHT11 to an ESP32. Follow for more electronics projects!"

---

# 8. ARDUINO CODE

Use the following as the source of truth for the code shown in the video:

```cpp
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Sensor read failed");
    delay(2000);
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" °C | Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  delay(2000);
}
```

Technical requirements:

- Use the Adafruit DHT library.
- Include the Adafruit Unified Sensor dependency where required.
- Use GPIO4.
- Use DHT11.
- Use 115200 baud.
- Use a 2000 ms delay.
- Handle failed readings.
- Ensure the code shown in the video is consistent with the actual source code.

Store the source code separately so it can be reused.

---

# 9. MOTION DESIGN REQUIREMENTS

Animation quality is extremely important.

Use:

- Smooth ease-in/ease-out curves.
- Controlled camera acceleration.
- Subtle camera depth.
- Realistic product reveals.
- Carefully timed transitions.
- Smooth text entrances.
- Clean wire-drawing animations.
- Subtle UI transitions.

Avoid:

- Sudden camera movements.
- Excessive zooms.
- Uncontrolled object rotation.
- Random animations.
- Unnecessary bounce effects.
- Overly fast text.
- Distracting background effects.

All animations should be deterministic and frame-based.

Remotion animations should use frame-based interpolation.

Blender animations should use explicit keyframes.

Avoid timing logic based on real-world clocks.

---

# 10. AUDIO AND NARRATION

Create a narration script that fits the complete 45-second timeline.

The voice should sound:

- Clear.
- Confident.
- Friendly.
- Technical but beginner-friendly.
- Natural rather than robotic.

If a suitable voice generation tool is available, use it only if it is accessible and authorized.

Otherwise:

- Create a narration script.
- Create a timing sheet.
- Leave an audio track slot for recorded narration.

Do not invent a voice-generation API key or assume access to a paid service.

Add subtle sound effects:

- Hardware reveal.
- Wire connection.
- Code transition.
- Successful output.
- Closing transition.

Use subtle background music only if a suitable licensed or original track is available.

Do not use copyrighted music without permission.

Ensure narration is clearly audible above the background music.

---

# 11. REUSABLE PRODUCTION SYSTEM

Do not make this a one-off collection of scripts.

Build a reusable system that makes future electronics Reels easier to produce.

The following should be configurable:

- Episode title.
- Duration.
- Scene timings.
- Hardware assets.
- GPIO pin numbers.
- Wiring definitions.
- Code snippets.
- Narration.
- Captions.
- Brand colors.
- Output resolution.
- Frame rate.

Use a central configuration file.

For example, the wiring should be represented as structured data instead of being independently hardcoded in multiple places.

Create reusable components for:

- Hardware product reveal.
- Wire connection animation.
- Component labels.
- Code editor.
- Serial Monitor.
- Measurement cards.
- Titles.
- Captions.
- Transitions.

Future episodes should be able to reuse these components.

---

# 12. QUALITY CONTROL

Quality matters more than speed.

Before final export, verify the following.

## Hardware

- ESP32-S3 matches the supplied reference.
- DHT11 matches the supplied reference.
- Correct sensor variant is used.
- Correct physical pins are connected.
- No wires float or terminate incorrectly.
- No geometry intersects unexpectedly.

## Video

- Correct vertical aspect ratio.
- Correct resolution.
- Correct frame rate.
- Consistent typography.
- No clipping.
- No overlapping captions.
- No text too small for mobile.
- No blank frames.
- No missing scene transitions.
- No visible rendering artifacts.

## Technical information

- GPIO4 is shown consistently.
- VCC connects to 3V3.
- DATA connects to GPIO4.
- GND connects to GND.
- DHT11 type is correct.
- Library name is correct.
- Serial Monitor baud is correct.
- Code compiles if an Arduino CLI environment is available.

## Audio

- Narration is synchronized.
- No clipping.
- Music does not overpower narration.
- No accidental silence or missing audio.

Create a quality-control report in:

`docs/QUALITY_CONTROL.md`

---

# 13. RENDERING AND DELIVERABLES

Create commands that allow me to render the video without manually opening Blender or Remotion every time.

At minimum, provide:

1. Environment check.
2. Blender scene render.
3. Low-resolution preview render.
4. Full-resolution final render.
5. Final MP4 validation.

Keep the rendering workflow documented.

Expected deliverables:

```text
output/
├── previews/
│   ├── hardware-preview.mp4
│   ├── wiring-preview.mp4
│   └── full-preview.mp4
│
├── scenes/
│   ├── scene-01/
│   ├── scene-02/
│   └── ...
│
└── final/
    ├── esp32-s3-dht11-reel.mp4
    └── production-report.md
```

Also provide:

- Complete editable source code.
- Blender scene files.
- Blender Python scripts.
- Remotion project.
- Narration script.
- Episode configuration.
- Render commands.
- Documentation.

Do not leave the final deliverable as a collection of unrelated image files.

---

# 14. IMPLEMENTATION WORKFLOW

Work through these milestones in order.

## MILESTONE 1: PROJECT AUDIT

Inspect the project and identify existing assets, dependencies, and executable paths.

Preserve all existing work.

Create the project documentation.

## MILESTONE 2: HARDWARE ASSETS

Validate the existing ESP32-S3 model.

Create or refine the DHT11 model based on the supplied reference.

Ensure that physical connection points are available.

Render a hardware preview.

## MILESTONE 3: 3D SCENES

Create the product reveal, hardware arrangement, wiring animation, and final hardware composition.

Render individual scene previews.

## MILESTONE 4: REMOTION PROJECT

Set up Remotion and build the reusable motion graphics system.

Implement titles, code presentation, labels, output UI, and scene transitions.

## MILESTONE 5: COMPLETE VIDEO

Combine Blender scenes and Remotion graphics into the full video.

Add narration slots, sound effects, and music where available.

## MILESTONE 6: QUALITY CONTROL

Render the complete preview.

Inspect it for technical and visual errors.

Correct issues before final rendering.

## MILESTONE 7: FINAL EXPORT

Render the final 1080 × 1920 MP4 at 30 FPS.

Validate the video and write the production report.

---

# 15. IMPORTANT WORKING RULES

1. Do not overwrite working assets.
2. Do not delete existing files.
3. Do not invent hardware specifications.
4. Do not fabricate actual sensor measurements.
5. Do not create fake screenshots of software installations.
6. Do not use generic AI-generated hardware imagery instead of the existing 3D models.
7. Do not hardcode the same configuration in multiple files.
8. Do not introduce unnecessary dependencies.
9. Do not silently ignore errors.
10. Keep the code readable and maintainable.
11. Use sensible file names.
12. Document important decisions.
13. Test commands before documenting them as working.
14. Render previews frequently.
15. Prioritize visual quality and technical correctness.

If an essential reference is missing, ask me for it.

If a tool is unavailable, explain the limitation and provide a practical alternative.

Do not claim that a render, installation, hardware test, or compilation succeeded unless it actually did.

---

# 16. FINAL EXPECTATION

I want a production-ready electronics explainer video, not just a prototype.

The final Reel should feel like it belongs to a professional engineering and electronics education brand.

It should have:

- Beautiful realistic 3D hardware.
- Accurate electrical connections.
- Cinematic camera work.
- Smooth motion graphics.
- Readable code.
- Clear technical explanations.
- Professional sound design.
- Consistent visual identity.
- High-quality final rendering.

Start by auditing the existing project.

Then implement the milestones in order.

Make reasonable decisions independently, but never compromise hardware accuracy or overwrite existing working assets.

At the end of every milestone:

- Update `PROJECT_STATUS.md`.
- List created and modified files.
- Run the relevant validation.
- Render a preview where applicable.
- Report any blockers.
- Clearly state what I need to review.

The ultimate goal is to create a reusable production pipeline that can produce many future electronics explainer Reels, not just this one video.
