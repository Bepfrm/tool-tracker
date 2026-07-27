from machine import Pin
import time
import ujson

import network
import urequests

import secrets


WIFI_PASSWORD = secrets.WIFI_PASSWORD
WIFI_SSID = secrets.WIFI_SSID
NTFY_TOPIC = secrets.NTFY_TOPIC
NOTIFICATIONS_START_ENABLED = getattr(
    secrets, "NOTIFICATIONS_START_ENABLED", True
)


led = Pin("LED", Pin.OUT)

tools = [
    {"number": 1, "pin": Pin(0, Pin.IN, Pin.PULL_UP)},  # Physical pin 1
    {"number": 2, "pin": Pin(4, Pin.IN, Pin.PULL_UP)},  # Physical pin 6
    {"number": 3, "pin": Pin(1, Pin.IN, Pin.PULL_UP)},  # Physical pin 2
]

NTFY_URL = "https://ntfy.sh/" + NTFY_TOPIC
POLL_INTERVAL_MS = 5000
DEBOUNCE_MS = 60

notifications_enabled = NOTIFICATIONS_START_ENABLED
last_message_id = None


def tool_is_present(tool):
    return tool["pin"].value() == 0


def update_led():
    led.value(1 if any(tool["stable_present"] for tool in tools) else 0)


def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if not wifi.isconnected():
        print("Connecting to Wi-Fi...")
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)

        while not wifi.isconnected():
            time.sleep(1)

    print("Connected:", wifi.ifconfig()[0])


def publish(title, message, force=False):
    if not notifications_enabled and not force:
        print("Notification skipped:", message)
        return

    response = None

    try:
        response = urequests.post(
            NTFY_URL,
            data=message,
            headers={"Title": title},
        )
        print("ntfy status:", response.status_code)
    except Exception as error:
        print("ntfy publish failed:", error)
    finally:
        if response is not None:
            response.close()


def handle_command(command):
    global notifications_enabled

    command = command.strip().lower()

    if command in ("/off", "/notifications off"):
        notifications_enabled = False
        publish(
            "Tool Tracker Controls",
            "Tool notifications are now OFF",
            force=True,
        )

    elif command in ("/on", "/notifications on"):
        notifications_enabled = True
        publish(
            "Tool Tracker Controls",
            "Tool notifications are now ON",
            force=True,
        )

    elif command == "/status":
        alert_state = "ON" if notifications_enabled else "OFF"
        status_lines = []

        for tool in tools:
            tool_state = "PRESENT" if tool_is_present(tool) else "REMOVED"
            status_lines.append(
                "Tool {}: {}".format(tool["number"], tool_state)
            )

        status_lines.append("Notifications: " + alert_state)
        publish(
            "Tool Tracker Status",
            "\n".join(status_lines),
            force=True,
        )


def check_commands(execute=True):
    global last_message_id

    since = last_message_id if last_message_id else "latest"
    url = NTFY_URL + "/json?poll=1&since=" + since
    response = None

    try:
        response = urequests.get(url)

        for line in response.text.splitlines():
            if not line:
                continue

            message = ujson.loads(line)
            if message.get("event") != "message":
                continue

            last_message_id = message.get("id", last_message_id)

            if execute:
                handle_command(message.get("message", ""))

    except Exception as error:
        print("ntfy command check failed:", error)
    finally:
        if response is not None:
            response.close()


connect_wifi()
publish(
    "Pico Connected",
    "Tool Tracker is online",
    force=True,
)

# Start after the online message so cached commands are not replayed on reboot.
check_commands(execute=False)

now = time.ticks_ms()

for tool in tools:
    present = tool_is_present(tool)
    tool["stable_present"] = present
    tool["last_raw_present"] = present
    tool["raw_changed_at"] = now
    print(
        "Tool {}: {}".format(
            tool["number"], "PRESENT" if present else "REMOVED"
        )
    )

last_poll_at = time.ticks_ms()
update_led()


while True:
    now = time.ticks_ms()

    for tool in tools:
        raw_present = tool_is_present(tool)

        if raw_present != tool["last_raw_present"]:
            tool["last_raw_present"] = raw_present
            tool["raw_changed_at"] = now

        if (
            raw_present != tool["stable_present"]
            and time.ticks_diff(now, tool["raw_changed_at"])
            >= DEBOUNCE_MS
        ):
            tool["stable_present"] = raw_present
            update_led()

            tool_number = tool["number"]

            if raw_present:
                print("Tool {} returned".format(tool_number))
                publish(
                    "Tool {} Returned".format(tool_number),
                    "Tool {} is back in its slot".format(tool_number),
                )
            else:
                print("Tool {} removed".format(tool_number))
                publish(
                    "Tool {} Removed".format(tool_number),
                    "Tool {} was removed from its slot".format(tool_number),
                )

    if time.ticks_diff(now, last_poll_at) >= POLL_INTERVAL_MS:
        last_poll_at = now
        check_commands()

    time.sleep_ms(20)
