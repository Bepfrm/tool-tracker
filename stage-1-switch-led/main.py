from machine import Pin
import time


# Physical pin 6 is GP4.
# The switch connects GP4 to ground when pressed.
switch = Pin(4, Pin.IN, Pin.PULL_UP)
led = Pin("LED", Pin.OUT)


while True:
    pressed = switch.value() == 0
    led.value(1 if pressed else 0)
    time.sleep_ms(20)
