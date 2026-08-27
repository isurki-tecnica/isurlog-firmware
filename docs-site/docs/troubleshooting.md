# 1. Troubleshooting

Common problems reported by customers, why they happen, and how to fix them. This page grows over time as new issues come up — if you hit something that isn't listed here, contact support (see the [Home](index.md) page) so it can be added.

---

## Batteries drain much faster than expected

This is the single most common issue reported, and it usually comes down to one or more of the following.

### 1. Outdated firmware (ESP32 and/or NB-IoT modem)

Older firmware versions were significantly less optimized for power consumption. On top of that, older **nRF9151 modem firmware did not support RAI** (Release Assistance Indication) — without it, even after the ISURLOG finished transmitting, the modem's cellular connection stayed in **RRC Connected** state for roughly 30 extra seconds before releasing, draining the battery the whole time for no benefit.

**Solution:** Update the firmware.

* **Recommended:** update the ESP32 firmware directly from IsurDASH — see **[6.8. Device Maintenance](isurdash-maintenance.md)**.
* **Manual alternative:** flash it yourself — see **[3. Flashing and Application Upload](flashing-application-upload.md)**.

Always use the **"Latest"** release from the [GitHub Releases page](https://github.com/isurki-tecnica/isurlog-firmware/releases) — **pre-release** versions may contain bugs that can *increase* power consumption rather than reduce it.

### 2. Keeping the battery charger enabled with no external power source

The charger circuit itself draws a small amount of power just by being active. In installations running on **batteries only** (no solar panel, TEG, or 5V charger connected), leaving the charger jumper enabled wastes power for no benefit — it has nothing to charge from.

**Solution:** Configure the jumpers for maximum power saving — see **[2. Power Supply Methods](power-supply.md)** for the correct jumper configuration for battery-only installations (Charger deactivated).

### 3. LoRaWAN-specific: device class and ADR

For **LoRaWAN** ISURLOG units specifically, two additional factors commonly cause excessive consumption:

* **Wrong device class.** Configuring **Class B or Class C** instead of **Class A** when the application doesn't actually need low-latency downlinks and the device is meant to run on batteries. Class B and C keep the radio listening far more often than Class A, which is by far the most power-efficient class.
* **ADR (Adaptive Data Rate) not enabled** on the LoRaWAN network server. Without ADR, the device may keep transmitting at a higher power / lower data rate than its actual link conditions require, wasting energy on every uplink.

---

## Missing data / gaps in received data / fewer records than expected

This is generally also caused by **outdated firmware handling connectivity loss poorly**. For example, when coverage is temporarily bad, or the ISURLOG has to reconnect to the network, older firmware versions don't correctly manage the records already stored in **RTC RAM** while this happens — and those pending records get lost instead of being sent once the connection is recovered.

**Solution:** Update the ESP32 firmware — same as above, **recommended** via IsurDASH (**[6.8. Device Maintenance](isurdash-maintenance.md)**) or manually (**[3. Flashing and Application Upload](flashing-application-upload.md)**), always using the **"Latest"** release rather than a pre-release.

---

## Configuration changes don't seem to apply

When you edit a device's configuration in IsurDASH and click save, the changes are saved in **IsurDASH's own database** — but they are **not sent to the ISURLOG yet**. This is intentional: it lets you keep editing several configuration sections before triggering a single transmission to the device, instead of sending one downlink per field.

While a device has unsaved changes, IsurDASH shows a warning banner:

!!! warning "IsurDASH banner"
    ⚠️ **"Configuración no sincronizada con el dispositivo"** *("Configuration not synchronized with the device")* — with two buttons, **Ignorar** *(Ignore)* and **Sincronizar** *(Synchronize)*.

During this state, the Configuration widget on the device's dashboard reads **"Sin enviar"** *("Not sent")*.

Clicking **Sincronizar** queues the configuration to be sent to the device — the widget then switches to **"Sincronizado"** *("Synchronized")*.

**Important — "Sincronizado" does not mean the device is already running the new configuration.** It only means the configuration has been sent from IsurDASH's side. For it to actually reach and take effect on the ISURLOG:

1. The ISURLOG has to perform an **uplink** (a data transmission) — this applies the same way to NB-IoT, LoRaWAN, and Wi-Fi devices.
      * **Exception — NB-IoT with eDRX:** on **NB-IoT devices with eDRX enabled**, the wait is much shorter. Instead of waiting for the next full transmission cycle, the configuration can reach the device within the configured **eDRX timer** — typically **40.96 seconds** on standard firmware versions.
2. Right after the uplink, the device receives the **downlink** carrying the new configuration, saves it, and goes back to sleep.
3. Only on the **next wake-up cycle** does the device read that saved configuration and start actually operating with it.

So there is an inherent delay of up to **two full transmission cycles** between clicking "Sincronizar" and the change actually taking effect in the field — worth keeping in mind, especially on devices configured with long latency times (see **[7. Reference Configuration Parameters](reference-parameters.md)**).

---

## Modbus sensor not responding / timeout

When a Modbus RTU sensor on the RS485 bus doesn't respond, or the ISURLOG reports a timeout reading it, the cause is almost always one of the following.

### 1. Mismatched slave address, baudrate, or parity

The **Slave Address**, **Baudrate**, **Parity**, **Data Bits**, and **Stop Bits** configured in IsurDASH for that Modbus Input must exactly match the sensor's own configuration (usually set via DIP switches or the manufacturer's own config tool). Any mismatch results in no response at all, not a garbled one — Modbus RTU doesn't degrade gracefully.

