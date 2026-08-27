# ISURLOG: Industrial IoT Datalogger (Open Source Firmware)

![ISURLOG — Industrial NB-IoT/LoRa Datalogger](images/gh-banner-isurlog.jpg){width="700"}

**ISURLOG** is an ESP32-based industrial datalogger built for field deployments where power is scarce and connectivity is never guaranteed. Real MicroPython firmware, real industrial signals, remotely managed from day one.

* **Industrial-grade sensing** — 4-20 mA analog, Modbus RTU (RS485), PT100/PT1000, digital pulse counting, internal/external temperature & humidity, and an on-board accelerometer for tamper/vandalism detection.
* **Built for batteries** — as low as ~20 µA in deep sleep. An on-board energy-harvesting charger tops up from almost anything: a 0.3V TEG, a micro solar panel, a full 5V panel, or a plain USB charger.
* **One firmware, multiple networks** — NB-IoT, LTE-M, DECT NR+, and satellite NTN via the nRF9151, or LoRaWAN, exclusively per unit, plus Wi-Fi and local BLE for setup.
* **Remotely manageable, not just remotely readable** — configuration, sensor setup, OTA updates, and a live MicroPython REPL, all from [IsurDASH](https://isurdash.isurki.com), without a truck roll.
* **Real MicroPython, not a black box** — a genuine fork of [MicroPython](https://micropython.org), readable and hackable at every layer.

---

## Where to begin

| 🛠️ Use and Hardware | 💻 Firmware Development | ☁️ Data Integration & APIs |
| :--- | :--- | :--- |
| Installation, sensor setup, and IsurDASH. | Build environment, architecture, contributing. | Historical/real-time data access, downlink API. |
| **Start here:** [1. Sensor Connections](sensor-connections.md) | **Start here:** [1. Build Environment Setup](build-environment.md) | **Start here:** [1. Data Access Overview](data-access-overview.md) |

Running into a problem in the field? See [Troubleshooting](troubleshooting.md).

---

## Estimate battery life

The interactive **[Power Budget Calculator](power-budget.md)** models a device's full duty cycle — connectivity, the sensors you'd configure in IsurDASH, and your battery setup (Li-Ion or Li-SOCl2) — for a real estimate instead of a rule of thumb.

---

## See it in action

Don't just take our word for it — try the real platform and pull real data yourself, no signup required:

* **IsurDASH demo account** — log in at [isurdash.isurki.com/login](https://isurdash.isurki.com/login) and explore the dashboard, device list, alarms, and configuration screens for yourself:
    * **Email:** `isurdash.demo@gmail.com`
    * **Password:** `TEST123456`
* **Data integration examples** — two ready-to-run Python scripts, pre-filled with public demo credentials, in the [`data_integration/`](https://github.com/isurki-tecnica/isurlog-firmware/tree/main/data_integration) folder of the firmware repo — pull historical data from InfluxDB, or subscribe to a live MQTT stream.

---

## Roadmap

ISURLOG is an actively maintained product with real field deployments, not a prototype — development is continuous, and this table is kept honest about what's battle-tested versus what's a newer, still-hardening addition.

| Feature | Type | Status | Available Since |
| :--- | :--- | :--- | :--- |
| Asynchronous function architecture for parallel task execution, reducing the time the datalogger is powered on | Firmware | 🧪 Experimental | v2.0.1 (pre-release) |
| Non-rechargeable Li-SOCl2 battery support | Hardware | 🧪 Experimental | PCB v3.3 |
| Larger transmission buffer using external I2C EEPROM (24LC1025), removing the current RTC RAM size limitation | Firmware | 🧪 Experimental | — |
| Accelerometer alarm → forced immediate transmission | Firmware | 🔜 Planned | — |
| Automatic NB-IoT/LTE-M connection mode | Firmware | 🔜 Planned | — |
| DECT NR+ (chip-capable via nRF9151) | Firmware | 🔜 Planned | — |
| Isurnode Modbus expansion module | Hardware + Firmware | 🔜 Planned | — |
| TinyML — on-device inference for lightweight tasks like local anomaly detection or predictive maintenance, without a round trip to the cloud | Firmware | 🔜 Planned | — |
| RAK3172 firmware updates directly from IsurDASH (currently requires an external web tool) | Firmware | 🔜 Planned | — |
| 3D-printable enclosure files, published on Printables | Hardware | 💬 In discussion | — |
| Migration from ESP32 to ESP32-S3 or the newly-announced ESP32-S31 (final choice not yet decided) — native USB and a RISC-V LP core in place of today's ULP FSM coprocessor | Hardware + Firmware | 💬 In discussion | — |

<details markdown="1">
<summary>✅ Already stable (11 features)</summary>

| Feature | Type | Status | Available Since |
| :--- | :--- | :--- | :--- |
| NB-IoT / LoRaWAN / BLE connectivity | Hardware + Firmware | ✅ Stable | v1.0.0 |
| Wi-Fi connectivity & remote REPL over Wi-Fi | Firmware | ✅ Stable | v1.0.5-beta |
| Core sensors (Analog, Digital, Modbus, PT100) | Firmware | ✅ Stable | v1.0.0 |
| Internal (SHT30) & external (BME280) temperature/humidity sensors | Firmware | ✅ Stable | v1.0.3 |
| IsurDASH integration (remote config, OTA updates, live REPL) | Firmware | ✅ Stable | v1.0.0 |
| Historical (InfluxDB) & real-time (MQTT) data access | Firmware | ✅ Stable | v1.0.0 |
| NB-IoT signal quality logging (RSRQ/RSRP) | Firmware | ✅ Stable | FW v1.1.6 |
| Configurable sensor supply voltage (9-24V) | Hardware | ✅ Stable | PCB v3.0 |
| Vandalism alert (accelerometer + GPS position) | Hardware + Firmware | ✅ Stable | PCB v3.0 · FW v1.1.6 |
| Battery type & State of Charge reporting | Hardware + Firmware | ✅ Stable | PCB v3.0 · FW v1.1.9 |
| Internal accelerometer (LIS2DH12) alarm thresholds | Firmware | ✅ Stable | FW v1.1.6 |

</details>

**Have a suggestion or an idea?** Open a [GitHub Issue](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) describing it — feature requests and hardware integration ideas are welcome, not just bug reports. See [7.4 Using the Issues Tracker](contribution-guide.md#74-using-the-issues-tracker) for what makes a good one.

---

## Get ISURLOG

ISURLOG is sold directly by ISURKI, configured for your specific connectivity and sensor setup — [request a quote](mailto:tecnica@isurki.com?subject=ISURLOG%20-%20Quote%20Request&body=Hi%20ISURKI%20team%2C%0A%0AI'm%20interested%20in%20ISURLOG%20for%20the%20following%20use%20case%3A%0A%0A-%20Application%2Fenvironment%3A%20%0A-%20Approximate%20quantity%3A%20%0A-%20Preferred%20connectivity%20(NB-IoT%2FLTE-M%2C%20LoRaWAN%2C%20or%20Wi-Fi)%3A%20%0A-%20Country%2Fregion%3A%20%0A%0AThanks!) and we'll get back to you with pricing and availability.

---

## Quick Resources

* **GitHub Repository:** [isurki-tecnica/isurlog-firmware](https://github.com/isurki-tecnica/isurlog-firmware)
* **Firmware Releases:** [Releases page](https://github.com/isurki-tecnica/isurlog-firmware/releases)
* **IsurDASH Cloud Platform Login:** [isurdash.isurki.com/login](https://isurdash.isurki.com/login)
* **Technical Support:** (+34) 943-635437 · tecnica@isurki.com
