# 2.1 Referencia de Módulos y Librerías (Guía de API)

!!! note "Alcance"
    Esta página documenta el árbol de código de **producción** — `app/main.py`, `ports/esp32/modules/modules/` (envoltorios de alto nivel) y `ports/esp32/modules/lib/` (drivers de bajo nivel) — tal como se sigue en la rama `main` de este repositorio. Si trabajas desde el sandbox de desarrollo interno, algunos módulos experimentales (variantes asíncronas, drivers de almacenamiento alternativos, etc.) pueden no estar todavía listados aquí porque aún no se han promovido a este repositorio. Ver **[8. Flujo de Desarrollo (Sandbox → Producción)]** *(próximamente)* para saber cómo funciona esa promoción.

Esta página complementa **[2. Visión General de la Arquitectura](architecture-overview.md)**: aquella página explica conceptualmente la separación entre `/lib` y `/modules`, esta es la referencia archivo por archivo — qué hace cada módulo, de qué depende, y qué configuración lee.

---

## 2.1.1 Referencia Rápida

| Módulo (`modules/`) | Propósito | Síncrono/Asíncrono |
|---|---|---|
| `utils.py` | Logging (`log_debug`/`log_info`/...) y pequeñas utilidades. Importado por casi todo. | síncrono |
| `config_manager.py` | Carga `static_config.json` / `dynamic_config.json`, aplica actualizaciones de configuración remota (downlink). | síncrono |
| `_auth.py` | Bloqueo de la consola REPL protegido por PIN (AES). | síncrono |
| `version.py` | Constante de versión del firmware. | síncrono |
| `power_manager.py` | RTC (DS3231/RV3028), programación de despertares, raíles de tensión, reposo profundo. | síncrono |
| `rtc_memory.py` | Estado persistente en reposo profundo (contador de ciclos, estados de válvulas, búfer de payloads). | síncrono |
| `wifi.py` | Conexión Wi-Fi STA, exige WPA2 o superior. | asíncrono |
| `nb_iot.py` | Driver del módem NB-IoT Nordic nRF9160: registro de red, MQTT sobre el módem, HTTP (OTA), GPS/NTN. | asíncrono |
| `lorawan.py` | Driver del módem LoRaWAN RAK3172 (RUI3 AT): unión a la red, uplink, downlink, sondeo de Clase C. | asíncrono |
| `umqttsimple.py` | Cliente MQTT ligero (solo transporte Wi-Fi). | síncrono |
| `ble_manager.py` | Servidor GATT BLE para configuración/monitorización local (activado por imán). | asíncrono |
| `downlink_manager.py` | Unifica la gestión de downlinks entre Wi-Fi/NB-IoT/LoRaWAN; dispara OTA y configuración remota. | asíncrono |
| `remote_repl.py` | REPL remota de Python sobre MQTT (puerta trasera de depuración — ver notas). | mixto |
| `analog_sensor.py` | Envoltorio de entrada analógica 4-20mA basado en ADS1115. | síncrono |
| `digital_sensor.py` | Contador de pulsos de bajo consumo basado en ULP. | síncrono |
| `bme_sensor.py` | Envoltorio con autodetección de BMP280/BME280/BME680 (temperatura/humedad/presión/gas + IAQ). | síncrono |
| `sht30_sensor.py` | Envoltorio de temperatura/humedad SHT30. | síncrono |
| `max31865_sensor.py` | Envoltorio PT100/PT1000 (vía MAX31865). | síncrono |
| `modbus_sensor.py` | Envoltorio maestro Modbus RTU sobre RS485. | síncrono |
| `accel_manager.py` | Detección antirrobo/manipulación con LIS2DH12 + MCP23008. | síncrono |
| `battery_monitor.py` | Lectura de tensión de batería por el ADC del ESP32 (respaldo sin MAX17048). | síncrono |
| `internal_storage.py` | Respaldo FIFO de payloads en la flash interna. | síncrono |
| `update_manager.py` | Soporte OTA: checksum, decodificación base64, sustitución segura de `main.py`. | síncrono |
| `led_manager.py` | Patrón de parpadeo del LED de estado, gestionado por ULP. | síncrono |

