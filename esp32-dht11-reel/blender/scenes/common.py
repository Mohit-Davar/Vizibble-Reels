"""Shared Blender production toolkit for electronics explainer reels.

Everything here is deterministic: no randomness, no wall-clock time. Scene
scripts call `build_stage()`, then position hardware, animate cameras and wires
with the helpers below, and finally `render_scene()`.

Units: hardware models are authored in millimetres under a root empty scaled by
MM (0.04 Blender units per mm). Layout constants below are in millimetres and
converted with `mm()`.

The approved ESP32-S3 model (blender/models/esp32_s3.py) is imported and
called, never modified.
"""

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
EPISODE = json.loads((ROOT / "config" / "episode.json").read_text(encoding="utf-8"))
MM = 0.04
FPS = EPISODE["video"]["fps"]
TRANSITION = EPISODE["transitionFrames"]


def mm(*values):
    return tuple(v * MM for v in values) if len(values) > 1 else values[0] * MM


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ESP = _load("esp32_s3_model", ROOT / "blender" / "models" / "esp32_s3.py")
DHT = _load("dht11_model", ROOT / "blender" / "models" / "dht11.py")
WIRING_HELPERS = _load("prepare_esp32_wiring", ROOT / "scripts" / "prepare_esp32_wiring.py")


# ------------------------------------------------------------------ easing
def ease_in_out(t):
    """Cubic ease-in-out, matching Remotion's easeInOut feel."""
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 4)


def progress(frame, start, end, ease=ease_in_out):
    if end <= start:
        return 1.0 if frame >= end else 0.0
    return ease((frame - start) / (end - start))


def lerp(a, b, t):
    if isinstance(a, (tuple, list, Vector)):
        return Vector(a).lerp(Vector(b), t)
    return a + (b - a) * t


# ------------------------------------------------------------------ validation
def validate_pinout():
    """config/episode.json must mirror the approved model's header pinout."""
    pinout = EPISODE["boardPinout"]
    if pinout["J1"] != ESP.J1_LEFT or pinout["J3"] != ESP.J3_RIGHT:
        raise RuntimeError("config/episode.json boardPinout does not match blender/models/esp32_s3.py")


def esp_pin(name):
    """Map a wiring pin name (3V3, GPIO4, GND) to (side, index) on the model."""
    label = name.replace("GPIO", "")
    if label != "GND" and label in ESP.J1_LEFT:
        return -1, ESP.J1_LEFT.index(label)
    if label in ESP.J3_RIGHT:
        return 1, ESP.J3_RIGHT.index(label)
    raise RuntimeError(f"Pin {name} not on the ESP32-S3 headers")


