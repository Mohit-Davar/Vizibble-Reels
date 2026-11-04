"""Procedural model of the 7Semi ESP32-S3-DevKitC-1-N8R2 development board.

Run with Blender in background mode:
    blender -b --python blender/models/esp32_s3.py

All board geometry is authored in millimetres and parented to one root empty
scaled by MM, so the camera, lights and render settings stay in the original
scene units. Dimensions follow Espressif's ESP32-S3-DevKitC-1 reference design
and standard part packages. Values marked VERIFY should be checked against the
actual 7Semi board (calipers or close-up photos) before the final render.
"""

import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"

MM = 0.04  # scene units per millimetre (board is ~2.76 units long)


CONFIG = {
    # Board outline (mm)
    "board_length": 69.0,  # VERIFY with calipers
    "board_width": 25.4,  # VERIFY
    "board_thickness": 1.6,
    "corner_radius": 1.0,
    # 2 x 22 male headers, 2.54 mm pitch, rows 0.9" apart
    "pins_per_row": 22,
    "pin_pitch": 2.54,
    "row_spacing": 22.86,
    "pin22_from_usb_edge": 8.0,  # VERIFY: centre of pin 22 (5V / GND end) to USB edge
    "header_installed": True,  # pins point down, black housing under the board
    "housing_height": 2.5,
    "pin_below_housing": 6.0,
    "pin_labels": True,
    # ESP32-S3-WROOM-1-N8R2 module: 18 x 25.5 x 3.1 mm
    "module_size": (18.0, 25.5, 3.1),
    "shield_size": (15.8, 17.6),
    "module_overhang": 0.0,  # VERIFY: antenna flush with the board end
    "module_variant_mark": "N8R2",
    # USB-C receptacles (one native USB, one through the USB-UART bridge)
    "usb_size": (8.94, 7.35, 3.26),  # width, depth, height
    "usb_center_x": 5.4,
    "usb_overhang": 0.6,
    "usb_labels": ("UART", "USB"),  # VERIFY order (left, right), USB end toward viewer
    "button_size": (4.2, 3.2, 1.4),
    "button_labels": ("BOOT", "RST"),  # VERIFY sides (left, right)
    # Addressable RGB LED: GPIO48 on DevKitC-1 v1.0, GPIO38 on v1.1
    "rgb_led_gpio": 48,  # VERIFY against the 7Semi listing
    "rgb_led_color": (0.10, 0.35, 1.0, 1.0),
    "rgb_led_strength": 6.0,
    "power_led_on": True,
    "brand_text": "7Semi",
    "board_title": "ESP32-S3-DevKitC-1",
    "render_samples": 64,
}


# Reference-design pinout, top view, USB connectors at the bottom.
# Index 0 is pin 1, at the antenna end.
J1_LEFT = [
    "3V3",
    "3V3",
    "RST",
    "4",
    "5",
    "6",
    "7",
    "15",
    "16",
    "17",
    "18",
    "8",
    "3",
    "46",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "5V",
    "GND",
]
J3_RIGHT = [
    "GND",
    "TX",
    "RX",
    "1",
    "2",
    "42",
    "41",
    "40",
    "39",
    "38",
    "37",
    "36",
    "35",
    "0",
    "45",
    "48",
    "47",
    "21",
    "20",
    "19",
    "GND",
    "GND",
]
# TX/RX are GPIO43/GPIO44 (UART0).


