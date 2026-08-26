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
| **Start here:** [2. Sensor Connections](sensor-connections.md) | **Start here:** [1. Build Environment Setup](build-environment.md) | **Start here:** [9. Data Access Overview](data-access-overview.md) |

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

## Get ISURLOG

ISURLOG is sold directly by ISURKI, configured for your specific connectivity and sensor setup — [request a quote](mailto:tecnica@isurki.com?subject=ISURLOG%20-%20Quote%20Request&body=Hi%20ISURKI%20team%2C%0A%0AI'm%20interested%20in%20ISURLOG%20for%20the%20following%20use%20case%3A%0A%0A-%20Application%2Fenvironment%3A%20%0A-%20Approximate%20quantity%3A%20%0A-%20Preferred%20connectivity%20(NB-IoT%2FLTE-M%2C%20LoRaWAN%2C%20or%20Wi-Fi)%3A%20%0A-%20Country%2Fregion%3A%20%0A%0AThanks!) and we'll get back to you with pricing and availability.

---

## Quick Resources

* **GitHub Repository:** [isurki-tecnica/isurlog-firmware](https://github.com/isurki-tecnica/isurlog-firmware)
* **Firmware Releases:** [Releases page](https://github.com/isurki-tecnica/isurlog-firmware/releases)
* **IsurDASH Cloud Platform Login:** [isurdash.isurki.com/login](https://isurdash.isurki.com/login)
* **Technical Support:** (+34) 943-635437 · tecnica@isurki.com
