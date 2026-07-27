# Wiring plan

## Hub

| Pico 2 W pin | Connection |
|---|---|
| 3V3 | OLED and MCP23017 power |
| GND | Common ground |
| GP0 / physical pin 1 | I2C SDA |
| GP1 / physical pin 2 | I2C SCL |
| GP2-GP5 | Keypad rows 1-4 |
| GP6-GP8 | Keypad columns 1-3 |
| GP9 | Optional door contact |
| GP10 | Optional shared MCP23017 interrupt |

The hub is the only place that should have the I2C pull-up resistors. The
Adafruit breakouts already include pull-ups, so do not add another pair to
every hand-wired module.

## Expansion module

Each module has:

- one MCP23017 breakout;
- 16 normally-open mechanical switches;
- one switch terminal connected to an expander input;
- the other switch terminal connected to ground;
- I2C input and output connectors for daisy chaining;
- address jumpers A0, A1, and A2.

| Module | A2 | A1 | A0 | Address | Tool numbers |
|---|---:|---:|---:|---:|---|
| 1 | 0 | 0 | 0 | `0x20` | 1-16 |
| 2 | 0 | 0 | 1 | `0x21` | 17-32 |
| 3 | 0 | 1 | 0 | `0x22` | 33-48 |
| 4 | 0 | 1 | 1 | `0x23` | 49-64 |
| 5 | 1 | 0 | 0 | `0x24` | 65-80 |
| 6 | 1 | 0 | 1 | `0x25` | 81-96 |
| 7 | 1 | 1 | 0 | `0x26` | 97-112 |
| 8 | 1 | 1 | 1 | `0x27` | 113-128 |

## Bus cable

The basic module cable has four conductors:

1. 3V3
2. GND
3. SDA
4. SCL

A fifth conductor can carry the shared interrupt signal. The first firmware
version polls every 20 ms, so the interrupt wire is optional.

Keep the prototype bus short and away from motors or power-tool wiring. Start
at 100 kHz. For several drawers or a full-size cabinet, each drawer should
become an RS-485 node instead of stretching this I2C bus.

## Mechanical keypad

The 12 Choc switches are scanned as a normal 3x4 matrix:

```text
1 2 3
4 5 6
7 8 9
* 0 #
```

- Digits build the member ID.
- `#` submits the ID.
- `*` clears the current entry.
- Pressing `*` with an empty entry ends the session.