# ------------------------------------------------------------------ materials
def material(name, color, roughness=0.4, metallic=0.0, coat=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color[:3], 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.08
    em = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if em is not None:
        em.default_value = (*color[:3], 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission
    return mat


# ------------------------------------------------------------------ scene setup
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    return scene


def set_render(scene, preview, frames):
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    ee = scene.eevee
    ee.taa_render_samples = 24 if preview else 96
    for attr, value in (
        ("use_raytracing", True),
        ("use_shadows", True),
        ("use_gtao", True),
        ("use_fast_gi", True),
    ):
        if hasattr(ee, attr):
            setattr(ee, attr, value)
    if hasattr(ee, "ray_tracing_options"):
        ee.ray_tracing_options.resolution_scale = "2" if preview else "1"
    scene.render.resolution_x = EPISODE["video"]["width"]
    scene.render.resolution_y = EPISODE["video"]["height"]
    scene.render.resolution_percentage = 50 if preview else 100
    scene.render.film_transparent = False
    scene.render.use_motion_blur = not preview
    if not preview:
        scene.render.motion_blur_shutter = 0.35
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.frame_start = 1
    scene.frame_end = frames


def build_studio(scene):
    """Product-film studio: pure black void (no floor, no backdrop glow).
    A large soft top light shapes the surfaces, a gentle front fill opens the
    shadows, and two narrow back rims draw clean edge highlights."""
    col = bpy.data.collections.new("Studio")
    scene.collection.children.link(col)

    world = bpy.data.worlds.new("Studio world")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1)
    bg.inputs["Strength"].default_value = 0.0

    target = mm(-10, -20, 40)
    lights = {
        # name: (location, watts, size, colour, spread degrees)
        "Top softbox": (mm(-60, -120, 380), 3200, mm(420), (1.0, 0.99, 0.97), 60),
        "Front fill": (mm(180, -320, 120), 500, mm(360), (0.97, 0.98, 1.0), 60),
        "Rim left": (mm(-220, 180, 160), 1400, mm(120), (0.95, 0.97, 1.0), 25),
        "Rim right": (mm(220, 200, 180), 1200, mm(120), (0.95, 0.97, 1.0), 25),
    }
    objs = {}
    for name, (loc, energy, size, color, spread) in lights.items():
        objs[name] = area_light(name, loc, energy, size, color, target, col)
        objs[name].data.spread = math.radians(spread)
    return col, objs


def build_stage(opts, frames, wires=False):
    """Fresh scene with studio + hardware (+ wires). Returns (scene, esp, dht, wires)."""
    scene = reset()
    set_render(scene, opts["preview"], frames)
    build_studio(scene)
    esp, dht = build_hardware(scene)
    built = build_wires(scene) if wires else []
    return scene, esp, dht, built


def area_light(name, location, energy, size, color, target, collection, shape="DISK", size_y=None):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = shape
    data.size = size
    if size_y is not None:
        data.size_y = size_y
    data.color = color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    aim(obj, target)
    return obj


def aim(obj, target):
    direction = Vector(target) - Vector(obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _move(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


# ------------------------------------------------------------------ hardware
# Assembly layout (mm). Board floats with the antenna end toward the camera so
# pin 1 of both headers (3V3 on J1, GND on J3) sits at the front corners and
# GPIO4 is three pins behind 3V3. The DHT11 module stands upright to the
# front-left, sensor facing the camera, header pins pointing down. With this
# arrangement the three wires never cross (see docs/HARDWARE_REFERENCE.md).
ESP_LOCATION_MM = (0.0, 0.0, 45.0)
ESP_ROTATION_Z = math.pi
DHT_LOCATION_MM = (-22.0, -60.0, 57.4)
# Columns are where local X, Y, Z land in world space: pins (local +X) point
# down, pin order axis (local +Y) runs along world +X, sensor face (local +Z)
# faces the camera (-Y).
DHT_ROTATION = Matrix(((0, 1, 0), (0, 0, -1), (-1, 0, 0))).to_euler()

DUPONT_LEN = 14.0  # female jumper housing length (mm)
DUPONT_SOCKET = 6.0  # how far the header pin enters the housing (mm)
DUPONT_W = 2.54


def build_hardware(scene):
    validate_pinout()
    esp_col = bpy.data.collections.new("ESP32_S3")
    scene.collection.children.link(esp_col)
    mats = ESP.build_materials()
    esp_root, _ = ESP.build_board(mats, esp_col)
    esp_root.location = mm(*ESP_LOCATION_MM)
    esp_root.rotation_euler = (0, 0, ESP_ROTATION_Z)

    _, dht_root = DHT.build_module(scene.collection, location=mm(*DHT_LOCATION_MM))
    dht_root.rotation_euler = DHT_ROTATION
    bpy.context.view_layer.update()

    # ESP32 connection points: real pin-tail tips, resolved by the existing
    # (approved) helper so both pipelines agree on geometry.
    conn = bpy.data.collections.new("Connection Points")
    esp_col.children.link(conn)
    inv = esp_root.matrix_world.inverted()
    for wire in EPISODE["wiring"]:
        side, index = esp_pin(wire["to"]["pin"])
        world = WIRING_HELPERS.find_pin_tail(esp_root, side, index, ESP)
        loc = bpy.data.objects.new(wire["to"]["locator"], None)
        conn.objects.link(loc)
        loc.parent = esp_root
        loc.location = inv @ world
        loc.empty_display_type = "SPHERE"
        loc.empty_display_size = 1.4
    bpy.context.view_layer.update()
    return esp_root, dht_root


def locator(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Missing connection locator {name}")
    return obj


# ------------------------------------------------------------------ wires
def _housing(name, color_mat, metal_mat, collection):
    """Female Dupont housing, built along local +Z from 0 to DUPONT_LEN (mm, scaled)."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.object
    body.name = name
    body.data.materials.append(color_mat)
    # Bake the mm size into the mesh, origin at the wire end (z=0).
    for v in body.data.vertices:
        v.co.x *= mm(DUPONT_W)
        v.co.y *= mm(DUPONT_W)
        v.co.z = (v.co.z + 0.5) * mm(DUPONT_LEN)
    bevel = body.modifiers.new("Bevel", "BEVEL")
    bevel.width = mm(0.25)
    bevel.segments = 2
    _move(body, collection)

    # Small crimp sleeve where the wire enters.
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=mm(0.95), depth=mm(2.0), location=(0, 0, -mm(0.8)))
    crimp = bpy.context.object
    crimp.name = name + " crimp"
    crimp.data.materials.append(metal_mat)
    crimp.parent = body
    crimp.location = (0, 0, -mm(0.6))
    _move(crimp, collection)
    return body


def _orient(obj, origin, direction):
    """Place obj with its local +Z along `direction`, origin at `origin`."""
    obj.location = origin
    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()


class Wire:
    """Animated jumper wire: grows from the sensor pin to the board pin.

    Both ends use female Dupont housings seated on the real pins; see
    `keyframe()` for the animation and blender/scripts/inspect_connections.py
    for the seating check.
    """

    def __init__(self, spec, collection, sag_mm=16.0, lateral_mm=(0.0, 0.0)):
        self.spec = spec
        rgb = EPISODE["wireColors"][spec["color"]]["render"]
        black = spec["color"] == "black"
        self.mat = material(
            f"Wire {spec['id']}", rgb, roughness=0.28 if black else 0.38, coat=0.6 if black else 0.25
        )
        if black:  # a black emitter is invisible; highlight the black wire in soft grey
            self.mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.5, 0.5, 0.52, 1)
        housing_mat = material("Dupont housing", (0.012, 0.012, 0.014), roughness=0.45)
        metal = bpy.data.materials.get("Crimp metal") or material("Crimp metal", (0.75, 0.76, 0.78), roughness=0.25, metallic=1.0)

        sensor_loc = locator(spec["from"]["locator"])
        board_loc = locator(spec["to"]["locator"])
        bpy.context.view_layer.update()

        # Pin directions in world space: board pin tails point down, sensor
        # pins point along the module's local +X.
        board_dir = (board_loc.parent.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        sensor_dir = (sensor_loc.parent.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
        self.board_seat = board_loc.matrix_world.translation - board_dir * mm(DUPONT_SOCKET)
        self.sensor_seat = sensor_loc.matrix_world.translation - sensor_dir * mm(DUPONT_SOCKET)
        p0 = self.sensor_seat + sensor_dir * mm(DUPONT_LEN)  # wire leaves sensor housing
        p3 = self.board_seat + board_dir * mm(DUPONT_LEN)  # wire enters board housing
        # The routing bias goes on the sensor-side handle only. The board-side
        # handle stays exactly on the pin axis, so the wire arrives straight up
        # the pin, coaxial with its housing.
        lateral = Vector((mm(lateral_mm[0]), mm(lateral_mm[1]), 0)) * 2.0
        self.ctrl = (
            p0,
            p0 + sensor_dir * mm(sag_mm) + lateral,
            p3 + board_dir * mm(sag_mm),
            p3,
        )
        self.board_dir, self.sensor_dir = board_dir, sensor_dir

        curve = bpy.data.curves.new(f"Wire {spec['id']}", "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = mm(0.8)
        curve.bevel_resolution = 4
        curve.use_fill_caps = True
        curve.resolution_u = 48
        spline = curve.splines.new("BEZIER")
        spline.bezier_points.add(1)
        a, b = spline.bezier_points
        a.co, a.handle_right, a.handle_left = self.ctrl[0], self.ctrl[1], self.ctrl[0] * 2 - self.ctrl[1]
        b.co, b.handle_left, b.handle_right = self.ctrl[3], self.ctrl[2], self.ctrl[3] * 2 - self.ctrl[2]
        self.obj = bpy.data.objects.new(f"Wire {spec['id']} ({spec['label']})", curve)
        self.obj.data.materials.append(self.mat)
        collection.objects.link(self.obj)

        self.sensor_housing = _housing(f"Dupont {spec['id']} sensor end", housing_mat, metal, collection)
        self.board_housing = _housing(f"Dupont {spec['id']} board end", housing_mat, metal, collection)

    # Housing local +Z points from the wire end toward the pin. `offset` is the
    # distance (mm) the housing still has to travel to be fully seated.
    def _place_sensor_housing(self, offset):
        origin = self.sensor_seat + self.sensor_dir * mm(DUPONT_LEN + offset)
        _orient(self.sensor_housing, origin, -self.sensor_dir)

    def _place_board_housing(self, offset):
        origin = self.board_seat + self.board_dir * mm(DUPONT_LEN + offset)
        _orient(self.board_housing, origin, -self.board_dir)

    @staticmethod
    def _key_housing(housing, frame, hidden):
        """Key transform + visibility. hide_render does not propagate to
        children in Blender, so the crimp sleeve is keyed explicitly."""
        housing.keyframe_insert("location", frame=frame)
        housing.keyframe_insert("rotation_euler", frame=frame)
        for obj in (housing, *housing.children):
            obj.hide_render = hidden
            obj.keyframe_insert("hide_render", frame=frame)

    def keyframe(self, frame, draw_start, draw_end):
        """Key every frame (deterministic, exact easing).

        1. The sensor-end housing slides 5 mm onto its pin just before drawing.
        2. The wire grows from the sensor toward the board.
        3. Over the last stretch the board-end housing appears on the pin axis
           and slides straight up onto the pin together with the wire tip.
        4. A brief, soft highlight in the wire's own colour marks the connection.
        """
        f = frame
        grow = progress(f, draw_start, draw_end)
        lead_in, seat_travel = 10, 5.0
        sensor_slide = 1.0 - progress(f, draw_start - lead_in, draw_start, ease_out)
        board_phase = progress(grow, 0.8, 1.0, ease_out)

        self.obj.data.bevel_factor_end = max(0.0005, grow)
        self.obj.data.keyframe_insert("bevel_factor_end", frame=f)
        self.obj.hide_render = f < draw_start
        self.obj.keyframe_insert("hide_render", frame=f)

        self._place_sensor_housing(seat_travel * sensor_slide)
        self._key_housing(self.sensor_housing, f, hidden=f < draw_start - lead_in)

        self._place_board_housing(12.0 * (1.0 - board_phase))
        self._key_housing(self.board_housing, f, hidden=grow < 0.8)

        bsdf = self.mat.node_tree.nodes["Principled BSDF"]
        pulse = 0.0
        if f >= draw_end:
            pulse = max(0.0, 1.0 - (f - draw_end) / 16.0) ** 2 * 0.9
        bsdf.inputs["Emission Strength"].default_value = pulse
        bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)

    def finished(self):
        """Static fully-connected state (for scenes after wiring)."""
        self.obj.data.bevel_factor_end = 1.0
        self.obj.hide_render = False
        self._place_sensor_housing(0.0)
        self._place_board_housing(0.0)
        self.sensor_housing.hide_render = False
        self.board_housing.hide_render = False


# Per-wire routing tweaks (mm): sag depth and lateral bias of the handles so
# the data wire passes cleanly between the others under the board.
WIRE_ROUTING = {
    # Black (GND) has the shortest run: shallow sag, biased away from camera so
    # it passes behind. Red (VCC) runs nearest the camera with the deepest sag.
    "vcc": {"sag_mm": 22.0, "lateral_mm": (2.0, -3.0)},
    "data": {"sag_mm": 17.0, "lateral_mm": (0.0, 0.0)},
    "gnd": {"sag_mm": 9.0, "lateral_mm": (-2.0, 5.0)},
}


def build_wires(scene):
    col = bpy.data.collections.new("Wires")
    scene.collection.children.link(col)
    return [Wire(spec, col, **WIRE_ROUTING.get(spec["id"], {})) for spec in EPISODE["wiring"]]


# ------------------------------------------------------------------ camera
def camera(scene, name="Camera", lens=50.0, fstop=5.6):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_fit = "VERTICAL"
    data.sensor_height = 36.0
    data.clip_start = 0.01
    data.dof.use_dof = True
    data.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def orbit_position(target, distance, azimuth_deg, elevation_deg):
    """Camera position around target. Azimuth 0 = looking from -Y toward +Y."""
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    t = Vector(target)
    return t + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * distance


def hardware_points():
    """World-space bounding-box corners of all visible hardware and wires."""
    pts = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for col_name in ("ESP32_S3", "DHT11", "Wires"):
        col = bpy.data.collections.get(col_name)
        if col is None:
            continue
        for obj in col.all_objects:
            if obj.hide_render:
                continue
            if obj.type == "MESH":
                pts.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
            elif obj.type == "CURVE":
                # A curve's bound_box includes its Bezier handles, which sit far
                # outside the visible wire. Use the evaluated (bevelled) mesh.
                ev = obj.evaluated_get(depsgraph)
                mesh = ev.to_mesh()
                verts = list(mesh.vertices)
                pts.extend(obj.matrix_world @ v.co for v in verts[::8])
                ev.to_mesh_clear()
    return pts


def _project_box(scene, cam, pts):
    w, h = EPISODE["video"]["width"], EPISODE["video"]["height"]
    xs, ys = [], []
    for p in pts:
        co = world_to_camera_view(scene, cam, p)
        xs.append(co.x * w)
        ys.append((1 - co.y) * h)
    return min(xs), max(xs), min(ys), max(ys)


def fit_view(scene, cam, target, azimuth, elevation, band_y, band_x=(90, 990), pts=None):
    """Find camera distance + target so the hardware fills a screen band.

    band_y / band_x are pixel ranges in the 1080x1920 frame. The hardware is
    scaled to fit inside the band (whichever axis is tighter) and centred in
    it. Returns (target, distance), ready for orbit_position().
    """
    pts = pts or hardware_points()
    target = Vector(target)
    h = EPISODE["video"]["height"]

    def place(t, d):
        cam.location = orbit_position(t, d, azimuth, elevation)
        aim(cam, t)
        bpy.context.view_layer.update()
        return _project_box(scene, cam, pts)

    dist = mm(250.0)
    for _ in range(4):
        lo, hi = mm(40.0), mm(2000.0)
        for _ in range(40):  # larger distance -> smaller on screen
            dist = (lo + hi) / 2
            x0, x1, y0, y1 = place(target, dist)
            fits = (y1 - y0) <= (band_y[1] - band_y[0]) and (x1 - x0) <= (band_x[1] - band_x[0])
            hi, lo = (dist, lo) if fits else (hi, dist)
        dist = hi
        x0, x1, y0, y1 = place(target, dist)
        # Shift the target along the camera's up/right axes to centre the box.
        frame_h = 2 * dist * math.tan(cam.data.angle_y / 2)
        px = frame_h / h
        up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
        right = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
        dy = ((y0 + y1) / 2 - (band_y[0] + band_y[1]) / 2) * px
        dx = ((x0 + x1) / 2 - (band_x[0] + band_x[1]) / 2) * px
        target = target - up * dy + right * dx
    return target, dist


def key_camera(cam, frame, position, target, lens=None, focus=None):
    cam.location = position
    aim(cam, target)
    cam.keyframe_insert("location", frame=frame)
    cam.keyframe_insert("rotation_euler", frame=frame)
    if lens is not None:
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=frame)
    cam.data.dof.focus_distance = (Vector(position) - Vector(focus or target)).length
    cam.data.dof.keyframe_insert("focus_distance", frame=frame)


def key_object(obj, frame, location=None, rotation=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert("rotation_euler", frame=frame)


# ------------------------------------------------------------------ output
def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = {"preview": "--preview" in argv, "still": None, "no_render": "--no-render" in argv}
    if "--still" in argv:
        opts["still"] = int(argv[argv.index("--still") + 1])
    return opts


def finish(scene, folder, preview, still=None, no_render=False):
    """Save the .blend, then render PNG frames (or one still)."""
    out_dir = ROOT / "output" / "scenes" / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    blend_dir = ROOT / "output" / "blend"
    blend_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_dir / f"{folder}.blend"))
    if no_render:
        return
    if still is not None:
        scene.frame_set(still)
        scene.render.filepath = str(ROOT / "output" / "previews" / f"{folder}-f{still:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"STILL {scene.render.filepath}")
        return
    scene.render.filepath = str(out_dir / "####")
    bpy.ops.render.render(animation=True)
    print(f"RENDERED {folder}: frames {scene.frame_start}-{scene.frame_end} -> {out_dir}")
