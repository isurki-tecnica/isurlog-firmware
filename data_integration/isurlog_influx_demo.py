"""
Reference implementation for querying ISURLOG historical data from InfluxDB.

This script includes a live, public, READ-ONLY demo you can run right now,
with no credentials of your own: the defaults below point at the
"Isurlog_DEMO" bucket, which contains only a single test device (c-866)
and nothing else. To query your own real devices, replace URL/TOKEN/BUCKET
with the private credentials Isurki gives you (see 10.3 Connection
Parameters in the wiki).

Dependencies: see requirements.txt in this folder
(pip install -r requirements.txt).
"""

import influxdb_client
from datetime import datetime

# --- Connection Parameters ---
# The values below are a PUBLIC, READ-ONLY demo token, scoped to a single
# bucket ("Isurlog_DEMO") that only contains one test device (c-866) - it
# cannot read any other client's data. Replace all three with your own
# private credentials to query your real devices.
URL = "https://influxisurdash.isurki.com"
ORG = "isurki"
TOKEN = "NYPRAdzMmRByMfPQSctfgtDYmGuXUvKdWFbhlPKw8fmwjXryQA1n94OlIYthBzZICr6uBHuVPm85mNuK09ZFfQ=="  # Public demo token (read-only)
BUCKET = "Isurlog_DEMO"  # Public demo bucket


def get_isurlog_readings(device_id: str, days_range: int = 7) -> list:
    """
    Connects to InfluxDB and queries ALL recorded values within a specified range
    for a given device and returns them as a structured list of dictionaries.

    Args:
        device_id: The unique identifier (e.g., EUI) of the Isurlog device.
        days_range: The number of past days to query data from.

    Returns:
        A list of dictionaries, where each dictionary represents one reading record,
        or an empty list if no data is found or an error occurs.
    """

    # It is recommended to create one client instance and reuse it.
    with influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
        query_api = client.query_api()

        # Flux query to get ALL values within the range for a device
        # We query for ALL fields that exist in the measurement (by removing the field filter)
        query = f'''
        from(bucket: "{BUCKET}")
          |> range(start: -{days_range}d)
          |> filter(fn: (r) => r["isurlog_id"] == "{device_id}")
        '''

        all_records = []

        try:
            tables = query_api.query(query, org=ORG)

            # Temporary dictionary to group measurements by timestamp (using the datetime object)
            grouped_readings = {}

            for table in tables:
                for record in table.records:
                    # The record.get_time() returns a native Python datetime object
                    time_dt = record.get_time()
                    field = record.get_field()
                    value = record.get_value()

                    # Use the raw datetime object as the key for grouping
                    if time_dt not in grouped_readings:
                        # Store the datetime object directly
                        grouped_readings[time_dt] = {"Time": time_dt}

                    grouped_readings[time_dt][field] = value

            # Convert dictionary into a sorted list of records
            for time in sorted(grouped_readings.keys()):
                all_records.append(grouped_readings[time])

        except Exception as e:
            print(f"An error occurred while querying InfluxDB: {e}")
            return []

        return all_records


def print_data_as_table(data: list):
    """Imprime los datos recuperados en un formato tabular limpio."""
    if not data:
        return

    # 1. Collect all unique column headers
    headers = set()
    for record in data:
        headers.update(record.keys())

    # Ensure "Time" is the first header
    sorted_headers = ["Time"] + sorted([h for h in headers if h != "Time"])

    # 2. Print Header Row
    print("\n| " + " | ".join(sorted_headers) + " |")
    print("|" + "---|" * len(sorted_headers))

    # 3. Print Data Rows
    for record in data:
        row_values = []
        for header in sorted_headers:
            value = record.get(header)

            if header == "Time" and isinstance(value, datetime):
                # Format the native datetime object directly
                row_values.append(value.strftime("%Y-%m-%d %H:%M:%S"))
            elif value is not None:
                # Format float/int values
                row_values.append(f"{value:.2f}" if isinstance(value, float) else str(value))
            else:
                row_values.append("-")  # Use dash for missing values

        print("| " + " | ".join(row_values) + " |")


def _plot_dual_axis(ax, data: list, left_field: str, left_label: str, left_color: str,
                     right_field: str = None, right_label: str = None, right_color: str = None,
                     title: str = None):
    """
    Plots up to two fields on a single subplot: `left_field` on the left
    Y-axis, and (optionally) `right_field` on a second, independent Y-axis
    on the right - useful when the two values are on very different scales
    (e.g. millivolts vs. a percentage rate).
    """
    left_points = sorted(
        ((r["Time"], r[left_field]) for r in data if r.get(left_field) is not None),
        key=lambda p: p[0],
    )
    ax.set_title(title or left_field)
    if left_points:
        lt, lv = zip(*left_points)
        ax.plot(lt, lv, color=left_color, marker="o", markersize=2, linewidth=1)
        ax.set_ylabel(left_label, color=left_color)
        ax.tick_params(axis="y", labelcolor=left_color)
    ax.grid(True, alpha=0.3)

    if right_field:
        right_points = sorted(
            ((r["Time"], r[right_field]) for r in data if r.get(right_field) is not None),
            key=lambda p: p[0],
        )
        if right_points:
            ax_right = ax.twinx()
            rt, rv = zip(*right_points)
            ax_right.plot(rt, rv, color=right_color, marker="o", markersize=2, linewidth=1)
            ax_right.set_ylabel(right_label, color=right_color)
            ax_right.tick_params(axis="y", labelcolor=right_color)


