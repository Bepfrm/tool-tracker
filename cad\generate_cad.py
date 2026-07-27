from pathlib import Path

import cadquery as cq


HERE = Path(__file__).resolve().parent
EXPORTS = HERE / "exports"
EXPORTS.mkdir(exist_ok=True)

TILE_WIDTH = 174.0
TILE_DEPTH = 60.0
TILE_BASE_HEIGHT = 16.0
TILE_PLATE_THICKNESS = 3.0
WALL = 2.4
FLOOR = 3.0
PITCH = 19.05

HUB_WIDTH = 84.0
HUB_DEPTH = 120.0
HUB_HEIGHT = 20.0
HUB_PLATE_THICKNESS = 3.0


def export_part(part, name):
    cq.exporters.export(part, str(EXPORTS / (name + ".step")))
    cq.exporters.export(part, str(EXPORTS / (name + ".stl")))


def screw_points(width, depth, inset=7.0):
    return [
        (-width / 2 + inset, -depth / 2 + inset),
        (width / 2 - inset, -depth / 2 + inset),
        (-width / 2 + inset, depth / 2 - inset),
        (width / 2 - inset, depth / 2 - inset),
    ]


def switch_points(columns, rows, pitch, y_offset=0):
    points = []
    x_start = -(columns - 1) * pitch / 2
    y_start = -(rows - 1) * pitch / 2 + y_offset

    for row in range(rows):
        for column in range(columns):
            points.append(
                (
                    x_start + column * pitch,
                    y_start + row * pitch,
                )
            )

    return points


def make_shell(width, depth, height, usb_slot=False):
    outer = cq.Workplane("XY").box(
        width, depth, height, centered=(True, True, False)
    )
    inner = (
        cq.Workplane("XY")
        .box(
            width - 2 * WALL,
            depth - 2 * WALL,
            height,
            centered=(True, True, False),
        )
        .translate((0, 0, FLOOR))
    )
    shell = outer.cut(inner)

    for x, y in screw_points(width, depth):
        post = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(3.2)
            .extrude(height - 1.0)
        )
        hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(1.45)
            .extrude(height + 2.0)
        )
        shell = shell.union(post).cut(hole)

    if usb_slot:
        slot = (
            cq.Workplane("XY")
            .box(16, WALL + 4, 9)
            .translate((0, -depth / 2, 8))
        )
        shell = shell.cut(slot)
    else:
        for x in (-width / 2, width / 2):
            slot = (
                cq.Workplane("XY")
                .box(WALL + 4, 13, 9)
                .translate((x, 0, 8))
            )
            shell = shell.cut(slot)

    return shell


def make_tile_base():
    base = make_shell(
        TILE_WIDTH,
        TILE_DEPTH,
        TILE_BASE_HEIGHT,
    )

    # Two small mounting pairs for a breakout or stripboard.
    for x in (-18, 18):
        for y in (-10, 10):
            post = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(2.6)
                .extrude(5.0)
            )
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(1.25)
                .extrude(7.0)
            )
            base = base.union(post).cut(hole)

    return base


def make_tile_plate(cutout):
    plate = cq.Workplane("XY").box(
        TILE_WIDTH,
        TILE_DEPTH,
        TILE_PLATE_THICKNESS,
        centered=(True, True, False),
    )
    points = switch_points(8, 2, PITCH)
    plate = (
        plate.faces(">Z")
        .workplane()
        .pushPoints(points)
        .rect(cutout, cutout)
        .cutThruAll()
    )
    relief = (
        cq.Workplane("XY")
        .pushPoints(points)
        .rect(18.0, 18.0)
        .extrude(1.5)
    )
    plate = plate.cut(relief)
    plate = (
        plate.faces(">Z")
        .workplane()
        .pushPoints(screw_points(TILE_WIDTH, TILE_DEPTH))
        .hole(3.4)
    )
    return plate


def make_switch_visual():
    switches = None

    for x, y in switch_points(8, 2, PITCH):
        body = (
            cq.Workplane("XY")
            .box(13.4, 13.4, 5.5, centered=(True, True, False))
            .translate((x, y, 0))
        )
        cap = (
            cq.Workplane("XY")
            .box(16.5, 16.5, 2.4, centered=(True, True, False))
            .translate((x, y, 5.5))
        )
        item = body.union(cap)
        switches = item if switches is None else switches.union(item)

    return switches


def make_hub_base():
    return make_shell(
        HUB_WIDTH,
        HUB_DEPTH,
        HUB_HEIGHT,
        usb_slot=True,
    )


