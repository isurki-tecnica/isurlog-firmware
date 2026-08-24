"""
Reference implementation for receiving real-time ISURLOG data via MQTT.

This script includes a live, public, READ-ONLY demo you can run right now:
the credentials below are scoped to a single test device's topic only
(c-866) - they cannot subscribe to any other client's data. To receive
your own real devices, replace USERNAME/PASSWORD, DEVICE_TYPE, and the
device-specific IDs below with the private credentials Isurki gives you
(see 11.2 Connection Parameters in the wiki).

In addition to printing every decoded message, this script keeps a live,
continuously-updating dashboard on screen (the same layout as the InfluxDB
reference implementation in 10.5, but fed by the MQTT stream in real time
instead of a one-off historical query).

Dependencies: see requirements.txt in this folder
(pip install -r requirements.txt).
"""

import sys
from collections import deque
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MaxNLocator, FuncFormatter

import IsurlogLPP

# Reference point all chart timestamps are measured from (elapsed seconds
# since this moment), rather than plotting raw Unix timestamps directly.
# Unix timestamps are huge numbers (~1.7 billion) - matplotlib's autoscale
# margin for a single data point is a *percentage of the value itself*,
# which on a number that large produces a wildly wrong, years-wide axis
# range from just one point. Small elapsed-seconds numbers don't have that
# problem; the axis formatter below converts back to a real clock time only
# for display.
_START_TIME = datetime.now()

# --- Connection Parameters ---
# The values below are PUBLIC, READ-ONLY demo credentials, scoped to a
# single topic (this device's data only) - they cannot subscribe to any
# other client's data. Replace with your own private credentials to
# receive your real devices.
BROKER_URL = "mqttisurdash.isurki.com"
BROKER_PORT = 8883
USERNAME = "YOUR_UNIQUE_USERNAME_HERE"  # TODO: public demo username
PASSWORD = "YOUR_UNIQUE_PASSWORD_HERE"  # TODO: public demo password

DEMO_DEVICE_ID = "c-866"

# Set this to match the target device's connectivity - the same "nb-iot" /
# "lorawan" values used in the ISURLOG's own static_config.json "modem"
# field. The script subscribes to ONE topic based on this, not both, since
# a given device is only ever one or the other.
DEVICE_TYPE = "nb-iot"  # or "lorawan"

if DEVICE_TYPE == "nb-iot":
    TOPIC = f"isurlog/datos/{DEMO_DEVICE_ID}"
elif DEVICE_TYPE == "lorawan":
    # Replace with your actual ChirpStack application ID and device EUI -
    # avoid a bare wildcard here, which would subscribe to every device on
    # every application your broker credentials can see.
    APPLICATION_ID = "YOUR_APPLICATION_ID_HERE"
    DEVICE_EUI = "YOUR_DEVICE_EUI_HERE"
    TOPIC = f"application/{APPLICATION_ID}/device/{DEVICE_EUI}/event/up"
else:
    raise ValueError(f"Unknown DEVICE_TYPE: {DEVICE_TYPE!r} - expected 'nb-iot' or 'lorawan'.")

# --- Live Data Buffers ---
# Each buffer holds the last HISTORY (time, value) points for one field,
# fed live as MQTT messages arrive - this is what the live dashboard below
# reads from. A bounded deque keeps memory and plotting width in check.
HISTORY = 200
buffers = {
    "VoltageInput0": deque(maxlen=HISTORY),
    "CRateInput0": deque(maxlen=HISTORY),
    "TemperatureSensor0": deque(maxlen=HISTORY),
    "HumiditySensor0": deque(maxlen=HISTORY),
    "ModemData0": deque(maxlen=HISTORY),
    "ModemData1": deque(maxlen=HISTORY),
    # Modbus soil probe (S-Soil MTEC-02B): Temperature, VWC, EC, Epsilon.
    "ModbusInput0": deque(maxlen=HISTORY),
    "ModbusInput1": deque(maxlen=HISTORY),
    "ModbusInput2": deque(maxlen=HISTORY),
    "ModbusInput3": deque(maxlen=HISTORY),
}

# Maps an IsurlogLPP sensor_types key to the InfluxDB-style _field prefix
# used throughout this wiki (see 10.4 Data Schema: Field Key Reference).
_FIELD_PREFIXES = {
    "addAnalogInput": "AnalogInput",
    "addDigitalInput": "DigitalInput",
    "addModbusInput": "ModbusInput",
    "addTemperatureInput": "TemperatureInput",
    "addTemperatureSensor": "TemperatureSensor",
    "addHumiditySensor": "HumiditySensor",
    "addVoltageInput": "VoltageInput",
    "addCRateInput": "CRateInput",
    "addModemData": "ModemData",
}