**Important — these communication parameters are bus-wide, not per-sensor.** IsurDASH lets you set Baudrate/Parity/Data Bits/Stop Bits individually for each of the 4 virtual Modbus Inputs, but physically there is only **one** RS485 bus. All sensors connected to it are electrically listening to the exact same signal, so **every sensor on the bus must actually be configured with the same values**. Setting a different baudrate on Modbus Input 2 than on Modbus Input 0, for example, doesn't give each sensor its own speed — it just breaks communication for the sensor(s) that don't match what's actually configured on the bus.

### 2. Bad bus wiring or missing termination resistor

On larger Modbus networks — several sensors on the same bus, and/or long cable runs — good wiring practice matters a lot more than it seems, and most field issues come down to it.

* **Wire the bus as a single daisy chain, never in parallel/star.** Modbus RTU over RS485 is a bus topology: connections must go ISURLOG → Sensor 1 → Sensor 2 → … → Sensor N, each sensor wired to the terminals of the *previous* one — not all sensors wired back independently to the ISURLOG's own terminals in a star pattern. A/B and GND all get chained through in the same way.
* **Terminate both physical ends of the bus with a 120 Ω resistor.** The ISURLOG's own RS485 input already includes a **built-in 120 Ω termination resistor** (see **[1. Sensor Connections](sensor-connections.md)**), covering the ISURLOG's end of the bus automatically. The other end — the **last sensor in the chain** — needs its own 120 Ω termination resistor added across A/B, either built into the sensor (some have a DIP switch or jumper for it) or added externally at that last connection point. Intermediate sensors in the middle of the chain must **not** be terminated.
* Missing termination doesn't always cause a hard failure — it often shows up as intermittent timeouts that get worse with more sensors, longer cable runs, or higher baudrates, which makes it easy to misdiagnose as a sensor or configuration problem instead of a wiring one.

**Solution:** Verify Slave Address, Baudrate, Parity, Data Bits, and Stop Bits are identical across every sensor on the bus and match what's configured in IsurDASH; wire sensors in a daisy chain rather than in parallel; and confirm a 120 Ω termination resistor is present only at the last sensor in the chain (the ISURLOG end is already terminated internally).

---

## BLE doesn't connect from the app / IsurDASH

Unlike NB-IoT/LoRaWAN, which the ISURLOG uses on its own schedule, **Bluetooth is off by default and has to be woken up deliberately** — this is a deliberate power-saving choice, not a bug.

### 1. BLE isn't advertising yet

To save battery, the ISURLOG doesn't keep its Bluetooth radio on. It has to be activated with the magnet first, as described in **[1.8. Internal Sensors and Diagnostics](sensor-connections.md#18-internal-sensors-and-diagnostics)**: holding the magnet near the Hall effect sensor for **more than 5 seconds** puts the device into **Bluetooth Diagnostics Mode**.

Once active, the Bluetooth interface stays open for **2 minutes** waiting for a pairing attempt. If nothing connects within that window, it automatically shuts back off to save power — so the app/IsurDASH has to attempt the connection inside that same 2-minute window, not before activating it or long after. Once a successful pairing happens, that 2-minute timeout no longer applies for the rest of the session.

**Solution:** Activate Bluetooth with the magnet (>5s) right before attempting to connect, and complete the connection within the following 2 minutes. If it times out, simply reactivate it with the magnet again.

### 2. Bluetooth range

The ISURLOG's ESP32 uses the antenna embedded directly on the PCB rather than an external one, so BLE range is inherently short — typically around **5 meters**, and less depending on enclosure material, obstacles, and the surrounding environment (metal enclosures/cabinets in particular can reduce it further).

**Solution:** Get within a few meters of the device, with as clear a line of sight as possible, before attempting to pair.
