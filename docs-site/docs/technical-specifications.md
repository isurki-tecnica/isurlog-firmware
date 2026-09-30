# Technical Specifications

A single-page reference for the ISURLOG's hardware specifications. For how to wire, configure, or program any of this, see [1. Sensor Connections](sensor-connections.md) onward.

## Physical

| | |
| :--- | :--- |
| **Dimensions** | 144 × 145 × 80 mm |
| **Weight** | ~540 g (without batteries or DIN mounting accessories) |
| **Enclosure** | 3D-printed PETG, **IP66** |
| **Mounting** | Wall (125 × 125 mm hole pattern) or DIN rail — see [4.2. Physical Mounting](installation-commissioning.md#42-physical-mounting) |
| **Operating temperature** | -20 °C to +60 °C |
| **Certification** | CE. Designed following the requirements of the Cyber Resilience Act (CRA) |

## Power

| | |
| :--- | :--- |
| **Deep sleep current** | As low as ~20 µA (full system, modem included and network-attached) — see [1. Consumption Graphs](consumption-graphs.md) |
| **Batteries** | 1–5× Li-Ion 18650 (rechargeable, up to 17000 mAh total), or up to 2× non-rechargeable Li-SOCl2 (up to 38000 mAh total, requires PCB v3.3+) |
| **Charging inputs** | 0.3V TEG, micro solar panel, full 5V solar panel, or USB charger — energy-harvesting charger built in (Li-Ion only; not used with Li-SOCl2) |
| **Sensor power outputs** | Software-configurable regulator, 9–24 V; plus a separate fixed 5 V regulator |

## Connectivity

One connectivity module per unit, fixed at build time:

| | |
| :--- | :--- |
| **Cellular** | NB-IoT / LTE-M, satellite (NTN), and DECT NR+ (chip-capable via the nRF9151; firmware support is planned, not yet available — see the [Roadmap](index.md#roadmap)). |
| **LoRaWAN** | Class A (Class B/C supported, not recommended for battery-powered use) |
| **Wi-Fi** | 802.11 b/g/n, 2.4 GHz (ESP32) |
| **Bluetooth (BLE)** | Bluetooth v4.2 BR/EDR + BLE (ESP32). On-demand, magnet-activated — see [1.8. Internal Sensors and Diagnostics](sensor-connections.md#18-internal-sensors-and-diagnostics) |
| **eSIM** | Integrated, 500 MB or 5 years (whichever comes first) — see [1. Parts and Accessories](parts-and-accessories.md) |
| **Nano SIM slot** | External Nano-SIM slot also available (e.g. for satellite/NTN service via a third-party SIM) |

## Inputs & Outputs

### Inputs

| Input | Spec |
| :--- | :--- |
| **Analog (4-20 mA)** | 4 channels (AIN0–AIN3), 16-bit ADC resolution, supports both passive (ISURLOG-powered) and active (externally powered) sensors — see [1.1. Analog Inputs (4-20mA)](sensor-connections.md#11-analog-inputs-4-20ma) |
| **Digital** | 1 channel, dry-contact style (ISURLOG sources the high signal, the sensor returns it) — state reading or pulse counting, minimum pulse width 200 ms — see [1.2. Digital Input (State and Pulse Counter)](sensor-connections.md#12-digital-input-state-and-pulse-counter) |
| **Extra digital I/O** | 3 general-purpose channels (GP3–GP5), through the onboard I/O expander — state reading, not ULP-based pulse counting like the main digital input — see [1.7. AUX-IO Connector](sensor-connections.md#17-aux-io-connector) |
| **Modbus (RS485)** | Up to 32 sensors, built-in 120 Ω termination. Standard firmware baud rates: 9600 / 19200 / 38400 / 57600 / 115200 — see [1.3. Modbus Input (RS485)](sensor-connections.md#13-modbus-input-rs485) |
| **PT100 / PT1000** | 1 channel, 15-bit ADC resolution, ~0.03125 °C nominal resolution (varies with RTD nonlinearity), ±0.5 °C (0.05% of full scale) max total accuracy over all operating conditions — see [1.4. PT100 Temperature Sensor Input](sensor-connections.md#14-pt100-temperature-sensor-input) |
| **I2C (QWIIC)** | I2C input for plug-in expansion sensors, standard QWIIC connector — see [1.6. QWIIC I2C Port](sensor-connections.md#16-qwiic-i2c-port) |
| **Internal temperature & humidity** | Onboard, inside the enclosure — early warning for water ingress or overheating — see [1.8. Internal Sensors and Diagnostics](sensor-connections.md#18-internal-sensors-and-diagnostics) |
| **Accelerometer** | Onboard, tamper/vandalism detection with configurable alarm thresholds — see [1.8. Internal Sensors and Diagnostics](sensor-connections.md#18-internal-sensors-and-diagnostics) |

### Outputs

| Output | Spec |
| :--- | :--- |
| **Relay (main terminal block)** | 1× solid-state relay, normally open (COM0/NO0), max 60 V / 2 A — see [1.5. Digital Output (Relay)](sensor-connections.md#15-digital-output-relay) |
| **Relays (AUX-IO)** | 2× additional solid-state relays, normally open, max 60 V / 500 mA per channel — see [1.7. AUX-IO Connector](sensor-connections.md#17-aux-io-connector) |

## Software

| | |
| :--- | :--- |
| **Firmware** | MicroPython, open source (GPL-3.0) — [GitHub](https://github.com/isurki-tecnica/isurlog-firmware) |
| **Cloud platform** | [IsurDASH](https://isurdash.isurki.com) — free, unlimited data storage, no per-device fee |
| **Data access** | Historical (InfluxDB) and real-time (MQTT) — see [1. Data Access Overview](data-access-overview.md) |
