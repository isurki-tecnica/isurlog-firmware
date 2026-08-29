# 3. Grabado del Firmware y Carga de la Aplicación

Esta guía cubre los dos pasos diferenciados necesarios para configurar el entorno de desarrollo del ISURLOG: primero, grabar el binario de MicroPython, y segundo, subir la lógica de la aplicación.

!!! note "¿Solo instalas una release oficial, no desarrollas firmware?"
    IsurDASH dispone de una herramienta guiada de actualización de firmware (método **Serial port (USB)**) que te lleva por esta misma secuencia RST/BOOT con una interfaz más amigable — ver **[6.8. Mantenimiento de Dispositivos](isurdash-maintenance.md)**. Esta página está pensada para desarrolladores que graban un `firmware.bin` personalizado o compilado localmente, que no es una release publicada.

## 3.1 Hardware Externo Necesario

La placa del ISURLOG **no** incluye un conversor USB-UART integrado. Los desarrolladores deben usar un **conversor externo UART TTL a USB** para comunicarse con el ESP32 y grabarlo.

### Componentes Clave de la PCB

Identificar los botones necesarios y el puerto de programación serie (UART) en la PCB del **ISURLOG**:

* **Botones:** RESET y BOOT.
* **Puerto de programación:** el puerto UART, etiquetado como "**ESP**".

![Botones RESET y BOOT y el puerto de programación UART ESP en la PCB del ISURLOG](images/3fw-flashing-esp-uart-port.jpg){ width="740" }

*Los botones RESET/BOOT y el puerto de programación UART ESP.*

## 3.2 Grabado del Núcleo del Firmware (firmware.bin)

Este procedimiento pone al ESP32 en modo de descarga para cargar el archivo `firmware.bin` compilado (Capa 1).

### Paso 1: Conectar el Hardware

1.  Conectar el conversor USB-UART externo a los pines del puerto "**ESP**" en la PCB del **ISURLOG**.
2.  Asegurarse de tener listo el archivo `firmware.bin` compilado (de **1. Configuración del Entorno de Compilación**).

### Paso 2: Entrar en Modo de Descarga (BOOT)

Para poner el ESP32 en modo de descarga:

1.  Mantener pulsado el botón **RST**.
2.  Sin soltar **RST**, mantener pulsado también el botón **BOOT**.
3.  Soltar el botón **RST**.
4.  Soltar el botón **BOOT**.

El monitor serie debería mostrar el mensaje "**Waiting for download**", confirmando que el ESP32 está listo para recibir el firmware.

### Paso 3: Usar una Herramienta de Grabado (p. ej. Thonny o esptool.py)

Aunque el método estándar usa `esptool.py`, la forma más sencilla en MicroPython suele ser a través de la interfaz de un IDE (aquí se muestra Thonny como ejemplo):

1.  Abrir **Thonny**.
2.  Ir a **Tools** > **Options** > **Interpreter**.
3.  Pulsar "**Install or update MicroPython (esptool)**".
4.  Seleccionar el **número de puerto** conectado al ISURLOG.
5.  Seleccionar el binario de MicroPython descargado previamente y pulsar "**Install**".
6.  Esperar a que termine el proceso de instalación. El entorno de desarrollo muestra información detallada de la operación.
7.  Una vez completado el proceso, pulsar el botón **RST** o accionar el interruptor **ON/OFF** para reiniciar el ISURLOG y arrancar en MicroPython.

## 3.3 Carga del Código de la Aplicación (Capa 2)

Después de grabar el `firmware.bin`, hay que subir los archivos de lógica de la aplicación de la carpeta `/app` al sistema de archivos del dispositivo.

Este proceso es más sencillo y **no** requiere la secuencia BOOT/RESET. Herramientas como **Thonny**, **rshell**, o los comandos estándar de MicroPython pueden usarse para copiar el contenido de la carpeta `/app` (incluyendo `main.py`, configuración y archivos auxiliares) en el sistema de archivos activo del ISURLOG, a través del conversor USB-UART.

!!! note "Consejo"
    Asegurarse de que el **ISURLOG** esté funcionando en su modo de operación normal (interruptor ON/OFF en ON) al subir el código de la aplicación desde la vista de sistema de archivos de Thonny.
