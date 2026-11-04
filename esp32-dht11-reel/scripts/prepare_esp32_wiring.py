"""Add persistent wiring connection markers to the existing ESP32-S3 project.

Run from the workspace with:
    blender -b output/esp32_s3.blend --python scripts/prepare_esp32_wiring.py

The approved source project is only read. The marked scene is saved to a new
project and rendered with a close-up camera aimed at the header-pin tails.
"""

import importlib.util
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PROJECT = ROOT / "output" / "esp32_s3.blend"
OUTPUT_PROJECT = ROOT / "output" / "esp32_s3_wiring.blend"
OUTPUT_RENDER = ROOT / "output" / "esp32_s3_connections_preview.png"
MODEL_SCRIPT = ROOT / "blender" / "models" / "esp32_s3.py"
BOARD_COLLECTIONS = (
    "01 | PCB",
    "02 | ESP32-S3-WROOM-1",
    "03 | Components",
    "04 | USB-C",
    "05 | GPIO headers",
    "06 | Silkscreen",
)


def load_board_definition():
    spec = importlib.util.spec_from_file_location("esp32_s3_definition", MODEL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load board definition: {MODEL_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_pin_tail(root, side, index, definition):
    config = definition.CONFIG
    expected_x = side * config["row_spacing"] / 2
    expected_y = definition.pin_y(index)
    root_inverse = root.matrix_world.inverted()
    matches = []

    for obj in bpy.data.objects:
        if not obj.name.startswith("Pin tail") or obj.parent != root:
            continue
        local_center = root_inverse @ obj.matrix_world.translation
        if (abs(local_center.x - expected_x) < 1e-5
                and abs(local_center.y - expected_y) < 1e-5):
            matches.append(obj)

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one modeled pin tail at ({expected_x}, {expected_y}); "
            f"found {len(matches)}"
        )

    tail = matches[0]
    local_tip_z = min(vertex.co.z for vertex in tail.data.vertices) + tail.location.z
    point = root.matrix_world @ Vector((tail.location.x, tail.location.y, local_tip_z))
    return point


def make_emissive_material(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 0.22
    shader.inputs["Roughness"].default_value = 0.24
    emission_color = shader.inputs.get("Emission Color") or shader.inputs.get("Emission")
    if emission_color:
        emission_color.default_value = color
    emission_strength = shader.inputs.get("Emission Strength")
    if emission_strength:
        emission_strength.default_value = 2.0
    return material


def parent_to_root(obj, root, local_mm):
    obj.parent = root
    obj.location = local_mm
    return obj


def add_marker(name, label, local_mm, color, root, collection, label_rotation):
    locator = bpy.data.objects.new(name, None)
    collection.objects.link(locator)
    parent_to_root(locator, root, local_mm)
    locator.empty_display_type = "SPHERE"
    locator.empty_display_size = 1.8
    locator.color = color

    bpy.ops.mesh.primitive_torus_add(
        major_segments=48,
        minor_segments=12,
        location=(0, 0, 0),
        major_radius=1.25,
        minor_radius=0.20,
    )
    ring = bpy.context.object
    ring.name = f"Render marker | {label}"
    ring.data.materials.append(make_emissive_material(f"Marker | {label}", color))
    for existing in list(ring.users_collection):
        if existing != collection:
            existing.objects.unlink(ring)
    if collection not in ring.users_collection:
        collection.objects.link(ring)
    ring.parent = locator
    ring.location = (0, 0, 0)

    text_curve = bpy.data.curves.new(f"Marker label | {label}", "FONT")
    text_curve.body = label
    text_curve.size = 2.15
    text_curve.align_x = "CENTER"
    text_curve.align_y = "CENTER"
    text_curve.extrude = 0.025
    text = bpy.data.objects.new(f"Marker label | {label}", text_curve)
    collection.objects.link(text)
    parent_to_root(text, root, local_mm)
    text.location.x += 5.0 if local_mm[0] < 0 else -5.0
    text.location.y += 2.2 if label != "GPIO4" else -2.2
    text.location.z -= 0.8
    text.rotation_euler = label_rotation
    text.data.materials.append(ring.data.materials[0])
    return locator


def add_preview_light(name, location, energy, size, target, collection):
    light_data = bpy.data.lights.new(name, type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new(name, light_data)
    collection.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector(target) - light.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE_PROJECT.resolve():
        raise RuntimeError(
            "Open the approved source project before running this script: "
            f"{SOURCE_PROJECT}"
        )
    if OUTPUT_PROJECT.resolve() == SOURCE_PROJECT.resolve():
        raise RuntimeError("The wiring project must not overwrite the source project")

    definition = load_board_definition()
    root = bpy.data.objects.get("ESP32-S3-DevKitC-1 (mm)")
    if root is None:
        raise RuntimeError("The expected ESP32-S3 model root is missing")

    board_collection = bpy.data.collections.new("ESP32_S3")
    bpy.context.scene.collection.children.link(board_collection)
    for name in BOARD_COLLECTIONS:
        collection = bpy.data.collections.get(name)
        if collection is None:
            raise RuntimeError(f"Expected board collection is missing: {name}")
        board_collection.children.link(collection)
        bpy.context.scene.collection.children.unlink(collection)
    for collection in list(root.users_collection):
        collection.objects.unlink(root)
    board_collection.objects.link(root)

    connection_collection = bpy.data.collections.new("Connection Points")
    board_collection.children.link(connection_collection)

    j1_gpio4 = definition.J1_LEFT.index("4")
    j1_3v3 = definition.J1_LEFT.index("3V3")
    j3_gnd = definition.J3_RIGHT.index("GND")
    pin_specs = (
        ("CONNECT_ESP32_GPIO4", "GPIO4", -1, j1_gpio4, (0.12, 0.83, 1.0, 1.0)),
        ("CONNECT_ESP32_3V3", "3V3", -1, j1_3v3, (1.0, 0.69, 0.16, 1.0)),
        ("CONNECT_ESP32_GND", "GND", 1, j3_gnd, (0.89, 0.34, 0.96, 1.0)),
    )
    marker_data = []
    for name, label, side, index, color in pin_specs:
        names = definition.J1_LEFT if side < 0 else definition.J3_RIGHT
        if names[index] != ("4" if label == "GPIO4" else label):
            raise RuntimeError(f"Pinout mismatch while resolving {label}")
        point = find_pin_tail(root, side, index, definition)
        local_point = root.matrix_world.inverted() @ point
        marker_data.append((name, label, point, local_point, color))

    camera_data = bpy.data.cameras.new("Wiring connection close-up")
    camera = bpy.data.objects.new("Wiring connection close-up", camera_data)
    scene = bpy.context.scene
    scene.collection.objects.link(camera)

    marker_center = Vector((0, 23.03 * definition.MM, -0.02))
    camera.location = (marker_center.x, marker_center.y, -4.5)
    camera.rotation_euler = (marker_center - camera.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 2.0
    camera_data.dof.use_dof = False

    camera_rotation = camera.rotation_euler.copy()
    marker_objects = []
    for name, label, point, local_point, color in marker_data:
        marker_local = tuple(local_point)
        marker_objects.append(add_marker(
            name, label, marker_local, color, root, connection_collection,
            camera_rotation,
        ))

    floor = bpy.data.objects.get("Studio floor")
    if floor is not None:
        floor.location.z -= 0.12
        floor.hide_render = True

    studio = bpy.data.collections.get("07 | Studio")
    if studio is None:
        raise RuntimeError("The original studio collection is missing")
    for light_args in (
        ("Connection underside key", (-1.5, 1.8, -1.5), 110, 2.2),
        ("Connection underside fill", (1.5, 0.5, -1.7), 85, 2.0),
        ("Connection underside rim", (0.0, 2.5, -1.0), 55, 1.8),
    ):
        name, location, energy, size = light_args
        add_preview_light(
            name, location, energy, size, (0, 0.92, -0.02), studio
        )

    scene.camera = camera
    scene.render.filepath = str(OUTPUT_RENDER)
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100

    OUTPUT_PROJECT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_PROJECT))
    bpy.ops.render.render(write_still=True)

    for obj, (_, label, point, _, _) in zip(marker_objects, marker_data):
        world_position = tuple(round(component, 6) for component in obj.matrix_world.translation)
        print(f"CONNECTION {label}: {world_position}")
    print(f"SOURCE PROJECT (unchanged): {SOURCE_PROJECT}")
    print(f"WIRING PROJECT: {OUTPUT_PROJECT}")
    print(f"PREVIEW: {OUTPUT_RENDER}")


if __name__ == "__main__":
    main()