def make_hub_plate():
    plate = cq.Workplane("XY").box(
        HUB_WIDTH,
        HUB_DEPTH,
        HUB_PLATE_THICKNESS,
        centered=(True, True, False),
    )

    keypad_points = switch_points(3, 4, PITCH, y_offset=-12)
    plate = (
        plate.faces(">Z")
        .workplane()
        .pushPoints(keypad_points)
        .rect(14.0, 14.0)
        .cutThruAll()
    )
    keypad_relief = (
        cq.Workplane("XY")
        .pushPoints(keypad_points)
        .rect(18.0, 18.0)
        .extrude(1.5)
    )
    plate = plate.cut(keypad_relief)

    display_cut = (
        cq.Workplane("XY")
        .center(0, 45)
        .rect(29, 16)
        .extrude(HUB_PLATE_THICKNESS + 2)
        .translate((0, 0, -1))
    )
    plate = plate.cut(display_cut)
    plate = (
        plate.faces(">Z")
        .workplane()
        .pushPoints(screw_points(HUB_WIDTH, HUB_DEPTH))
        .hole(3.4)
    )
    return plate


def make_keypad_visual():
    keys = None

    for x, y in switch_points(3, 4, PITCH, y_offset=-12):
        key = (
            cq.Workplane("XY")
            .box(16.5, 16.5, 7.0, centered=(True, True, False))
            .translate((x, y, 0))
        )
        keys = key if keys is None else keys.union(key)

    display = (
        cq.Workplane("XY")
        .box(29, 16, 2.0, centered=(True, True, False))
        .translate((0, 45, 0))
    )
    return keys, display


def make_tool_pad():
    pad = cq.Workplane("XY").box(
        18, 18, 4, centered=(True, True, False)
    )
    groove = (
        cq.Workplane("YZ")
        .circle(7)
        .extrude(22, both=True)
        .translate((0, 0, 8))
    )
    recess = (
        cq.Workplane("XY")
        .box(14.2, 14.2, 1.6, centered=(True, True, False))
        .translate((0, 0, -0.1))
    )
    return pad.cut(groove).cut(recess)


def main():
    tile_base = make_tile_base()
    tile_choc = make_tile_plate(13.8)
    tile_mx = make_tile_plate(14.0)
    tile_switches = make_switch_visual()
    hub_base = make_hub_base()
    hub_plate = make_hub_plate()
    keypad_keys, display = make_keypad_visual()
    tool_pad = make_tool_pad()

    export_part(tile_base, "tool_tile_base")
    export_part(tile_choc, "tool_tile_top_choc")
    export_part(tile_mx, "tool_tile_top_mx")
    export_part(hub_base, "keypad_hub_base")
    export_part(hub_plate, "keypad_hub_top")
    export_part(tool_pad, "universal_tool_pad")

    cq.exporters.export(
        tile_switches, str(EXPORTS / "preview_tile_switches.stl")
    )
    cq.exporters.export(
        keypad_keys, str(EXPORTS / "preview_keypad_keys.stl")
    )
    cq.exporters.export(
        display, str(EXPORTS / "preview_display.stl")
    )

    tile_assembly = cq.Assembly(name="tool_tile")
    tile_assembly.add(tile_base, name="base")
    tile_assembly.add(
        tile_choc.translate((0, 0, TILE_BASE_HEIGHT)),
        name="top_choc",
    )
    tile_assembly.add(
        tile_switches.translate(
            (0, 0, TILE_BASE_HEIGHT + TILE_PLATE_THICKNESS)
        ),
        name="switches",
    )
    tile_assembly.save(str(EXPORTS / "tool_tile_assembly.step"))

    hub_assembly = cq.Assembly(name="keypad_hub")
    hub_assembly.add(hub_base, name="base")
    hub_assembly.add(
        hub_plate.translate((0, 0, HUB_HEIGHT)),
        name="top",
    )
    hub_assembly.add(
        keypad_keys.translate(
            (0, 0, HUB_HEIGHT + HUB_PLATE_THICKNESS)
        ),
        name="keys",
    )
    hub_assembly.add(
        display.translate(
            (0, 0, HUB_HEIGHT + HUB_PLATE_THICKNESS)
        ),
        name="display",
    )
    hub_assembly.save(str(EXPORTS / "keypad_hub_assembly.step"))

    print("CAD exports written to", EXPORTS)


if __name__ == "__main__":
    main()
