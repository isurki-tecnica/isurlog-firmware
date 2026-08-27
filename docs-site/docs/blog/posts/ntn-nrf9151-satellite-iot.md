---
draft: true
date: 2026-08-27
authors:
  - isurki
---

# NTN on the nRF9151: Low-Cost Satellite IoT Without a Separate Satellite Modem

## Why

Satellite connectivity has always meant a trade-off nobody actually wanted to make: either your device lives in cellular coverage, or you pay for it. A dedicated satellite modem alone can cost more than an entire ISURLOG unit does today — before you've added a single sensor, an enclosure, or a battery that survives a season in the field. That cost has quietly drawn a line across the map: everything inside cellular coverage gets real-time IoT, and everything outside it — the forest, the mountain pass, the offshore platform, the pipeline crossing open country — gets a manual visit, or nothing at all.

NTN is the reason that line is starting to move.

<!-- more -->

Non-Terrestrial Networks — standardized in 3GPP Release 17 — do something deceptively simple: they let a normal NB-IoT device talk to a satellite using the *same* protocol stack it already uses to talk to a cell tower. No proprietary satellite radio. No second modem bolted onto the board. No separate ecosystem to integrate. If your device's modem supports NTN, reaching a satellite is a firmware capability, not a hardware redesign.

ISURLOG's NB-IoT connectivity already runs on the Nordic nRF9151 — the same chip driving this shift. That's the part worth sitting with for a second: a datalogger built from well under €500 in materials, open-source down to the firmware, engineered from day one to run for years on a couple of Li-Ion 18650 cells — is standing on hardware that can also reach a satellite. Not a €5,000 satellite-only unit. Not a closed platform where you rent connectivity and hope the vendor is still around in three years. The same board, the same firmware repo, the same low-power discipline that gets ISURLOG to ~20µA in deep sleep — extended to cover the one gap terrestrial cellular could never close.

That combination — satellite reach, industrial-grade sensing, real battery life, and a firmware anyone can read line by line — isn't something the IoT industry has been able to offer at this price point. It's usually pick two. This is what it looks like to not have to.

This post walks through what NTN actually is, what it takes to bring it up on an nRF9151, and what ISURLOG looked like the first time it reached a satellite instead of a tower.

