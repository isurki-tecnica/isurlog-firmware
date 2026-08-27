# 3. Communications

The ISURLOG includes integrated Wi-Fi and Bluetooth capabilities. Additionally, it can contain either a LoRa or an NB-IoT communication module, as these two options are mutually exclusive.

## 3.1. LoRaWAN

The ISURLOG utilizes LoRaWAN technology (derived from LoRa, Long Range modulation) for long-range wireless data transmission. It operates in the license-free 868 MHz frequency band, which is standard for Europe.

!!! note "Note"
    868 MHz is the only factory configuration available. If you require a different regional frequency, please contact ISURKI directly.

### Connection Requirements and Safety

It is **imperative** that the antenna is always connected before powering on the device to avoid permanent damage to the radio frequency circuit.

* The antenna used must be designed for **868 MHz**.
* It must have an **impedance of 50 Ohms** and a low VSWR to ensure maximum efficiency.
* The ISURLOG board is equipped with a **U.FL type antenna connector**.

![The U.FL antenna connector for the LoRaWAN module](images/4-lorawan-antenna-connector.jpg){width="400"}

*The U.FL antenna connector, LoRaWAN module.*

## 3.2. NB-IoT (Narrowband IoT)

NB-IoT is a wireless communication technology specifically designed for the Internet of Things (IoT). Its narrow band approach enables efficient connectivity in urban and suburban environments, excelling in penetration into hard-to-reach areas.

### Energy Efficiency and Bi-Directional Communication

While NB-IoT offers lower data speeds compared to broadband technologies, it is ideal for IoT applications that do not require real-time transmission, focusing on **energy efficiency** and **prolonging battery life**.

Thanks to the combination of NB-IoT and the eDRX (extended Discontinuous Reception) power-saving mode, the NB version of the ISURLOG offers **bi-directional communication**. This key feature allows the user to remotely "wake up" the datalogger at any time to force a reading or change parameters, an operation managed from the **IsurDASH** cloud platform.

### Connection Requirements and Safety

It is **imperative** to connect an LTE antenna to avoid damaging the radio frequency circuit.

* The connector for the LTE antenna provided on the ISURLOG is of the **U.FL type**.
* Thanks to its advanced RF front-end architecture, this same connector and antenna also serve **GPS** reception — a single antenna is enough for both, no separate GPS antenna or connector is needed.

![The U.FL antenna connector for the NB-IoT module, shared with GPS](images/4-nbiot-antenna-connector.png){width="600"}

*The U.FL antenna connector, NB-IoT module — shared with GPS, no separate antenna needed.*

### SIM Management Flexibility

The ISURLOG offers two flexible options for managing the NB-IoT subscription:

* **Integrated eSIM:** The device features an embedded SIM (eSIM) soldered onto the board. This eSIM can be used with a data plan provided by ISURKI (consult terms and conditions).
* **External Nano-SIM:** Users have the option to utilize their own physical Nano-SIM card by inserting it into the corresponding slot on the ISURLOG. This SIM must have an NB-IoT compatible data plan contracted with the user's preferred operator.

## 3.3. Wi-Fi & BLE

Unlike LoRaWAN and NB-IoT, which are external radio modules and mutually exclusive with each other, **Wi-Fi and Bluetooth Low Energy (BLE) are built into the ESP32 chip itself** — they are present on **every** ISURLOG regardless of which external communication module (if any) is fitted.

* **Wi-Fi:** 802.11 b/g/n, 2.4 GHz. Can be used as an alternative way to upload data to the platform.
* **Bluetooth:** v4.2 (BR/EDR + BLE). Used for the local, real-time connection described in **[1.8 Internal Sensors and Diagnostics](sensor-connections.md#18-internal-sensors-and-diagnostics)** (device configuration and live sensor viewing over Bluetooth) — available regardless of which external communication module is installed.

Both radios use the **antenna integrated directly on the PCB** — no external antenna or connector is required for Wi-Fi or Bluetooth.
