"""Procedural model of a common blue 3-pin DHT11 breakout module.

The layout is based on representative KY-015-style modules. Dimensions are
nominal visual dimensions, not a measured drawing of a particular supplier's
board. All object coordinates are in millimetres before the root scale is
applied (0.04 Blender units per millimetre, matching the ESP32-S3 model).

Run this file from Blender's Scripting workspace. It creates a collection
named ``DHT11`` with an independently movable root empty.
"""

import math
import bpy

MM = 0.04

CONFIG = {
    "dimensions_verified": False,
    # PCB: long axis is X, short axis is Y.
    "pcb_length": 28.0,
    "pcb_width": 12.6,
    "pcb_thickness": 1.6,
    "pcb_corner_radius": 0.45,
    # Blue DHT11 sensing package, mounted flat on the PCB.
    "sensor_length": 15.5,
    "sensor_width": 12.0,
    "sensor_height": 5.5,
    "sensor_center_x": -5.85,
    "sensor_center_y": 0.0,
    "sensor_base_gap": 0.08,
    "sensor_corner_bevel": 0.45,
    # Square ventilation grid on the top face of the blue package.
    "vent_columns": 5,
    "vent_rows": 4,
    "vent_border": 0.75,
    "vent_bar_width": 0.72,
    "vent_bar_height": 0.22,
    # Right-angle, three-pin header at the opposite short edge of the PCB.
    "connector_pin_order": ("VCC", "DATA", "GND"),
    "connector_pin_pitch": 2.54,
    "connector_pin_width": 0.65,
    "connector_pin_length": 7.7,
    # Typical visible board components.
    "resistor_positions": ((8.0, 4.55), (10.6, 4.55)),
    "led_position": (9.7, -4.1),
    "mounting_hole_position": (4.2, 0.0),
}


COLORS = {
    "blue_plastic": (0.025, 0.40, 0.82, 1.0),
    "blue_highlight": (0.075, 0.53, 0.96, 1.0),
    "grille_dark": (0.006, 0.018, 0.035, 1.0),
    "pcb_blue": (0.006, 0.16, 0.23, 1.0),
    "silkscreen": (0.88, 0.94, 0.91, 1.0),
    "metal": (0.66, 0.72, 0.77, 1.0),
    "gold": (0.72, 0.48, 0.20, 1.0),
    "black": (0.012, 0.018, 0.022, 1.0),
    "ceramic": (0.78, 0.76, 0.66, 1.0),
    "led": (0.9, 0.018, 0.012, 1.0),
}


