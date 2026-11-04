"""Add a reusable DHT11 module to a copy of the wiring-ready ESP32 project.

Run with:
    blender -b output/esp32_s3_wiring.blend --python scripts/add_dht11_module.py

The approved ESP32 source and wiring-ready project are read-only inputs.
"""

import importlib.util
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PROJECT = ROOT / "output" / "esp32_s3_wiring.blend"
OUTPUT_PROJECT = ROOT / "output" / "esp32_s3_dht11.blend"
MODEL_SCRIPT = ROOT / "blender" / "models" / "dht11.py"
STANDALONE_RENDER = ROOT / "output" / "dht11_module_preview.png"
INTEGRATED_RENDER = ROOT / "output" / "esp32_dht11_integrated_preview.png"
PORTRAIT_SIZE = (1080, 1920)
INTEGRATED_DHT_POSITION_MM = (32.0, 0.0, 0.0)


def load_model():
    spec = importlib.util.spec_from_file_location("dht11_model", MODEL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load DHT11 model: {MODEL_SCRIPT}")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def aim_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


def make_material(name, color, roughness=0.42):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return material


def add_area_light(name, location, energy, size, target, collection):
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


def build_preview_studio(scene):
    studio = bpy.data.collections.new("08 | DHT11 preview studio")
    scene.collection.children.link(studio)

    floor_material = make_material(
        "DHT11 studio midnight", (0.019, 0.032, 0.05, 1.0), roughness=0.48
    )
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.48))
    floor = bpy.context.object
    floor.name = "DHT11 standalone studio floor"
    floor.dimensions = (200, 200, 0.08)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    floor.data.materials.append(floor_material)
    for existing in list(floor.users_collection):
        existing.objects.unlink(floor)
    studio.objects.link(floor)

    add_area_light("DHT11 key softbox", (2.8, -2.0, 4.0), 360, 3.2,
                   (0.0, 0.0, 0.12), studio)
    add_area_light("DHT11 cool fill", (-2.5, -0.2, 2.8), 240, 2.8,
                   (0.0, 0.0, 0.12), studio)
    add_area_light("DHT11 warm rim", (0.4, 3.2, 3.0), 300, 2.4,
                   (0.0, 0.2, 0.18), studio)

    camera_data = bpy.data.cameras.new("DHT11 standalone camera")
    camera = bpy.data.objects.new("DHT11 standalone camera", camera_data)
    studio.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 1.9
    camera_data.dof.use_dof = False
    aim_camera(camera, (2.5, -4.4, 4.4), (0.0, 0.0, 0.11))
    return studio, floor, camera


def set_render(scene, filepath):
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 64
    scene.render.resolution_x, scene.render.resolution_y = PORTRAIT_SIZE
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.filepath = str(filepath)


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE_PROJECT.resolve():
        raise RuntimeError(
            "Open the wiring-ready source project before running this script: "
            f"{SOURCE_PROJECT}"
        )
    if OUTPUT_PROJECT.resolve() == SOURCE_PROJECT.resolve():
        raise RuntimeError("The new DHT11 project must not overwrite its source")
    if bpy.data.collections.get("ESP32_S3") is None:
        raise RuntimeError("The existing ESP32_S3 collection is missing")

    model = load_model()
    initial_location = tuple(value * model.MM for value in INTEGRATED_DHT_POSITION_MM)
    dht_collection, dht_root = model.build_module(location=initial_location)
    _, standalone_floor, standalone_camera = build_preview_studio(bpy.context.scene)
    scene = bpy.context.scene
    set_render(scene, STANDALONE_RENDER)

    board_collection = bpy.data.collections["ESP32_S3"]
    original_board_visibility = board_collection.hide_render
    try:
        board_collection.hide_render = True
        dht_root.location = (0.0, 0.0, 0.0)
        scene.camera = standalone_camera
        bpy.ops.render.render(write_still=True)
    finally:
        board_collection.hide_render = original_board_visibility
        dht_root.location = initial_location

    standalone_floor.hide_render = True
    integrated_camera_data = bpy.data.cameras.new("ESP32 + DHT11 portrait camera")
    integrated_camera = bpy.data.objects.new(
        "ESP32 + DHT11 portrait camera", integrated_camera_data
    )
    scene.collection.objects.link(integrated_camera)
    integrated_camera_data.type = "ORTHO"
    integrated_camera_data.ortho_scale = 5.3
    integrated_camera_data.dof.use_dof = False
    aim_camera(integrated_camera, (-3.7, -4.4, 6.2), (0.42, 0.0, 0.02))
    scene.camera = integrated_camera
    set_render(scene, INTEGRATED_RENDER)

    OUTPUT_PROJECT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_PROJECT))
    bpy.ops.render.render(write_still=True)

    for name in (
        "CONNECT_DHT11_VCC",
        "CONNECT_DHT11_DATA",
        "CONNECT_DHT11_GND",
    ):
        locator = bpy.data.objects[name]
        local = tuple(round(component, 5) for component in locator.location)
        world = tuple(
            round(component, 6)
            for component in locator.matrix_world.translation
        )
        print(f"CONNECTION {name}: local_mm={local}, world={world}")
    print(f"DHT11 DIMENSIONS (illustrative mm): {model.CONFIG}")
    print(f"DHT11 COLLECTION: {dht_collection.name}")
    print(f"NEW PROJECT: {OUTPUT_PROJECT}")
    print(f"STANDALONE PREVIEW: {STANDALONE_RENDER}")
    print(f"INTEGRATED PREVIEW: {INTEGRATED_RENDER}")


if __name__ == "__main__":
    main()
