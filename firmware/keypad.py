from machine import Pin
import time


KEYS = (
    ("1", "2", "3"),
    ("4", "5", "6"),
    ("7", "8", "9"),
    ("*", "0", "#"),
)


class MatrixKeypad:
    def __init__(self, row_gpios, column_gpios):
        self.rows = [Pin(gpio, Pin.OUT, value=1) for gpio in row_gpios]
        self.columns = [
            Pin(gpio, Pin.IN, Pin.PULL_UP) for gpio in column_gpios
        ]

    def read(self):
        for row_index, row in enumerate(self.rows):
            row.value(0)
            time.sleep_us(20)

            for column_index, column in enumerate(self.columns):
                if column.value() == 0:
                    row.value(1)
                    return KEYS[row_index][column_index]

            row.value(1)

        return None
