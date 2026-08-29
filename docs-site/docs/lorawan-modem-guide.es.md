# 6. Guía Avanzada del Módem LoRaWAN

Esta guía está pensada para desarrolladores que necesitan modificar, compilar o grabar aplicaciones personalizadas en el módem **RAK3172** que usa el ISURLOG, sustituyendo la aplicación de comandos AT por defecto.

## 6.1 Arquitectura del Firmware (Framework RUI3)

Al desarrollar para el RAK3172, el entorno de software se apoya en la plataforma **RUI3 (RAKwireless Unified Interface V3)**. Es importante entender cómo puede utilizarse el módulo:

1. **Firmware de Comandos AT por Defecto:** el módulo viene grabado de fábrica con el firmware AT estándar de RUI3. En este esquema, el RAK3172 actúa como un periférico de comunicación estándar, controlado por completo por el ESP32 mediante consultas por interfaz serie.
2. **Firmware de Aplicación Personalizado (API de Arduino):** RUI3 permite a los desarrolladores compilar y ejecutar aplicaciones C++/Arduino independientes directamente dentro del microcontrolador STM32WLE55 interno del RAK3172. Esta capa puede prescindir del controlador externo para tareas concretas, o personalizar por completo el comportamiento del stack de radio.

---

## 6.2 Requisitos Previos e Instalación del SDK

Para desarrollar, modificar o compilar firmware de aplicación personalizado para el RAK3172 usando el framework RUI3, hay que configurar un entorno de desarrollo compatible.

### IDEs Soportados
El núcleo RUI3 del RAK3172 soporta de forma nativa el desarrollo mediante **Arduino IDE** o Visual Studio Code (con la extensión PlatformIO).

* **Configuración e Instalación:** para instalar el paquete de soporte de placas (BSP) de RAKwireless necesario en el entorno de desarrollo, seguir las instrucciones oficiales: [https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/supported-ide](https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/supported-ide)

### Referencia de la API de Arduino de RUI3
Al compilar firmware personalizado para ejecutarlo de forma nativa en el módulo, los desarrolladores pueden usar la API unificada de Arduino que ofrece RAKwireless para gestionar los parámetros LoRaWAN, el hardware interno y los periféricos: [https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/arduino-api](https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/arduino-api)

