# 2.1 Module & Library Reference (API Guide)

!!! note "Scope"
    this page documents the **production** code tree — `app/main.py`, `ports/esp32/modules/modules/` (high-level wrappers) and `ports/esp32/modules/lib/` (low-level drivers) — as tracked on this repository's `main` branch. If you work from the internal development sandbox, some experimental modules (async variants, alternate storage drivers, etc.) may not be listed here yet because they haven't been promoted to this repository. See **[8. Development Workflow (Sandbox → Production)]** *(coming soon)* for how that promotion works.

This page complements **[2. Architecture Overview](architecture-overview.md)**: that page explains the `/lib` vs `/modules` split conceptually, this one is the per-file reference — what each module does, what it depends on, and what configuration it reads.

---

## 2.1.1 Quick Reference

| Module (`modules/`) | Purpose | Sync/Async |
|---|---|---|
| `utils.py` | Logging (`log_debug`/`log_info`/...) and small helpers. Imported by almost everything. | sync |
| `config_manager.py` | Loads `static_config.json` / `dynamic_config.json`, applies remote (downlink) config updates. | sync |
| `_auth.py` | PIN-protected REPL console lock (AES). | sync |
| `version.py` | Firmware version constant. | sync |
| `power_manager.py` | RTC (DS3231/RV3028), wake-up scheduling, voltage rails, deep sleep. | sync |
| `rtc_memory.py` | Deep-sleep-persistent state (cycle counter, valve states, payload buffer). | sync |
| `wifi.py` | Wi-Fi STA connection, enforces WPA2+. | async |
| `nb_iot.py` | Nordic nRF9160 modem driver: network registration, MQTT-over-modem, HTTP (OTA), GPS/NTN. | async |
| `lorawan.py` | RAK3172 (RUI3 AT) LoRaWAN modem driver: join, uplink, downlink, Class C polling. | async |
| `umqttsimple.py` | Lightweight MQTT client (Wi-Fi transport only). | sync |
| `ble_manager.py` | BLE GATT server for local config/monitoring (magnet-triggered). | async |
| `downlink_manager.py` | Unifies downlink handling across Wi-Fi/NB-IoT/LoRaWAN; triggers OTA and remote config. | async |
| `remote_repl.py` | Remote Python REPL over MQTT (debugging backdoor — see notes). | mixed |
| `analog_sensor.py` | ADS1115 4-20mA analog input wrapper. | sync |
| `digital_sensor.py` | ULP-based low-power pulse counter. | sync |
| `bme_sensor.py` | Auto-detecting BMP280/BME280/BME680 wrapper (temp/hum/press/gas + IAQ). | sync |
| `sht30_sensor.py` | SHT30 temp/humidity wrapper. | sync |
| `max31865_sensor.py` | PT100/PT1000 (via MAX31865) wrapper. | sync |
| `modbus_sensor.py` | Modbus RTU master wrapper over RS485. | sync |
| `accel_manager.py` | LIS2DH12 + MCP23008 anti-theft/tamper detection. | sync |
| `battery_monitor.py` | ESP32 ADC battery voltage fallback (no MAX17048). | sync |
| `internal_storage.py` | FIFO payload backup on internal flash. | sync |
| `update_manager.py` | OTA support: checksum, base64 decode, safe `main.py` replacement. | sync |
| `led_manager.py` | ULP-driven status LED blink pattern. | sync |

---

## 2.1.2 Modules — Detailed Reference

### Core / Boot

**`utils.py`**