def _material(name, color, metallic=0.0, roughness=0.36, coat=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness

    coat_weight = shader.inputs.get("Coat Weight")
    if coat_weight:
        coat_weight.default_value = coat
    coat_roughness = shader.inputs.get("Coat Roughness")
    if coat_roughness:
        coat_roughness.default_value = 0.22
    return material


def _make_materials():
    materials = {}
    for key, color in COLORS.items():
        materials[key] = _material(
            key.replace("_", " ").title(),
            color,
            metallic=0.72 if key in {"gold", "metal"} else 0.0,
            roughness=0.22 if key in {"blue_plastic", "led"} else 0.34,
            coat=0.28 if key == "blue_plastic" else 0.0,
        )
    return materials


def _move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def _add_box(name, location, dimensions, material, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)

    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")

    return _move_to_collection(obj, collection)


def _add_text(name, body, location, size, material, collection, rotation_z=0.0):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.008
    curve.bevel_depth = 0.002

    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler.z = rotation_z
    obj.data.materials.append(material)
    return obj


def _add_cylinder(name, location, radius, depth, material, collection):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=40,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Rounded rim", "BEVEL")
    bevel.width = min(0.04, depth * 0.2)
    bevel.segments = 2
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return _move_to_collection(obj, collection)


def _add_resistor(name, x, y, top_z, mats, collection, labels_collection):
    body_width = 2.0
    body_depth = 1.05
    body_height = 0.62

    _add_box(
        name,
        (x, y, top_z + body_height / 2),
        (body_width, body_depth, body_height),
        mats["ceramic"],
        collection,
        bevel=0.12,
    )

    for side in (-1, 1):
        _add_box(
            name + " metal end cap",
            (x + side * (body_width / 2 - 0.13), y, top_z + body_height / 2),
            (0.30, body_depth, body_height * 0.92),
            mats["metal"],
            collection,
            bevel=0.05,
        )

    _add_text(
        name + " 102 marking",
        "102",
        (x, y, top_z + body_height + 0.018),
        0.42,
        mats["black"],
        labels_collection,
    )


def _add_pin(name, x_start, y, z, mats, collection):
    """Create a horizontal right-angle header pin extending along +X."""
    length = CONFIG["connector_pin_length"]
    width = CONFIG["connector_pin_width"]
    pin = _add_box(
        name,
        (x_start + length / 2, y, z),
        (length, width, width),
        mats["metal"],
        collection,
        bevel=0.07,
    )
    return pin, x_start + length


def _build_sensor_housing(mats, collection):
    length = CONFIG["sensor_length"]
    width = CONFIG["sensor_width"]
    height = CONFIG["sensor_height"]
    center_x = CONFIG["sensor_center_x"]
    center_y = CONFIG["sensor_center_y"]

    pcb_top = CONFIG["pcb_thickness"] / 2
    base_z = pcb_top + CONFIG["sensor_base_gap"]
    top_z = base_z + height
    center_z = base_z + height / 2

    _add_box(
        "DHT11 light-blue sensor housing",
        (center_x, center_y, center_z),
        (length, width, height),
        mats["blue_plastic"],
        collection,
        bevel=CONFIG["sensor_corner_bevel"],
    )

    # A dark inset below the blue lattice gives the ventilation holes depth.
    border = CONFIG["vent_border"]
    inner_length = length - 2 * border
    inner_width = width - 2 * border
    panel_height = 0.12
    _add_box(
        "Dark recessed ventilation cavity",
        (center_x, center_y, top_z - 0.16),
        (inner_length, inner_width, panel_height),
        mats["grille_dark"],
        collection,
        bevel=0.06,
    )

    bar_width = CONFIG["vent_bar_width"]
    bar_height = CONFIG["vent_bar_height"]
    bar_z = top_z - bar_height / 2 + 0.015
    columns = CONFIG["vent_columns"]
    rows = CONFIG["vent_rows"]

    # Bars parallel to X divide the grille into rows.
    row_step = inner_width / rows
    for index in range(1, rows):
        y = center_y - inner_width / 2 + index * row_step
        _add_box(
            f"Vent grille horizontal rail {index:02d}",
            (center_x, y, bar_z),
            (inner_length, bar_width, bar_height),
            mats["blue_highlight"],
            collection,
            bevel=0.08,
        )

    # Bars parallel to Y divide the grille into columns.
    column_step = inner_length / columns
    for index in range(1, columns):
        x = center_x - inner_length / 2 + index * column_step
        _add_box(
            f"Vent grille vertical rail {index:02d}",
            (x, center_y, bar_z),
            (bar_width, inner_width, bar_height),
            mats["blue_highlight"],
            collection,
            bevel=0.08,
        )

    # The housing's solid perimeter remains visible as the outer grille frame.
    return base_z, top_z


def _build_pcb(mats, board_collection, component_collection, labels_collection):
    length = CONFIG["pcb_length"]
    width = CONFIG["pcb_width"]
    thickness = CONFIG["pcb_thickness"]
    bottom_z = -thickness / 2
    top_z = thickness / 2
    board_edge_x = length / 2

    _add_box(
        "Blue DHT11 breakout PCB",
        (0, 0, 0),
        (length, width, thickness),
        mats["pcb_blue"],
        board_collection,
        bevel=CONFIG["pcb_corner_radius"],
    )

    # Three right-angle pins emerge from the short end of the PCB.
    pin_tips = {}
    for index, pin_name in enumerate(CONFIG["connector_pin_order"]):
        y = (1 - index) * CONFIG["connector_pin_pitch"]
        _add_cylinder(
            f"{pin_name} solder pad",
            (board_edge_x - 0.35, y, top_z + 0.025),
            0.52,
            0.07,
            mats["gold"],
            board_collection,
        )
        _add_box(
            f"{pin_name} solder joint",
            (board_edge_x - 0.12, y, top_z + 0.05),
            (0.52, 0.78, 0.16),
            mats["metal"],
            board_collection,
            bevel=0.07,
        )
        _add_pin(
            f"DHT11 {pin_name} right-angle pin",
            board_edge_x,
            y,
            0.0,
            mats,
            board_collection,
        )
        pin_tips[pin_name] = (board_edge_x + CONFIG["connector_pin_length"], y, 0.0)

        _add_text(
            f"PCB pin label {pin_name}",
            pin_name,
            (12.15, y, top_z + 0.035),
            0.66,
            mats["silkscreen"],
            labels_collection,
            rotation_z=math.pi / 2,
        )

    # Circular mounting feature and white silkscreen ring.
    hole_x, hole_y = CONFIG["mounting_hole_position"]
    _add_cylinder(
        "Dark mounting hole insert",
        (hole_x, hole_y, top_z + 0.012),
        1.30,
        0.025,
        mats["black"],
        board_collection,
    )
    bpy.ops.mesh.primitive_torus_add(
        major_segments=48,
        minor_segments=12,
        location=(hole_x, hole_y, top_z + 0.055),
        major_radius=1.48,
        minor_radius=0.11,
    )
    ring = bpy.context.object
    ring.name = "Mounting hole white silkscreen ring"
    ring.data.materials.append(mats["silkscreen"])
    _move_to_collection(ring, labels_collection)

    # Two 102 surface-mount resistors near the header end of the board.
    for index, (x, y) in enumerate(CONFIG["resistor_positions"], start=1):
        _add_resistor(
            f"DHT11 pull-up resistor {index}",
            x,
            y,
            top_z + 0.035,
            mats,
            component_collection,
            labels_collection,
        )

    # Red power-indicator LED near the lower edge.
    led_x, led_y = CONFIG["led_position"]
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        radius=0.78,
        location=(led_x, led_y, top_z + 0.50),
    )
    led = bpy.context.object
    led.name = "Red power indicator LED"
    led.scale.z = 0.78
    led.data.materials.append(mats["led"])
    _move_to_collection(led, component_collection)

    _add_text(
        "Power LED silkscreen",
        "PWR",
        (led_x - 1.75, led_y, top_z + 0.035),
        0.58,
        mats["silkscreen"],
        labels_collection,
    )
    _add_text(
        "DHT11 module marking",
        "DHT11",
        (8.0, 0.0, top_z + 0.035),
        0.78,
        mats["silkscreen"],
        labels_collection,
    )

    # Small solder pads on the underside indicate the sensor's four leads.
    sensor_edge_x = CONFIG["sensor_center_x"] + CONFIG["sensor_length"] / 2 - 0.65
    for index, y in enumerate((-4.1, -1.35, 1.35, 4.1), start=1):
        _add_cylinder(
            f"Sensor lead solder pad {index}",
            (sensor_edge_x, y, bottom_z - 0.025),
            0.48,
            0.05,
            mats["gold"],
            board_collection,
        )

    return pin_tips


