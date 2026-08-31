# 1. Parts and Accessories

A complete reference for every piece of hardware that can go with an ISURLOG — the unit itself, mounting/enclosure, antennas, batteries, external/solar power, and connectivity. For each item: what you can get directly **from Isurki**, and what you can **source yourself** if you'd rather buy or already have it.

Want to build a custom order instead of reading through tables? See **[2. Build Your Own ISURLOG](configurator.md)** for an interactive configurator that adds up the total as you go.

!!! note "Work in progress"
    🚧 Several rows below are placeholders — real prices, models, and supplier links need to be filled in. Nothing here is fabricated; where we don't have a confirmed figure yet, it's marked explicitly rather than guessed.

## 1.1 The Datalogger

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **ISURLOG — NB-IoT/LTE-M variant** | **€387** | *No alternative — this is the core hardware* |
| **ISURLOG — LoRaWAN variant** | **€330** | *No alternative — this is the core hardware* |
| **ISURLOG — Wi-Fi only** | **€310** | *No alternative — this is the core hardware* |

### Protective Coating Options

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **Standard conformal coating** (50–200 µm) | *Included on every board, standard* | *Not applicable — factory process* |
| **Extra conformal coating layer** | **+€15** | Apply your own — e.g. [Multicomp Pro MP014781, silicone conformal coating, 55 ml](https://es.farnell.com/multicomp-pro/mp014781/conformal-coating-silicone-55ml/dp/4538715) |
| **Resin potting** — the board is cast in transparent resin, leaving only the sensor and power connectors exposed | **+€80** | Apply your own — needs 2 packs of [Electrolube UR5634RP250G, clear polyurethane resin, 250 g](https://es.farnell.com/electrolube/ur5634rp250g/resina-poliuretano-clara-aplicac/dp/2476085). Only compatible with **Li-SOCl2** batteries. |

For more details on resin potting, [contact Isurki](mailto:tecnica@isurki.com).

## 1.2 Enclosure & Mounting

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **3D-printed enclosure** (PETG, IP66) | **€35** | 💬 In discussion |
| **DIN rail mount** — direct, or via a separate 3D-printed piece fixed to the wall | **€28** | 💬 In discussion |
| **Pole mount** | **€18** | 💬 In discussion |
| **ER34615 battery holder/adapter** — small PCB that takes power from up to 2 ER34615 cells and combines it into a single output feeding the ISURLOG. Required to use [Li-SOCl2 batteries](#14-batteries). | **€20** | 💬 In discussion |

💬 **A self-sourced/DIY path for these parts (enclosure, mounting) isn't available yet — direction still in discussion.** [Let us know](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) if you'd find this useful.

See [4.2 Physical Mounting](installation-commissioning.md#42-physical-mounting) for the standard mounting-hole dimensions if you're designing your own bracket instead.

## 1.3 Antennas

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **NB-IoT / LTE-M antenna** *(shares GPS reception, no separate GPS antenna needed)* | *Included with the NB-IoT/LTE-M unit* | [Molex 209142-0180](https://www.mouser.es/es/ProductDetail/Molex/209142-0180) — ~€3.78, or any other NB-IoT-compatible antenna with 50 Ω impedance |
| **LoRaWAN antenna** (868 MHz) | *Included with the LoRaWAN unit* | [TE Connectivity 2195835-3](https://www.digikey.es/es/products/detail/te-connectivity-amp-connectors/2195835-3/13926726) — must be 868 MHz, 50 Ω, low VSWR. **Not the same antenna as NB-IoT** — different frequency band. |

Both use a **U.FL connector** on the PCB. Wi-Fi and Bluetooth don't need an external antenna — they use the one integrated directly on the PCB. See [3. Communications](communications.md) for the full connection requirements.

## 1.4 Batteries

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **18650 (Li-Ion, rechargeable)** — 1 to 5 cells, up to 17000 mAh total | **€30** *(set of 5, rechargeable)* | [Samsung INR18650-35E, 3400mAh / 8A](https://www.nkon.nl/es/samsung-inr18650-35e.html) or equivalent — ~€2.59/unit. Must be **18650 format, Li-Ion, rechargeable**. |
| **Li-SOCl2 (non-rechargeable)** — requires **ISURLOG v3.3+** and the [ER34615 battery holder/adapter](#12-enclosure-mounting) above | **€40** *(set of 2)* | Any **ER34615 format, Li-SOCl2** battery. Recommended: [EVE ER34615EHR2](https://www.tme.eu/es/details/eve-er34615ehr2/pilas/eve-battery/er34615ehr2/) |
| **CR2032 (coin cell)** — RTC backup only, not main power | *Included on the standard PCB* | For replacements/spares: **EEMB CR2032**, 3V, with cable and **Molex 51021-02 connector (2mm pitch)** — not just any CR2032, the connector must match. See [2.3 RTC Backup Battery](power-supply.md#23-rtc-backup-battery-cr2032) for the connector pinout. |

See [2. Power Supply Methods](power-supply.md) for jumper configuration and battery-holder details.

## 1.5 External / Solar Power (Hybrid Mode)

For deployments combining batteries with an external charging source. The MPPC input accepts one of three voltage ranges — see [2.2 Jumper Configuration](power-supply.md#22-jumper-configuration-for-power-modes) for the required jumper settings.

| MPPC Input | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **5V** — solar panel or a standard 5V charger | **€34** | [Example panel](https://www.amazon.es/dp/B09Q87WKGR?ref=fed_asin_title&th=1) — see warning below before choosing your own |
| **1.5V** — micro solar panel | — | 🚧 *No specific recommended model yet* |
| **0.3V** — TEG (Thermoelectric Generator) | — | 🚧 *No specific recommended model yet* |

!!! warning "Regulated 5V Required"
    Many panels labeled "5V" actually reach up to **7V in open-circuit conditions** (i.e. with nothing connected, or under low load), which can damage the ISURLOG's input. Only use a panel with an **internal regulator** that keeps its output stable and never exceeds **5.5V**, even unloaded.

## 1.6 External Power (Mains)

For deployments powered from mains/external power rather than batteries alone — see [2.1.2 External Power Only](power-supply.md#212-external-power-only). Power comes in either via the **USB-C** port, or via the **PIN** pressure terminals. Batteries can still be installed alongside external power as a backup for outages — see [2.1.3 Batteries + External Power (Hybrid Mode)](power-supply.md#213-batteries-external-power-hybrid-mode).

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **5V/1A wall power adapter** | **€20** | [Example adapter](https://www.amazon.es/dp/B01J2G52O6?ref=fed_asin_title&th=1) |
| **USB-A to Micro-USB cable** — only needed to power via the **PIN** terminals instead of USB-C | **€10** | [Amazon Basics USB-A 2.0 to Micro-USB, 3 m](https://www.amazon.es/dp/B071S5NTDR?ref=fed_asin_title&th=1) — see note below |

!!! note "This cable gets wired into the PIN terminals, not used as a USB cable"
    Cut the Micro-USB end open and identify the two power wires inside — the data wires aren't needed. Connect the positive and negative power wires directly to the ISURLOG's **PIN 5V MAX** pressure terminals.

## 1.7 Connectivity

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **Integrated eSIM + data plan** (NB-IoT/LTE-M) — 500 MB or 5 years, whichever comes first. A typical ISURLOG uses ~1.5–2 MB/month, well within the plan. Data usage can be tracked per device in IsurDASH, under [Data Visualization, Location and SIM Data](isurdash-devices.md#data-visualization-location-and-sim-data). | **€36** | *Not applicable, it's built in* |
| **External Nano-SIM** (NB-IoT/LTE-M) | — | Any NB-IoT/LTE-M-compatible operator SIM |
| **NTN SIM** (satellite, via nRF9151) | — | [Monogoto](https://monogoto.io) — check [NTN satellite coverage](https://docs.monogoto.io/getting-started/ntn-satellite-coverage) for your region |

See [3.2 SIM Management Flexibility](communications.md#sim-management-flexibility) for how the eSIM/Nano-SIM switch works.

## 1.8 Firmware

| Item | From Isurki | Bring your own |
| :--- | :--- | :--- |
| **Standard firmware** — pre-flashed, integrates with IsurDASH out of the box | **€0** *(included)* | See [GitHub Releases](https://github.com/isurki-tecnica/isurlog-firmware/releases) for released firmware versions |
| **Flash your own firmware** — the firmware is open source ([GitHub](https://github.com/isurki-tecnica/isurlog-firmware)), compile and flash a custom build instead | **€0** | See [1. Build Environment Setup](build-environment.md) and [3. Flashing and Application Upload](flashing-application-upload.md) |

## 1.9 Developer Tools *(one-time, reusable across units — not per-deployment)*

| Item | Needed for |
| :--- | :--- |
| **UART-to-USB TTL cable** | Flashing the ESP32 side — see [3. Flashing and Application Upload](flashing-application-upload.md). |
| **[nRF9160-DK](https://www.digikey.es/es/products/detail/nordic-semiconductor-asa/NRF9160-DK/9740721)** + **[6-pin TAG-Connect cable](https://www.tag-connect.com/product/tc2030-ctx-nl-6-pin-no-legs-cable-with-10-pin-micro-connector-for-cortex-processors)** + **[nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)** | Updating the nRF9151 modem firmware — see [5.6 Flashing Hardware Requirements](nbiot-modem-guide.md#56-flashing-hardware-requirements-and-connection). |

---

Missing something you'd expect to see here, or have a supplier recommendation for one of the 🚧 rows? [Open a GitHub Issue](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) — see [7.4 Using the Issues Tracker](contribution-guide.md#74-using-the-issues-tracker).
