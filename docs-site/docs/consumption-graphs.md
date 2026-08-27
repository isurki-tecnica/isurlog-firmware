# 1. Consumption Graphs

Real current-vs-time captures showing what each part of the duty cycle actually costs — a companion to the [Power Budget & Battery Life Calculator](power-budget.md), grounded in measurement instead of estimates. This page grows over time as new captures become available.

## 1.1 Measurement Method

**Equipment.** ISURLOG's current draw spans a very wide range — roughly 20µA in deep sleep up to 0.5A+ during a transmit burst — so a regular multimeter can't track both ends of that swing accurately. A meter with **autoranging** is required. Captures on this page use the **Nordic Power Profiler Kit II (PPK2)**, with its **Power Profiler** app for nRF Connect for Desktop, but any autoranging current meter is valid — the choice is left to the reader.

**Wiring — the I_SENSE jumper.** All battery current passes through the **I_SENSE** jumper (see [2.2. Jumper Configuration for Power Modes](power-supply.md)). In normal operation it stays **closed** (shorted). To measure consumption:

1. Open/remove the I_SENSE jumper.
2. Insert the meter in series: the **inner pin** (pin 1 below) is **VIN** (battery side) — connect it to the meter's VIN. The **outer pin** (pin 2) connects to the meter's VOUT.
3. Tie the meter's **GND** to an ISURLOG GND — e.g. at the ESP32 or RAK3172 UART header pins.

![I_SENSE jumper — PPK2 wiring](images/isense-ppk2-wiring.png){width="220"}

**Conditions.** Each capture below notes the firmware version, connectivity, and sensor configuration it was taken under — real numbers vary with these, so treat them as a reference point, not a spec sheet.

---

## 1.2 Captures

### Deep Sleep — NB-IoT/LTE-M

![Deep sleep current — NB-IoT](images/deep-sleep-nbiot.png)

Captured with the PPK2 in Ampere meter mode, 1,000 samples/second, over a 3-second window:

* **Average:** 77.44 µA
* **Peak:** 1.22 mA (periodic short spikes visible in the trace)
* **Window:** 3.001 s · **Charge:** 232.39 µC

!!! note "What this figure includes"
    This is the **full system** at rest, not the ESP32 alone: ESP32 deep sleep **plus** the nRF9151 modem, powered on and already attached to the NB-IoT network — no reconnect/re-attach pending when the next scheduled transmission comes due. That's why it reads higher than a bare-ESP32 deep sleep figure; it's the more realistic number for a deployed unit.

!!! note "The periodic spikes"
    The regular short spikes riding on top of the baseline come from the board's own power regulator: at very light load (like deep sleep), it switches to a pulsed low-power operating mode — firing brief current pulses to top up its output capacitor instead of switching continuously. The downstream draw itself stays smooth; the pulses are the regulator's own behavior, not the ESP32 or modem doing anything.

**Longer window — eDRX paging cycle:**

![Deep sleep current — NB-IoT, eDRX paging cycle over a 1-minute window](images/deep-sleep-nbiot-edrx-cycle.png)

Zooming out to a 1-minute window reveals a second, larger periodic spike (30-38 mA) on top of the baseline — these are the modem's **eDRX paging occasions**, where it briefly wakes to listen for the network. The interval between two consecutive occasions is **40.96 s on standard firmware**, matching the **40.92 s** measured here.

* **Window average:** 173.21 µA · **Window max:** 38.08 mA · **Window charge:** 10.39 mC (1 minute)
* **Between two paging occasions:** 158.71 µA average · 40.92 s · 6.49 mC charge

!!! note "Coming soon"
    Deep Sleep — LoRaWAN, Deep Sleep — Wi-Fi, Wake + Sensor Read, and a transmission-cycle capture for each connectivity option.