def _field_name(entry: dict) -> str:
    """
    Maps a decoded IsurlogLPP entry ({'channel', 'name', 'value'}) to the
    same _field naming convention used in InfluxDB, e.g. channel 0 of
    'addVoltageInput' -> 'VoltageInput0'. Accelerometer sub-values are
    already split and named by IsurlogLPP.decodeIsurlogLPP() (e.g.
    'addAccelerometerX'), so they're handled separately.
    """
    if entry["name"].startswith("addAccelerometer"):
        axis = entry["name"].replace("addAccelerometer", "")
        return f"Accelerometer{axis}{entry['channel']}"

    prefix = _FIELD_PREFIXES.get(entry["name"])
    if prefix is None:
        return entry["name"]  # e.g. addUnixTime - not a plotted field
    return f"{prefix}{entry['channel']}"


# --- MQTT Callback Functions ---

def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the broker."""
    if rc == 0:
        print("Successfully connected to MQTT Broker!")
        client.subscribe(TOPIC)
        print(f"Subscribed to ({DEVICE_TYPE}) topic: {TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")


def on_message(client, userdata, msg):
    """Callback function for when a message is received."""
    now = datetime.now()
    print(f"\n--- Message received on topic: {msg.topic} at {now:%H:%M:%S} ---")

    # Check if the message is from a LoRaWAN device via ChirpStack
    if msg.topic.startswith("application/"):
        try:
            # 1. Decode the main JSON payload from ChirpStack
            import json
            chirpstack_data = json.loads(msg.payload.decode('utf-8'))
            device_name = chirpstack_data.get('deviceInfo', {}).get('deviceName', 'unknown')

            # 2. Extract the already decoded 'object'
            decoded_object = chirpstack_data.get('object')

            print(f"LoRaWAN device Name: {device_name}")
            if decoded_object:
                print(f"Decoded data (from ChirpStack 'object'): {decoded_object}")
                rssi = chirpstack_data.get('rxInfo', [{}])[0].get('rssi', 'N/A')
                print(f"Network Info: RSSI = {rssi}")
            else:
                print("Message contains no decoded 'object'.")

        except Exception as e:
            print(f"An error occurred processing LoRaWAN message: {e}")

    # Otherwise, assume it's a direct payload from an NB-IoT device
    else:
        try:
            device_id = msg.topic.split('/')[-1]
            hex_payload = msg.payload.decode()

            print(f"NB-IoT device ID: {device_id}")
            print(f"Raw payload (hex): {hex_payload}")

            decoded = IsurlogLPP.decodeIsurlogLPP(hex_payload)
            print(f"Decoded data: {decoded}")

            # Feed the live dashboard buffers, if this is a field we chart.
            for entry in decoded:
                field = _field_name(entry)
                if field in buffers:
                    buffers[field].append((now, entry["value"]))

        except Exception as e:
            print(f"An error occurred processing NB-IoT message: {e}")


# --- Live Dashboard ---

# Each entry describes one dual-axis panel: which subplot it lives in, and
# the (field, label, color) for its left and right Y-axes. "soil_*" panels
# come from a Modbus soil probe (S-Soil MTEC-02B) wired to the demo device -
# they're the point of this demo, so they get the two large panels; the
# device's own housekeeping metrics (battery, internal temp/humidity, NB-IoT
# quality) get the three smaller ones.
_PANEL_SPECS = [
    ("soil_irrigation", "ModbusInput1", "VWC (%)", "tab:blue",
                         "ModbusInput2", "EC (µS/cm)", "tab:orange", "Soil — Irrigation (VWC / EC)"),
    ("soil_diagnostics", "ModbusInput0", "Temperature (°C)", "tab:red",
                          "ModbusInput3", "Epsilon (ε)", "tab:purple", "Soil — Diagnostics (Temperature / Epsilon)"),
    ("battery", "VoltageInput0", "Voltage (mV)", "tab:blue",
                "CRateInput0", "C-Rate (%/h)", "tab:orange", "Battery"),
    ("temp_humidity", "TemperatureSensor0", "Temperature (°C)", "tab:red",
                       "HumiditySensor0", "Humidity (%)", "tab:cyan", "Internal Temperature & Humidity"),
    ("network", "ModemData0", "RSRQ (dB)", "tab:green",
                "ModemData1", "RSRP (dBm)", "tab:purple", "NB-IoT Network Quality"),
]


def build_dashboard():
    """
    Creates the figure, subplots, and (crucially) the twin Y-axes for each
    dual-field panel ONCE, up front - along with one empty Line2D per
    field, to be updated in place on every animation frame.

    This matters: calling ax.twinx() again after ax.clear() on every
    redraw (an earlier version of this script did that) creates a BRAND
    NEW twin axes each time without removing the old one - they pile up
    invisibly on top of each other frame after frame, which is what
    caused the overlapping/misaligned scales and labels spilling outside
    the window. Twin axes must be created only once; only the line data
    should change afterwards.

    Layout: 2 rows built with GridSpec rather than a uniform plt.subplots()
    grid, so the top row (soil probe) can be taller and each of its 2
    panels can span what would otherwise be 1.5 columns of a plain
    3-column grid, while the bottom row holds the 3 smaller panels.
    """
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(f"ISURLOG Live Dashboard — {DEMO_DEVICE_ID}")
    gs = fig.add_gridspec(2, 6, height_ratios=[2, 1])

    subplot_for = {
        "soil_irrigation": fig.add_subplot(gs[0, 0:3]),
        "soil_diagnostics": fig.add_subplot(gs[0, 3:6]),
        "battery": fig.add_subplot(gs[1, 0:2]),
        "temp_humidity": fig.add_subplot(gs[1, 2:4]),
        "network": fig.add_subplot(gs[1, 4:6]),
    }

    panels = {}
    for key, left_field, left_label, left_color, right_field, right_label, right_color, title in _PANEL_SPECS:
        ax = subplot_for[key]
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        # Deliberately NOT using matplotlib's date machinery here
        # (xaxis_date() / DateFormatter / AutoDateLocator). That path is
        # only wired up automatically when you call ax.plot() with real
        # datetime data - since these lines start out empty (ax.plot([],
        # [])) and get their real data later via line.set_data(), that
        # auto-detection never triggers, and date-locator/formatter combos
        # end up fighting the plain numeric axis underneath (showing raw
        # numbers, oddly fine sub-second zoom levels, or "00:00:00" for
        # every tick - each was tried and failed here). Instead, the x
        # values are elapsed seconds since _START_TIME (small numbers, see
        # _update_line), a regular numeric locator picks the tick
        # positions, and this formatter converts each one back to a real
        # clock time only for display - fully manual, nothing left for
        # matplotlib to guess about dates.
        ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, _pos: (_START_TIME + timedelta(seconds=x)).strftime("%H:%M:%S"))
        )
        ax.text(0.5, 0.5, "Waiting for data…", transform=ax.transAxes,
                 ha="center", va="center", color="gray", fontsize=9)

        (left_line,) = ax.plot([], [], color=left_color, marker="o", markersize=2, linewidth=1)
        ax.set_ylabel(left_label, color=left_color)
        ax.tick_params(axis="y", labelcolor=left_color)

        ax_right = ax.twinx()
        (right_line,) = ax_right.plot([], [], color=right_color, marker="o", markersize=2, linewidth=1)
        ax_right.set_ylabel(right_label, color=right_color)
        ax_right.tick_params(axis="y", labelcolor=right_color)

        panels[key] = {
            "left_field": left_field, "left_ax": ax, "left_line": left_line,
            "right_field": right_field, "right_ax": ax_right, "right_line": right_line,
        }

    return fig, panels


def _update_line(ax, line, field):
    """Updates one line's data in place and rescales its own axis to fit."""
    if not buffers[field]:
        return False
    times, values = zip(*buffers[field])
    # Elapsed seconds since _START_TIME (small numbers), not raw datetimes
    # or Unix timestamps - see the note in build_dashboard() on why this
    # line avoids matplotlib's date-aware axis machinery entirely.
    elapsed = [(t - _START_TIME).total_seconds() for t in times]
    line.set_data(elapsed, values)
    ax.relim()
    ax.autoscale_view()
    return True


