# Tool Tracker

This uses three limit switches to check whether tools are in their slots. A
Raspberry Pi Pico W reads the switches and sends updates through ntfy. The 
main goal of this is to try to mimic the usage cases of the more expensive
tool tracking boxes such as the one from snap-on. In the future, I'll 
impement features such as ID pin, or cloud storage, or maybe even a display.

## Wiring

| Tool | Signal | Ground |
|---|---|---|
| Tool 1 | Pin 1 (GP0) | Pin 3 |
| Tool 2 | Pin 6 (GP4) | Pin 8 |
| Tool 3 | Pin 2 (GP1) | Pin 3 |

Only connect the signal and ground wires from each VEX switch. Leave the red
wire disconnected.

## Commands

- `/status` shows the state of all three tools.
- `/off` stops tool notifications.
- `/on` starts them again.

The longer commands `/notifications off` and `/notifications on` also work.

## Work Done

- Cad files - me
- Code - me, my brother, and codex for debugging
- wiring and such - me 
