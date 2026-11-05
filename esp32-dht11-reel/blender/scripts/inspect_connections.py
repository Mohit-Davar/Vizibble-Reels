"""QC: close-up renders of every wire connection (board end + sensor end).

    blender -b --python blender/scripts/inspect_connections.py
Writes output/previews/qc-connection-*.png and prints distances between each
housing and its pin so a misaligned connector fails loudly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scenes"))
import common as C  # noqa: E402

opts = {"preview": False, "still": None, "no_render": False}
scene, esp, dht, wires = C.build_stage(opts, 1, wires=True)
for w in wires:
    w.finished()
C.bpy.context.view_layer.update()
scene.render.resolution_percentage = 50

# Numeric check: housing socket end must sit on the pin seat.
for w in wires:
    for end, housing, seat in (("board", w.board_housing, w.board_seat), ("sensor", w.sensor_housing, w.sensor_seat)):
        far = housing.matrix_world @ C.Vector((0, 0, C.mm(C.DUPONT_LEN)))
        print(f"QC {w.spec['id']:5s} {end:6s} socket-to-seat {(far - seat).length / C.MM:.3f} mm")

cam = C.camera(scene, lens=100.0, fstop=11.0)
fails = 0
for w in wires:
    for housing, seat in ((w.board_housing, w.board_seat), (w.sensor_housing, w.sensor_seat)):
        if ((housing.matrix_world @ C.Vector((0, 0, C.mm(C.DUPONT_LEN)))) - seat).length / C.MM > 0.05:
            fails += 1
print(f"QC RESULT {'PASS' if fails == 0 else f'FAIL ({fails} connectors off-pin)'}")

# Board pin tips are at z ~ 35.7 mm, housings run down to ~21.7 mm.
views = {
    "board-front": (C.mm(0, -27, 30), C.mm(120), 0, 4),
    "board-right": (C.mm(11, -23, 30), C.mm(100), 70, 4),
    "sensor": (C.mm(-22, -60, 22), C.mm(90), 15, 8),
}
for name, (target, dist, az, el) in views.items():
    C.key_camera(cam, 1, C.orbit_position(target, dist, az, el), target)
    scene.render.filepath = str(C.ROOT / "output" / "previews" / f"qc-connection-{name}.png")
    C.bpy.ops.render.render(write_still=True)
    print(f"QC view {scene.render.filepath}")
