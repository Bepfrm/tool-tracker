# Tool Tracker

Tool Tracker is a beginner-friendly Raspberry Pi Pico 2 W project that detects
when a tool presses or releases a storage switch.

The project is split into two stages:

1. **Switch and LED:** Pressing the switch turns on the Pico's onboard LED.
2. **ntfy notifications:** The Pico connects to Wi-Fi and sends tool removal
   and return notifications to a phone.

Stage 2 also accepts these commands through the same ntfy topic:

```text
/off
/on
/status
```

## Hardware

- Raspberry Pi Pico 2 W with MicroPython
- VEX limit switch or another normally-open microswitch
- USB power cable
- Jumper wires or a finished wire harness

## Wiring

Stage 2 uses all three switch connections from the prototype:

| Tool | Switch signal | Switch ground |
|---|---|---|
| Tool 1 | Physical pin 1 / GP0 | Physical pin 3 / GND |
| Tool 2 | Physical pin 6 / GP4 | Physical pin 8 / GND |
| Tool 3 | Physical pin 2 / GP1 | Physical pin 3 / GND |

The code uses the Pico's internal pull-up resistor:

- Switch pressed: its GPIO is connected to ground and the tool is present.
- Switch released: its GPIO is high and the tool is removed.

Leave the red VEX wire disconnected. Connect only the switch signal and ground
wires.

Do not connect a 5 V signal to a Pico GPIO.

## VS Code setup

1. Install Visual Studio Code.
2. Install the **Raspberry Pi Pico** and **MicroPico** extensions.
3. Connect the Pico 2 W by USB.
4. Open one stage folder at a time in VS Code.
5. Open the command palette with `Ctrl+Shift+P`.
6. Run `MicroPico: Configure project` and select the Pico.
7. Run `MicroPico: Upload project to Pico`.
8. Restart the Pico.

The file must be named `main.py` on the Pico to run automatically at startup.

## Stage 1

Open `stage-1-switch-led` and upload its `main.py`.

Expected behavior:

- Press switch: onboard LED turns on.
- Release switch: onboard LED turns off.

Do not continue until Stage 1 works reliably.

## Stage 2

Open `stage-2-ntfy`.

Copy:

```text
secrets.py.example
```

to:

```text
secrets.py
```

Enter your Wi-Fi credentials and a long, private ntfy topic. Subscribe to the
same topic in the ntfy phone app.

Upload both files:

```text
main.py
secrets.py
```

Expected behavior:

- Pico starts: `Pico Connected`
- A tool presses its switch: `Tool 1 Returned`, `Tool 2 Returned`, or
  `Tool 3 Returned`
- A tool releases its switch: `Tool 1 Removed`, `Tool 2 Removed`, or
  `Tool 3 Removed`

Type `/off` in the ntfy topic to stop tool alerts. Type `/on` to resume them.
The switch and onboard LED continue operating while notifications are off.
Type `/status` to request the current state of all three tools.

Commands are checked approximately every five seconds. The notification
setting returns to its configured default after the Pico restarts.

## Privacy

Never commit `secrets.py`. It contains the Wi-Fi password and private ntfy
topic. This repository ignores that file automatically.

For a larger deployment, use separate protected alert and control topics
instead of a shared public topic.

## License

MIT