def run_live_dashboard(fig, panels):
    """
    Updates each panel's line data from the live buffers on a timer, so
    new points appear as MQTT messages arrive - no need to close and
    reopen a window for each update, and no axes are recreated after the
    initial build_dashboard() call.
    """

    def redraw(_frame):
        for spec in panels.values():
            got_left = _update_line(spec["left_ax"], spec["left_line"], spec["left_field"])
            got_right = _update_line(spec["right_ax"], spec["right_line"], spec["right_field"])
            if got_left or got_right:
                # Remove the "Waiting for data..." placeholder once real
                # data has arrived for this panel.
                for txt in list(spec["left_ax"].texts):
                    txt.remove()

        # fig.autofmt_xdate() assumes a uniform plt.subplots() grid to
        # decide which row needs date labels - it doesn't know what to do
        # with this GridSpec layout, where rows don't share column
        # boundaries, and ends up hiding the top row's x-axis labels
        # entirely. Rotate each panel's labels individually instead.
        for ax in fig.axes:
            for label in ax.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment("right")

        # Recompute spacing on every redraw, not just once at startup.
        # tight_layout() sizes the gaps between panels based on how wide
        # the current tick labels are - called once up front (as in the
        # InfluxDB script) works there because all its data, and therefore
        # all its final tick label widths, already exist before that single
        # call. Here, data (and label widths) keep changing as new points
        # arrive, so the spacing has to be recalculated each time too,
        # or panels drift into overlapping each other as the numbers grow.
        fig.tight_layout()

    # Re-render every 2 seconds; cache_frame_data=False avoids unbounded
    # memory growth for a long-running live plot.
    return FuncAnimation(fig, redraw, interval=2000, cache_frame_data=False)


# --- Main Execution ---

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"Connecting to broker at {BROKER_URL}...")
        client.connect(BROKER_URL, BROKER_PORT, 60)
    except Exception as e:
        print(f"Could not connect to broker: {e}")
        sys.exit(1)

    # Run the MQTT network loop in a background thread so the main thread
    # is free to run matplotlib's own event loop (plt.show()).
    client.loop_start()

    fig, panels = build_dashboard()
    animation = run_live_dashboard(fig, panels)  # noqa: F841 - keep a reference so it isn't garbage-collected
    plt.tight_layout()

    try:
        plt.show()
    finally:
        client.loop_stop()
        client.disconnect()
