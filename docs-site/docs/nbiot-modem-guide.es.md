# 5. Guía Avanzada del Módem NB-IoT

Esta guía está pensada para desarrolladores que necesitan modificar, compilar o grabar aplicaciones personalizadas en el módem **nRF9151** (Actinius-SoM) que usa el ISURLOG, sustituyendo la aplicación de comandos AT por defecto.

## 5.1 Distinción en la Arquitectura del Firmware

Al desarrollar para el nRF9151, es fundamental distinguir entre dos capas de software diferenciadas:

1.  **Firmware del Módem (Stack de Radio de Bajo Nivel):** es el firmware interno que controla los protocolos de radio (LTE-M/NB-IoT), la seguridad y el procesado de señal. Este firmware puede actualizarse con la aplicación **Programmer** dentro de **nRF Connect for Desktop**. **Normalmente no es necesario actualizar este firmware**, ya que la versión de fábrica suele ser estable.
    * **Dónde descargarlo:** el firmware del módem puede obtenerse directamente de Nordic Semiconductor descargando el paquete ZIP de la versión deseada: [https://www.nordicsemi.com/Products/nRF9151/Download?lang=en#infotabs](https://www.nordicsemi.com/Products/nRF9151/Download?lang=en#infotabs).

2.  **Firmware de Aplicación (Programa):** es el código que se ejecuta *sobre* el firmware del módem, como el **serial_lte_modem** (el intérprete de comandos AT) o cualquier otra aplicación personalizada. Esta es la capa que los desarrolladores suelen modificar y grabar.

---

## 5.2 Requisitos Previos e Instalación del SDK

Para compilar Firmware de Aplicación para el nRF9151, es necesario instalar la toolchain de Nordic Semiconductor, gestionada a través de nRF Connect for Desktop.

### Procedimiento de Instalación

1.  Instalar **nRF Connect for Desktop**.
2.  Abrir nRF Connect for Desktop e instalar la aplicación **Toolchain Manager**.
3.  Abrir el Toolchain Manager e instalar **nRF Connect SDK v.2.6.2**. Se recomienda esta versión para una compatibilidad óptima con el firmware base del ISURLOG.

!!! note "Ver También"
    Para el hardware físico necesario para grabar el módem (programador, cable, conexión), ver **[5.6 Requisitos de Hardware de Grabado y Conexión](#56-requisitos-de-hardware-de-grabado-y-conexion)** más abajo.

---
## 5.3 Comunicación UART y Comandos AT

El ISURLOG usa el módem nRF9151 para establecer la comunicación NB-IoT a través de un puerto UART y **comandos AT**. La configuración del puerto UART por defecto (lado ESP32) es:

* **TX:** GPIO4
* **RX:** GPIO2
* **Baudrate:** 115200 8N1

!!! note "Referencia"
    La referencia completa y oficial de comandos AT para el módem nRF9151 se encuentra en la documentación de Nordic Semiconductor: [https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/applications/serial_lte_modem/README.html](https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/applications/serial_lte_modem/README.html)

    Si estás construyendo una aplicación de **sustitución** para el firmware del módem, debe seguir soportando el mismo conjunto de comandos AT del que realmente depende el driver propio del ISURLOG (`modules/nb_iot.py`) — ver la lista de comandos verificada en **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)** a modo de lista de comprobación de compatibilidad.

---
## 5.4 Gestión Avanzada de Energía: Pines ESP32 - nRF9151

Además de la comunicación de datos por el puerto UART, el ESP32 y el módem nRF9151 están conectados mediante dos líneas GPIO dedicadas. Estas conexiones permiten una gestión dinámica y eficiente de los modos de bajo consumo de ambos procesadores, optimizando la autonomía del **ISURLOG**.

La conexión entre los módulos es la siguiente:

| Nombre | Pin ESP32 | Pin nRF9151 | Descripción |
| :--- | :--- | :--- | :--- |
| **ESP_WAKE_UP** | GPIO35 (Entrada) | GPIO30 (Salida) | Entrada digital usada para despertar el ESP32 cuando el módulo NB-IoT está en modo eDRX y recibe un paquete de datos. |
| **NRF_WAKE_UP** | GPIO26 (Salida) | GPIO31 (Entrada) | Salida digital usada por el ESP32 para despertar el módulo NB-IoT cuando este está en modo de reposo. |

Esta funcionalidad es especialmente útil cuando el módem nRF9151 opera en modo **eDRX (Recepción Discontinua Extendida)**. La señal `ESP_WAKE_UP` permite al módem nRF9151 activar el ESP32. Una vez despierto, el ESP32 puede comunicarse con el nRF9151 por UART para procesar los datos recibidos. Esta capacidad de "despertar bajo demanda" reduce significativamente la latencia para recibir comandos o configuraciones del servidor.

---
## 5.5 Selección de SIM y Control por GPIO

El módem nRF9151 selecciona entre la **eSIM** y la **Nano-SIM** en función del estado del **GPIO12**. El ESP32 puede controlar el estado del GPIO12 mediante comandos AT.

**1. Configurar el GPIO12 como salida:**

`AT#XGPIOCFG=1,12`

**2. Poner el GPIO12 en alto/bajo (seleccionar SIM):**

`AT#XGPIO=0,12,val` (donde `val` es el valor deseado, 0 para bajo y 1 para alto).

## 5.6 Requisitos de Hardware de Grabado y Conexión

Para cargar físicamente nuevo firmware en el módem nRF9151, se necesita hardware especializado:

* **Programador:** un programador **Segger J-Link**.
* **Método de conexión:** un cable **Tag-Connect** o un conector equivalente compatible con el puerto JTAG del nRF9151.

### Conexión Física

La secuencia de programación consiste en conectar el programador **J-Link** al PC por USB. A continuación, se conecta el programador al **puerto JTAG** de la PCB del ISURLOG mediante el cable Tag-Connect.

El puerto JTAG en la PCB del ISURLOG (que es el puerto de programación del módem nRF9151) se encuentra como se muestra a continuación:

![Disposición de la PCB del ISURLOG con el puerto de programación JTAG resaltado](images/5-jtag-port-location.jpg){ width="502" }

*El puerto de programación JTAG, para el módem nRF9151.*

## 5.7 Actualizar el Firmware del Módem desde Binarios Oficiales

A diferencia de los escenarios anteriores (que asumen que compilas tu propio firmware de aplicación desde el código fuente), no necesitas el SDK de nRF Connect en absoluto si solo quieres actualizar el módem a una **build oficial proporcionada por ISURKI** — basta con **nRF Connect for Desktop**, ya que son binarios ya compilados.

### Dónde Obtener los Binarios

Cada [release de firmware del ISURLOG](https://github.com/isurki-tecnica/isurlog-firmware/releases) incluye un archivo `nrf9151_bins.zip` (junto a los binarios del ESP32) que contiene:

* **`merged.hex`** — el Firmware de Aplicación (`serial_lte_modem` / intérprete de comandos AT).
* **`mfw_nrf91x1_x.x.x.zip`** — el Firmware del Módem (stack de radio).

Actualizar uno u otro (o ambos) es la forma de incorporar correcciones o mejoras del lado del módem del ISURLOG sin tocar el firmware del ESP32.

### Hardware Necesario

* Una placa programadora: **[nRF9160-DK](https://www.digikey.es/es/products/detail/nordic-semiconductor-asa/NRF9160-DK/9740721)**.
* Un **[cable TAG-Connect de 6 pines](https://www.tag-connect.com/product/tc2030-ctx-nl-6-pin-no-legs-cable-with-10-pin-micro-connector-for-cortex-processors)**.
* **[nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)** instalado (no se necesita SDK/toolchain para esto).

### Conexión

* El nRF9160-DK se conecta al ordenador por USB.
* El conector "**nRF91 Debug In**" del nRF9160-DK va al **puerto JTAG** del ISURLOG (cara inferior de la PCB) mediante el cable TAG-Connect.
* El ISURLOG se alimenta desde sus baterías.

### Procedimiento de Actualización

1.  Encender el ISURLOG y poner el ESP32 en modo **BOOT**.
2.  Encender el nRF9160-DK.
3.  Abrir **nRF Connect for Desktop** y lanzar la aplicación **Programmer**.
4.  Seleccionar el dispositivo **nRF9160-DK**.
5.  Usar **"Add file"** para cargar cualquiera de los dos binarios:
    1.  Para **`merged.hex`**: pulsar **"Erase and write"** y esperar a que termine.
    2.  Para **`mfw_nrf91x1_x.x.x.zip`** (el propio zip, sin extraer): pulsar **"Write"** y esperar a que termine.
6.  El orden no importa — se puede grabar primero el `merged.hex` o primero el firmware del módem.

![nRF Connect Programmer: grabando merged.hex seguido del firmware del módem](images/5-modem-firmware-update.gif){ width="1000" }

*Grabando merged.hex seguido del firmware del módem, en la aplicación Programmer.*
