"""Scene 1: hook. Close on the DHT11 under a soft light sweep, then the camera
pulls back as the ESP32-S3 glides into its place."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

SCENE = next(s for s in C.EPISODE["scenes"] if s["id"] == "hook")
FRAMES = SCENE["duration"] + C.TRANSITION
# Title occupies the top; hardware lives below it.
MACRO_BAND, WIDE_BAND = (680, 1160), (640, 1120)
MACRO_VIEW, WIDE_VIEW = (-8.0, 18.0), (20.0, 34.0)
MACRO_LENS, WIDE_LENS = 85.0, 60.0


def dht_points():
    col = C.bpy.data.collections["DHT11"]
    return [o.matrix_world @ C.Vector(c) for o in col.all_objects if o.type == "MESH" for c in o.bound_box]


def main():
    opts = C.parse_args()
    scene, esp, dht, _ = C.build_stage(opts, FRAMES)
    cam = C.camera(scene, lens=MACRO_LENS, fstop=2.8)

    sensor_world = dht.matrix_world @ C.Vector((-5.85, 0.0, 6.0))
    cam.data.lens = MACRO_LENS
    t0, d0 = C.fit_view(scene, cam, sensor_world, *MACRO_VIEW, MACRO_BAND, pts=dht_points())
    cam.data.lens = WIDE_LENS
    t1, d1 = C.fit_view(scene, cam, C.mm(-12.0, -26.0, 34.0), *WIDE_VIEW, WIDE_BAND)

    # Soft white strip light sweeping across the sensor face.
    sweep = C.area_light("Light sweep", (0, 0, 0), 90, C.mm(8.0), (1.0, 1.0, 1.0),
                         (0, 0, 0), scene.collection, shape="RECTANGLE", size_y=C.mm(120.0))

    esp_home = C.Vector(esp.location)
    esp_from = esp_home + C.Vector(C.mm(70.0, 40.0, 0.0))
    for f in range(1, FRAMES + 1):
        # Sweep 1 -> 50, hold, then pull back 40 -> 110.
        s = C.progress(f, 1, 50)
        sweep.location = sensor_world + C.Vector(C.mm(-40.0 + 80.0 * s, -45.0, 30.0))
        C.aim(sweep, sensor_world)
        sweep.keyframe_insert("location", frame=f)
        sweep.keyframe_insert("rotation_euler", frame=f)
        sweep.data.energy = 90 * (1.0 - C.progress(f, 45, 75))
        sweep.data.keyframe_insert("energy", frame=f)

        pull = C.progress(f, 40, 110)
        target = C.lerp(t0, t1, pull)
        pos = C.orbit_position(target, C.lerp(d0, d1, pull), C.lerp(MACRO_VIEW[0], WIDE_VIEW[0], pull), C.lerp(MACRO_VIEW[1], WIDE_VIEW[1], pull))
        cam.data.lens = C.lerp(MACRO_LENS, WIDE_LENS, pull)
        cam.data.keyframe_insert("lens", frame=f)
        cam.data.dof.aperture_fstop = C.lerp(2.8, 8.0, pull)
        cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
        C.key_camera(cam, f, pos, target, focus=C.lerp(sensor_world, t1, pull))

        glide = C.progress(f, 55, 115, C.ease_out)
        C.key_object(esp, f, location=C.lerp(esp_from, esp_home, glide))

    C.finish(scene, SCENE["folder"], opts["preview"], opts["still"], opts["no_render"])


main()
