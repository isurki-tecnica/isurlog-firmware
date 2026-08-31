# ISURLOG: Datalogger Industrial IoT (Firmware de Código Abierto)

![ISURLOG — Datalogger Industrial NB-IoT/LoRa](images/gh-banner-isurlog.jpg){width="700"}

**ISURLOG** es un datalogger industrial basado en ESP32, diseñado para despliegues de campo donde la energía escasea y la conectividad nunca está garantizada. Firmware MicroPython genuino, trabajando con señales industriales reales, y gestionable en remoto desde el primer momento.

* **Sensores de grado industrial** — 4-20 mA analógico, Modbus RTU (RS485), PT100/PT1000, conteo de pulsos digital, temperatura y humedad interna/externa, y un acelerómetro integrado para detección de manipulación/vandalismo.
* **Pensado para baterías** — hasta ~20 µA en reposo (deep sleep). Un cargador de recolección de energía integrado se alimenta de casi cualquier fuente: un TEG de 0.3V, un panel solar micro, un panel de 5V completo, o un cargador USB convencional.
* **Un firmware, múltiples redes** — NB-IoT, LTE-M, DECT NR+, y satélite NTN a través del nRF9151, o LoRaWAN, de forma exclusiva por unidad, además de Wi-Fi y BLE local para la configuración.
* **Gestionable en remoto, no solo legible en remoto** — configuración, ajuste de sensores, actualizaciones OTA, y una REPL de MicroPython en vivo, todo desde [IsurDASH](https://isurdash.isurki.com), sin desplazamiento a campo.
* **MicroPython real, no una caja negra** — un fork genuino de [MicroPython](https://micropython.org), legible y modificable en cada capa.
* **Sin dependencia del fabricante** — el firmware es de código abierto en GitHub, y cualquier dispositivo puede reconfigurarse para apuntar a otro broker MQTT o backend en cualquier momento. Si ISURKI desapareciera mañana, tus ISURLOG seguirían funcionando: se reprograman y se sigue adelante, nunca se quedan de pisapapeles.

---

## Por dónde empezar

| 🛠️ Uso y Hardware | 💻 Desarrollo de Firmware | ☁️ Integración de Datos y APIs |
| :--- | :--- | :--- |
| Instalación, configuración de sensores, e IsurDASH. | Entorno de compilación, arquitectura, contribución. | Acceso a datos históricos/tiempo real, API de downlink. |
| **Empezar aquí:** [1. Conexión de Sensores](sensor-connections.md) | **Empezar aquí:** [1. Configuración del Entorno de Compilación](build-environment.md) | **Empezar aquí:** [1. Resumen de Acceso a Datos](data-access-overview.md) |

¿Problemas en el campo? Consultar [Resolución de Problemas](troubleshooting.md).

---

## Estimar la duración de la batería

La **[calculadora interactiva de consumo de energía](power-budget.md)** modela el ciclo de trabajo completo de un dispositivo — conectividad, los sensores configurados en IsurDASH, y la configuración de batería (Li-Ion o Li-SOCl2) — para una estimación real en vez de una regla general.

---

## Verlo en acción

La mejor forma de comprobarlo es usar la plataforma real y extraer datos reales, sin necesidad de registrarse:

* **Cuenta demo de IsurDASH** — acceder en [isurdash.isurki.com/login](https://isurdash.isurki.com/login) para explorar el dashboard, la lista de dispositivos, las alarmas, y las pantallas de configuración:
    * **Email:** `isurdash.demo@gmail.com`
    * **Contraseña:** `TEST123456`
* **Ejemplos de integración de datos** — dos scripts de Python listos para ejecutar, ya rellenados con las credenciales demo públicas, en la carpeta [`data_integration/`](https://github.com/isurki-tecnica/isurlog-firmware/tree/main/data_integration) del repositorio de firmware — permiten extraer datos históricos de InfluxDB, o suscribirse a un flujo MQTT en vivo.

---

## Hoja de ruta

ISURLOG es un producto en mantenimiento activo con despliegues reales en campo, no un prototipo — el desarrollo es continuo, y esta tabla se mantiene honesta sobre qué está ya probado en campo frente a qué es una incorporación más reciente, todavía en proceso de maduración.

| Función | Tipo | Estado | Disponible Desde |
| :--- | :--- | :--- | :--- |
| Arquitectura de funciones asíncronas para ejecución de tareas en paralelo, reduciendo el tiempo que el datalogger permanece encendido | Firmware | 🧪 Experimental | v2.0.1 (pre-release) |
| Soporte de baterías no recargables Li-SOCl2 | Hardware | 🧪 Experimental | PCB v3.3 |
| Búfer de transmisión ampliado mediante EEPROM I2C externa (24LC1025), eliminando la limitación actual de tamaño de la RAM del RTC | Firmware | 🧪 Experimental | — |
| Alarma del acelerómetro → transmisión inmediata forzada | Firmware | 🔜 Planificado | — |
| Modo de conexión automática NB-IoT/LTE-M | Firmware | 🔜 Planificado | — |
| DECT NR+ (compatible a nivel de chip vía nRF9151) | Firmware | 🔜 Planificado | — |
| Módulo de expansión Modbus Isurnode | Hardware + Firmware | 🔜 Planificado | — |
| TinyML — inferencia en el propio dispositivo para tareas ligeras como detección local de anomalías o mantenimiento predictivo, sin ida y vuelta a la nube | Firmware | 🔜 Planificado | — |
| Actualización de firmware del RAK3172 directamente desde IsurDASH (actualmente requiere una herramienta web externa) | Firmware | 🔜 Planificado | — |
| Archivos de caja imprimible en 3D, publicados en Printables | Hardware | 💬 En debate | — |
| Migración de ESP32 a ESP32-S3 o al recién anunciado ESP32-S31 (elección final aún sin decidir) — USB nativo y un núcleo RISC-V LP en lugar del actual coprocesador ULP FSM | Hardware + Firmware | 💬 En debate | — |

<details markdown="1">
<summary>✅ Ya estable (11 funciones)</summary>

| Función | Tipo | Estado | Disponible Desde |
| :--- | :--- | :--- | :--- |
| Conectividad NB-IoT / LoRaWAN / BLE | Hardware + Firmware | ✅ Estable | v1.0.0 |
| Conectividad Wi-Fi y REPL remota por Wi-Fi | Firmware | ✅ Estable | v1.0.5-beta |
| Sensores principales (Analógico, Digital, Modbus, PT100) | Firmware | ✅ Estable | v1.0.0 |
| Sensores de temperatura/humedad interno (SHT30) y externo (BME280) | Firmware | ✅ Estable | v1.0.3 |
| Integración con IsurDASH (configuración remota, actualizaciones OTA, REPL en vivo) | Firmware | ✅ Estable | v1.0.0 |
| Acceso a datos históricos (InfluxDB) y en tiempo real (MQTT) | Firmware | ✅ Estable | v1.0.0 |
| Registro de calidad de señal NB-IoT (RSRQ/RSRP) | Firmware | ✅ Estable | FW v1.1.6 |
| Tensión de alimentación de sensores configurable (9-24V) | Hardware | ✅ Estable | PCB v3.0 |
| Alerta de vandalismo (acelerómetro + posición GPS) | Hardware + Firmware | ✅ Estable | PCB v3.0 · FW v1.1.6 |
| Tipo de batería y reporte del estado de carga | Hardware + Firmware | ✅ Estable | PCB v3.0 · FW v1.1.9 |
| Umbrales de alarma del acelerómetro interno (LIS2DH12) | Firmware | ✅ Estable | FW v1.1.6 |

</details>

**¿Alguna sugerencia o idea?** Abrir una [GitHub Issue](https://github.com/isurki-tecnica/isurlog-firmware/issues/new) describiéndola — se aceptan tanto peticiones de nuevas funciones como ideas de integración de hardware, no solo reportes de errores. Ver [7.4 Uso del Rastreador de Issues](contribution-guide.md#74-uso-del-rastreador-de-issues) para qué hace que una petición sea buena.

---

## Conseguir un ISURLOG

ISURLOG se vende directamente desde ISURKI, configurado según la conectividad y los sensores de cada proyecto. Usa el **[configurador interactivo](configurator.md)** para montar tu configuración exacta, ver el precio de cada opción, y solicitar presupuesto — o consulta antes la referencia completa de **[Piezas y Accesorios](parts-and-accessories.md)**.

---

## Recursos rápidos

* **Repositorio en GitHub:** [isurki-tecnica/isurlog-firmware](https://github.com/isurki-tecnica/isurlog-firmware)
* **Versiones del firmware:** [Página de Releases](https://github.com/isurki-tecnica/isurlog-firmware/releases)
* **Acceso a la plataforma cloud IsurDASH:** [isurdash.isurki.com/login](https://isurdash.isurki.com/login)
* **Soporte técnico:** (+34) 943-635437 · tecnica@isurki.com
