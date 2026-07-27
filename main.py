from machine import Pin
import time
import ujson

import network
import urequests
import secrets


# Tool number, GPIO number
TOOLS = (
    (1, 0),
    (2, 4),
    (3, 1),
)

switches = [Pin(gpio, Pin.IN, Pin.PULL_UP) for _, gpio in TOOLS]
led = Pin("LED", Pin.OUT)

topic_url = "https://ntfy.sh/" + secrets.NTFY_TOPIC
notifications_on = getattr(secrets, "NOTIFICATIONS_START_ENABLED", True)
last_message_id = None


def tool_present(index):
    return switches[index].value() == 0


def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)

    while not wifi.isconnected():
        time.sleep(1)

    print("Wi-Fi connected")


def send(title, message, always=False):
    if not notifications_on and not always:
        return

    response = None
    try:
        response = urequests.post(
            topic_url,
            data=message,
            headers={"Title": title},
        )
    except Exception as error:
        print("ntfy error:", error)
    finally:
        if response:
            response.close()


def send_status():
    lines = []

    for index, (tool_number, _) in enumerate(TOOLS):
        state = "PRESENT" if tool_present(index) else "REMOVED"
        lines.append("Tool {}: {}".format(tool_number, state))

    state = "ON" if notifications_on else "OFF"
    lines.append("Notifications: " + state)
    send("Tool Tracker Status", "\n".join(lines), always=True)


def handle_command(message):
    global notifications_on

    message = message.strip().lower()

    if message in ("/off", "/notifications off"):
        notifications_on = False
        send("Tool Tracker", "Notifications are OFF", always=True)
    elif message in ("/on", "/notifications on"):
        notifications_on = True
        send("Tool Tracker", "Notifications are ON", always=True)
    elif message == "/status":
        send_status()


def check_commands(ignore=False):
    global last_message_id

    since = last_message_id or "latest"
    response = None

    try:
        response = urequests.get(
            topic_url + "/json?poll=1&since=" + since
        )

        for line in response.text.splitlines():
            if not line:
                continue

            item = ujson.loads(line)
            if item.get("event") != "message":
                continue

            last_message_id = item.get("id", last_message_id)
            if not ignore:
                handle_command(item.get("message", ""))
    except Exception as error:
        print("ntfy check error:", error)
    finally:
        if response:
            response.close()


connect_wifi()
send("Pico Connected", "Tool Tracker is online", always=True)
check_commands(ignore=True)

states = [tool_present(index) for index in range(len(TOOLS))]
raw_states = states[:]
changed_at = [time.ticks_ms()] * len(TOOLS)
last_poll = time.ticks_ms()
led.value(any(states))

for index, (tool_number, _) in enumerate(TOOLS):
    state = "PRESENT" if states[index] else "REMOVED"
    print("Tool {}: {}".format(tool_number, state))


while True:
    now = time.ticks_ms()

    for index, (tool_number, _) in enumerate(TOOLS):
        reading = tool_present(index)

        if reading != raw_states[index]:
            raw_states[index] = reading
            changed_at[index] = now

        if (
            reading != states[index]
            and time.ticks_diff(now, changed_at[index]) >= 60
        ):
            states[index] = reading
            led.value(any(states))

            if reading:
                print("Tool {} returned".format(tool_number))
                send(
                    "Tool {} Returned".format(tool_number),
                    "Tool {} is back in its slot".format(tool_number),
                )
            else:
                print("Tool {} removed".format(tool_number))
                send(
                    "Tool {} Removed".format(tool_number),
                    "Tool {} was removed from its slot".format(tool_number),
                )

    if time.ticks_diff(now, last_poll) >= 5000:
        last_poll = now
        check_commands()

    time.sleep_ms(20)