---

## 2.1.2 Módulos — Referencia Detallada

### Core / Arranque

**`utils.py`**

- Propósito: logging centralizado (`log_debug`, `log_info`, `log_warning`, `log_error`) controlado por `static_config.log_level`, además de `get_datetime_string()` / `save_data_to_file()`.
- Depende de: nada (módulo base — importado por casi todos los demás).
- Configuración: `static_config.log_level`, resuelto desde `config_manager` en el primer uso (una importación diferida — `config_manager.py` importa `utils` a nivel de módulo, así que importar de vuelta en `utils` a nivel de módulo sería circular).

**`config_manager.py`**

- Propósito: el propietario canónico de `static_config.json` (inmutable, de hardware) y `dynamic_config.json` (mutable en tiempo de ejecución). Aplica actualizaciones de configuración remota mediante `CONFIG_MAP`, que asocia ~90 nombres de comandos remotos (p. ej. `setLatencyTime`) con rutas JSON anidadas.
- API pública: `ConfigManager.get_static(*keys, default=None)`, `get_dynamic(*keys, default=None)`, `apply_single_update(...)`, `apply_conf_update(decoded_data)`, `save_dynamic_config()`. Singleton global: `config_manager`.
- Depende de: `utils`.

**`_auth.py`**

- Propósito: bloqueo de la consola REPL protegido por PIN. Se ejecuta automáticamente al importarse (no solo definiciones) — hasta 3 intentos, reinicia el dispositivo si fallan todos.
- API pública: `run_authentication()`, `pad_data(...)`, `get_encrypted_pin_secret()`.
- Depende de: `config_manager` (lee `static_config.pin`); usa directamente el módulo integrado `cryptolib` (AES-ECB).

**`version.py`**

- Propósito: una única constante `VERSION`, mostrada en el mensaje de arranque. Incrementarla en cada release.

### Energía y Tiempo

**`power_manager.py`**

- Propósito: el centro del sistema de energía/tiempo. Detecta el chip RTC presente (DS3231 o RV3028), sincroniza la hora desde NB-IoT/Wi-Fi (NTP)/LoRaWAN/GPS, calcula el próximo despertar alineado, controla los raíles de 12V/5V y las salidas digitales, ajusta la frecuencia de la CPU, configura las fuentes de despertar, y activa el reposo profundo. Singleton global: `pm`.
- API pública (selección): `check_rtc_status()`, `set_rtc_time(time_str, mode)`, `seconds2wakeup()`, `control_5v(state)`, `control_vdc(state)`, `configure_wakeup_sources(...)`, `go_to_sleep()`.
- Depende de: `lib/uds3231` o `lib/RV3028` (el que se detecte en el I2C).
- Configuración: `static_config.pinout.{i2c,rs485,control,magnet_pin}`, `dynamic_config.general.{rtc_sync,latency_time,magnet_wakeup}`, `dynamic_config.digital_config.{enable,counter}`.
- Nota: las esperas de la válvula proporcional (EV) y de fallo OTA en `downlink_manager.py` usan directamente `time.sleep_ms()` / `await asyncio.sleep_ms()`, no un método de `power_manager` — tenlo en cuenta si buscas aquí un helper de "sleep", no lo hay.

**`rtc_memory.py`**

- Propósito: estado guardado en la memoria RTC del ESP32 (sobrevive al reposo profundo, no a un corte de alimentación): contador de ciclos acumulado, flag de alarma, estados manuales de válvula (EV), marca de tiempo de la última sincronización RTC, y un búfer de payloads LPP codificados pendientes de transmisión.
- API pública: `get_alarm_flag`/`set_alarm_flag`, `get_last_rtc_sync`/`set_last_rtc_sync`, `rtc_resync_due(...)`, `get_ev_state`/`set_ev_state`, `store_payload(...)`, `get_payloads()`, `should_transmit()`.
- Depende de: `config_manager` (lee `general.register_acumulator`).
- Nota: estructura binaria hecha a mano con desplazamientos de byte fijos; respeta el límite de hardware de ~2048 bytes de `rtc.memory()`, recortando `n_cycles` automáticamente si la configuración lo excede.

