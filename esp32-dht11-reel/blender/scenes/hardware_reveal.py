"""Scene 2: hardware reveal. Same arrangement as the wiring scene (no wires
yet) with a slow, controlled orbit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

SCENE = next(s for s in C.EPISODE["scenes"] if s["id"] == "hardware")
FRAMES = SCENE["duration"] + C.TRANSITION
# Screen band (px) between the title and the two labels at the bottom.
BAND = (540, 1000)
START_VIEW, END_VIEW = (38.0, 34.0), (24.0, 38.0)


def main():
    opts = C.parse_args()
    scene, _, _, _ = C.build_stage(opts, FRAMES)
    cam = C.camera(scene, lens=50.0, fstop=8.0)
    base = C.mm(-12.0, -26.0, 36.0)
    t0, d0 = C.fit_view(scene, cam, base, *START_VIEW, BAND)
    t1, d1 = C.fit_view(scene, cam, base, *END_VIEW, BAND)
    for f in range(1, FRAMES + 1):
        t = C.progress(f, 1, FRAMES)
        target = C.lerp(t0, t1, t)
        # Slight push-in on top of the fitted framing.
        dist = C.lerp(d0 * 1.04, d1, t)
        pos = C.orbit_position(target, dist, C.lerp(START_VIEW[0], END_VIEW[0], t), C.lerp(START_VIEW[1], END_VIEW[1], t))
        C.key_camera(cam, f, pos, target)
    C.finish(scene, SCENE["folder"], opts["preview"], opts["still"], opts["no_render"])


main()