- Purpose: centralized logging (`log_debug`, `log_info`, `log_warning`, `log_error`) gated by `static_config.log_level`, plus `get_datetime_string()` / `save_data_to_file()`.
- Depends on: nothing (base module — imported by nearly every other module).
- Config: `static_config.log_level`, resolved from `config_manager` on first use (a deferred import — `config_manager.py` imports `utils` at module level, so importing back at `utils`' module level would be circular).

**`config_manager.py`**

- Purpose: the canonical owner of `static_config.json` (immutable, hardware) and `dynamic_config.json` (runtime-mutable). Applies remote config updates via `CONFIG_MAP`, which maps ~90 remote command names (e.g. `setLatencyTime`) to nested JSON paths.
- Public API: `ConfigManager.get_static(*keys, default=None)`, `get_dynamic(*keys, default=None)`, `apply_single_update(...)`, `apply_conf_update(decoded_data)`, `save_dynamic_config()`. Global singleton: `config_manager`.
- Depends on: `utils`.

**`_auth.py`**

- Purpose: PIN-gated REPL console lock. Runs automatically on import (not just definitions) — up to 3 attempts, resets the device on failure.
- Public API: `run_authentication()`, `pad_data(...)`, `get_encrypted_pin_secret()`.
- Depends on: `config_manager` (reads `static_config.pin`); uses builtin `cryptolib` (AES-ECB) directly.

**`version.py`**

- Purpose: single `VERSION` constant, shown in the boot banner. Bump this on every release.

### Power & Time

**`power_manager.py`**

- Purpose: the system's power/time hub. Detects the RTC chip present (DS3231 or RV3028), syncs time from NB-IoT/Wi-Fi(NTP)/LoRaWAN/GPS, computes the next aligned wake-up, drives the 12V/5V rails and digital outputs, sets CPU frequency, configures wake sources, and triggers deep sleep. Global singleton: `pm`.
- Public API (selection): `check_rtc_status()`, `set_rtc_time(time_str, mode)`, `seconds2wakeup()`, `control_5v(state)`, `control_vdc(state)`, `configure_wakeup_sources(...)`, `go_to_sleep()`.
- Depends on: `lib/uds3231` or `lib/RV3028` (whichever is detected on I2C).
- Config: `static_config.pinout.{i2c,rs485,control,magnet_pin}`, `dynamic_config.general.{rtc_sync,latency_time,magnet_wakeup}`, `dynamic_config.digital_config.{enable,counter}`.
- Note: `downlink_manager.py`'s proportional-valve (EV) and OTA-failure sleeps use plain `time.sleep_ms()` / `await asyncio.sleep_ms()` directly rather than a method on `power_manager` — keep that in mind if you're looking for a "sleep" helper here, there isn't one.

**`rtc_memory.py`**

- Purpose: state kept in ESP32 RTC memory (survives deep sleep, not power loss): accumulated cycle counter, alarm flag, manual valve (EV) states, last RTC-sync timestamp, and a buffer of encoded LPP payloads pending transmission.
- Public API: `get_alarm_flag`/`set_alarm_flag`, `get_last_rtc_sync`/`set_last_rtc_sync`, `rtc_resync_due(...)`, `get_ev_state`/`set_ev_state`, `store_payload(...)`, `get_payloads()`, `should_transmit()`.
- Depends on: `config_manager` (reads `general.register_acumulator`).
- Note: hand-rolled binary layout with fixed byte offsets; respects the ~2048-byte hardware limit of `rtc.memory()`, trimming `n_cycles` automatically if config exceeds it.

### Connectivity

**`wifi.py`**

- Purpose: Wi-Fi STA connection with a security gate — refuses to associate below WPA2-PSK (explicit CRA/Cyber Resilience Act compliance comment in the code).
- Public API: `is_connected()`, `do_connect(ssid, password, timeout_seconds=15)` *(async)*, `do_disconnect()` *(async)*.
- Depends on: builtin `network` only. SSID/password are passed in by `main.py` from `dynamic_config.communications.wifi`.

**`nb_iot.py`** *(largest module, ~57 KB)*

- Purpose: driver for the Nordic nRF9160-family NB-IoT/LTE-M modem (Nordic SLM AT%/AT#X command set): network registration (with operator selection/blacklist), MQTT client over the modem, HTTP client for OTA downloads, GPS/NTN, sleep/wake management.
- Public API (all `async` unless noted): `connect(connection_preference, edrx=True, apn=None, ntn=False)`, `wake_up()`, `sleep()`, `hard_reset()`, `mqtt_configure/connect/publish/subscribe`, `get_mqtt_messages()` *(sync)*, `send_udp_data(...)`, `download_file(...)` (chunked HTTP range requests for OTA), `get_gps_coords(...)`, `connect_ntn(...)`, `get_signal_data()`.
- Depends on: no `lib/` drivers — talks AT directly over UART.
- Config: `dynamic_config.communications.cellular_iot.{external_sim,preference,apn,ntn,signal_data}`, `static_config.pinout.control.en_nbiot_pin`, `static_config.pinout.nb-iot.{tx_pin,rx_pin}`.
- **AT command groups used** (grep-verified against source):
  - *Network:* `AT+CFUN=`, `AT#XGPIOCFG`/`AT#XGPIO` (SIM select), `AT%XSYSTEMMODE=`, `AT%XBANDLOCK=`, `AT+CGDCONT=`, `AT%XMONITOR`, `AT%RAI`, `AT%PERIODICSEARCHCONF=`, `AT+CEDRXS=`, `AT%XPTW=`, `AT+COPS=` (scan/manual/auto), `AT+CPSMS=`, `AT+CEDRXRDP`, `AT+CESQ`, `AT+CGPADDR=`.
  - *Clock:* `AT+CCLK?`.
  - *Sleep/reset:* `AT#XSLEEP=`, `AT#XRESET` (soft); `hard_reset()` instead cuts modem power physically via `en_nbiot_pin` for 5s.
  - *GPS:* `AT#XGPS=1,0,0,0` / `AT#XGPS=0`.
  - *MQTT over modem:* `AT#XMQTTCFG=`, `AT#XMQTTCON=`, `AT#XMQTTPUB=`, `AT#XMQTTSUB=` (inbound messages arrive as `#XMQTTMSG:` URCs).
  - *UDP socket:* `AT#XSOCKET=`, `AT#XSENDTO=`.
  - *HTTP (OTA):* `AT#XHTTPCCON=`, `AT#XHTTPCREQ="GET",...,"Range: bytes=X-Y"` (chunked download; response via `#XHTTPCRSP:` URC).
- Note: comments like `"USER BASE v17"`, `"CHANGE"`, `"NEW"` around the OTA download path suggest this is the most actively iterated/least stable part of the module currently — worth extra care/testing before shipping changes here.

**`lorawan.py`**

- Purpose: driver for a RAK3172-class LoRaWAN modem (standard RUI3 AT set): join, uplink send, downlink receive (including Class C via polling), network time sync.
- Public API (all `async` unless noted): `connect(lorawan_class="A", attempts=1)`, `join_network()`, `send_uplink(port, data)`, `get_downlink_messages()`, `request_time()`, `get_network_time()`, `sleep()`, `check_network_connection()`.
- Depends on: no `lib/` drivers — talks AT directly over UART. Reuses the **same physical UART pins** as `nb_iot.py` (`static_config.pinout.nb-iot.{tx_pin,rx_pin}`) — confirms WiFi/NB-IoT/LoRaWAN modem variants are mutually exclusive at the hardware level, selected by `static_config`'s modem field.
- Config: `dynamic_config.communications.lorawan.{dev_eui,app_key,app_eui,class,network_mode,join_mode,band}`.
- **AT command groups used**: `AT+NWM=` (network mode), `AT+NJM=` (join mode ABP/OTAA), `AT+CLASS=`, `AT+BAND=`, `AT+CFM=` (confirmed uplinks), `AT+DEVEUI=`/`AT+APPEUI=`/`AT+APPKEY=`, `AT+JOIN=1:0:<interval>:<attempts>` (waits for `+EVT:JOINED`), `AT+TIMEREQ=1` + `AT+LTIME=?` (network time), `AT+SEND=<port>:<data>` (waits `+EVT:SEND_CONFIRMED_OK` or `+EVT:TX_DONE`), `AT+LPM=1`/`AT+SLEEP` (low power), `ATZ` (reset), `AT+NJS=?` (join status), `ATC+GETDL` (custom: poll buffered Class C downlinks), and passive `+EVT:RX...` URCs parsed for real-time downlinks.

**`umqttsimple.py`**

- Purpose: lightweight MQTT 3.1.1 client over TCP/TLS socket, used only for the Wi-Fi transport.
- Origin: based on Paul Sokolovsky's classic `micropython-lib` MQTT client (2013–2016), modified by ISURKI/Steminds — `check_msg()` was rewritten to return a list of all pending messages instead of a single callback. QoS 2 is not implemented. Technically lives in `modules/` but is functionally a third-party library — arguably belongs closer to `lib/`.

**`ble_manager.py`**

- Purpose: BLE GATT server for local configuration/monitoring, activated by the magnet-wakeup mode. One notify characteristic (data) and one write characteristic (commands).
- Public API: `BLEManager(device_name=..., command_callback=...)`, `update_data_payload(payload)`, `stop()`.
- Depends on: `lib/aioble` (Service/Characteristic/advertise/security).
- Config: `static_config.pin` (same 6-digit PIN as `_auth.py`, used for fixed BLE pairing).
- Note: implements LE Secure pairing/bonding with MITM protection and a fixed PIN (DISPLAY_ONLY IO capability); rejects commands on unencrypted characteristics.

**`downlink_manager.py`**

- Purpose: unifies downlink handling across the three transports (Wi-Fi, NB-IoT, LoRaWAN): manual SD/EV commands, remote config application (LPP-decoded), and OTA kick-off (NB-IoT only).
- Public API: `process_wifi_downlinks(...)`, `process_nbiot_downlinks(...)`, `process_lorawan_downlinks(...)` (all `async`), `apply_config(hex_text)`, `is_manual_command(text)`.
- Depends on: `lib/IsurlogLPP`, `lib/ota.rollback`; deferred imports of `modbus_sensor`, `update_manager`, `remote_repl`.
- Note: contains the full OTA flow — download, SHA-256 checksum verification, base64 decode, partition write, and `rollback.cancel_force()` on failure.

**`remote_repl.py`**

- Purpose: remote Python REPL over MQTT (Wi-Fi or NB-IoT) for field debugging — receives Python code as an MQTT message, `eval`/`exec`s it, returns captured stdout on another topic.
- ⚠️ **Security note**: this executes arbitrary code with no authentication beyond whatever the MQTT broker/channel provides. It's a powerful admin backdoor — worth confirming the MQTT channel is properly secured (TLS + broker ACLs) wherever this is enabled in the field.

### Sensors

**`analog_sensor.py`** — ADS1115-based 4-20mA/0-10V wrapper; `read_analog(channel)`, `convert_value(value, zero, full_scale)`. Depends on `lib/ADS1115`. Config: `static_config.pinout.i2c.*`, `static_config.ads1115_addr`; per-channel `zero`/`full_scale` come from `dynamic_config.analog_config.inputs[]`.

**`digital_sensor.py`** — ULP-based low-power pulse counter with software debounce (only GPIO 36/39, RTC-capable pins). Depends on `lib/esp32_ulp`. Reads its wake-up edge count from `dynamic_config.digital_config.inputs[]` — a list with one entry per channel — by finding the entry where `channel == 0` and reading its `wake` key.

**`bme_sensor.py`** — auto-detects BMP280/BME280/BME680 via I2C `CHIP_ID`; optional IAQ (air quality) calculation with gas-sensor burn-in. Depends on `lib/pimoroni_bme680`, `lib/bme280_float`. Note: `_burn_in()` blocks for up to 300s if `IAQ=True` — `main.py` currently instantiates it with `IAQ=False`.

**`sht30_sensor.py`** — SHT30 temp/humidity wrapper. Depends on `lib/SHT30`.

**`max31865_sensor.py`** — PT100/PT1000 wrapper over SPI. Depends on `lib/adafruit_max31865`. Reads `wires` from `dynamic_config.pt100_config.wires` (default 4 if absent).

**`modbus_sensor.py`** — Modbus RTU master over RS485 (holding/input registers, coils, discrete inputs, register writes, 2-register-to-float conversion). Depends on `lib/umodbus`. Heavily used by `main.py`, `downlink_manager.py`, and isurnode integrations.

**`accel_manager.py`** — anti-theft: LIS2DH12 accelerometer + MCP23008 I/O expander to detect movement/tamper and wake from deep sleep. Depends on `lib/mcp23008`, `lib/LIS2DH12`. Note: `_verify_theft()` blocks for up to 10s polling — fine as called today, but not asyncio-friendly if reused elsewhere.

**`battery_monitor.py`** — ESP32-internal ADC battery voltage reading (fallback when no MAX17048 fuel gauge is present). No config, no `lib/` dependency.

### Storage & OTA

**`internal_storage.py`** — FIFO payload backup on internal flash (used when `general.internal_register` is enabled); auto-trims oldest lines when free space or line count thresholds are hit. Note: `delete_oldest_lines()` rewrites the whole file each time — O(n) per cleanup, worth watching flash wear if the log grows large.

**`update_manager.py`** — OTA support utilities: SHA-256 checksum verification, chunked base64 decode, and safe `main.py` replacement (backup + rename, with rollback attempt on failure).

### Peripherals

**`led_manager.py`** — ULP-driven status LED blink pattern (configurable pulses/bursts/timing), so the CPU doesn't have to stay awake for it. Depends on `lib/esp32_ulp`. Shares the ULP coprocessor with `digital_sensor.py`'s pulse counter — `is_enabled()` acts as a mutex between the two (they can't run simultaneously).

---

## 2.1.3 Library Reference (`lib/`)

| File / package | What it is | Origin |
|---|---|---|
| `adafruit_max31865.py` | MAX31865 RTD amplifier driver (SPI) | Third-party — Adafruit, MIT |
| `ADS1115.py` | ADS1115 16-bit ADC driver (I2C) | Third-party — W. Ewald, MIT |
| `aioble/` | Async BLE (GATT, pairing, L2CAP) | Third-party — official micropython-lib, MIT |
| `bme280_float.py` | BME280 driver (I2C) | Third-party — Adafruit-derived, MIT/BSD-style |
| `esp32_ulp/` | ULP coprocessor assembler/linker | Third-party — micropython-esp32-ulp, MIT |
| `IsurlogLPP.py` | ISURKI's own "Isurlog LPP" payload codec (Cayenne-LPP-like, custom sensor + config types) | **ISURKI own**, GPL-3.0-or-later. Central interoperability piece with `config_manager.py`'s `CONFIG_MAP`. |
| `LIS2DH12.py` | LIS2DH12 accelerometer driver (I2C) | Third-party — Quectel, Apache 2.0 |
| `max1704x.py` | MAX17048/17044 LiPo fuel-gauge driver (I2C) | Third-party (A. Peeters), adapted |
| `mcp23008.py` | MCP23008 I/O expander driver (I2C) | Third-party — M. Causer, MIT |
| `mcp4017.py` | MCP4017 digital potentiometer driver (I2C), sets the VDC boost regulator output | **ISURKI own**, GPL-3.0-or-later |
| `ota/` | ESP32 partition OTA framework (block writer, rollback, status) | Third-party — G. Moloney, MIT |
| `pimoroni_bme680.py` | BME680 driver (I2C) | Third-party — Pimoroni, MIT |
| `RV3028.py` | RV3028 low-power RTC driver (I2C) | Third-party — Core Electronics/Makerverse |
| `SHT30.py` | SHT30 temp/humidity driver (I2C) | Third-party — R. Sánchez, Apache 2.0 |
| `uds3231.py` | DS3231 RTC driver (I2C) | Third-party — Adafruit-derived, adapted by ISURKI, MIT |
| `umodbus/` | Full Modbus RTU/TCP master+slave stack (v2.3.7) | Third-party — Pycom, GPL v3 + Pycom License v1.0 |

---

## 2.1.4 Module Dependency Map

```
main.py
 ├─ power_manager ──── lib/uds3231 | lib/RV3028
 ├─ rtc_memory
 ├─ led_manager ─────── lib/esp32_ulp
 ├─ accel_manager ───── lib/mcp23008, lib/LIS2DH12
 ├─ downlink_manager ── lib/IsurlogLPP, lib/ota.rollback
 │                       ├─ modbus_sensor ── lib/umodbus
 │                       ├─ update_manager
 │                       └─ remote_repl
 ├─ config_manager ──── utils
 ├─ lib/mcp4017, lib/IsurlogLPP, lib/ota.rollback   (direct, top-level)
 └─ (deferred, config/hardware-dependent)
     ├─ wifi ─────────── umqttsimple
     ├─ nb_iot
     ├─ lorawan
     ├─ ble_manager ──── lib/aioble
     ├─ battery_monitor
     ├─ sht30_sensor ─── lib/SHT30
     ├─ bme_sensor ────── lib/pimoroni_bme680, lib/bme280_float
     ├─ max31865_sensor ─ lib/adafruit_max31865
     ├─ analog_sensor ─── lib/ADS1115
     ├─ digital_sensor ── lib/esp32_ulp
     └─ internal_storage

utils.py is imported by nearly every module above (omitted from the tree for readability).
```

`main.py` doesn't import every module unconditionally — sensors and connectivity modules are imported lazily, gated by `static_config`/`dynamic_config` (which modem, which sensors are enabled, whether a magnet-wakeup or OTA/REPL downlink was received). This keeps RAM usage down at boot, which matters on MicroPython.
