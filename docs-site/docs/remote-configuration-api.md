# 12. Remote Configuration API (Downlink)

This guide documents the structure and mapping of configuration commands that can be sent remotely to the **ISURLOG** device via Downlink messages (e.g., through LoRaWAN downlinks or specific NB-IoT commands). The commands utilize a binary structure, processed by the accompanying Python library, `IsurlogLPP.py`.

!!! note "Note"
    This is the full list of parameters the **firmware** supports over downlink — it doesn't necessarily match **[8. Reference Configuration Parameters](reference-parameters.md)**. Page 8 documents only what **IsurDASH currently lets you configure** through its UI; the ISURLOG firmware can support more parameters than IsurDASH currently exposes. Where the **IsurDASH Configurable** column says **Yes**, it links to the corresponding section of page 8.

## Configuration Parameter Reference (config_types)

This comprehensive table defines all available remote configuration functions, their unique type code, data size, and scaling factors for encoding values.

| Function Name | Type (Hex) | Size (Bytes) | Multiplier | Range (Min/Max) | IsurDASH Configurable | Description / Equivalent Parameter |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Global Parameters** | | | | | | |
| `setLatencyTime` | `A0` | 1 | 1 | 1-255 | [Yes](reference-parameters.md#latency-time-tiempo-de-latencia-min) | Sets the time (minutes) between reading cycles. |
| `setRtcSync` | `A1` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#rtc-synchronization-sincronizacion-rtc) | Sets whether readings occur at fixed clock-synchronized intervals (1, e.g. 14:00, 14:05, 14:10 for a 5-min latency) or at intervals relative to power-on time instead (0). |
| `setRegisterMode` | `A2` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#logging-mode-modo-de-registro) | Sets Logging Mode (0=Fixed, 1=Conditional). |
| `setRegisterAccumulator` | `A3` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#record-accumulator-acumulador-de-registros) | Sets the number of records to accumulate before sending. |
| `setMagnetWakeup` | `A4` | 1 | 1 | 0-1 | No | Enables/Disables the magnetic switch wake-up feature. |
| `setDebugLED` | `A5` | 1 | 1 | 0-1 | No | Enables/Disables the STATUS LED on the PCB. |
| `setMaxPayloadSize` | `8E` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#payload-size-tamano-del-payload-bytes) | Sets the payload size. |
| `setBatteryInputSoC` | `8F` | 1 | 1 | 0-1 | No | Enables/Disables logging of battery State of Charge. |
| `setBatteryInputCRate` | `90` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#83-battery-configuration-parameters) | Enables/Disables logging of the battery's charge/discharge rate. |
| `setVDCVoltage` | `91` | 1 | 1 | 0-24 | [Yes](reference-parameters.md#sensor-supply-voltage-tension-de-alimentacion-sensores-voltios) | Sets the sensor supply voltage. |
| `setContinuousMode` | `83` | 1 | 1 | 0-1 | No | Enables/Disables Continuous Mode. When enabled, the ISURLOG keeps reading sensors without sleeping between readings — filling as many reading cycles as fit in the time available until the next transmission — instead of the fixed number of cycles set by **Loop Cycles**. Overrides `setLoopCycles`. |
| `setLoopCycles` | `84` | 1 | 1 | 0-255 | No | Sets the number of readings taken per record, averaged together (used for analog-type inputs — Analog, Modbus, PT100). Ignored when Continuous Mode is enabled. |
| **Wireless Communications (BLE-only)** | | | | | | |
| `setLoRaWANDevEUI` | `A6` | 8 | 1 | N/A | [Yes](reference-parameters.md#lorawan) | Sets the LoRaWAN Device EUI. |
| `setLoRaWANAppEUI` | `A7` | 8 | 1 | N/A | [Yes](reference-parameters.md#lorawan) | Sets the LoRaWAN Application EUI. |
| `setLoRaWANAppKey` | `A8` | 16 | 1 | N/A | [Yes](reference-parameters.md#lorawan) | Sets the LoRaWAN Application Key. |
| `setAPN` | `93` | Variable | 1 | N/A | [Yes](reference-parameters.md#nb-iotlte-m) | Sets the NB-IoT/LTE-M APN. |
| `setExternalSIM` | `94` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#nb-iotlte-m) | Toggles between the integrated eSIM and an external Nano-SIM. |
| `setConPreference` | `95` | 1 | 1 | 0-2 | [Yes](reference-parameters.md#nb-iotlte-m) | Sets the NB-IoT/LTE-M connection preference: `0` = Automatic (not fully supported by the firmware yet — currently falls back to NB-IoT), `1` = LTE-M, `2` = NB-IoT. |
| `setMaxRetryCon` | `A9` | 1 | 1 | 1-10 | No | Sets the maximum number of connection retry attempts. |
| `setWiFiSSID` | `96` | Variable | 1 | N/A | [Yes](reference-parameters.md#wi-fi) | Sets the Wi-Fi network SSID. |
| `setWiFiPsswd` | `97` | Variable | 1 | N/A | [Yes](reference-parameters.md#wi-fi) | Sets the Wi-Fi network password. |
| `setLoRaWANClass` | `98` | 1 | 1 | 0-2 | [Yes](reference-parameters.md#lorawan) | Sets the LoRaWAN device class (A/B/C). |
| `setMQTTIP` | `99` | Variable | 1 | N/A | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Sets the MQTT broker IP/hostname. |
| `setMQTTPort` | `9A` | Variable | 1 | N/A | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Sets the MQTT broker port. |
| `setMQTTUser` | `9B` | Variable | 1 | N/A | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Sets the MQTT username. |
| `setMQTTPasswd` | `9C` | Variable | 1 | N/A | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Sets the MQTT password. |
| `setMQTTBaseTopic` | `9D` | Variable | 1 | N/A | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Sets the MQTT base topic. |
| `setSignalData` | `9E` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#mqtt-nb-iotlte-m-and-wi-fi) | Enables/Disables logging NB-IoT signal quality (RSRQ/RSRP). |

!!! warning "Important"
    In IsurDASH, the parameters in the **Wireless Communications (BLE-only)** section above can only be changed **locally over Bluetooth** (see **[8.2 Wireless Communications Parameters](reference-parameters.md#82-wireless-communications-parameters)**) — this protects against a bad remote configuration leaving the ISURLOG unreachable. However, **the firmware itself does not reject these same type codes if they arrive over a WiFi, LoRaWAN, or NB-IoT downlink** — IsurDASH simply never sends them that way. If you are integrating downlink configuration into a third-party SCADA or backend, keep this in mind: nothing in the firmware stops you from sending these over the air, only IsurDASH's own UI restricts it.

| Function Name | Type (Hex) | Size (Bytes) | Multiplier | Range (Min/Max) | IsurDASH Configurable | Description / Equivalent Parameter |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Analog Input Configuration** | | | | | | |
| `setAnalogPreAcquisition` | `AA` | 2 | 1 | 0-65535 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Sets pre-acquisition time (ms) for analog inputs. |
| `setAnalogInputEnable` | `AB` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Enables/Disables the Analog Input. |
| `setAnalogInputZero` | `AC` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Sets the 4mA engineering value (scaled by 100). |
| `setAnalogInputFullScale` | `AD` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Sets the 20mA engineering value (scaled by 100). |
| `setAnalogInputLow` | `AE` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Sets the Low Alarm threshold (scaled by 100). |
| `setAnalogInputHigh` | `AF` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Sets the High Alarm threshold (scaled by 100). |
| `setAnalogInputLowCond` | `B0` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Enables/Disables Low Alarm conditional transmission. |
| `setAnalogInputHighCond` | `B1` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#analog-sensor-4-20ma-inputs) | Enables/Disables High Alarm conditional transmission. |
| **Digital Input Configuration** | | | | | | |
| `setDigitalEnable` | `B2` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#digital-sensor) | Enables/Disables the Digital Input. |
| `setDigitalCounter` | `B3` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#digital-sensor) | Enables/Disables Digital Input Counter Mode. |
| `setDigitalPulseWeight` | `B4` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#digital-sensor) | Sets the Pulse Value/Weight (e.g., 10 liters/pulse). |
| `setDigitalWake` | `B5` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#digital-sensor) | Sets the number of pulses required to wake the device. |
| `setDigitalLow` | `B6` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#digital-sensor) | Sets the Low Alarm threshold. |
| `setDigitalHigh` | `B7` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#digital-sensor) | Sets the High Alarm threshold. |
| `setDigitalLowCond` | `B8` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#digital-sensor) | Enables/Disables Low Alarm conditional transmission. |
| `setDigitalHighCond` | `B9` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#digital-sensor) | Enables/Disables High Alarm conditional transmission. |
| **Modbus Configuration (Base)** | | | | | | |
| `setModbusPreAcquisition` | `BA` | 2 | 1 | 0-65535 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets pre-acquisition time (ms) for Modbus inputs. |
| `setModbusInputEnable` | `BB` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Enables/Disables the Modbus Input. |
| `setModbusInputSlaveAddress` | `BC` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Slave Address. |
| `setModbusInputRegisterAddress` | `BD` | 2 | 1 | 0-65535 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Register Address to read. |
| `setModbusInputFc` | `BE` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Function Code (FC). |
| `setModbusInputNumberOfDecimals` | `BF` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the number of decimal places for scaling. |
| `setModbusInputIsFP` | `C0` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Enables/Disables Floating Point (IEEE754) decoding. |
| `setModbusInputInvert` | `C1` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Enables/Disables Inverse Offset Mode. |
| `setModbusInputOffset` | `C2` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus reading Offset (scaled by 100). |
| `setModbusInputLow` | `C3` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Low Alarm threshold (scaled by 100). |
| `setModbusInputHigh` | `C4` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the High Alarm threshold (scaled by 100). |
| `setModbusInputLowCond` | `C5` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Enables/Disables Low Alarm conditional transmission. |
| `setModbusInputHighCond` | `C6` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Enables/Disables High Alarm conditional transmission. |
| **Modbus Configuration (Advanced)** | | | | | | |
| `setModbusInputBaudrate` | `FF` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Baudrate. |
| `setModbusInputDataBits` | `80` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Data Bits. |
| `setModbusInputStopBits` | `81` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Stop Bits. |
| `setModbusInputParity` | `82` | 1 | 1 | 0-255 | [Yes](reference-parameters.md#modbus-inputs-rs485) | Sets the Modbus Parity. |
| **PT100 Configuration** | | | | | | |
| `setPT100Enable` | `C7` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Enables/Disables the PT100 Input. |
| `setPT100Wires` | `C8` | 1 | 1 | 2-4 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Sets the number of wires (2, 3, or 4). |
| `setPT100Low` | `C9` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Sets the Low Alarm threshold (scaled by 100). |
| `setPT100High` | `CA` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Sets the High Alarm threshold (scaled by 100). |
| `setPT100LowCond` | `CB` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Enables/Disables Low Alarm conditional transmission. |
| `setPT100HighCond` | `CC` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#pt100-temperature-sensor) | Enables/Disables High Alarm conditional transmission. |
| **Internal T/H Sensors (BME680/SHT30)** | | | | | | |
| `setINTTHEnable` | `CD` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Enables/Disables the internal temperature and humidity sensor. |
| `setINTTHTemperatureLow` | `CE` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Sets the Low Temp Alarm threshold (scaled by 100). |
| `setINTTHTemperatureHigh` | `CF` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Sets the High Temp Alarm threshold (scaled by 100). |
| `setINTTHTemperatureLowCond` | `D0` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Enables/Disables Low Temp Alarm conditional transmission. |
| `setINTTHTemperatureHighCond` | `D1` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Enables/Disables High Temp Alarm conditional transmission. |
| `setINTTHHumidityLow` | `D2` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Sets the Low Humidity Alarm threshold (scaled by 100). |
| `setINTTHHumidityHigh` | `D3` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Sets the High Humidity Alarm threshold (scaled by 100). |
| `setINTTHHumidityLowCond` | `D4` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Enables/Disables Low Humidity Alarm conditional transmission. |
| `setINTTHHumidityHighCond` | `D5` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-temperature-and-humidity-sensor-sht30) | Enables/Disables High Humidity Alarm conditional transmission. |
| **External T/H Sensors (BME280/680)** | | | | | | |
| `setEXTTHEnable` | `85` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Enables/Disables the External T/H Sensor. |
| `setEXTTHTemperatureLow` | `86` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Sets the Low Temp Alarm threshold (scaled by 100). |
| `setEXTTHTemperatureHigh` | `87` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Sets the High Temp Alarm threshold (scaled by 100). |
| `setEXTTHTemperatureLowCond` | `88` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Enables/Disables Low Temp Alarm conditional transmission. |
| `setEXTTHTemperatureHighCond` | `89` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Enables/Disables High Temp Alarm conditional transmission. |
| `setEXTTHHumidityLow` | `8A` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Sets the Low Humidity Alarm threshold (scaled by 100). |
| `setEXTTHHumidityHigh` | `8B` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Sets the High Humidity Alarm threshold (scaled by 100). |
| `setEXTTHHumidityLowCond` | `8C` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Enables/Disables Low Humidity Alarm conditional transmission. |
| `setEXTTHHumidityHighCond` | `8D` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#external-temperature-and-humidity-sensor-bme280) | Enables/Disables High Humidity Alarm conditional transmission. |
| **Internal Accelerometer (LIS2DH12)** | | | | | | |
| `setAccelEnable` | `00` | 1 | 1 | 0-1 | [Yes](reference-parameters.md#internal-accelerometer-lis2dh12) | Enables/Disables the internal accelerometer. |
| `setAccellowCond` | `01` | 1 | 1 | 0-1 | No (coming soon) | Enables/Disables Low Alarm conditional transmission (per axis, via channel). |
| `setAccelhighCond` | `02` | 1 | 1 | 0-1 | No (coming soon) | Enables/Disables High Alarm conditional transmission (per axis, via channel). |
| `setAccelLow` | `03` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-accelerometer-lis2dh12) | Sets the Low Alarm threshold, in g (per axis, via channel). |
| `setAccelHigh` | `04` | 2 | 100 | -327.68 to 327.67 | [Yes](reference-parameters.md#internal-accelerometer-lis2dh12) | Sets the High Alarm threshold, in g (per axis, via channel). |

---