def plot_dashboard(data: list, target_device: str):
    """
    Builds a single window with a 2-row grid of charts summarizing the
    device's data - instead of one matplotlib window per field, which
    would force you to close each one before seeing the next.

    Layout (2 large panels on top, 3 smaller ones below - built with
    GridSpec rather than plt.subplots() so the top row can be taller and
    each of its 2 panels can span what would otherwise be 1.5 columns of
    a uniform 3-column grid):
        Top row (large) - the soil probe, the reason for this layout:
            1. Soil - Irrigation: VWC/ModbusInput1 (left) vs. EC/ModbusInput2 (right)
            2. Soil - Diagnostics: Temperature/ModbusInput0 (left) vs. Epsilon/ModbusInput3 (right)
        Bottom row (small) - the device's own housekeeping metrics:
            3. Battery: VoltageInput0 (left) vs. CRateInput0 (right)
            4. Internal Temperature & Humidity: TemperatureSensor0 (left) vs. HumiditySensor0 (right)
            5. NB-IoT Network Quality: ModemData0/RSRQ (left) vs. ModemData1/RSRP (right)
    """
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(f"ISURLOG Dashboard — {target_device}")
    gs = fig.add_gridspec(2, 6, height_ratios=[2, 1])

    # --- Top row (large): soil probe (Modbus S-Soil MTEC-02B) ---

    # 1. Soil - Irrigation: moisture vs. electrical conductivity.
    _plot_dual_axis(
        fig.add_subplot(gs[0, 0:3]), data,
        left_field="ModbusInput1", left_label="VWC (%)", left_color="tab:blue",
        right_field="ModbusInput2", right_label="EC (µS/cm)", right_color="tab:orange",
        title="Soil — Irrigation (VWC / EC)",
    )

    # 2. Soil - Diagnostics: temperature vs. raw dielectric permittivity.
    _plot_dual_axis(
        fig.add_subplot(gs[0, 3:6]), data,
        left_field="ModbusInput0", left_label="Temperature (°C)", left_color="tab:red",
        right_field="ModbusInput3", right_label="Epsilon (ε)", right_color="tab:purple",
        title="Soil — Diagnostics (Temperature / Epsilon)",
    )

    # --- Bottom row (small): the device's own housekeeping metrics ---

    # 3. Battery: voltage vs. C-rate.
    _plot_dual_axis(
        fig.add_subplot(gs[1, 0:2]), data,
        left_field="VoltageInput0", left_label="Voltage (mV)", left_color="tab:blue",
        right_field="CRateInput0", right_label="C-Rate (%/h)", right_color="tab:orange",
        title="Battery",
    )

    # 4. Internal temperature and humidity.
    _plot_dual_axis(
        fig.add_subplot(gs[1, 2:4]), data,
        left_field="TemperatureSensor0", left_label="Temperature (°C)", left_color="tab:red",
        right_field="HumiditySensor0", right_label="Humidity (%)", right_color="tab:cyan",
        title="Internal Temperature & Humidity",
    )

    # 5. NB-IoT network quality: RSRQ vs. RSRP.
    _plot_dual_axis(
        fig.add_subplot(gs[1, 4:6]), data,
        left_field="ModemData0", left_label="RSRQ (dB)", left_color="tab:green",
        right_field="ModemData1", right_label="RSRP (dBm)", right_color="tab:purple",
        title="NB-IoT Network Quality",
    )

    # fig.autofmt_xdate() assumes a uniform plt.subplots() grid to decide
    # which row needs date labels - it doesn't know what to do with a
    # GridSpec layout where rows don't share column boundaries (the top
    # row's 2 wide panels vs. the bottom row's 3 narrower ones), and ends
    # up hiding the top row's x-axis labels entirely. Rotate each panel's
    # labels individually instead, so every panel keeps its own dates.
    for ax in fig.axes:
        for label in ax.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment("right")

    plt.tight_layout()
    plt.show()


# --- Example Usage ---
if __name__ == "__main__":
    # c-866 is the public demo device (see Isurlog_DEMO above). It reports:
    # accelerometer (X/Y/Z), internal temperature/humidity, battery C-rate,
    # battery voltage, NB-IoT signal quality (RSRQ/RSRP), and readings from
    # a Modbus soil probe (S-Soil MTEC-02B): Temperature (ModbusInput0),
    # VWC (ModbusInput1), EC (ModbusInput2), and Epsilon (ModbusInput3).
    target_device = "c-866"
    data = get_isurlog_readings(target_device, days_range=7)

    if data:
        print(f"--- Retrieved Data for device '{target_device}' (Last 7 Days) ---")
        print_data_as_table(data)
        plot_dashboard(data, target_device)
    else:
        print(f"No data found for device '{target_device}' or an error occurred.")
