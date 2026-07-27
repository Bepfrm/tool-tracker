from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "wiring-diagram.png"
WIDTH = 1600
HEIGHT = 1000

INK = "#1c2327"
MUTED = "#59656a"
PAPER = "#f4f5f1"
WHITE = "#ffffff"
ORANGE = "#d98b18"
GREEN = "#299477"
BLUE = "#2b78a3"
RED = "#c9483b"
BLACK = "#252b2f"


def font(size, bold=False):
    name = "seguisb.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(
        str(Path("C:/Windows/Fonts") / name),
        size,
    )


def label(draw, xy, text, size=20, color=INK, bold=False, anchor="la"):
    draw.text(
        xy,
        text,
        fill=color,
        font=font(size, bold),
        anchor=anchor,
    )


def rounded(draw, box, fill=WHITE, outline=INK, radius=12, width=3):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def wire(draw, points, color, width=7):
    draw.line(points, fill=color, width=width, joint="curve")


def pin(draw, x, y, name, color):
    draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color)
    label(draw, (x + 18, y), name, 17, INK, True, "lm")


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)

    label(draw, (70, 55), "TOOL TRACKER V2 WIRING", 42, INK, True)
    label(
        draw,
        (70, 112),
        "One 16-switch tile shown. Add another at address 0x21.",
        23,
        MUTED,
    )

    pico = (70, 205, 390, 705)
    rounded(draw, pico, "#20272c", "#101416", radius=16)
    label(draw, (105, 245), "PICO 2 W", 29, WHITE, True)
    label(draw, (105, 282), "HUB", 19, "#bac4c7", True)

    pico_pins = (
        (335, 350, "3V3", RED),
        (335, 405, "GND", BLACK),
        (335, 460, "GP0 / SDA", GREEN),
        (335, 515, "GP1 / SCL", BLUE),
    )
    for x, y, name, color in pico_pins:
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color)
        label(draw, (x - 18, y), name, 18, WHITE, True, "rm")

    label(draw, (105, 610), "GP2-GP5", 18, WHITE, True)
    label(draw, (105, 639), "keypad rows", 17, "#bac4c7")
    label(draw, (245, 610), "GP6-GP8", 18, WHITE, True)
    label(draw, (245, 639), "keypad cols", 17, "#bac4c7")

    expander = (575, 235, 965, 700)
    rounded(draw, expander, WHITE, "#414a4f", radius=14)
    label(draw, (610, 270), "MCP23017 TILE 1", 27, INK, True)
    label(draw, (610, 307), "Address 0x20", 19, MUTED)

    expander_pins = (
        (610, 350, "VIN / 3V3", RED),
        (610, 405, "GND", BLACK),
        (610, 460, "SDA", GREEN),
        (610, 515, "SCL", BLUE),
    )
    for x, y, name, color in expander_pins:
        pin(draw, x, y, name, color)

    label(draw, (610, 575), "A0", 18, INK, True)
    label(draw, (660, 575), "A1", 18, INK, True)
    label(draw, (710, 575), "A2", 18, INK, True)
    label(draw, (610, 605), "open  open  open", 17, MUTED)
    label(draw, (610, 650), "GPA0-GPB7 = 16 inputs", 19, INK, True)

    bus_x = 500
    wire(draw, ((335, 350), (bus_x, 350), (bus_x, 350), (610, 350)), RED)
    wire(draw, ((335, 405), (520, 405), (520, 405), (610, 405)), BLACK)
    wire(draw, ((335, 460), (540, 460), (540, 460), (610, 460)), GREEN)
    wire(draw, ((335, 515), (560, 515), (560, 515), (610, 515)), BLUE)

    label(draw, (465, 325), "4-wire bus", 17, MUTED, True, "ma")

    switches_box = (1060, 205, 1530, 705)
    rounded(draw, switches_box, "#e9edec", "#879397", radius=14)
    label(draw, (1095, 245), "16 TOOL SWITCHES", 27, INK, True)
    label(draw, (1095, 284), "Normally open, one input each", 19, MUTED)

    y_start = 350
    for index in range(4):
        y = y_start + index * 78
        input_name = (
            "GPA0 / Tool 01",
            "GPA1 / Tool 02",
            "...",
            "GPB7 / Tool 16",
        )[index]
        label(draw, (1095, y), input_name, 18, INK, True, "lm")
        draw.line((1270, y, 1320, y), fill=ORANGE, width=5)
        draw.line((1320, y - 14, 1350, y + 12), fill=INK, width=4)
        draw.line((1355, y, 1390, y), fill=INK, width=4)
        draw.ellipse(
            (1315, y - 5, 1325, y + 5),
            fill=INK,
        )
        draw.ellipse(
            (1385, y - 5, 1395, y + 5),
            fill=INK,
        )
        draw.line((1390, y, 1480, y), fill=BLACK, width=5)

    wire(draw, ((965, 470), (1010, 470), (1010, 350), (1060, 350)), ORANGE)
    label(draw, (1008, 438), "inputs", 16, "#8b5b14", True, "ma")

    wire(draw, ((1480, 350), (1480, 584)), BLACK, 5)
    label(draw, (1465, 620), "common GND", 17, INK, True, "ma")

    keypad = (70, 785, 760, 940)
    rounded(draw, keypad, WHITE, "#414a4f", radius=12)
    label(draw, (105, 820), "MECHANICAL ID PAD", 24, INK, True)
    label(
        draw,
        (105, 860),
        "12 Choc switches in a 4 x 3 matrix",
        19,
        MUTED,
    )
    label(
        draw,
        (105, 900),
        "Rows: GP2-GP5     Columns: GP6-GP8",
        19,
        INK,
        True,
    )

    second_tile = (825, 785, 1530, 940)
    rounded(draw, second_tile, "#fff5e6", "#c77b12", radius=12)
    label(draw, (860, 820), "TO ADD TILE 2", 24, INK, True)
    label(
        draw,
        (860, 860),
        "Daisy-chain the same 3V3, GND, SDA and SCL.",
        19,
        MUTED,
    )
    label(
        draw,
        (860, 900),
        "Bridge A0 to 3V3 for address 0x21.",
        19,
        INK,
        True,
    )

    image.save(OUTPUT)
    print("Diagram written to", OUTPUT)


if __name__ == "__main__":
    main()