def build_module(scene_collection=None, location=(0.0, 0.0, 0.0)):
    """Create the DHT11 module collection and return (collection, root)."""
    scene_collection = scene_collection or bpy.context.scene.collection

    dht_collection = bpy.data.collections.new("DHT11")
    scene_collection.children.link(dht_collection)

    board_collection = bpy.data.collections.new("01 | DHT11 PCB")
    component_collection = bpy.data.collections.new("02 | DHT11 components")
    housing_collection = bpy.data.collections.new("03 | DHT11 blue housing")
    labels_collection = bpy.data.collections.new("04 | DHT11 silkscreen")
    connection_collection = bpy.data.collections.new("05 | Connection Points")

    for collection in (
        board_collection,
        component_collection,
        housing_collection,
        labels_collection,
        connection_collection,
    ):
        dht_collection.children.link(collection)

    root = bpy.data.objects.new("DHT11 | module root (mm)", None)
    dht_collection.objects.link(root)
    root.empty_display_type = "CUBE"
    root.empty_display_size = 3.0
    root.location = location
    root.scale = (MM, MM, MM)

    mats = _make_materials()
    pin_tips = _build_pcb(
        mats,
        board_collection,
        component_collection,
        labels_collection,
    )
    _build_sensor_housing(mats, housing_collection)

    for pin_name in CONFIG["connector_pin_order"]:
        locator = bpy.data.objects.new(f"CONNECT_DHT11_{pin_name}", None)
        connection_collection.objects.link(locator)
        locator.parent = root
        locator.location = pin_tips[pin_name]
        locator.empty_display_type = "SPHERE"
        locator.empty_display_size = 1.4
        locator.color = COLORS["gold"]

    # Parent all generated geometry to one root so the module moves as one part.
    for collection in (
        board_collection,
        component_collection,
        housing_collection,
        labels_collection,
    ):
        for obj in list(collection.objects):
            if obj.parent is None:
                obj.parent = root

    return dht_collection, root


if __name__ == "__main__":
    build_module()
