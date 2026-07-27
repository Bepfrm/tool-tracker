# Funding pitch

## Short description

Tool Tracker V2 is an expandable toolbox insert that detects when individual
tools leave or return to their slots. Low-profile mechanical switches sit
under the tools, and 16-input expansion modules let one Pico 2 W monitor many
slots without a bundle of wires going back to the hub.

The first build tracks 32 tools. A 12-key mechanical pad lets a team member
enter an ID before taking something, and a small OLED shows who is signed in
and how many tools are missing. The Pico logs the event and can send an ntfy
alert.

## What is different from V1

V1 used one Pico GPIO for every switch and only handled three tools. V2 moves
the switches onto addressable MCP23017 modules. Each module adds 16 tool
inputs while using the same SDA and SCL wires. Eight modules provide 128
inputs on one bus.

## What I will build with the grant

- One Pico 2 W hub with keypad and OLED
- Two removable 16-switch tray modules
- Thirty-two active tool slots
- 3D-printed Choc and MX switch plates
- Member sessions, named tool events, quiet mode, and ntfy status
- A repeatable test of at least 100 remove/return cycles per slot

## Why funding helps

I already proved the sensing idea with three VEX limit switches. The grant
would let me move from loose breadboard wires to a complete 32-slot modular
prototype. The switches, expanders, display, connectors, and case hardware
are the parts I do not already have.

## Requested amount

The current BOM is $112.15 before tax. I am requesting the $120 A-tier budget
for the listed parts and small price changes.

## Demo goal

For the final demo, a member will enter an ID, lift two tools from different
expansion modules, and show the OLED and ntfy status updating with the correct
tool names. The same tools will then be returned and cleared from the missing
list.
