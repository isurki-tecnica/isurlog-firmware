# Reference Configuration Parameters

This section details the meaning of each parameter that can be configured on an **ISURLOG** through the IsurDASH platform.

## 8.1. General Parameters

These parameters affect the global behavior of the datalogger.

### Latency Time (**Tiempo de latencia (min)**)

* **Description:** Defines the frequency with which the **ISURLOG** wakes up from deep sleep mode to perform a complete sensor reading cycle.
* **Values:** Can currently be configured in predefined intervals of 5, 10, 15, 30, 60, or 120 minutes. (The firmware itself supports up to 255 minutes — IsurDASH's own range will be updated to match in a future release.)
* **Example:** A value of **60** will cause the device to take a data sample every hour.

### Sensor Supply Voltage (**Tensión de alimentación sensores (Voltios)**)

!!! note "Hardware Note"
    Only available on **ISURLOG v3.0 and later**.

* **Description:** Configures the supply voltage delivered to sensors through the pressure terminals marked **VDC**.
* **Values:** 9, 12, 18, or 24 V.

### Logging Mode (**Modo de registro**)

* **Description:** Determines the logic that the **ISURLOG** uses to decide when it must transmit the accumulated data. This parameter is fundamental for alarm management.
* **Options:**
    * **Fixed:** In this mode, the **ISURLOG** transmits data only when the number of cycles defined in the **Record Accumulator** has been completed. Any alarms that may be generated will be saved in the record but will not force an immediate send.
    * **Conditional:** In this mode, the **ISURLOG** transmits if either of the following two conditions is met: 1) the cycle count of the **Record Accumulator** has been completed, OR 2) an alarm condition has been detected in any of the sensors. This mode ensures that critical events are notified instantly.

### Payload size (**Tamaño del payload (bytes)**)

* **Description:** Defines the size of the data packet (payload) that the ISURLOG transmits. This value must be adjusted to ensure it is large enough to accommodate all currently activated sensors. Selecting a smaller payload size is more efficient as it allows the device to accumulate a higher number of records in its internal RAM before performing an upload to the cloud. The user can currently select between 32, 64, or 128 bytes. To optimize the payload size, please refer to the following table:

| Sensor Name | Size (hex characters) |
| :--- | :--- |
| **Digital Input** | 6 |
| **Analog Input** | 8 |
| **Modbus Input** | 8 |
| **PT100 Temperature** | 8 |
| **Internal Temperature** | 8 |
| **Internal Humidity** | 6 |
| **Battery Voltage** | 8 |
| **Unix Timestamp** | 12 |

* **Example:** If the datalogger is configured with 2 analog inputs (2*8), 2 modbus inputs (2*8), the battery voltage (1*8) and the always mandatory unix timestamp (1*12), the total is 52. In this case the optimal payload size to configure would be 64 bytes.

### Record Accumulator (**Acumulador de registros**)

* **Description:** Controls how many reading cycles (records) the **ISURLOG** must store in its internal memory before performing a data transmission to the IsurDASH platform.
* **Example:** If the Latency Time is **10 minutes** and the Accumulator is **6**, the **ISURLOG** will wake up every 10 minutes to read, but will only connect to the network and send the 6 accumulated records every **60 minutes**, thereby optimizing battery consumption.

### Latitude and Longitude (**Latitud y longitud**)

* **Description:** Allows establishing the geographical coordinates (in decimal degrees) where the device is installed. This information is used to correctly position the **ISURLOG** on the Dashboard map.

### RTC Synchronization (**Sincronización RTC**)

* **Description:** This parameter (activated/deactivated) controls whether sensor readings are performed at fixed and predictable time intervals (synchronized with the clock) or at intervals relative to the device's power-on time.
* **Options:**
    * **Activated (Recommended):** When this option is activated, the **ISURLOG** adjusts its work cycle to perform readings at exact multiples of the latency time.
        * **Example:** If the Latency Time is 5 minutes, the device will schedule its readings to occur on the hour, and five, and ten, etc. (e.g., 14:00, 14:05, 14:10).
    * **Deactivated:** If synchronization is deactivated, the **ISURLOG** will perform the first reading at the moment it is powered on, and subsequent readings will occur at intervals relative to that start time.
        * **Example:** If the Latency Time is 5 minutes and the device is powered on at 14:12, the subsequent readings will occur at 14:17, 14:22, 14:27, and so on.

