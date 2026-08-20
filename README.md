![ISURLOG — Industrial NB-IoT/LoRa Datalogger](docs/img/gh-banner-isurlog.jpg)

# ISURLOG Firmware

Open-source MicroPython firmware for the **ISURLOG**, ISURKI's industrial IoT datalogger.

![GitHub release (latest by date)](https://img.shields.io/github/v/release/isurki-tecnica/isurlog-firmware)
![GitHub Release Date](https://img.shields.io/github/release-date/isurki-tecnica/isurlog-firmware)
![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue)
![GitHub issues](https://img.shields.io/github/issues/isurki-tecnica/isurlog-firmware)

---

## What is ISURLOG?

**ISURLOG** is an ESP32-based industrial datalogger built for field deployments where power is scarce and connectivity is never guaranteed. The same board reads real industrial signals and gets its data out over whichever network is actually available at the site — NB-IoT, LoRaWAN, or Wi-Fi, exclusively per unit, plus a local Bluetooth Low Energy link for on-site setup and diagnostics.

* **Industrial-grade sensing:** 4-20 mA analog inputs, Modbus RTU (RS485), PT100/PT1000 (2/3/4-wire), digital pulse counting, internal/external temperature & humidity, an on-board accelerometer for tamper/vandalism detection, and Isurnode expansion support.
* **Built for batteries:** as low as **~20 µA** in deep sleep, with the ESP32 waking on a schedule, on an external interrupt, or on-demand from the network (eDRX/Class C).
* **One firmware, three networks:** NB-IoT (Nordic nRF9160/nRF9151) and LoRaWAN (RAK3172, RUI3/AT) are interchangeable on the same hardware; Wi-Fi is available where cellular/LoRa coverage isn't. All three enforce modern security (WPA2+, TLS, LoRaWAN OTAA).
* **Remotely manageable, not just remotely readable:** configuration, sensor setup, firmware updates (OTA and wired), and even a live MicroPython REPL are all reachable from **[IsurDASH](https://isurdash.isurki.com)**, ISURKI's cloud platform — without a truck roll.
* **Real MicroPython, not a black box:** this is a genuine fork of [MicroPython](https://micropython.org), with ISURKI's own application code and drivers frozen in as regular Python modules (`app/`, `ports/esp32/modules/`) — readable, debuggable, and hackable, not a proprietary firmware blob.
* **Open data, no lock-in:** integrate directly with historical (InfluxDB) or real-time (MQTT) data access — see the reference implementations in the wiki, including a live public demo you can query with zero setup.

---

## Documentation

Everything — hardware, firmware architecture, the IsurDASH platform, and data integration APIs — lives in the **[Project Wiki](https://github.com/isurki-tecnica/isurlog-firmware/wiki)**.

| I want to... | Start here |
| :--- | :--- |
| Install and operate an ISURLOG in the field | [Sensor Connections](https://github.com/isurki-tecnica/isurlog-firmware/wiki/2-Sensor-Connections), [Installation and Commissioning](https://github.com/isurki-tecnica/isurlog-firmware/wiki/5-Installation-and-Commissioning) |
| Manage a fleet from IsurDASH | [7. IsurDASH Platform](https://github.com/isurki-tecnica/isurlog-firmware/wiki/7-IsurDASH-Platform) |
| Build, modify, or contribute to the firmware | [1. Build Environment Setup](https://github.com/isurki-tecnica/isurlog-firmware/wiki/1-Build-Environment-Setup), [2.1 Module & Library Reference](https://github.com/isurki-tecnica/isurlog-firmware/wiki/2.1-Module-and-Library-Reference), [7. Contribution Guide](https://github.com/isurki-tecnica/isurlog-firmware/wiki/7-Contribution-Guide) |
| Pull ISURLOG data into my own systems | [9. Data Access Overview](https://github.com/isurki-tecnica/isurlog-firmware/wiki/9-Data-Access-Overview) |

---

## Firmware Releases

Every release publishes ready-to-flash binaries — the ESP32 firmware, plus the NB-IoT (nRF9151) and LoRaWAN (RAK3172) modem firmware — so you don't need to compile anything unless you're modifying the firmware itself.

➡️ **[Releases](https://github.com/isurki-tecnica/isurlog-firmware/releases)**

Prefer a guided, no-cable-required update? IsurDASH can push new ESP32 firmware to a deployed device directly — see **[7.8 Device Maintenance](https://github.com/isurki-tecnica/isurlog-firmware/wiki/7.8-Device-Maintenance)**.

---

## Contributing

Bug fixes, new sensor drivers, and documentation improvements are all welcome — see the **[Contribution Guide](https://github.com/isurki-tecnica/isurlog-firmware/wiki/7-Contribution-Guide)** for how this repository is organized (it's a full MicroPython fork — ISURKI's own code lives in `app/` and `ports/esp32/modules/`) and how to submit a pull request.

---

## License

This project is a derivative work of [MicroPython](https://github.com/micropython/micropython) (MIT-licensed). Due to the inclusion of GPL-3.0-licensed components, the combined work is distributed under the **GNU General Public License v3.0** — see [`LICENSE`](LICENSE) for the full text.

## Quick Links

* **IsurDASH Cloud Platform:** [isurdash.isurki.com/login](https://isurdash.isurki.com/login)
* **3D-Printed Accessories:** [Printables @isurki_3854777](https://www.printables.com/@isurki_3854777/models)
* **Support:** (+34) 943-635437 · tecnica@isurki.com
