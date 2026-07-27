import gc
import time
import ujson

import network
from machine import I2C, Pin

import settings
from keypad import MatrixKeypad
from mcp23017 import MCP23017

try:
    import urequests as requests
except ImportError:
    import requests

try:
    from ssd1306 import SSD1306_I2C
except ImportError:
    SSD1306_I2C = None


class DebouncedValue:
    def __init__(self, value):
        self.raw = value
        self.stable = value
        self.changed_at = time.ticks_ms()

    def update(self, value, now):
        if value != self.raw:
            self.raw = value
            self.changed_at = now

        if (
            self.stable != self.raw
            and time.ticks_diff(now, self.changed_at)
            >= settings.DEBOUNCE_MS
        ):
            self.stable = self.raw
            return True

        return False


class ToolTile:
    def __init__(self, i2c, definition):
        self.address = definition["address"]
        self.names = definition["tools"]
        self.expander = MCP23017(i2c, self.address)
        pressed = self.expander.read_pressed()
        self.states = [
            DebouncedValue(bool(pressed & (1 << bit))) for bit in range(16)
        ]

    def update(self, now):
        pressed = self.expander.read_pressed()
        changes = []

        for bit, state in enumerate(self.states):
            if state.update(bool(pressed & (1 << bit)), now):
                changes.append((self.names[bit], state.stable))

        return changes

    def missing(self):
        return [
            self.names[index]
            for index, state in enumerate(self.states)
            if not state.stable
        ]


