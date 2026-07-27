from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "system-diagram.png"
WIDTH = 1600
HEIGHT = 900


def font(size, bold=False):
    name = "seguisb.ttf" if bold else "segoeui.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size)


def rounded(draw, box, fill, outline, radius=14, width=3):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def arrow(draw, start, end, fill, width=7):
    draw.line((start, end), fill=fill, width=width)
    x, y = end
    draw.polygon(
        ((x, y), (x - 18, y - 11), (x - 18, y + 11)),
        fill=fill,
    )


def label(draw, xy, text, size, color, bold=False, anchor="la"):
    draw.text(
        xy,
        text,
        font=font(size, bold),
        fill=color,
        anchor=anchor,
    )


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f2f3ef")
    draw = ImageDraw.Draw(image)

    label(
        draw,
        (80, 62),
        "TOOL TRACKER V2",
        44,
        "#171b1f",
        True,
    )
    label(
        draw,
        (80, 120),
        "32-slot grant build, expandable to 128 slots on one bus",
        25,
        "#4a5358",
    )

    hub = (80, 245, 430, 650)
    rounded(draw, hub, "#20272c", "#111518")
    label(draw, (115, 285), "PICO 2 W HUB", 29, "#ffffff", True)
    label(draw, (115, 345), "Wi-Fi + ntfy", 23, "#cdd4d6")
    label(draw, (115, 390), "Member sessions", 23, "#cdd4d6")
    label(draw, (115, 435), "Event log", 23, "#cdd4d6")
    label(draw, (115, 480), "100 kHz I2C", 23, "#cdd4d6")

    display = (115, 535, 260, 610)
    rounded(draw, display, "#0b453b", "#55c99b", radius=8, width=2)
    label(draw, (187, 557), "OLED", 21, "#ffffff", True, "ma")
    label(draw, (187, 588), "2 missing", 18, "#b8f5df", False, "ma")

    keypad = (285, 535, 395, 610)
    rounded(draw, keypad, "#e39a1f", "#9a6210", radius=8, width=2)
    label(draw, (340, 557), "KEYPAD", 19, "#1e2428", True, "ma")
    label(draw, (340, 588), "ID + #", 18, "#1e2428", False, "ma")

    bus_y = 447
    arrow(draw, (430, bus_y), (560, bus_y), "#cf8415")
    label(draw, (485, 420), "3V3  GND  SDA  SCL", 15, "#785015", True, "ma")

    tile1 = (560, 215, 970, 470)
    rounded(draw, tile1, "#ffffff", "#3d454a")
    label(draw, (595, 255), "MODULE 1  /  0x20", 26, "#1c2327", True)
    label(draw, (595, 300), "16 low-profile switches", 22, "#475157")
    label(draw, (595, 337), "Tool 01 - Tool 16", 22, "#475157")

    tile2 = (560, 520, 970, 775)
    rounded(draw, tile2, "#ffffff", "#3d454a")
    label(draw, (595, 560), "MODULE 2  /  0x21", 26, "#1c2327", True)
    label(draw, (595, 605), "16 low-profile switches", 22, "#475157")
    label(draw, (595, 642), "Tool 17 - Tool 32", 22, "#475157")

    for box, color in ((tile1, "#e39a1f"), (tile2, "#38a582")):
        left, top, right, bottom = box
        x0 = left + 36
        y0 = top + 150
        for row in range(2):
            for column in range(8):
                x = x0 + column * 43
                y = y0 + row * 42
                draw.rounded_rectangle(
                    (x, y, x + 28, y + 28),
                    radius=5,
                    fill=color,
                    outline="#252b2f",
                    width=2,
                )

    draw.line((765, 470, 765, 520), fill="#cf8415", width=7)
    draw.polygon(
        ((765, 520), (754, 501), (776, 501)),
        fill="#cf8415",
    )

    future = (1080, 215, 1515, 775)
    rounded(draw, future, "#e8ecec", "#9aa4a7")
    label(draw, (1115, 255), "MORE MODULES", 27, "#1c2327", True)
    label(draw, (1115, 305), "0x22 through 0x27", 22, "#4a555a")
    label(draw, (1115, 355), "16 slots each", 22, "#4a555a")
    label(draw, (1115, 405), "128 total inputs", 22, "#4a555a", True)

    for index in range(6):
        top = 455 + index * 43
        rounded(
            draw,
            (1120, top, 1470, top + 30),
            "#ffffff",
            "#a4adaf",
            radius=5,
            width=2,
        )
        label(
            draw,
            (1140, top + 15),
            "Expansion module {}".format(index + 3),
            17,
            "#4a555a",
            anchor="lm",
        )

    arrow(draw, (970, 345), (1080, 345), "#cf8415")
    arrow(draw, (970, 650), (1080, 650), "#cf8415")

    label(
        draw,
        (80, 838),
        "Every switch closes one expander input to ground. No matrix ghosting.",
        22,
        "#3d474c",
        True,
    )

    image.save(OUTPUT)
    print("Diagram written to", OUTPUT)


if __name__ == "__main__":
    main()
