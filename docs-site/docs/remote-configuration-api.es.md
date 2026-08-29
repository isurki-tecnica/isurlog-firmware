# 4. API de Configuración Remota (Downlink)

Esta guía documenta la estructura y la correspondencia de los comandos de configuración que pueden enviarse de forma remota al dispositivo **ISURLOG** mediante mensajes Downlink (por ejemplo, a través de downlinks LoRaWAN o comandos específicos de NB-IoT). Los comandos utilizan una estructura binaria, procesada por la librería Python que se adjunta, **[IsurlogLPP.py](https://github.com/isurki-tecnica/isurlog-firmware/blob/main/data_integration/IsurlogLPP.py)**.

!!! note "Nota"
    Esta es la lista completa de parámetros que el **firmware** soporta por downlink — no tiene por qué coincidir con la **[7. Referencia de Parámetros de Configuración](reference-parameters.md)**. La página 7 documenta solo lo que **IsurDASH permite configurar actualmente** a través de su interfaz; el firmware del ISURLOG puede soportar más parámetros de los que IsurDASH expone hoy. Donde la columna **Configurable en IsurDASH** dice **Sí**, enlaza a la sección correspondiente de la página 7.

## Referencia de Parámetros de Configuración (config_types)

Esta tabla completa define todas las funciones de configuración remota disponibles, su código de tipo único, el tamaño del dato, y los factores de escalado para codificar los valores.

| Nombre de Función | Tipo (Hex) | Tamaño (Bytes) | Multiplicador | Rango (Mín/Máx) | Configurable en IsurDASH | Descripción / Parámetro Equivalente |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Parámetros Globales** | | | | | | |
| `setLatencyTime` | `A0` | 1 | 1 | 1-255 | [Sí](reference-parameters.md#tiempo-de-latencia-min) | Define el tiempo (en minutos) entre ciclos de lectura. |
| `setRtcSync` | `A1` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sincronizacion-rtc) | Define si las lecturas ocurren en intervalos fijos sincronizados con el reloj (1, p. ej. 14:00, 14:05, 14:10 para una latencia de 5 min), o en intervalos relativos al momento de encendido (0). |
| `setRegisterMode` | `A2` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#modo-de-registro) | Define el Modo de registro (0=Fijo, 1=Condicional). |
| `setRegisterAccumulator` | `A3` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#acumulador-de-registros) | Define el número de registros a acumular antes de enviar. |
| `setMagnetWakeup` | `A4` | 1 | 1 | 0-1 | No | Activa/Desactiva la función de despertar por interruptor magnético. |
| `setDebugLED` | `A5` | 1 | 1 | 0-1 | No | Activa/Desactiva el LED STATUS de la PCB. |
| `setMaxPayloadSize` | `8E` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#tamano-del-payload-bytes) | Define el tamaño del payload. |
| `setBatteryInputSoC` | `8F` | 1 | 1 | 0-1 | No | Activa/Desactiva el registro del estado de carga de la batería. |
| `setBatteryInputCRate` | `90` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#73-parametros-de-configuracion-de-bateria) | Activa/Desactiva el registro de la tasa de carga/descarga de la batería. |
| `setVDCVoltage` | `91` | 1 | 1 | 0-24 | [Sí](reference-parameters.md#tension-de-alimentacion-sensores-voltios) | Define la tensión de alimentación de los sensores. |
| `setContinuousMode` | `83` | 1 | 1 | 0-1 | No | Activa/Desactiva el Modo Continuo. Cuando está activado, el ISURLOG sigue leyendo sensores sin dormir entre lecturas — completando tantos ciclos de lectura como quepan en el tiempo disponible hasta la siguiente transmisión — en vez del número fijo de ciclos definido por **Loop Cycles**. Tiene prioridad sobre `setLoopCycles`. |
| `setLoopCycles` | `84` | 1 | 1 | 0-255 | No | Define el número de lecturas tomadas por registro, promediadas entre sí (se usa para entradas de tipo analógico — Analógica, Modbus, PT100). Se ignora cuando el Modo Continuo está activado. |
| **Comunicaciones Inalámbricas (Solo BLE)** | | | | | | |
| `setLoRaWANDevEUI` | `A6` | 8 | 1 | N/A | [Sí](reference-parameters.md#lorawan) | Define el Device EUI de LoRaWAN. |
| `setLoRaWANAppEUI` | `A7` | 8 | 1 | N/A | [Sí](reference-parameters.md#lorawan) | Define el Application EUI de LoRaWAN. |
| `setLoRaWANAppKey` | `A8` | 16 | 1 | N/A | [Sí](reference-parameters.md#lorawan) | Define la Application Key de LoRaWAN. |
| `setAPN` | `93` | Variable | 1 | N/A | [Sí](reference-parameters.md#nb-iotlte-m) | Define el APN de NB-IoT/LTE-M. |
| `setExternalSIM` | `94` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#nb-iotlte-m) | Alterna entre la eSIM integrada y una Nano-SIM externa. |
| `setConPreference` | `95` | 1 | 1 | 0-2 | [Sí](reference-parameters.md#nb-iotlte-m) | Define la preferencia de conexión NB-IoT/LTE-M: `0` = Automático (todavía no está totalmente soportado por el firmware — actualmente recurre a NB-IoT), `1` = LTE-M, `2` = NB-IoT. |
| `setMaxRetryCon` | `A9` | 1 | 1 | 1-10 | No | Define el número máximo de reintentos de conexión. |
| `setWiFiSSID` | `96` | Variable | 1 | N/A | [Sí](reference-parameters.md#wi-fi) | Define el SSID de la red Wi-Fi. |
| `setWiFiPsswd` | `97` | Variable | 1 | N/A | [Sí](reference-parameters.md#wi-fi) | Define la contraseña de la red Wi-Fi. |
| `setLoRaWANClass` | `98` | 1 | 1 | 0-2 | [Sí](reference-parameters.md#lorawan) | Define la clase de dispositivo LoRaWAN (A/B/C). |
| `setMQTTIP` | `99` | Variable | 1 | N/A | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Define la IP/hostname del broker MQTT. |
| `setMQTTPort` | `9A` | Variable | 1 | N/A | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Define el puerto del broker MQTT. |
| `setMQTTUser` | `9B` | Variable | 1 | N/A | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Define el usuario de MQTT. |
| `setMQTTPasswd` | `9C` | Variable | 1 | N/A | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Define la contraseña de MQTT. |
| `setMQTTBaseTopic` | `9D` | Variable | 1 | N/A | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Define el topic base de MQTT. |
| `setSignalData` | `9E` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#mqtt-nb-iotlte-m-y-wi-fi) | Activa/Desactiva el registro de calidad de señal NB-IoT (RSRQ/RSRP). |

!!! warning "Importante"
    En IsurDASH, los parámetros de la sección **Comunicaciones Inalámbricas (Solo BLE)** de arriba solo pueden cambiarse **localmente por Bluetooth** (ver **[7.2 Parámetros de Comunicaciones Inalámbricas](reference-parameters.md#72-parametros-de-comunicaciones-inalambricas)**) — esto protege frente a una configuración remota incorrecta que deje el ISURLOG inalcanzable. Sin embargo, **el propio firmware no rechaza estos mismos códigos de tipo si llegan por un downlink de WiFi, LoRaWAN o NB-IoT** — IsurDASH simplemente nunca los envía por esa vía. Si estás integrando configuración por downlink en un SCADA o backend de terceros, ten esto en cuenta: nada en el firmware te impide enviarlos por el aire, solo la propia interfaz de IsurDASH lo restringe.

| Nombre de Función | Tipo (Hex) | Tamaño (Bytes) | Multiplicador | Rango (Mín/Máx) | Configurable en IsurDASH | Descripción / Parámetro Equivalente |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Configuración de Entrada Analógica** | | | | | | |
| `setAnalogPreAcquisition` | `AA` | 2 | 1 | 0-65535 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Define el tiempo de preadquisición (ms) para las entradas analógicas. |
| `setAnalogInputEnable` | `AB` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Activa/Desactiva la Entrada Analógica. |
| `setAnalogInputZero` | `AC` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Define el valor de ingeniería para 4mA (escalado por 100). |
| `setAnalogInputFullScale` | `AD` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Define el valor de ingeniería para 20mA (escalado por 100). |
| `setAnalogInputLow` | `AE` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Define el umbral de Alarma de Bajo (escalado por 100). |
| `setAnalogInputHigh` | `AF` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Define el umbral de Alarma de Alto (escalado por 100). |
| `setAnalogInputLowCond` | `B0` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Activa/Desactiva la transmisión condicional por Alarma de Bajo. |
| `setAnalogInputHighCond` | `B1` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-analogico-entradas-4-20ma) | Activa/Desactiva la transmisión condicional por Alarma de Alto. |
| **Configuración de Entrada Digital** | | | | | | |
| `setDigitalEnable` | `B2` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-digital) | Activa/Desactiva la Entrada Digital. |
| `setDigitalCounter` | `B3` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-digital) | Activa/Desactiva el Modo Contador de la Entrada Digital. |
| `setDigitalPulseWeight` | `B4` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#sensor-digital) | Define el Valor/Peso del Pulso (p. ej., 10 litros/pulso). |
| `setDigitalWake` | `B5` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#sensor-digital) | Define el número de pulsos necesarios para despertar el dispositivo. |
| `setDigitalLow` | `B6` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#sensor-digital) | Define el umbral de Alarma de Bajo. |
| `setDigitalHigh` | `B7` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#sensor-digital) | Define el umbral de Alarma de Alto. |
| `setDigitalLowCond` | `B8` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-digital) | Activa/Desactiva la transmisión condicional por Alarma de Bajo. |
| `setDigitalHighCond` | `B9` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-digital) | Activa/Desactiva la transmisión condicional por Alarma de Alto. |
| **Configuración Modbus (Básica)** | | | | | | |
| `setModbusPreAcquisition` | `BA` | 2 | 1 | 0-65535 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el tiempo de preadquisición (ms) para las entradas Modbus. |
| `setModbusInputEnable` | `BB` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Activa/Desactiva la Entrada Modbus. |
| `setModbusInputSlaveAddress` | `BC` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define la Dirección de Esclavo Modbus. |
| `setModbusInputRegisterAddress` | `BD` | 2 | 1 | 0-65535 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define la Dirección de Registro a leer. |
| `setModbusInputFc` | `BE` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el Código de Función Modbus (FC). |
| `setModbusInputNumberOfDecimals` | `BF` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el número de decimales para el escalado. |
| `setModbusInputIsFP` | `C0` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Activa/Desactiva la decodificación en Coma Flotante (IEEE754). |
| `setModbusInputInvert` | `C1` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Activa/Desactiva el Modo Offset Inverso. |
| `setModbusInputOffset` | `C2` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el Offset de la lectura Modbus (escalado por 100). |
| `setModbusInputLow` | `C3` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el umbral de Alarma de Bajo (escalado por 100). |
| `setModbusInputHigh` | `C4` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el umbral de Alarma de Alto (escalado por 100). |
| `setModbusInputLowCond` | `C5` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Activa/Desactiva la transmisión condicional por Alarma de Bajo. |
| `setModbusInputHighCond` | `C6` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Activa/Desactiva la transmisión condicional por Alarma de Alto. |
| **Configuración Modbus (Avanzada)** | | | | | | |
| `setModbusInputBaudrate` | `FF` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define el Baudrate de Modbus. |
| `setModbusInputDataBits` | `80` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define los Data Bits de Modbus. |
| `setModbusInputStopBits` | `81` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define los Stop Bits de Modbus. |
| `setModbusInputParity` | `82` | 1 | 1 | 0-255 | [Sí](reference-parameters.md#entradas-modbus-rs485) | Define la Paridad de Modbus. |
| **Configuración PT100** | | | | | | |
| `setPT100Enable` | `C7` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Activa/Desactiva la Entrada PT100. |
| `setPT100Wires` | `C8` | 1 | 1 | 2-4 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Define el número de hilos (2, 3, o 4). |
| `setPT100Low` | `C9` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Define el umbral de Alarma de Bajo (escalado por 100). |
| `setPT100High` | `CA` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Define el umbral de Alarma de Alto (escalado por 100). |
| `setPT100LowCond` | `CB` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Activa/Desactiva la transmisión condicional por Alarma de Bajo. |
| `setPT100HighCond` | `CC` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-pt100) | Activa/Desactiva la transmisión condicional por Alarma de Alto. |
| **Sensores Internos T/H (BME680/SHT30)** | | | | | | |
| `setINTTHEnable` | `CD` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Activa/Desactiva el sensor interno de temperatura y humedad. |
| `setINTTHTemperatureLow` | `CE` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Define el umbral de Alarma de Temperatura Baja (escalado por 100). |
| `setINTTHTemperatureHigh` | `CF` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Define el umbral de Alarma de Temperatura Alta (escalado por 100). |
| `setINTTHTemperatureLowCond` | `D0` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Activa/Desactiva la transmisión condicional por Alarma de Temperatura Baja. |
| `setINTTHTemperatureHighCond` | `D1` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Activa/Desactiva la transmisión condicional por Alarma de Temperatura Alta. |
| `setINTTHHumidityLow` | `D2` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Define el umbral de Alarma de Humedad Baja (escalado por 100). |
| `setINTTHHumidityHigh` | `D3` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Define el umbral de Alarma de Humedad Alta (escalado por 100). |
| `setINTTHHumidityLowCond` | `D4` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Activa/Desactiva la transmisión condicional por Alarma de Humedad Baja. |
| `setINTTHHumidityHighCond` | `D5` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-interno-sht30) | Activa/Desactiva la transmisión condicional por Alarma de Humedad Alta. |
| **Sensores Externos T/H (BME280/680)** | | | | | | |
| `setEXTTHEnable` | `85` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Activa/Desactiva el Sensor Externo T/H. |
| `setEXTTHTemperatureLow` | `86` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Define el umbral de Alarma de Temperatura Baja (escalado por 100). |
| `setEXTTHTemperatureHigh` | `87` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Define el umbral de Alarma de Temperatura Alta (escalado por 100). |
| `setEXTTHTemperatureLowCond` | `88` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Activa/Desactiva la transmisión condicional por Alarma de Temperatura Baja. |
| `setEXTTHTemperatureHighCond` | `89` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Activa/Desactiva la transmisión condicional por Alarma de Temperatura Alta. |
| `setEXTTHHumidityLow` | `8A` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Define el umbral de Alarma de Humedad Baja (escalado por 100). |
| `setEXTTHHumidityHigh` | `8B` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Define el umbral de Alarma de Humedad Alta (escalado por 100). |
| `setEXTTHHumidityLowCond` | `8C` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Activa/Desactiva la transmisión condicional por Alarma de Humedad Baja. |
| `setEXTTHHumidityHighCond` | `8D` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#sensor-de-temperatura-y-humedad-externo-bme280) | Activa/Desactiva la transmisión condicional por Alarma de Humedad Alta. |
| **Acelerómetro Interno (LIS2DH12)** | | | | | | |
| `setAccelEnable` | `00` | 1 | 1 | 0-1 | [Sí](reference-parameters.md#acelerometro-interno-lis2dh12) | Activa/Desactiva el acelerómetro interno. |
| `setAccellowCond` | `01` | 1 | 1 | 0-1 | No (próximamente) | Activa/Desactiva la transmisión condicional por Alarma de Bajo (por eje, mediante el canal). |
| `setAccelhighCond` | `02` | 1 | 1 | 0-1 | No (próximamente) | Activa/Desactiva la transmisión condicional por Alarma de Alto (por eje, mediante el canal). |
| `setAccelLow` | `03` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#acelerometro-interno-lis2dh12) | Define el umbral de Alarma de Bajo, en g (por eje, mediante el canal). |
| `setAccelHigh` | `04` | 2 | 100 | -327.68 a 327.67 | [Sí](reference-parameters.md#acelerometro-interno-lis2dh12) | Define el umbral de Alarma de Alto, en g (por eje, mediante el canal). |

---
