IODIRA = 0x00
IODIRB = 0x01
GPPUA = 0x0C
GPPUB = 0x0D
GPIOA = 0x12


class MCP23017:
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address

        # All 16 pins are inputs with pull-ups.
        self._write(IODIRA, 0xFF)
        self._write(IODIRB, 0xFF)
        self._write(GPPUA, 0xFF)
        self._write(GPPUB, 0xFF)

    def _write(self, register, value):
        self.i2c.writeto_mem(self.address, register, bytes((value,)))

    def read_pressed(self):
        data = self.i2c.readfrom_mem(self.address, GPIOA, 2)
        raw = data[0] | (data[1] << 8)
        return (~raw) & 0xFFFF