### Conectividad

**`wifi.py`**

- Propósito: conexión Wi-Fi STA con una barrera de seguridad — rechaza asociarse por debajo de WPA2-PSK (comentario explícito en el código sobre cumplimiento de la CRA/Cyber Resilience Act).
- API pública: `is_connected()`, `do_connect(ssid, password, timeout_seconds=15)` *(asíncrono)*, `do_disconnect()` *(asíncrono)*.
- Depende de: solo del módulo integrado `network`. El SSID/contraseña los pasa `main.py` desde `dynamic_config.communications.wifi`.

**`nb_iot.py`** *(el módulo más grande, ~57 KB)*

- Propósito: driver para la familia de módems NB-IoT/LTE-M Nordic nRF9160 (conjunto de comandos Nordic SLM AT%/AT#X): registro de red (con selección/lista negra de operador), cliente MQTT sobre el módem, cliente HTTP para descargas OTA, GPS/NTN, gestión de reposo/despertar.
- API pública (todo `async` salvo que se indique): `connect(connection_preference, edrx=True, apn=None, ntn=False)`, `wake_up()`, `sleep()`, `hard_reset()`, `mqtt_configure/connect/publish/subscribe`, `get_mqtt_messages()` *(síncrono)*, `send_udp_data(...)`, `download_file(...)` (peticiones HTTP range en bloques para OTA), `get_gps_coords(...)`, `connect_ntn(...)`, `get_signal_data()`.
- Depende de: ningún driver de `lib/` — habla AT directamente por UART.
- Configuración: `dynamic_config.communications.cellular_iot.{external_sim,preference,apn,ntn,signal_data}`, `static_config.pinout.control.en_nbiot_pin`, `static_config.pinout.nb-iot.{tx_pin,rx_pin}`.
- **Grupos de comandos AT usados** (verificados con grep contra el código fuente):
  - *Red:* `AT+CFUN=`, `AT#XGPIOCFG`/`AT#XGPIO` (selección de SIM), `AT%XSYSTEMMODE=`, `AT%XBANDLOCK=`, `AT+CGDCONT=`, `AT%XMONITOR`, `AT%RAI`, `AT%PERIODICSEARCHCONF=`, `AT+CEDRXS=`, `AT%XPTW=`, `AT+COPS=` (escaneo/manual/automático), `AT+CPSMS=`, `AT+CEDRXRDP`, `AT+CESQ`, `AT+CGPADDR=`.
  - *Reloj:* `AT+CCLK?`.
  - *Reposo/reinicio:* `AT#XSLEEP=`, `AT#XRESET` (suave); `hard_reset()` en cambio corta físicamente la alimentación del módem vía `en_nbiot_pin` durante 5s.
  - *GPS:* `AT#XGPS=1,0,0,0` / `AT#XGPS=0`.
  - *MQTT sobre el módem:* `AT#XMQTTCFG=`, `AT#XMQTTCON=`, `AT#XMQTTPUB=`, `AT#XMQTTSUB=` (los mensajes entrantes llegan como URC `#XMQTTMSG:`).
  - *Socket UDP:* `AT#XSOCKET=`, `AT#XSENDTO=`.
  - *HTTP (OTA):* `AT#XHTTPCCON=`, `AT#XHTTPCREQ="GET",...,"Range: bytes=X-Y"` (descarga en bloques; respuesta vía URC `#XHTTPCRSP:`).
- Nota: comentarios como `"USER BASE v17"`, `"CHANGE"`, `"NEW"` alrededor de la ruta de descarga OTA sugieren que esta es la parte del módulo más activamente iterada/menos estable actualmente — merece cuidado y pruebas extra antes de enviar cambios aquí.

**`lorawan.py`**

- Propósito: driver para un módem LoRaWAN de la clase RAK3172 (conjunto AT RUI3 estándar): unión a la red, envío de uplink, recepción de downlink (incluida Clase C por sondeo), sincronización de hora de red.
- API pública (todo `async` salvo que se indique): `connect(lorawan_class="A", attempts=1)`, `join_network()`, `send_uplink(port, data)`, `get_downlink_messages()`, `request_time()`, `get_network_time()`, `sleep()`, `check_network_connection()`.
- Depende de: ningún driver de `lib/` — habla AT directamente por UART. Reutiliza los **mismos pines UART físicos** que `nb_iot.py` (`static_config.pinout.nb-iot.{tx_pin,rx_pin}`) — confirma que las variantes de módem Wi-Fi/NB-IoT/LoRaWAN son mutuamente excluyentes a nivel de hardware, seleccionadas por el campo de módem de `static_config`.
- Configuración: `dynamic_config.communications.lorawan.{dev_eui,app_key,app_eui,class,network_mode,join_mode,band}`.
- **Grupos de comandos AT usados**: `AT+NWM=` (modo de red), `AT+NJM=` (modo de unión ABP/OTAA), `AT+CLASS=`, `AT+BAND=`, `AT+CFM=` (uplinks confirmados), `AT+DEVEUI=`/`AT+APPEUI=`/`AT+APPKEY=`, `AT+JOIN=1:0:<interval>:<attempts>` (espera `+EVT:JOINED`), `AT+TIMEREQ=1` + `AT+LTIME=?` (hora de red), `AT+SEND=<port>:<data>` (espera `+EVT:SEND_CONFIRMED_OK` o `+EVT:TX_DONE`), `AT+LPM=1`/`AT+SLEEP` (bajo consumo), `ATZ` (reinicio), `AT+NJS=?` (estado de unión), `ATC+GETDL` (comando propio: consulta downlinks de Clase C en búfer), y URC pasivos `+EVT:RX...` analizados para downlinks en tiempo real.

**`umqttsimple.py`**

- Propósito: cliente MQTT 3.1.1 ligero sobre socket TCP/TLS, usado solo para el transporte Wi-Fi.
- Origen: basado en el cliente MQTT clásico de `micropython-lib` de Paul Sokolovsky (2013–2016), modificado por ISURKI/Steminds — `check_msg()` se reescribió para devolver una lista con todos los mensajes pendientes en vez de un único callback. QoS 2 no está implementado. Técnicamente vive en `modules/`, pero funcionalmente es una librería de terceros — podría decirse que encajaría mejor en `lib/`.

**`ble_manager.py`**

- Propósito: servidor GATT BLE para configuración/monitorización local, activado por el modo de despertar por imán. Una característica de notificación (datos) y una de escritura (comandos).
- API pública: `BLEManager(device_name=..., command_callback=...)`, `update_data_payload(payload)`, `stop()`.
- Depende de: `lib/aioble` (Service/Characteristic/advertise/security).
- Configuración: `static_config.pin` (el mismo PIN de 6 dígitos que `_auth.py`, usado para el emparejamiento BLE fijo).
- Nota: implementa emparejamiento/vinculación LE Secure con protección MITM y un PIN fijo (capacidad de E/S DISPLAY_ONLY); rechaza comandos en características no cifradas.

**`downlink_manager.py`**

- Propósito: unifica la gestión de downlinks entre los tres transportes (Wi-Fi, NB-IoT, LoRaWAN): comandos manuales de SD/EV, aplicación de configuración remota (decodificada por LPP), e inicio de OTA (solo NB-IoT).
- API pública: `process_wifi_downlinks(...)`, `process_nbiot_downlinks(...)`, `process_lorawan_downlinks(...)` (todas `async`), `apply_config(hex_text)`, `is_manual_command(text)`.
- Depende de: `lib/IsurlogLPP`, `lib/ota.rollback`; importaciones diferidas de `modbus_sensor`, `update_manager`, `remote_repl`.
- Nota: contiene todo el flujo de OTA — descarga, verificación de checksum SHA-256, decodificación base64, escritura de partición, y `rollback.cancel_force()` si falla.

**`remote_repl.py`**

- Propósito: REPL remota de Python sobre MQTT (Wi-Fi o NB-IoT) para depuración en campo — recibe código Python como mensaje MQTT, lo ejecuta con `eval`/`exec`, y devuelve el stdout capturado en otro topic.
- ⚠️ **Nota de seguridad**: esto ejecuta código arbitrario sin más autenticación que la que ofrezca el broker/canal MQTT. Es una puerta trasera de administración muy potente — merece la pena confirmar que el canal MQTT esté debidamente asegurado (TLS + ACL del broker) allí donde esté habilitado en campo.

### Sensores

**`analog_sensor.py`** — envoltorio de entrada 4-20mA/0-10V basado en ADS1115; `read_analog(channel)`, `convert_value(value, zero, full_scale)`. Depende de `lib/ADS1115`. Configuración: `static_config.pinout.i2c.*`, `static_config.ads1115_addr`; el `zero`/`full_scale` de cada canal viene de `dynamic_config.analog_config.inputs[]`.

**`digital_sensor.py`** — contador de pulsos de bajo consumo basado en ULP con antirrebote por software (solo GPIO 36/39, pines con capacidad RTC). Depende de `lib/esp32_ulp`. Lee el conteo de flancos de despertar desde `dynamic_config.digital_config.inputs[]` — una lista con una entrada por canal — buscando la entrada donde `channel == 0` y leyendo su clave `wake`.

**`bme_sensor.py`** — autodetecta BMP280/BME280/BME680 por `CHIP_ID` en I2C; cálculo opcional de IAQ (calidad del aire) con rodaje (burn-in) del sensor de gas. Depende de `lib/pimoroni_bme680`, `lib/bme280_float`. Nota: `_burn_in()` bloquea hasta 300s si `IAQ=True` — `main.py` actualmente lo instancia con `IAQ=False`.

**`sht30_sensor.py`** — envoltorio de temperatura/humedad SHT30. Depende de `lib/SHT30`.

**`max31865_sensor.py`** — envoltorio PT100/PT1000 sobre SPI. Depende de `lib/adafruit_max31865`. Lee `wires` de `dynamic_config.pt100_config.wires` (4 por defecto si no está presente).

**`modbus_sensor.py`** — maestro Modbus RTU sobre RS485 (registros holding/input, coils, entradas discretas, escritura de registros, conversión de 2 registros a float). Muy usado por `main.py`, `downlink_manager.py`, e integraciones isurnode.

**`accel_manager.py`** — antirrobo: acelerómetro LIS2DH12 + expansor de I/O MCP23008 para detectar movimiento/manipulación y despertar desde el reposo profundo. Depende de `lib/mcp23008`, `lib/LIS2DH12`. Nota: `_verify_theft()` bloquea hasta 10s haciendo polling — funciona bien tal como se usa hoy, pero no es asyncio-friendly si se reutiliza en otro sitio.

**`battery_monitor.py`** — lectura de tensión de batería por el ADC interno del ESP32 (respaldo cuando no hay fuel gauge MAX17048). Sin configuración, sin dependencia de `lib/`.

### Almacenamiento y OTA

**`internal_storage.py`** — respaldo FIFO de payloads en la flash interna (usado cuando `general.internal_register` está activado); recorta automáticamente las líneas más antiguas al alcanzar los umbrales de espacio libre o número de líneas. Nota: `delete_oldest_lines()` reescribe todo el archivo cada vez — O(n) por limpieza, vigilar el desgaste de la flash si el registro crece mucho.

**`update_manager.py`** — utilidades de soporte OTA: verificación de checksum SHA-256, decodificación base64 en bloques, y sustitución segura de `main.py` (copia de seguridad + renombrado, con intento de rollback si falla).

### Periféricos

**`led_manager.py`** — patrón de parpadeo del LED de estado gestionado por ULP (pulsos/ráfagas/temporización configurables), para que la CPU no tenga que permanecer despierta por esto. Depende de `lib/esp32_ulp`. Comparte el coprocesador ULP con el contador de pulsos de `digital_sensor.py` — `is_enabled()` actúa como mutex entre ambos (no pueden ejecutarse simultáneamente).

---

## 2.1.3 Referencia de Librerías (`lib/`)

| Archivo / paquete | Qué es | Origen |
|---|---|---|
| `adafruit_max31865.py` | Driver del amplificador RTD MAX31865 (SPI) | Terceros — Adafruit, MIT |
| `ADS1115.py` | Driver del ADC de 16 bits ADS1115 (I2C) | Terceros — W. Ewald, MIT |
| `aioble/` | BLE asíncrono (GATT, emparejamiento, L2CAP) | Terceros — micropython-lib oficial, MIT |
| `bme280_float.py` | Driver BME280 (I2C) | Terceros — derivado de Adafruit, MIT/estilo BSD |
| `esp32_ulp/` | Ensamblador/enlazador del coprocesador ULP | Terceros — micropython-esp32-ulp, MIT |
| `IsurlogLPP.py` | Códec de payload propio de ISURKI, "Isurlog LPP" (similar a Cayenne-LPP, con tipos propios de sensor + configuración) | **Propio de ISURKI**, GPL-3.0-or-later. Pieza central de interoperabilidad con el `CONFIG_MAP` de `config_manager.py`. |
| `LIS2DH12.py` | Driver del acelerómetro LIS2DH12 (I2C) | Terceros — Quectel, Apache 2.0 |
| `max1704x.py` | Driver del fuel gauge LiPo MAX17048/17044 (I2C) | Terceros (A. Peeters), adaptado |
| `mcp23008.py` | Driver del expansor de I/O MCP23008 (I2C) | Terceros — M. Causer, MIT |
| `mcp4017.py` | Driver del potenciómetro digital MCP4017 (I2C), ajusta la salida del regulador boost de VDC | **Propio de ISURKI**, GPL-3.0-or-later |
| `ota/` | Framework OTA de particiones ESP32 (escritor de bloques, rollback, estado) | Terceros — G. Moloney, MIT |
| `pimoroni_bme680.py` | Driver BME680 (I2C) | Terceros — Pimoroni, MIT |
| `RV3028.py` | Driver del RTC de bajo consumo RV3028 (I2C) | Terceros — Core Electronics/Makerverse |
| `SHT30.py` | Driver de temperatura/humedad SHT30 (I2C) | Terceros — R. Sánchez, Apache 2.0 |
| `uds3231.py` | Driver del RTC DS3231 (I2C) | Terceros — derivado de Adafruit, adaptado por ISURKI, MIT |
| `umodbus/` | Stack completo maestro+esclavo Modbus RTU/TCP (v2.3.7) | Terceros — Pycom, GPL v3 + Pycom License v1.0 |

---

## 2.1.4 Mapa de Dependencias entre Módulos

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
 ├─ lib/mcp4017, lib/IsurlogLPP, lib/ota.rollback   (directo, de primer nivel)
 └─ (diferido, según config/hardware)
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

utils.py es importado por casi todos los módulos de arriba (omitido del árbol por claridad).
```

`main.py` no importa todos los módulos incondicionalmente — los módulos de sensores y conectividad se importan de forma diferida, condicionados por `static_config`/`dynamic_config` (qué módem, qué sensores están activados, si se recibió un despertar por imán o un downlink de OTA/REPL). Esto mantiene bajo el uso de RAM al arrancar, algo que importa en MicroPython.
