# 4. GPIO Mapping (Hardware-Software)

This section details the pins used by the **ISURLOG** datalogger on the ESP32 and their specific functions, serving as the interface between the MicroPython firmware and the on-board peripherals.

## 4.1 Power and Enable Controls

These GPIOs control the main power regulators and communication modules, allowing the device to optimize energy consumption during deep sleep modes.

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO5** | Enable nRF9160 | Controls power to the NB-IoT communication module. Pull-down. |
| **GPIO18** | Enable VDC | Activates the 6-24V step-up converter. This power supply is used to feed sensors connected to the VDC pressure terminal. Maximum 2A current. Pull-down. |
| **GPIO13** | Enable 5V | Activates the fixed 5V step-up converter. Maximum 150mA current. Pull-down. |

## 4.2 Analog and Digital Inputs

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO39** | Digital Input 0 | Digital input 0, potential-free contact. |
| **GPIO35** | Wake up from NB-IoT Module | Digital input used to wake up the ESP32 when the NB-IoT module is in eDRX mode and receives a data packet. |
| **GPIO26** | Wake up to NB-IoT Module | Digital output used to wake up the NB-IoT module from the ESP32 when the NB-IoT module is in sleep mode. |
| **GPIO36** | Wake up from Magnetic Switch | Digital input used to wake up the ESP32 when the low-power magnetic switch detects a magnetic field nearby. |
| **GPIO34** | Wake up from MCP23008 | Digital input used to wake up the ESP32 when the MCP23008 creates an interrupt event. |

## 4.3 Digital Output to Relay

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO25** | Enable SD0 | Activates the **ISURLOG** solid-state relay. Maximum 2A commutation. |

## 4.4 Serial Communication Interfaces

### RS485 (using MAX485 Converter)

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO23** | DI MAX485 | Connected to the DI pin of the MAX485 converter. |
| **GPIO14** | RO MAX485 | Connected to the RO pin of the MAX485 converter. |
| **GPIO33** | RE/DE MAX485 | Connected to the RE/DE pin of the MAX485 converter. |

### Shared UART Line (NB-IoT and LoRaWAN Modems)

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO2** | RX nRF9160/RAK3172 | RX pin for the NB-IoT/LoRaWAN modem. |
| **GPIO4** | TX nRF9160/RAK3172 | TX pin for the NB-IoT/LoRaWAN modem. |

### SPI Line (for MAX31865)

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO19** | MOSI | MOSI Pin MAX31865 module. |
| **GPIO27** | MISO | MISO Pin MAX31865 module. |
| **GPIO12** | SCK | SCK Pin MAX31865 module. |
| **GPIO15** | NSS | Chip select MAX31865 module. |

### I2C Line (Shared between RV-3028, ADS1115, MAX17048, LIS2DH12, 24LC1025, MCP23008, MCP4017 and SHT30)

| Pin | Function | Description |
| :--- | :--- | :--- |
| **GPIO21** | I2C SDA | I2C SDA Pin. |
| **GPIO22** | I2C SCL | I2C SCL Pin. |

## 4.5 MCP23008 I/O Expander Pinout

The MCP23008 (reached over the shared I2C bus above) adds 8 extra GPIO pins (GP0-GP7), wired as follows:

| MCP Pin | Function | Description |
| :--- | :--- | :--- |
| **INT** | Interrupt output | Goes to ESP32 **GPIO34** — see **4.2 Analog and Digital Inputs** ("Wake up from MCP23008"). |
| **GP0** | RV3028 Interrupt | Connected to the RV3028 RTC's interrupt output. |
| **GP1** | SSR 1 Enable | Enables the first relay of the dual solid-state relay (GAQW212GEH). |
| **GP2** | SSR 2 Enable | Enables the second relay of the dual solid-state relay (GAQW212GEH). |
| **GP3** | AUX-IO — Pin 6 | Routed directly to the ISURLOG's AUX-IO connector, Pin 6. |
| **GP4** | AUX-IO — Pin 7 | Routed directly to the ISURLOG's AUX-IO connector, Pin 7. |
| **GP5** | AUX-IO — Pin 8 | Routed directly to the ISURLOG's AUX-IO connector, Pin 8. |
| **GP6** | LIS2DH12 INT1 | Connected to the accelerometer's INT1 interrupt output. |
| **GP7** | LIS2DH12 INT2 | Connected to the accelerometer's INT2 interrupt output. |
