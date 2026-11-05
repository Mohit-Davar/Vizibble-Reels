"""Render one or all Blender scenes from the command line.

    python-less usage (run through Blender's bundled Python):
    blender -b --python blender/render.py -- --scene wiring [--preview]
    blender -b --python blender/render.py -- --scene all [--preview]

Each scene runs in a fresh Blender process so scenes never share state.
"""
import subprocess
import sys
from pathlib import Path

import bpy

SCENES = {
    "hook": "intro.py",
    "hardware": "hardware_reveal.py",
    "wiring": "wiring.py",
    "final": "final_scene.py",
}

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
name = argv[argv.index("--scene") + 1] if "--scene" in argv else "all"
passthrough = [a for a in argv if a in ("--preview", "--no-render")]
targets = list(SCENES) if name == "all" else [name]
here = Path(__file__).resolve().parent

failed = []
for target in targets:
    script = here / "scenes" / SCENES[target]
    print(f"=== {target}: {script.name} {' '.join(passthrough)}", flush=True)
    code = subprocess.call([bpy.app.binary_path, "-b", "--factory-startup", "--python-exit-code", "1",
                            "--python", str(script), "--", *passthrough])
    if code != 0:
        failed.append(target)

if failed:
    print(f"FAILED: {', '.join(failed)}")
    sys.exit(1)
print("ALL SCENES RENDERED")