### Vandalism Alert (**Alarmas por vandalismo**)

!!! note "Hardware/Firmware Note"
    Only available on **ISURLOG v3.0 and later**, with firmware **1.1.6 or later**.

* **Description:** Enables sending vandalism alarms. The device uses its internal accelerometer to detect movement, and the NB-IoT (NRF9151) modem to obtain GPS coordinates. Every time movement is detected, it sends the current coordinates through the notification channels configured by the user.
* **Consumption Note:** Because the LIS2DH12 accelerometer must stay in active (low-power) mode for this feature to work, it adds a small extra current draw. This remains compatible with battery-powered operation, but is worth taking into account when sizing battery life.

## 8.2. Wireless Communications Parameters

These parameters configure the wireless method the **ISURLOG** uses to communicate with the platform (MQTT broker, NB-IoT/LTE-M cellular settings, LoRaWAN credentials, or Wi-Fi credentials, depending on the modem fitted).

!!! note "Important"
    Unlike the other parameters on this page, wireless communication parameters are **not editable remotely via downlink** — since a bad value could cut off connectivity entirely, they can only be edited **locally over Bluetooth** (see **[6.1 Bluetooth Diagnostics Mode](datalogger-operation.md#61-bluetooth-diagnostics-mode-magnet-activated)**). Available from **firmware 1.0.8 or later**.

The fields shown depend on which communication module is fitted — NB-IoT/LTE-M, LoRaWAN, or Wi-Fi.

### MQTT (NB-IoT/LTE-M and Wi-Fi)

* **Server (Servidor):** IP address or hostname of the MQTT broker.
* **Port (Puerto):** MQTT broker port.
* **Username (Usuario):** MQTT authentication username.
* **Password (Contraseña):** MQTT authentication password.
* **Topic:** Base MQTT topic the device publishes to.
* **Log Network Quality (Registrar calidad de red):** checkbox, **NB-IoT only, firmware 1.1.6 or later**. When enabled, the device appends the NB-IoT signal quality reading (RSRQ/RSRP) to the last payload of each transmission batch — see **[11.4 Data Type Reference](https://github.com/isurki-tecnica/isurlog-firmware/wiki/11-Real-Time-Data-MQTT#114-payload-decoding-nb-iotcayenne-lpp)**.

### NB-IoT/LTE-M

* **APN:** Access Point Name for the cellular data connection.
* **External SIM (SIM externa):** checkbox. Toggles between the integrated eSIM and an external Nano-SIM — see **[4.2 SIM Management Flexibility](communications.md#sim-management-flexibility)**.
* **Connection Preference (Preferencia de conexión):** dropdown — **Automatic**, **LTE-M**, or **NB-IoT**. Selects which cellular technology the modem should connect with.
    * **Note:** **Automatic** is not fully supported by the firmware yet — selecting it currently makes the device fall back to NB-IoT.

### LoRaWAN

* **DEV EUI:** LoRaWAN Device EUI.
* **APP EUI:** LoRaWAN Application EUI.
* **APP KEY:** LoRaWAN Application Key (OTAA).
* **LoRaWAN Class (Clase LoRaWAN):** dropdown — device class (A, B, or C).
* **Confirmed Downlinks (Downlinks confirmados):** checkbox. When enabled, the device requests acknowledgment from the network for downlink messages.

### Wi-Fi

* **Wifi SSID:** Wi-Fi network name to connect to.
* **Wifi Pass:** Wi-Fi network password.
* Plus the same **MQTT** parameters described above.

## 8.3. Battery Configuration Parameters

!!! note "Hardware/Firmware Note"
    Only available on **ISURLOG v3.0 and later**, with firmware **1.1.9 or later**.

These parameters configure how the **ISURLOG's** battery is reported and monitored.

* **Battery Type (Tipo de batería):** dropdown — **Rechargeable (Li-Ion)** or **Non-rechargeable (Li-SOCl2)** — see **[3.1.4 Non-Rechargeable Batteries (Li-SOCl2)](power-supply.md#314-non-rechargeable-batteries-li-socl2)** for the corresponding hardware setup.
    * **Important:** This parameter does **not** affect the ISURLOG's own firmware behavior. It is used exclusively by **IsurDASH** to correctly convert the reported battery voltage into a percentage and apply the right low-battery thresholds for the selected battery chemistry.
* **Log Battery Variation (Registrar variación de batería):** checkbox. Enables logging of the battery's charge/discharge rate (**C-Rate**).
* **Activate Low Battery Alarms (Activar alarmas de batería baja):** checkbox. Enables or disables low-battery alarm notifications.

## 8.4. Sensor Parameters

These parameters are configured when adding or editing a specific sensor from the "Sensor List" in the configuration tab of the device.

### Analog Sensor (4-20mA Inputs)

This section allows configuring any of the **four analog inputs** of the **ISURLOG** to read sensors with a 4-20mA current output, whether they are active (externally powered) or passive (powered by the **ISURLOG**).

!!! note
    For the physical connection scheme of the sensors to the terminals, refer to the **2. Sensor Connections** section.

#### Analog Input Parameters

* **Analog Input Number (Número de entrada analógica):**
    * **Description:** Selects the physical terminal of the **ISURLOG** board (numbered from **0 to 3**) to which the sensor is connected.
* **Pre-acquisition Time (Tiempo preadquisición (ms)):**
    * **Description:** Defines a waiting time in milliseconds (ms) from when the **ISURLOG** powers the 12V output until it performs the reading. This is useful for sensors that require time to stabilize after being powered on.
* **Description (Descripción):**
    * **Description:** A name or descriptive text to identify this input in the IsurDASH platform (e.g., "North Tank Level," "Pump 2 Pressure").
* **Units (Unidad):**
    * **Description:** The engineering units in which the measured value will be displayed after conversion (e.g., "m," "bar," "pH").
* **Zero (Cero):**
    * **Description:** The engineering value that corresponds to the **4mA** current reading from the sensor.
    * **Example:** If a 0 to 5 meter level sensor measures 4mA when the tank is empty, the "Zero" value would be **0**.
* **Full Scale (Fondo de escala):**
    * **Description:** The engineering value that corresponds to the **20mA** current reading from the sensor.
    * **Example:** For the same 0 to 5 meter level sensor, the "Full Scale" would be **5**, as this corresponds to the 20mA reading when the tank is full.
* **Low Alarm (Alarma de bajo):**
    * **Description:** Defines the lower numerical threshold for this input. If the measured value (in its engineering units) falls below this threshold, an alarm will be recorded.
* **High Alarm (Alarma de alto):**
    * **Description:** Defines the upper numerical threshold. If the measured value exceeds this threshold, an alarm will be recorded.
* **Activate Low Alarm (Activar alarma de bajo):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Alarm (Activar alarma de alto):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Alarm Condition (Activar condición de alarmas de bajo):**
    * **Description:** This is a checkbox field. If activated, a low-value alarm will force an **immediate data transmission** when the Logging Mode is set to "**Conditional**".
* **Activate High Alarm Condition (Activar condición de alarmas de alto):**
    * **Description:** This is a checkbox field. If activated, a high-value alarm will force an **immediate transmission** when the Logging Mode is set to "**Conditional**".

### Digital Sensor

This section details the configuration of the digital input on the **ISURLOG**. The input can operate as a state detector (open/closed) or as a pulse counter.

!!! note
    For the physical connection scheme of the sensor to the terminals, the user should consult the **2. Sensor Connections** section.

#### Digital Sensor Parameters

* **Description (Descripción):**
    * **Description:** A name or descriptive text to identify this input in the IsurDASH platform (e.g., "Farm Water Meter," "Ship Hatch Alarm").
* **Unit (Unidad):**
    * **Description:** The unit of measure for the registered value. In "Counter" mode, this can be "pulses," "liters," "m³," "kW," etc..
* **Mode (Modo):**
    * **Description:** Defines the behavior of the digital input.
    * **Options:**
        * **State:** In this mode, the **ISURLOG** will read and register the binary state of the input in each cycle: **1** (active/closed) or **0** (inactive/open).
        * **Counter:** In this mode, the **ISURLOG** utilizes its ultra-low consumption processor to count the pulses received, even while the device is in deep sleep. In each reading cycle, the total number of pulses counted since the last counter reset is registered.
* **Pulse Value (Valor impulso):**
    * **Description:** Parameter applicable only in "Counter" mode. It allows assigning a weight or value to each counted pulse to convert it to engineering units. The final registered value will be (Number of Pulses) x (Pulse Value).
    * **Example:** If a water meter emits one pulse for every 10 liters, the "Pulse Value" should be configured to **10**.
* **Pulses to Wake Up (Pulsos para despertar):**
    * **Description:** Parameter applicable only in "Counter" mode. Defines a number of pulses that, when reached, will immediately wake up the **ISURLOG** and force a data transmission, without waiting for the next Latency Time.
* **Low Alarm (Alarma de bajo):**
    * **Description:** Defines the lower numerical threshold. If the final measured value (the state, or the pulses multiplied by their value) falls below this threshold, an alarm will be recorded.
* **High Alarm (Alarma de alto):**
    * **Description:** Defines the upper numerical threshold. If the final measured value exceeds this threshold, an alarm will be recorded.
* **Activate Low Alarm (Activar alarma de bajo):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Alarm (Activar alarma de alto):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Alarm Condition (Activar condición de alarmas de bajo):**
    * **Description:** This is a checkbox field. If activated, a low-value alarm will force an **immediate data transmission** when the Logging Mode is set to "**Conditional**".
* **Activate High Alarm Condition (Activar condición de alarmas de alto):**
    * **Description:** This is a checkbox field. If activated, a high-value alarm will force an **immediate transmission** when the Logging Mode is set to "**Conditional**".

### Modbus Inputs (RS485)

This section allows configuring readings from external devices that utilize the Modbus RTU protocol via the **ISURLOG's** RS485 interface.

!!! note
    For the physical wiring scheme of the sensors to the RS485 bus, the user should consult the **2. Sensor Connections** section.

#### Modbus Parameters

* **Modbus Input Number (Número de entrada modbus):**
    * **Description:** A virtual identifier for a Modbus reading (the **ISURLOG** admits up to 4). It is important to note that although multiple inputs can be configured, all Modbus sensors are physically connected to the same RS485 bus.
* **Baudrate:**
    * **Description:** Defines the baudrate for modbus communication.
* **Data bits:**
    * **Description:** Defines the data bits for modbus communication.
* **Stop bits:**
    * **Description:** Defines the stop bits for modbus communication.
* **Parity:**
    * **Description:** Defines the parity for modbus communication.
* **Pre-acquisition Time (Tiempo preadquisición (ms)):**
    * **Description:** Defines a waiting time in milliseconds (ms) from when the **ISURLOG** powers the external sensors until it starts Modbus communication. This is useful to allow time for Modbus slaves to start up and stabilize.
* **Description (Descripción):**
    * **Description:** A name or descriptive text to identify this reading in the platform (e.g., "Pump 1 Status," "Chlorine Analyzer").
* **Units (Unidad):**
    * **Description:** The units in which the read value will be displayed (e.g., "RPM," "mg/L," "Status").
* **Slave Address (Dirección esclavo):**
    * **Description:** The ID address of the Modbus slave device on the RS485 bus, typically a value between 1 and 247.
* **Register Address (Dirección registro):**
    * **Description:** The address of the specific register to be read within the slave device.
* **Function Code (Function code):**
    * **Description:** The Modbus function code that will be used for the reading. Possible values are 1 (Read Coils), 2 (Read Discrete Inputs), 3 (Read Holding Registers), or 4 (Read Input Registers).
* **IEEE754 Register (Registro IEEE 754):**
    * **Description:** This is a checkbox field. It must be activated if the value to be read occupies two consecutive registers and is encoded in the 32-bit IEEE 754 floating-point format.
* **Number of Decimals (Número de decimales):**
    * **Description:** Applies a division factor to the numerical values read to position the decimal point. The value read is divided by 10 raised to this number.
    * **Example:** If the device returns 2530 and 2 decimals are configured, the final value will be 25.30 (because $2530 / 10^2 = 25.30$).
* **Offset:**
    * **Description:** A numerical value that is added or subtracted from the read value (already adjusted by the decimals) to perform a final calibration or adjustment.
* **Mode (Modo):**
    * **Description:** Defines how the Offset is applied to the value.
    * **Options:**
        * **Direct (Directo):** The final value is calculated as: (Read Value) - Offset.
        * **Inverse (Inverso):** The final value is calculated as: Offset - (Read Value).
* **Low Alarm (Alarma de bajo):**
    * **Description:** Defines the lower numerical threshold. If the final measured value (the state, or the pulses multiplied by their value) falls below this threshold, an alarm will be recorded.
* **High Alarm (Alarma de alto):**
    * **Description:** Defines the upper numerical threshold. If the final measured value exceeds this threshold, an alarm will be recorded.
* **Activate Low Alarm (Activar alarma de bajo):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Alarm (Activar alarma de alto):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Alarm Condition (Activar condición de alarmas de bajo):**
    * **Description:** This is a checkbox field. If activated, a low-value alarm will force an **immediate data transmission** when the Logging Mode is set to "**Conditional**".
* **Activate High Alarm Condition (Activar condición de alarmas de alto):**
    * **Description:** This is a checkbox field. If activated, a high-value alarm will force an **immediate transmission** when the Logging Mode is set to "**Conditional**".

### PT100 Temperature Sensor

This section details the parameters for configuring the input for PT100 temperature probes.

!!! note
    For the physical connection scheme and the probe's hardware configuration, the user should consult the **2. Sensor Connections** section (specifically the PT100 subsection).

#### PT100 Parameters

* **Number of Wires (Número de hilos):**
    * **Description:** Allows selecting the configuration of the PT100 temperature probe according to the number of wires it utilizes.
    * **Options:** 2, 3, or 4 wires.

!!! note "Important Note"
    The wire count configuration must be performed both in **software** (via this parameter) and in **hardware** (by soldering jumpers on the PCB board). Both settings must match to ensure an accurate reading.

* **Low Alarm (Alarma de bajo):**
    * **Description:** Defines the minimum temperature threshold. If the measured temperature falls below this value, an alarm will be recorded.
    * **Units:** Degrees Celsius (ºC).
* **High Alarm (Alarma de alto):**
    * **Description:** Defines the maximum temperature threshold. If the measured temperature exceeds this value, an alarm will be recorded.
    * **Units:** Degrees Celsius (ºC).

* **Activate Low Alarm (Activar alarma de bajo):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Alarm (Activar alarma de alto):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Alarm Condition (Activar condición de alarmas de bajo):**
    * **Description:** This is a checkbox field. If activated, a low-value alarm will force an **immediate data transmission** when the Logging Mode is set to "**Conditional**".
* **Activate High Alarm Condition (Activar condición de alarmas de alto):**
    * **Description:** This is a checkbox field. If activated, a high-value alarm will force an **immediate transmission** when the Logging Mode is set to "**Conditional**".

### Internal Temperature and Humidity Sensor (SHT30)

These parameters configure the alarms for the temperature and humidity sensor integrated onto the **ISURLOG** board itself.

#### Temperature Parameters

* **Low Temperature Alarm (Alarma de bajo de temperatura):**
    * **Description:** Defines the minimum temperature threshold. If the temperature measured by the internal sensor falls below this value, an alarm event will be recorded.
    * **Units:** Degrees Celsius (ºC).
* **High Temperature Alarm (Alarma de alto de temperatura):**
    * **Description:** Defines the maximum temperature threshold. If the temperature measured exceeds this value, an alarm event will be recorded.
    * **Units:** Degrees Celsius (ºC).
* **Activate Low Temperature Alarm (Activar alarma de bajo de temperatura):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Temperature Alarm (Activar alarma de alto de temperatura):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Temperature Alarm Condition (Activar condición de alarmas de bajo de temperatura):**
    * **Description:** This is a checkbox field (activated/deactivated). If activated, a low temperature alarm will contribute to the general alarm condition that forces an **immediate transmission** when the Logging Mode is set to "**Conditional**". If deactivated, the alarm event will only be informative.
* **Activate High Temperature Alarm Condition (Activar condición de alarmas de alto de temperatura):**
    * **Description:** This is a checkbox field. If activated, a high temperature alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**". If deactivated, the alarm will only be informative.

#### Humidity Parameters

* **Low Humidity Alarm (Alarma de bajo de humedad):**
    * **Description:** Defines the minimum relative humidity threshold. If the measured humidity falls below this value, an alarm event will be recorded.
    * **Units:** Relative Humidity Percentage (%RH).
* **High Humidity Alarm (Alarma de alto de humedad):**
    * **Description:** Defines the maximum relative humidity threshold. If the measured humidity exceeds this value, an alarm event will be recorded.
    * **Units:** Relative Humidity Percentage (%RH).
* **Activate Low Humidity Alarm (Activar alarma de bajo de humedad):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Humidity Alarm (Activar alarma de alto de humedad):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Humidity Alarm Condition (Activar condición de alarmas de bajo de humedad):**
    * **Description:** This is a checkbox field. When activated, a low humidity alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**".
* **Activate High Humidity Alarm Condition (Activar condición de alarmas de alto de humedad):**
    * **Description:** This is a checkbox field. When activated, a high humidity alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**".

### External Temperature and Humidity Sensor (BME280)

These parameters configure the alarms for the external temperature and humidity sensor connected via I2C the **ISURLOG**.

#### Temperature Parameters

* **Low Temperature Alarm (Alarma de bajo de temperatura):**
    * **Description:** Defines the minimum temperature threshold. If the temperature measured by the internal sensor falls below this value, an alarm event will be recorded.
    * **Units:** Degrees Celsius (ºC).
* **High Temperature Alarm (Alarma de alto de temperatura):**
    * **Description:** Defines the maximum temperature threshold. If the temperature measured exceeds this value, an alarm event will be recorded.
    * **Units:** Degrees Celsius (ºC).
* **Activate Low Temperature Alarm (Activar alarma de bajo de temperatura):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Temperature Alarm (Activar alarma de alto de temperatura):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Temperature Alarm Condition (Activar condición de alarmas de bajo de temperatura):**
    * **Description:** This is a checkbox field (activated/deactivated). If activated, a low temperature alarm will contribute to the general alarm condition that forces an **immediate transmission** when the Logging Mode is set to "**Conditional**". If deactivated, the alarm event will only be informative.
* **Activate High Temperature Alarm Condition (Activar condición de alarmas de alto de temperatura):**
    * **Description:** This is a checkbox field. If activated, a high temperature alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**". If deactivated, the alarm will only be informative.

#### Humidity Parameters

* **Low Humidity Alarm (Alarma de bajo de humedad):**
    * **Description:** Defines the minimum relative humidity threshold. If the measured humidity falls below this value, an alarm event will be recorded.
    * **Units:** Relative Humidity Percentage (%RH).
* **High Humidity Alarm (Alarma de alto de humedad):**
    * **Description:** Defines the maximum relative humidity threshold. If the measured humidity exceeds this value, an alarm event will be recorded.
    * **Units:** Relative Humidity Percentage (%RH).
* **Activate Low Humidity Alarm (Activar alarma de bajo de humedad):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.".
* **Activate High Humidity Alarm (Activar alarma de alto de humedad):**
    * **Description:** This is a checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **Activate Low Humidity Alarm Condition (Activar condición de alarmas de bajo de humedad):**
    * **Description:** This is a checkbox field. When activated, a low humidity alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**".
* **Activate High Humidity Alarm Condition (Activar condición de alarmas de alto de humedad):**
    * **Description:** This is a checkbox field. When activated, a high humidity alarm will force an **immediate transmission** in the Logging Mode set to "**Conditional**".

### Internal Accelerometer (LIS2DH12)

!!! note "Hardware/Firmware Note"
    Only available on **ISURLOG v3.0 and later**, with firmware **1.1.6 or later**.

This section configures independent alarm thresholds for each of the three acceleration axes (X, Y, Z) measured by the on-board **LIS2DH12** accelerometer.

The same four parameters repeat per axis (**X**, **Y**, **Z**):

* **Low Alarm (Alarma de bajo eje X/Y/Z):** Defines the lower acceleration threshold (in g) for that axis. If the measured value falls below this threshold, an alarm will be recorded.
* **Activate Low Alarm (Activar alarma de bajo eje X/Y/Z):** Checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.
* **High Alarm (Alarma de alto eje X/Y/Z):** Defines the upper acceleration threshold (in g) for that axis. If the measured value exceeds this threshold, an alarm will be recorded.
* **Activate High Alarm (Activar alarma de alto eje X/Y/Z):** Checkbox field. If activated, the system will send an alarm notification via the configured text/messaging options (SMS, Telegram, Email) *in addition* to recording the alarm on the platform. This is independent of the "Conditional" Logging Mode transmission.

!!! note "Coming Soon"
    The firmware already supports forcing an immediate transmission from an axis alarm when the Logging Mode is set to "Conditional" (the same **Activate Alarm Condition** behavior available for the other sensors), but this option is **not yet exposed in IsurDASH** for the accelerometer axes. It will be made available in an upcoming platform update.