PALETTE = {
    "pcb": (0.012, 0.024, 0.034, 1.0),
    "soldermask": (0.018, 0.033, 0.044, 1.0),
    "silkscreen": (0.88, 0.91, 0.86, 1.0),
    "metal": (0.56, 0.63, 0.68, 1.0),
    "metal_dark": (0.19, 0.24, 0.28, 1.0),
    "solder": (0.70, 0.72, 0.74, 1.0),
    "gold": (0.72, 0.43, 0.12, 1.0),
    "black": (0.012, 0.016, 0.019, 1.0),
    "chip": (0.035, 0.043, 0.048, 1.0),
    "ceramic": (0.73, 0.69, 0.57, 1.0),
    "plastic_white": (0.85, 0.85, 0.82, 1.0),
    "module_pcb": (0.020, 0.030, 0.035, 1.0),
    "antenna_trace": (0.050, 0.075, 0.085, 1.0),
    "laser_mark": (0.30, 0.33, 0.35, 1.0),
}


# ---------------------------------------------------------------- helpers


def make_material(name, color, metallic=0.0, roughness=0.35, emission=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        emission_color = shader.inputs.get("Emission Color") or shader.inputs.get(
            "Emission"
        )
        if emission_color:
            emission_color.default_value = color
        strength = shader.inputs.get("Emission Strength")
        if strength:
            strength.default_value = emission
    return material


def build_materials():
    metallic = {"metal": 0.9, "gold": 0.85, "solder": 0.9, "metal_dark": 0.6}
    roughness = {
        "metal": 0.28,
        "gold": 0.25,
        "solder": 0.2,
        "laser_mark": 0.65,
        "silkscreen": 0.6,
    }
    mats = {
        key: make_material(
            key.replace("_", " ").title(),
            color,
            metallic=metallic.get(key, 0.0),
            roughness=roughness.get(key, 0.4),
        )
        for key, color in PALETTE.items()
    }
    mats["led_red"] = make_material(
        "Power LED",
        (1.0, 0.05, 0.02, 1.0),
        roughness=0.2,
        emission=3.0 if CONFIG["power_led_on"] else 0.0,
    )
    mats["rgb_led"] = make_material(
        "RGB LED",
        CONFIG["rgb_led_color"],
        roughness=0.15,
        emission=CONFIG["rgb_led_strength"],
    )
    return mats


def make_collection(name, parent):
    collection = bpy.data.collections.new(name)
    parent.children.link(collection)
    return collection


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def smooth(obj):
    if hasattr(bpy.ops.object, "shade_smooth_by_angle"):
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
            return
        except (RuntimeError, TypeError):
            pass
    bpy.ops.object.shade_smooth()
    if hasattr(obj.data, "use_auto_smooth"):
        obj.data.use_auto_smooth = True


def add_box(name, location, dimensions, material, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel:
        modifier = obj.modifiers.new("Soft edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return move_to_collection(obj, collection)


def add_cylinder(name, location, radius, depth, material, collection, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    smooth(obj)
    return move_to_collection(obj, collection)


def add_cone(name, location, r1, r2, depth, material, collection, vertices=20):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    smooth(obj)
    return move_to_collection(obj, collection)


def rounded_rect_points(width, length, radius, segments=8):
    radius = min(radius, width / 2 - 1e-4, length / 2 - 1e-4)
    corners = (
        (width / 2 - radius, length / 2 - radius, 0),
        (-width / 2 + radius, length / 2 - radius, 90),
        (-width / 2 + radius, -length / 2 + radius, 180),
        (width / 2 - radius, -length / 2 + radius, 270),
    )
    points = []
    for cx, cy, start in corners:
        for k in range(segments + 1):
            angle = math.radians(start + 90 * k / segments)
            points.append(
                (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
            )
    return points


def add_slab(
    name,
    width,
    length,
    thickness,
    radius,
    location,
    material,
    collection,
    rotation=None,
    edge_bevel=0.0,
):
    """Rounded-rectangle outline extruded along local Z (crisp faces)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [
        bm.verts.new((x, y, -thickness / 2))
        for x, y in rounded_rect_points(width, length, radius)
    ]
    face = bm.faces.new(verts)
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    top_verts = [g for g in extruded["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top_verts, vec=(0, 0, thickness))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    if rotation:
        obj.rotation_euler = rotation
    mesh.materials.append(material)
    if edge_bevel:
        modifier = obj.modifiers.new("Edge highlight", "BEVEL")
        modifier.width = edge_bevel
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
    return obj


def add_text(
    name, body, location, size, material, collection, rotation=None, align_x="LEFT"
):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align_x
    curve.align_y = "CENTER"
    curve.extrude = 0.015
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    if rotation:
        obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj


# ------------------------------------------------------------- geometry


def board_top():
    return CONFIG["board_thickness"] / 2


def module_bottom_y():
    return (
        CONFIG["board_length"] / 2
        + CONFIG["module_overhang"]
        - CONFIG["module_size"][1]
    )


def pin_y(index):
    first_from_usb = -CONFIG["board_length"] / 2 + CONFIG["pin22_from_usb_edge"]
    return first_from_usb + (CONFIG["pins_per_row"] - 1 - index) * CONFIG["pin_pitch"]


def build_pcb(mats, cols):
    length, width, thickness = (
        CONFIG["board_length"],
        CONFIG["board_width"],
        CONFIG["board_thickness"],
    )
    add_slab(
        "7Semi PCB",
        width,
        length,
        thickness,
        CONFIG["corner_radius"],
        (0, 0, 0),
        mats["pcb"],
        cols["board"],
        edge_bevel=0.12,
    )
    add_slab(
        "Solder mask face",
        width - 0.3,
        length - 0.3,
        0.02,
        CONFIG["corner_radius"] - 0.15,
        (0, 0, board_top() + 0.01),
        mats["soldermask"],
        cols["board"],
    )


def add_pin_label(label, x, y, side, mats, cols):
    z = board_top() + 0.03
    if y > module_bottom_y() - 0.8:
        # Beside the module there is only a narrow strip between pads and module,
        # so these labels run along the board.
        label_x = side * (CONFIG["module_size"][0] / 2 + 0.8)
        add_text(
            "Pin label " + label,
            label,
            (label_x, y, z),
            0.75,
            mats["silkscreen"],
            cols["labels"],
            rotation=(0, 0, math.pi / 2),
            align_x="CENTER",
        )
    else:
        add_text(
            "Pin label " + label,
            label,
            (x - side * 1.45, y, z),
            1.0,
            mats["silkscreen"],
            cols["labels"],
            align_x="LEFT" if side < 0 else "RIGHT",
        )


def build_headers(mats, cols):
    top, bottom = board_top(), -board_top()
    count = CONFIG["pins_per_row"]
    for side, names in ((-1, J1_LEFT), (1, J3_RIGHT)):
        x = side * CONFIG["row_spacing"] / 2
        for index, label in enumerate(names):
            y = pin_y(index)
            if index == 0:  # square pad marks pin 1
                add_box(
                    "Pad pin 1",
                    (x, y, top + 0.02),
                    (1.7, 1.7, 0.04),
                    mats["solder"],
                    cols["headers"],
                    bevel=0.05,
                )
            else:
                add_cylinder(
                    "Pad",
                    (x, y, top + 0.02),
                    0.85,
                    0.04,
                    mats["solder"],
                    cols["headers"],
                )
            if CONFIG["header_installed"]:
                add_cone(
                    "Solder fillet",
                    (x, y, top + 0.34),
                    0.8,
                    0.36,
                    0.6,
                    mats["solder"],
                    cols["headers"],
                )
                add_box(
                    "Pin stub",
                    (x, y, top + 0.7),
                    (0.64, 0.64, 1.4),
                    mats["metal"],
                    cols["headers"],
                    bevel=0.08,
                )
                tail = CONFIG["housing_height"] + CONFIG["pin_below_housing"]
                add_box(
                    "Pin tail",
                    (x, y, bottom - tail / 2),
                    (0.64, 0.64, tail),
                    mats["gold"],
                    cols["headers"],
                    bevel=0.08,
                )
            if CONFIG["pin_labels"]:
                add_pin_label(label, x, y, side, mats, cols)
        if CONFIG["header_installed"]:
            y_mid = (pin_y(0) + pin_y(count - 1)) / 2
            add_box(
                "Header housing",
                (x, y_mid, bottom - CONFIG["housing_height"] / 2),
                (2.5, count * CONFIG["pin_pitch"], CONFIG["housing_height"]),
                mats["black"],
                cols["headers"],
                bevel=0.15,
            )


def build_module(mats, cols):
    top = board_top()
    width, length, height = CONFIG["module_size"]
    y0 = module_bottom_y()
    pcb_t = 0.8
    col = cols["module"]

    add_box(
        "WROOM-1 PCB",
        (0, y0 + length / 2, top + pcb_t / 2),
        (width, length, pcb_t),
        mats["module_pcb"],
        col,
        bevel=0.1,
    )

    shield_w, shield_l = CONFIG["shield_size"]
    shield_h = height - pcb_t
    shield_y = y0 + 0.9 + shield_l / 2
    add_box(
        "RF shield",
        (0, shield_y, top + pcb_t + shield_h / 2),
        (shield_w, shield_l, shield_h),
        mats["metal"],
        col,
        bevel=0.25,
    )

    # Castellated pads: 14 per long side, 12 along the end facing the USB ports.
    for side in (-1, 1):
        for k in range(14):
            y = y0 + 1.5 + k * 1.27
            add_box(
                "Castellation",
                (side * (width / 2 - 0.2), y, top + pcb_t / 2),
                (0.5, 0.9, pcb_t + 0.02),
                mats["gold"],
                col,
            )
            add_box(
                "Module joint",
                (side * (width / 2 + 0.15), y, top + 0.12),
                (0.5, 0.8, 0.24),
                mats["solder"],
                col,
                bevel=0.1,
            )
    for k in range(12):
        x = (k - 5.5) * 1.27
        add_box(
            "Castellation",
            (x, y0 + 0.2, top + pcb_t / 2),
            (0.9, 0.5, pcb_t + 0.02),
            mats["gold"],
            col,
        )
        add_box(
            "Module joint",
            (x, y0 - 0.15, top + 0.12),
            (0.8, 0.5, 0.24),
            mats["solder"],
            col,
            bevel=0.1,
        )

    # PCB meander antenna under the solder mask.
    z = top + pcb_t + 0.01
    ay0, ay1 = y0 + 0.9 + shield_l + 0.8, y0 + length - 0.8
    trace = 0.35
    xs = [-6.0 + 1.5 * k for k in range(9)]
    for k, x in enumerate(xs):
        add_box(
            "Antenna trace",
            (x, (ay0 + ay1) / 2, z),
            (trace, ay1 - ay0, 0.02),
            mats["antenna_trace"],
            col,
        )
        if k < len(xs) - 1:
            y = ay1 if k % 2 == 0 else ay0
            add_box(
                "Antenna trace",
                (x + 0.75, y, z),
                (1.5 + trace, trace, 0.02),
                mats["antenna_trace"],
                col,
            )
    add_box(
        "Antenna feed",
        (xs[0], ay0 - 0.4, z),
        (trace, 0.8, 0.02),
        mats["antenna_trace"],
        col,
    )

    # Laser marking on the shield.
    mark_z = top + height + 0.01
    for text, dy, size in (
        ("ESPRESSIF", 4.5, 1.6),
        ("ESP32-S3-WROOM-1", 1.5, 1.25),
        (CONFIG["module_variant_mark"], -1.0, 1.25),
    ):
        add_text(
            "Shield marking " + text,
            text,
            (0, shield_y + dy, mark_z),
            size,
            mats["laser_mark"],
            cols["labels"],
            align_x="CENTER",
        )


def add_usb_c(name, x, mats, col):
    width, depth, height = CONFIG["usb_size"]
    top = board_top()
    yc = -CONFIG["board_length"] / 2 - CONFIG["usb_overhang"] + depth / 2
    zc = top + height / 2
    front = yc - depth / 2
    upright = (math.pi / 2, 0, 0)  # outline in XZ, extruded along Y
    add_slab(
        name + " shell",
        width,
        height,
        depth,
        height / 2 - 0.05,
        (x, yc, zc),
        mats["metal"],
        col,
        rotation=upright,
        edge_bevel=0.08,
    )
    add_slab(
        name + " opening",
        width - 0.7,
        height - 0.7,
        0.1,
        (height - 0.7) / 2 - 0.05,
        (x, front - 0.02, zc),
        mats["black"],
        col,
        rotation=upright,
    )
    add_box(
        name + " tongue",
        (x, front - 0.09, zc),
        (5.6, 0.08, 0.7),
        mats["metal_dark"],
        col,
    )
    for k in range(12):
        add_box(
            name + " contact",
            (x + (k - 5.5) * 0.45, front - 0.14, zc + 0.2),
            (0.22, 0.03, 0.18),
            mats["gold"],
            col,
        )
    for side in (-1, 1):
        add_box(
            name + " shell tab",
            (x + side * (width / 2 + 0.25), yc + 1.0, top + 0.4),
            (0.5, 1.4, 0.8),
            mats["solder"],
            col,
            bevel=0.1,
        )
    label_y = front + depth + 1.0
    return label_y


def add_button(name, label, x, y, mats, cols):
    top = board_top()
    width, length, height = CONFIG["button_size"]
    col = cols["components"]
    add_box(
        name + " body",
        (x, y, top + height / 2),
        (width, length, height),
        mats["black"],
        col,
        bevel=0.15,
    )
    add_box(
        name + " frame",
        (x, y, top + height + 0.05),
        (width * 0.92, length * 0.92, 0.1),
        mats["metal"],
        col,
        bevel=0.05,
    )
    add_cylinder(
        name + " actuator",
        (x, y, top + height + 0.35),
        min(width, length) * 0.28,
        0.5,
        mats["black"],
        col,
    )
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(
                name + " lead",
                (x + sx * (width / 2 + 0.3), y + sy * (length / 2 - 0.5), top + 0.1),
                (0.6, 0.6, 0.2),
                mats["solder"],
                col,
            )
    add_text(
        label + " marking",
        label,
        (x, y + length / 2 + 1.3, top + 0.03),
        1.0,
        mats["silkscreen"],
        cols["labels"],
        align_x="CENTER",
    )


def add_chip_2term(name, x, y, width, length, height, body, mats, col):
    """0402/0603/0805-style two-terminal part, terminals at the X ends."""
    top = board_top()
    add_box(
        name + " body",
        (x, y, top + height / 2),
        (width, length, height),
        mats[body],
        col,
        bevel=min(width, length, height) * 0.12,
    )
    for sign in (-1, 1):
        add_box(
            name + " terminal",
            (x + sign * (width / 2 - width * 0.12), y, top + height / 2),
            (width * 0.25, length * 1.02, height * 1.02),
            mats["solder"],
            col,
        )


def add_qfn(name, x, y, size, height, mats, col):
    top = board_top()
    add_box(
        name,
        (x, y, top + height / 2),
        (size, size, height),
        mats["chip"],
        col,
        bevel=0.05,
    )
    pads = 6
    for k in range(pads):
        offset = (k - (pads - 1) / 2) * (size / (pads + 1))
        for dx, dy, dims in (
            (size / 2, offset, (0.25, 0.25, 0.08)),
            (-size / 2, offset, (0.25, 0.25, 0.08)),
            (offset, size / 2, (0.25, 0.25, 0.08)),
            (offset, -size / 2, (0.25, 0.25, 0.08)),
        ):
            add_box(
                name + " pad", (x + dx, y + dy, top + 0.04), dims, mats["solder"], col
            )
    add_cylinder(
        name + " pin1 dot",
        (x - size / 2 + 0.6, y + size / 2 - 0.6, top + height),
        0.18,
        0.02,
        mats["laser_mark"],
        col,
    )


def add_sot223(name, x, y, mats, col):
    top = board_top()
    add_box(
        name + " body", (x, y, top + 0.8), (6.5, 3.5, 1.6), mats["chip"], col, bevel=0.1
    )
    add_box(
        name + " tab", (x, y + 2.6, top + 0.12), (3.0, 1.8, 0.24), mats["solder"], col
    )
    for k in (-1, 0, 1):
        add_box(
            name + " lead",
            (x + k * 2.3, y - 2.4, top + 0.12),
            (0.7, 1.4, 0.24),
            mats["solder"],
            col,
        )


def build_components(mats, cols):
    col = cols["components"]
    top = board_top()
    length = CONFIG["board_length"]

    left_label, right_label = CONFIG["usb_labels"]
    cx = CONFIG["usb_center_x"]
    label_y = add_usb_c("USB-C left", -cx, mats, cols["connectors"])
    add_usb_c("USB-C right", cx, mats, cols["connectors"])
    for x, text in ((-cx, left_label), (cx, right_label)):
        add_text(
            "USB label " + text,
            text,
            (x, label_y, top + 0.03),
            1.0,
            mats["silkscreen"],
            cols["labels"],
            align_x="CENTER",
        )

    button_y = -length / 2 + 13.0
    boot, rst = CONFIG["button_labels"]
    add_button("Left button", boot, -7.0, button_y, mats, cols)
    add_button("Right button", rst, 7.0, button_y, mats, cols)

    add_qfn("USB-UART bridge", 2.0, -14.0, 4.0, 0.9, mats, col)  # VERIFY chip on 7Semi
    add_sot223("3V3 LDO", -3.5, -3.0, mats, col)
    add_box(
        "ESD diode body",
        (-1.5, -24.5, top + 0.55),
        (2.7, 1.6, 1.1),
        mats["chip"],
        col,
        bevel=0.1,
    )
    add_box(
        "ESD diode band",
        (-2.4, -24.5, top + 1.11),
        (0.35, 1.6, 0.02),
        mats["silkscreen"],
        col,
    )

    # RGB LED (WS2812-type, 3.5 x 3.5 mm) and red power LED. VERIFY positions.
    add_box(
        "RGB LED body",
        (5.5, 3.5, top + 0.45),
        (3.5, 3.5, 0.9),
        mats["plastic_white"],
        col,
        bevel=0.1,
    )
    add_cylinder(
        "RGB LED lens", (5.5, 3.5, top + 0.92), 1.2, 0.06, mats["rgb_led"], col
    )
    add_text(
        "RGB label",
        "RGB@IO{}".format(CONFIG["rgb_led_gpio"]),
        (5.5, 6.2, top + 0.03),
        0.8,
        mats["silkscreen"],
        cols["labels"],
        align_x="CENTER",
    )
    add_chip_2term("Power LED", -6.5, 3.5, 1.6, 0.8, 0.5, "plastic_white", mats, col)
    add_box(
        "Power LED glow",
        (-6.5, 3.5, top + 0.52),
        (0.9, 0.6, 0.04),
        mats["led_red"],
        col,
    )

    passives = (
        (-1.0, -9.0, "ceramic"),
        (4.5, -9.0, "chip"),
        (-5.0, -9.0, "ceramic"),
        (5.5, -17.0, "ceramic"),
        (-1.5, -17.5, "chip"),
        (6.5, -12.0, "ceramic"),
        (-6.0, -14.0, "ceramic"),
        (0.5, 0.5, "chip"),
        (-7.0, 0.0, "ceramic"),
        (7.0, 0.0, "ceramic"),
        (2.5, -19.5, "ceramic"),
        (-4.5, -19.5, "chip"),
    )
    for x, y, body in passives:
        add_chip_2term("Passive", x, y, 1.6, 0.8, 0.5, body, mats, col)

    add_text(
        "Board title",
        CONFIG["board_title"],
        (0, 7.2, top + 0.03),
        1.3,
        mats["silkscreen"],
        cols["labels"],
        align_x="CENTER",
    )
    add_text(
        "Brand",
        CONFIG["brand_text"],
        (3.5, -3.0, top + 0.03),
        2.0,
        mats["silkscreen"],
        cols["labels"],
        align_x="CENTER",
    )


def build_board(mats, root_collection):
    cols = {
        "board": make_collection("01 | PCB", root_collection),
        "module": make_collection("02 | ESP32-S3-WROOM-1", root_collection),
        "components": make_collection("03 | Components", root_collection),
        "connectors": make_collection("04 | USB-C", root_collection),
        "headers": make_collection("05 | GPIO headers", root_collection),
        "labels": make_collection("06 | Silkscreen", root_collection),
    }
    build_pcb(mats, cols)
    build_module(mats, cols)
    build_components(mats, cols)
    build_headers(mats, cols)

    root = bpy.data.objects.new("ESP32-S3-DevKitC-1 (mm)", None)
    root_collection.objects.link(root)
    root.scale = (MM, MM, MM)
    for collection in cols.values():
        for obj in collection.objects:
            obj.parent = root
    return root, cols


# ----------------------------------------------------------------- scene


def add_area_light(name, location, energy, size, target, collection):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (
        (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    )
    return obj


def set_eevee(scene):
    # 4.2-4.5 use BLENDER_EEVEE_NEXT; earlier and 5.x use BLENDER_EEVEE.
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            return
        except TypeError:
            continue


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)

    scene = bpy.context.scene
    root_collection = scene.collection
    mats = build_materials()
    build_board(mats, root_collection)

    # Floor touches the header pin tips (or the PCB underside without headers).
    lowest_mm = -board_top()
    if CONFIG["header_installed"]:
        lowest_mm -= CONFIG["housing_height"] + CONFIG["pin_below_housing"]
    stage = make_collection("07 | Studio", root_collection)
    floor_mat = make_material(
        "Studio midnight", (0.019, 0.032, 0.05, 1.0), roughness=0.52
    )
    add_box(
        "Studio floor",
        (0, 0, lowest_mm * MM - 0.04),
        (200, 200, 0.08),
        floor_mat,
        stage,
    )

    camera_data = bpy.data.cameras.new("Portrait product camera")
    camera = bpy.data.objects.new("Portrait product camera", camera_data)
    stage.objects.link(camera)
    camera.location = (3.0, -3.4, 5.2)
    target = Vector((0, 0, 0.02))
    camera.rotation_euler = (
        (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    )
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.55
    camera_data.dof.use_dof = True
    camera_data.dof.focus_distance = (camera.location - target).length
    camera_data.dof.aperture_fstop = 8.0
    scene.camera = camera

    add_area_light("Key softbox", (2.8, -2.0, 4.0), 520, 3.4, (0, 0, 0), stage)
    add_area_light("Cool fill", (-2.5, -0.2, 2.6), 300, 3.0, (0, 0, 0), stage)
    add_area_light("Warm rim", (0.3, 3.2, 3.0), 430, 2.5, (0, 0.3, 0), stage)

    world = (
        bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("Studio world")
    )
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.11, 0.14, 0.19, 1)
    background.inputs["Strength"].default_value = 0.35

    set_eevee(scene)
    scene.eevee.taa_render_samples = CONFIG["render_samples"]
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
    except TypeError:
        scene.view_settings.view_transform = "Filmic"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.filepath = str(OUTPUT / "esp32_s3_preview.png")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "esp32_s3.blend"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    build_scene()
