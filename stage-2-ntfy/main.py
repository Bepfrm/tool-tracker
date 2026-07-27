from machine import Pin
import time
import ujson

import network
import urequests

from secrets import (
    WIFI_PASSWORD,
    WIFI_SSID,
    NOTIFICATIONS_START_ENABLED,
    NTFY_TOPIC,
)


switch = Pin(4, Pin.IN, Pin.PULL_UP)
led = Pin("LED", Pin.OUT)

NTFY_URL = "https://ntfy.sh/" + NTFY_TOPIC
POLL_INTERVAL_MS = 5000
DEBOUNCE_MS = 60

notifications_enabled = NOTIFICATIONS_START_ENABLED
last_message_id = None


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
        tool_state = "PRESENT" if switch.value() == 0 else "REMOVED"
        alert_state = "ON" if notifications_enabled else "OFF"
        publish(
            "Tool Tracker Status",
            "Tool: {}\nNotifications: {}".format(tool_state, alert_state),
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

stable_pressed = switch.value() == 0
last_raw_pressed = stable_pressed
raw_changed_at = time.ticks_ms()
last_poll_at = time.ticks_ms()
led.value(1 if stable_pressed else 0)


while True:
    now = time.ticks_ms()
    raw_pressed = switch.value() == 0

    if raw_pressed != last_raw_pressed:
        last_raw_pressed = raw_pressed
        raw_changed_at = now

    if (
        raw_pressed != stable_pressed
        and time.ticks_diff(now, raw_changed_at) >= DEBOUNCE_MS
    ):
        stable_pressed = raw_pressed
        led.value(1 if stable_pressed else 0)

        if stable_pressed:
            print("Tool returned")
            publish("Tool Returned", "The tool is back in its slot")
        else:
            print("Tool removed")
            publish("Tool Removed", "The tool was removed from its slot")

    if time.ticks_diff(now, last_poll_at) >= POLL_INTERVAL_MS:
        last_poll_at = now
        check_commands()

    time.sleep_ms(20)
