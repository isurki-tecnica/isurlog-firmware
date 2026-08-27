# ISURLOG: Datalogger Industrial IoT (Firmware de Código Abierto)

![ISURLOG — Datalogger Industrial NB-IoT/LoRa](images/gh-banner-isurlog.jpg){width="700"}

**ISURLOG** es un datalogger industrial basado en ESP32, diseñado para despliegues de campo donde la energía escasea y la conectividad nunca está garantizada. Firmware MicroPython genuino, trabajando con señales industriales reales, y gestionable en remoto desde el primer momento.

* **Sensores de grado industrial** — 4-20 mA analógico, Modbus RTU (RS485), PT100/PT1000, conteo de pulsos digital, temperatura y humedad interna/externa, y un acelerómetro integrado para detección de manipulación/vandalismo.
* **Pensado para baterías** — hasta ~20 µA en reposo (deep sleep). Un cargador de recolección de energía integrado se alimenta de casi cualquier fuente: un TEG de 0.3V, un panel solar micro, un panel de 5V completo, o un cargador USB convencional.
* **Un firmware, múltiples redes** — NB-IoT, LTE-M, DECT NR+, y satélite NTN a través del nRF9151, o LoRaWAN, de forma exclusiva por unidad, además de Wi-Fi y BLE local para la configuración.
* **Gestionable en remoto, no solo legible en remoto** — configuración, ajuste de sensores, actualizaciones OTA, y una REPL de MicroPython en vivo, todo desde [IsurDASH](https://isurdash.isurki.com), sin desplazamiento a campo.
* **MicroPython real, no una caja negra** — un fork genuino de [MicroPython](https://micropython.org), legible y modificable en cada capa.

---

## Por dónde empezar

| 🛠️ Uso y Hardware | 💻 Desarrollo de Firmware | ☁️ Integración de Datos y APIs |
| :--- | :--- | :--- |
| Instalación, configuración de sensores, e IsurDASH. | Entorno de compilación, arquitectura, contribución. | Acceso a datos históricos/tiempo real, API de downlink. |
| **Empezar aquí:** [1. Conexión de Sensores](sensor-connections.md) | **Empezar aquí:** [1. Configuración del Entorno de Compilación](build-environment.md) | **Empezar aquí:** [1. Resumen de Acceso a Datos](data-access-overview.md) |

¿Problemas en el campo? Consultar [Resolución de Problemas](troubleshooting.md).

---

## Estimar la duración de la batería

La **[calculadora interactiva de presupuesto energético](power-budget.md)** modela el ciclo de trabajo completo de un dispositivo — conectividad, los sensores configurados en IsurDASH, y la configuración de batería (Li-Ion o Li-SOCl2) — para una estimación real en vez de una regla general.

---

## Verlo en acción

La mejor forma de comprobarlo es usar la plataforma real y extraer datos reales, sin necesidad de registrarse:

* **Cuenta demo de IsurDASH** — acceder en [isurdash.isurki.com/login](https://isurdash.isurki.com/login) para explorar el dashboard, la lista de dispositivos, las alarmas, y las pantallas de configuración:
    * **Email:** `isurdash.demo@gmail.com`
    * **Contraseña:** `TEST123456`
* **Ejemplos de integración de datos** — dos scripts de Python listos para ejecutar, ya rellenados con las credenciales demo públicas, en la carpeta [`data_integration/`](https://github.com/isurki-tecnica/isurlog-firmware/tree/main/data_integration) del repositorio de firmware — permiten extraer datos históricos de InfluxDB, o suscribirse a un flujo MQTT en vivo.

---

## Conseguir un ISURLOG

ISURLOG se vende directamente desde ISURKI, configurado según la conectividad y los sensores de cada proyecto. Para precio y disponibilidad, [solicitar presupuesto](mailto:tecnica@isurki.com?subject=ISURLOG%20-%20Solicitud%20de%20Presupuesto&body=Hola%20equipo%20de%20ISURKI%2C%0A%0AEstoy%20interesado%2Fa%20en%20ISURLOG%20para%20el%20siguiente%20caso%20de%20uso%3A%0A%0A-%20Aplicaci%C3%B3n%2Fentorno%3A%20%0A-%20Cantidad%20aproximada%3A%20%0A-%20Conectividad%20preferida%20(NB-IoT%2FLTE-M%2C%20LoRaWAN%2C%20o%20Wi-Fi)%3A%20%0A-%20Pa%C3%ADs%2Fregi%C3%B3n%3A%20%0A%0AGracias!).

---

## Recursos rápidos

* **Repositorio en GitHub:** [isurki-tecnica/isurlog-firmware](https://github.com/isurki-tecnica/isurlog-firmware)
* **Versiones del firmware:** [Página de Releases](https://github.com/isurki-tecnica/isurlog-firmware/releases)
* **Acceso a la plataforma cloud IsurDASH:** [isurdash.isurki.com/login](https://isurdash.isurki.com/login)
* **Soporte técnico:** (+34) 943-635437 · tecnica@isurki.com