!!! note "Ver También"
    Para el hardware físico necesario para grabar el módem, ver **[6.5 Requisitos de Hardware de Grabado y Conexión](#65-requisitos-de-hardware-de-grabado-y-conexion)** más abajo.

---
## 6.3 Comunicación UART y Comandos AT

El ISURLOG usa el módulo RAK3172 para establecer la comunicación LoRaWAN a través de un puerto UART hardware (`UART1`) mediante **comandos AT**. La configuración serie por defecto entre el ESP32 y el RAK3172 es:

* **TX:** GPIO2
* **RX:** GPIO4
* **Baudrate:** 115200 8N1

!!! note "Referencia"
    El manual completo y oficial de comandos AT de RUI3, para gestionar la unión a la red (OTAA/ABP), las claves (DevEUI, AppEUI, AppKey) y la configuración de transmisión de datos, se encuentra aquí: [https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/at-command-manual/](https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/at-command-manual/)

    Si estás construyendo una aplicación de **sustitución** para el firmware del módem, debe seguir soportando el mismo conjunto de comandos AT del que realmente depende el driver propio del ISURLOG (`modules/lorawan.py`) — ver la lista de comandos verificada en **[2.1 Referencia de Módulos y Librerías](module-library-reference.md)** a modo de lista de comprobación de compatibilidad.

---
## 6.4 Gestión Avanzada de Energía

El RAK3172 está muy optimizado para un consumo ultrabajo. Cuando el sistema está en reposo entre intervalos de registro, el ESP32 puede llevar al módulo LoRaWAN a su estado de menor consumo mediante comandos por software:

* **Comando de Reposo:** enviar el comando `AT+SLEEP` pone al módulo en modo de reposo de bajo consumo (reduciendo el consumo hasta microamperios).
* **Rutina de Despertar:** el RAK3172 puede despertarse automáticamente del reposo al detectar flancos de bajada/actividad en la línea RX del UART. Enviar una secuencia de caracteres de relleno desde la línea TX del ESP32 despierta al módulo, dejándolo listo al instante para recibir los siguientes comandos AT operativos.

Además de la comunicación de datos por el puerto UART, el ESP32 y el módulo RAK3172 están conectados mediante una línea GPIO dedicada. Esta conexión permite una gestión dinámica y eficiente de los modos de bajo consumo del procesador principal, optimizando la autonomía del **ISURLOG**.

La conexión entre los módulos es la siguiente:

| Nombre | Pin ESP32 | Pin RAK3172 | Descripción |
| :--- | :--- | :--- | :--- |
| **ESP_WAKE_UP** | GPIO35 (Entrada) | PA8 (Salida) | Entrada digital usada para despertar el ESP32 cuando el módulo LoRaWAN recibe un paquete de downlink del gateway/servidor. |

Esta funcionalidad es especialmente útil cuando el módulo RAK3172 opera en **LoRaWAN Clase B** (balizas sincronizadas) o **Clase C** (escucha continua). La señal `ESP_WAKE_UP` permite al RAK3172 activar de inmediato el ESP32 siempre que se recibe un **paquete de datos downlink** asíncrono desde la red. Una vez despierto, el ESP32 puede comunicarse con el RAK3172 por UART para procesar los datos o comandos entrantes.

Esta capacidad de "despertar bajo demanda" permite al ESP32 permanecer en reposo profundo indefinidamente, reduciendo significativamente el consumo del sistema y manteniendo una latencia casi nula para configuraciones remotas o downlinks del servidor.

---
## 6.5 Requisitos de Hardware de Grabado y Conexión

La placa del ISURLOG no incluye un conversor USB-UART integrado para el RAK3172, con el fin de mantener un perfil de hardware minimalista, económico y de bajo consumo.

### Hardware de Grabado Necesario
* **Conversor:** un **conversor externo UART TTL a USB**.
* **Conexión:** cables jumper o un conector de programación dedicado, compatible con el diseño de la placa.

!!! warning "Importante (Modo Bootloader)"
    Antes de compilar y subir un nuevo sketch o firmware desde el Arduino IDE, hay que poner al RAK3172 en modo bootloader enviando el comando `AT+BOOT` por la interfaz serie.

### Conexión Física

Para grabar físicamente nuevo firmware, actualizar el núcleo de RUI3, o subir un sketch de Arduino al RAK3172, hay que conectar las líneas de la interfaz serie de programación del módulo al PC mediante el conversor externo UART TTL a USB.

El flujo de conexión requiere hacer coincidir el **TX**, **RX** y **GND** del conversor con los pines de programación correspondientes del RAK3172 en la PCB.

El puerto/pines de programación para el módulo RAK3172 en la PCB del ISURLOG se encuentran como se muestra a continuación:

![Disposición de la PCB del ISURLOG con el puerto de programación del RAK3172 resaltado](images/6-rak3172-programming-port.jpg){: width="750" }

*El puerto de programación, para el módem RAK3172.*

## 6.6 Actualizar el Firmware del Módem desde Binarios Oficiales

A diferencia de los escenarios anteriores (que asumen que compilas tu propio firmware de aplicación desde el código fuente), no necesitas el Arduino IDE ni el BSP de RUI3 en absoluto si solo quieres actualizar el módem a una **build oficial proporcionada por ISURKI** — es un binario ya compilado.

### Dónde Obtener el Binario

Cada [release de firmware del ISURLOG](https://github.com/isurki-tecnica/isurlog-firmware/releases) incluye un archivo `rak3172_bins.zip` (junto a los binarios del ESP32 y del nRF9151) que contiene un único archivo:

* **`System_Custom_ATCMD.ino.bin`**

!!! note "🚧 Próximamente"
    IsurDASH podrá actualizar el firmware del RAK3172 directamente, de la misma forma en que el flujo de **[6.8 Mantenimiento de Dispositivos](isurdash-maintenance.md)** ya actualiza el **ESP32**. Mientras tanto, usa la herramienta de más abajo.

### Herramienta de Actualización

La forma recomendada actualmente para actualizar el firmware del RAK3172 es la herramienta web en **[firmwareupgrade.fencyboy.com](https://firmwareupgrade.fencyboy.com/)**.

### Procedimiento de Actualización

1.  Conectar el conversor UART-USB al puerto "**RAK**" del ISURLOG.
2.  Encender el ISURLOG en modo **BOOT**.
3.  Seleccionar el puerto serie en la herramienta y conectar.
4.  Enviar el comando `AT+BOOT` y confirmar que el módulo responde correctamente.
5.  Seleccionar el archivo **`System_Custom_ATCMD.ino.bin`** y pulsar **"Upload firmware"**.

![Actualizando el firmware del módem RAK3172 mediante firmwareupgrade.fencyboy.com](images/6-modem-firmware-update.gif){: width="1000" }

*Actualizando el firmware del módem RAK3172 mediante la herramienta web.*
