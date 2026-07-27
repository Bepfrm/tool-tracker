# Tool Tracker

This uses three limit switches to check whether tools are in their slots. A
Raspberry Pi Pico W reads the switches and sends updates through ntfy.

## Wiring

| Tool | Signal | Ground |
|---|---|---|
| Tool 1 | Pin 1 (GP0) | Pin 3 |
| Tool 2 | Pin 6 (GP4) | Pin 8 |
| Tool 3 | Pin 2 (GP1) | Pin 3 |

Only connect the signal and ground wires from each VEX switch. Leave the red
wire disconnected.

## Setup

1. Make a copy of `secrets.py.example` named `secrets.py`.
2. Put your Wi-Fi information and ntfy topic in that file.
3. Upload `main.py` and `secrets.py` to the Pico.
4. Subscribe to the same topic in the ntfy app.

Do not upload `secrets.py` to GitHub. It is ignored by the repository.

## Commands

- `/status` shows the state of all three tools.
- `/off` stops tool notifications.
- `/on` starts them again.

The longer commands `/notifications off` and `/notifications on` also work.
