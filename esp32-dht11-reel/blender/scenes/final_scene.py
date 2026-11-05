"""Scene 6: final hero shot of the complete circuit, slow push-in."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

SCENE = next(s for s in C.EPISODE["scenes"] if s["id"] == "final")
FRAMES = SCENE["duration"]
# Screen band (px) between the closing title and the call to action.
BAND_START, BAND_END = (500, 1060), (480, 1070)
START_VIEW, END_VIEW = (4.0, 40.0), (16.0, 34.0)


def main():
    opts = C.parse_args()
    scene, _, _, wires = C.build_stage(opts, FRAMES, wires=True)
    for w in wires:
        w.finished()
    cam = C.camera(scene, lens=50.0, fstop=6.0)
    base = C.mm(-12.0, -26.0, 22.0)
    t0, d0 = C.fit_view(scene, cam, base, *START_VIEW, BAND_START)
    t1, d1 = C.fit_view(scene, cam, base, *END_VIEW, BAND_END)
    for f in range(1, FRAMES + 1):
        t = C.progress(f, 1, FRAMES)
        target = C.lerp(t0, t1, t)
        pos = C.orbit_position(target, C.lerp(d0, d1, t), C.lerp(START_VIEW[0], END_VIEW[0], t), C.lerp(START_VIEW[1], END_VIEW[1], t))
        C.key_camera(cam, f, pos, target)
    C.finish(scene, SCENE["folder"], opts["preview"], opts["still"], opts["no_render"])


main()