## What you'll need

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **ISURLOG datalogger** — PCB with NB-IoT module (nRF9151) | **€387** | *No alternative — this is the core hardware* |
| **Antenna** — same one used for regular terrestrial NB-IoT, no NTN-specific antenna needed | **€5** | [Molex 209142-0180](https://www.mouser.es/es/ProductDetail/Molex/209142-0180) — ~€3.78 |
| **3D-printed enclosure** *(optional)* | **From €35** *(depends on accessories)* | 🚧 Coming soon — printable files on Printables |
| **Li-Ion 18650 batteries** — 2 minimum for transmission current peaks, 5 for full internal capacity | **€30** *(set of 5, rechargeable)* | e.g. [Samsung INR18650-35E, 3400mAh / 8A](https://www.nkon.nl/es/samsung-inr18650-35e.html) — ~€2.59/unit |
| **NTN SIM card** | — | [Monogoto](https://monogoto.io) — check [NTN satellite coverage](https://docs.monogoto.io/getting-started/ntn-satellite-coverage) for your region before ordering |
| **Sensor** *(optional — any ISURLOG-compatible sensor works)* | — | Example used here: a **Paratronic NRV485** radar level sensor over Modbus RS485. No extra sensor needed to just test the NTN link — the onboard **SHT30** (temperature/humidity) or **LIS2DH12** (accelerometer) work fine too. |

**Total hardware cost:** ~€422 without the enclosure, from ~€457 with it — plus the Monogoto SIM/data plan (pricing depends on the plan chosen, not included above).

### Tools you'll also need

Beyond the materials above, a bit of general-purpose tooling — reusable across projects, not something bought per unit:

* **A computer** (Windows, macOS, or Linux) — to flash firmware and run the tools below.
* **A UART-to-USB TTL cable** — the ISURLOG doesn't have an onboard USB-to-UART converter, so this is how the ESP32 side gets flashed. Full details in [Flashing and Application Upload](https://docs.isurlog.isurki.com/flashing-application-upload/).
* **An [nRF9160-DK](https://www.digikey.es/es/products/detail/nordic-semiconductor-asa/NRF9160-DK/9740721)**, a **[6-pin TAG-Connect cable](https://www.tag-connect.com/product/tc2030-ctx-nl-6-pin-no-legs-cable-with-10-pin-micro-connector-for-cortex-processors)**, and **[nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)** — this is what actually loads the NTN modem firmware in the next section. No SDK or toolchain needed, just the Programmer app. Full details in [5.6 Flashing Hardware Requirements](https://docs.isurlog.isurki.com/nbiot-modem-guide/#56-flashing-hardware-requirements-and-connection).

## How NTN actually works

NB-IoT already solved the "long battery life, low bandwidth" side of the equation for terrestrial cellular. What Release 17 changes is where "cellular" is allowed to originate from.

A satellite in low Earth orbit (LEO) is hundreds of kilometers away and moving at roughly 7 km/s relative to the ground. Both of those facts break assumptions terrestrial NB-IoT takes for granted: round-trip signal delay goes from milliseconds to tens or hundreds of milliseconds, and the Doppler shift from a satellite crossing overhead is large enough to shift the carrier frequency the modem is listening on. NB-NTN — the NB-IoT flavor of NTN — extends the standard's timing advance, random access procedure, and frequency compensation to handle both, without changing the underlying waveform or the AT-command interface a device already speaks to reach a terrestrial tower.

That's the part that matters for hardware: the nRF9151 doesn't need a different radio to do this. Nordic ships NB-NTN support as a modem firmware capability on the same chip already driving ISURLOG's terrestrial NB-IoT connection — same antenna, same SIM slot, same low-power sleep behavior between transmissions. Bringing NTN up on ISURLOG is a firmware and configuration change, not a new bill of materials.

The practical difference shows up at connection time, not before it. A cell tower is always there; a satellite isn't always overhead. Where a terrestrial NB-IoT device attaches to the network in seconds, an NTN device may need to wait for a satellite pass within view before it can register and send — a real, physical constraint of orbital mechanics, not a firmware limitation. Understanding that window is most of what changes about designing for NTN versus designing for terrestrial NB-IoT.

## Setting it up on ISURLOG

### Step 1: Flash the NTN modem firmware

The nRF9151 ships from the factory speaking terrestrial NB-IoT/LTE-M. Reaching a satellite starts with loading Nordic's dedicated NTN modem firmware — at the time of writing, [`mfw_nrf9151-ntn_1.0.1`](https://www.nordicsemi.com/Products/nRF9151/Download?lang=en#infotabs), available from the same Nordic downloads page as the regular modem firmware.

The flashing procedure is exactly the one already documented for updating any modem firmware binary: nRF9160-DK connected via the TAG-Connect cable to the ISURLOG's JTAG port, loaded through the Programmer app in nRF Connect for Desktop. Only the binary changes — swap the usual `mfw_nrf91x1_x.x.x.zip` for the NTN one. The full step-by-step is in [5.7 Updating Modem Firmware from Official Binaries](https://docs.isurlog.isurki.com/nbiot-modem-guide/#57-updating-modem-firmware-from-official-binaries).

### Step 2: Install the latest ISURLOG firmware

With the modem side updated, the ESP32 application firmware needs to be current too. The easiest path is IsurDASH's own guided updater: **Mantenimiento de dispositivos → Actualización de firmware**, picking either **Remoto** (over the air, on firmware v1.1.9+) or **Serial port (USB)** (wired, works on any version — IsurDASH walks through the RST/BOOT sequence itself). Either way, choose the release marked **Latest** from the list pulled from GitHub. Full details in [6.8. Device Maintenance](https://docs.isurlog.isurki.com/isurdash-maintenance/#firmware-update).

That flow only installs official published releases. Flashing outside of IsurDASH — using the UART-to-USB cable directly, with a locally-built `firmware.bin` — is also an option, and the only one if you're working from a custom or not-yet-published build. See [Flashing and Application Upload](https://docs.isurlog.isurki.com/flashing-application-upload/) for that procedure.

### Step 3: Insert the SIM, connect the antenna, power on

With both firmwares up to date, insert the Monogoto NTN SIM and double-check the antenna is properly connected to the PCB's U.FL socket — before powering on, not after, since transmitting without an antenna connected can damage the RF circuit. From there it's the same power-up sequence as any ISURLOG: flip the **ON/OFF** switch on the PCB. Full details in [4.4. Power-Up Sequence](https://docs.isurlog.isurki.com/installation-commissioning/#44-power-up-sequence).

---

🚧 **Coming next:** the rest of the setup (SIM/network configuration, waiting for a satellite pass), the first real satellite transmission — with the actual current-draw numbers — and what's still rough around the edges.
