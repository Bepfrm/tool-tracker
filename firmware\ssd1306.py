import framebuf


SET_CONTRAST = 0x81
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_MEM_ADDR = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_IREF_SELECT = 0xAD
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


class SSD1306_I2C:
    def __init__(self, width, height, i2c, address=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.address = address
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer, width, height, framebuf.MONO_VLSB
        )
        self._init_display()

    def _command(self, command):
        self.i2c.writeto(self.address, bytes((0x80, command)))

    def _init_display(self):
        commands = (
            SET_DISP,
            SET_MEM_ADDR,
            0x00,
            SET_DISP_START_LINE,
            SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x12,
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0xF1,
            SET_VCOM_DESEL,
            0x30,
            SET_CONTRAST,
            0xFF,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_IREF_SELECT,
            0x30,
            SET_CHARGE_PUMP,
            0x14,
            SET_DISP | 0x01,
        )

        for command in commands:
            self._command(command)

        self.fill(0)
        self.show()

    def fill(self, color):
        self.framebuf.fill(color)

    def text(self, text, x, y, color=1):
        self.framebuf.text(text, x, y, color)

    def show(self):
        self._command(SET_COL_ADDR)
        self._command(0)
        self._command(self.width - 1)
        self._command(SET_PAGE_ADDR)
        self._command(0)
        self._command(self.pages - 1)
        self.i2c.writevto(self.address, (b"\x40", self.buffer))
