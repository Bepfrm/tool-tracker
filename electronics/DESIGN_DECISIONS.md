# Design decisions

## Direct expander inputs instead of a tool matrix

A keyboard matrix is efficient, but several tools can hold several switches
down at once. Without a diode at every switch, that can create ghost presses.
The MCP23017 has 16 independent inputs, so the first version wires one tool to
one input.

This costs more wire inside a module, but the wire stays inside the removable
tray. Only the I2C bus runs back to the Pico.

## Sixteen slots per module

Sixteen matches the MCP23017 and makes the address math easy. A 2-by-8 plate
is narrow enough for a drawer and can be printed diagonally or split if a
printer bed is smaller.

## Choc first, MX backup

Kailh Choc switches reduce the tray height. MX switches are easier to find and
have stronger mounting clips. Both plate files are included so the physical
test can decide which one works better under tools. The plates stay 3 mm thick
for stiffness, with 1.5 mm underside pockets around the switch openings so the
mounting clips can latch.

## Keypad instead of NFC

The keypad is cheaper and easier to debug for the first full prototype. It
tests whether identifying the person is useful before adding an NFC reader.
The event model can accept NFC later without changing the switch modules.

## Practical scale

The MCP23017 supports eight addresses, giving 128 inputs on one I2C bus. That
is the supported target for one cabinet. A TCA9548A can create more I2C
branches, but a physically larger installation should use RS-485 drawer nodes
for better noise and cable-length tolerance.