class ToolTracker:
    def __init__(self):
        self.led = Pin("LED", Pin.OUT)
        self.i2c = I2C(
            0,
            sda=Pin(settings.I2C_SDA_GPIO),
            scl=Pin(settings.I2C_SCL_GPIO),
            freq=settings.I2C_FREQUENCY,
        )
        self.keypad = MatrixKeypad(
            settings.KEYPAD_ROW_GPIOS,
            settings.KEYPAD_COLUMN_GPIOS,
        )
        self.display = None
        self.tiles = []
        self.member_id = None
        self.member_name = None
        self.member_deadline = None
        self.id_buffer = ""
        self.raw_key = None
        self.stable_key = None
        self.key_changed_at = time.ticks_ms()
        self.alerts_paused_until = None
        self.control_cursor = None
        self.last_control_poll = 0
        self.last_display_update = 0

    def start(self):
        if settings.NTFY_ENABLED:
            self.connect_wifi()
        else:
            print("ntfy disabled; starting offline")

        found = self.i2c.scan()

        if (
            settings.OLED_ENABLED
            and SSD1306_I2C is not None
            and settings.OLED_ADDRESS in found
        ):
            self.display = SSD1306_I2C(
                128,
                64,
                self.i2c,
                settings.OLED_ADDRESS,
            )

        for definition in settings.TILES:
            address = definition["address"]
            if address not in found:
                print("Tile not found: 0x{:02X}".format(address))
                continue

            self.tiles.append(ToolTile(self.i2c, definition))
            print("Tile ready: 0x{:02X}".format(address))

        if not self.tiles:
            raise RuntimeError("No MCP23017 tool tiles were found")

        self.send_ntfy(
            "Tool Tracker V2",
            "Hub online with {} tool slots".format(len(self.tiles) * 16),
            force=True,
        )
        self.poll_controls(execute=False)
        self.update_display()

        while True:
            self.loop()

    def connect_wifi(self):
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)

        if not wifi.isconnected():
            wifi.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)
            started = time.ticks_ms()

            while not wifi.isconnected():
                if time.ticks_diff(time.ticks_ms(), started) > 20000:
                    raise RuntimeError("Wi-Fi connection timed out")
                self.led.toggle()
                time.sleep_ms(250)

        print("Wi-Fi:", wifi.ifconfig()[0])
        self.led.value(0)

    def loop(self):
        now = time.ticks_ms()
        changed = False

        for tile in self.tiles:
            for tool_name, present in tile.update(now):
                changed = True
                self.handle_tool_change(tool_name, present)

        key = self.keypad.read()
        if key != self.raw_key:
            self.raw_key = key
            self.key_changed_at = now

        if (
            key != self.stable_key
            and time.ticks_diff(now, self.key_changed_at) >= 40
        ):
            self.stable_key = key
            if key is not None:
                changed = True
                self.handle_key(key)

        if (
            self.member_deadline is not None
            and time.ticks_diff(now, self.member_deadline) >= 0
        ):
            self.end_session()
            changed = True

        if time.ticks_diff(now, self.last_control_poll) >= 5000:
            self.last_control_poll = now
            self.poll_controls()

        if (
            changed
            or time.ticks_diff(now, self.last_display_update) >= 1000
        ):
            self.last_display_update = now
            self.update_display()

        self.led.value(1 if self.missing_tools() else 0)
        time.sleep_ms(20)

    def handle_key(self, key):
        if key.isdigit() and len(self.id_buffer) < 8:
            self.id_buffer += key
        elif key == "*":
            if self.id_buffer:
                self.id_buffer = ""
            else:
                self.end_session()
        elif key == "#":
            self.start_session(self.id_buffer)
            self.id_buffer = ""

    def start_session(self, member_id):
        member_name = settings.MEMBERS.get(member_id)

        if member_name is None:
            print("Unknown member ID")
            return

        self.member_id = member_id
        self.member_name = member_name
        self.member_deadline = time.ticks_add(
            time.ticks_ms(),
            settings.SESSION_TIMEOUT_SECONDS * 1000,
        )
        print("{} signed in".format(member_name))

    def end_session(self):
        if self.member_name:
            print("{} signed out".format(self.member_name))

        self.member_id = None
        self.member_name = None
        self.member_deadline = None

    def handle_tool_change(self, tool_name, present):
        if self.member_deadline is not None:
            self.member_deadline = time.ticks_add(
                time.ticks_ms(),
                settings.SESSION_TIMEOUT_SECONDS * 1000,
            )

        user = self.member_name or "Unknown user"

        if present:
            message = "{} returned by {}".format(tool_name, user)
            print(message)
            if settings.NOTIFY_RETURNS:
                self.send_ntfy("Tool Returned", message)
        else:
            message = "{} removed by {}".format(tool_name, user)
            print(message)
            self.send_ntfy("Tool Removed", message)

    def missing_tools(self):
        missing = []
        for tile in self.tiles:
            missing.extend(tile.missing())
        return missing

    def status_message(self):
        missing = self.missing_tools()
        tools = (
            "All tools present"
            if not missing
            else "Missing: " + ", ".join(missing)
        )
        member = self.member_name or "No active member"
        return "{}\nUser: {}".format(tools, member)

    def alerts_paused(self):
        return (
            self.alerts_paused_until is not None
            and time.ticks_diff(
                self.alerts_paused_until,
                time.ticks_ms(),
            )
            > 0
        )

    def send_ntfy(self, title, message, force=False):
        if not settings.NTFY_ENABLED:
            return
        if self.alerts_paused() and not force:
            return

        response = None
        try:
            response = requests.post(
                "{}/{}".format(
                    settings.NTFY_SERVER.rstrip("/"),
                    settings.NTFY_ALERT_TOPIC,
                ),
                data=message,
                headers={"Title": title},
            )
        except Exception as error:
            print("ntfy error:", error)
        finally:
            if response is not None:
                response.close()
            gc.collect()

    def pause_alerts(self, value):
        value = value.lower()
        multiplier = 60

        if value.endswith("h"):
            multiplier = 3600
            value = value[:-1]
        elif value.endswith("m"):
            value = value[:-1]

        seconds = max(60, min(int(value) * multiplier, 12 * 3600))
        self.alerts_paused_until = time.ticks_add(
            time.ticks_ms(), seconds * 1000
        )
        self.send_ntfy(
            "Tool Tracker V2",
            "Alerts paused for {} minutes".format(seconds // 60),
            force=True,
        )

    def handle_control(self, message):
        command = message.strip().lower()

        if command.startswith("/pause "):
            try:
                self.pause_alerts(command.split(None, 1)[1])
            except Exception:
                self.send_ntfy(
                    "Tool Tracker V2",
                    "Use /pause 30m or /pause 2h",
                    force=True,
                )
        elif command == "/resume":
            self.alerts_paused_until = None
            self.send_ntfy(
                "Tool Tracker V2", "Alerts resumed", force=True
            )
        elif command == "/status":
            self.send_ntfy(
                "Tool Tracker V2 Status",
                self.status_message(),
                force=True,
            )

    def poll_controls(self, execute=True):
        if not settings.NTFY_ENABLED:
            return

        since = self.control_cursor or "latest"
        response = None

        try:
            url = "{}/{}/json?poll=1&since={}".format(
                settings.NTFY_SERVER.rstrip("/"),
                settings.NTFY_CONTROL_TOPIC,
                since,
            )
            response = requests.get(url)

            for line in response.text.splitlines():
                if not line:
                    continue

                item = ujson.loads(line)
                if item.get("event") != "message":
                    continue

                self.control_cursor = item.get(
                    "id", self.control_cursor
                )
                if execute:
                    self.handle_control(item.get("message", ""))
        except Exception as error:
            print("ntfy control error:", error)
        finally:
            if response is not None:
                response.close()
            gc.collect()

    def update_display(self):
        if self.display is None:
            return

        missing = len(self.missing_tools())
        member = self.member_name or "No member"

        self.display.fill(0)
        self.display.text("TOOL TRACKER V2", 0, 0)
        self.display.text(member[:16], 0, 18)

        if self.id_buffer:
            self.display.text("ID: " + self.id_buffer, 0, 34)
        else:
            self.display.text("Missing: {}".format(missing), 0, 34)

        paused = "PAUSED" if self.alerts_paused() else "Alerts on"
        self.display.text(paused, 0, 50)
        self.display.show()

if __name__ == "__main__":
    ToolTracker().start()
