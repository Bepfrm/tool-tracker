# Design journal

## July 27, 2026 - V2 architecture

Time was recorded with Lookout.

I reviewed the three-switch prototype and wrote down the main problem with
scaling it: every new switch used another Pico pin and another long signal
wire. I compared keyboard matrices with I/O expanders. A matrix uses fewer
pins, but multiple tools can press switches at the same time, so it needs
diodes and more complicated wiring.

I chose one MCP23017 for each 16-switch module. The inputs use the chip's
pull-ups and every switch closes to ground. The three address pins allow eight
modules on one I2C bus, which makes 128 tool inputs.

I also kept the typed member-ID idea. Twelve Choc switches form a 3x4 keypad,
using seven Pico pins. An OLED on the I2C bus shows the current session.

## July 27, 2026 - Mechanical design

Time was recorded with Lookout.

I designed a 2-by-8 switch tray so a module fits inside a normal toolbox
drawer. The tray has a separate top plate and base. I made top plates for
Kailh Choc and MX-size switches so I can compare the height and durability.

The electronics fit below the plate. Both ends have cable openings so the I2C
bus can continue to the next module. The hub has a separate enclosure for the
Pico, mechanical keypad, and OLED.

## Next session

- Print a small corner of each switch plate to check snap fit.
- Measure the actual switches before printing a full tray.
- Wire one expander and confirm all 16 inputs.
- Test two expanders with different addresses.
- Adjust the CAD from the physical fit test.
