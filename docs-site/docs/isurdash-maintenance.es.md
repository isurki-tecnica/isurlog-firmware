*Parte de [6. Plataforma IsurDASH](isurdash-platform.md).*

# 6.8. Mantenimiento de Dispositivos

El menú "**Mantenimiento de dispositivos**" enumera todos los ISURLOG (ID, nombre, versión de firmware actual) junto con una fila de acciones de mantenimiento para cada dispositivo:

* **Actualización de firmware:** actualiza el firmware del dispositivo (ver más abajo).
* **MicroPython REPL:** abre una sesión remota de consola Python en el dispositivo (ver `remote_repl.py` en el firmware) para depuración en vivo.
* **Reset de fábrica:** restaura el dispositivo a su configuración de fábrica.
* **Revocar acceso:** revoca el acceso/credenciales del dispositivo. 🚧 *Todavía no disponible.*
* **Fin de vida:** da de baja el dispositivo. 🚧 *Todavía no disponible.*

![Mantenimiento de dispositivos en IsurDASH](images/7-maintenance-list.png){width="1000"}

*El listado de Mantenimiento de dispositivos, con las acciones de mantenimiento por dispositivo.*

!!! warning "Acciones Destructivas"
    Varias de estas acciones (reset de fábrica, revocar acceso, fin de vida) son destructivas y no fácilmente reversibles — usar con precaución.

## Actualización de Firmware

Al pulsar **Actualización de firmware** se abre una elección de método de actualización:

* **Remoto:** actualiza el dispositivo por aire (OTA). Solo disponible para dispositivos que ya ejecuten firmware **v1.1.9 o posterior**.
* **Serial port (USB):** actualiza el dispositivo mediante una conexión por cable. Disponible para **cualquier** versión de firmware, incluido un ESP32 en blanco o inutilizado. Requiere un **conversor UART a USB** conectado entre el ISURLOG y el ordenador — IsurDASH guía paso a paso por la secuencia de botones RST/BOOT necesaria para poner el chip en modo de descarga.

Tras elegir un método, se selecciona qué versión de firmware instalar. El listado de versiones disponibles se obtiene directamente de la [página de Releases de GitHub](https://github.com/isurki-tecnica/isurlog-firmware/releases) del proyecto. Algunas cosas a tener en cuenta sobre ese listado:

* Las releases marcadas como **Pre-release** no se recomiendan salvo que se necesite específicamente una función que solo exista en esa release.
* Elegir siempre la release marcada como **Latest**, salvo que haya un motivo concreto para no hacerlo.

![Flujo de actualización de firmware en IsurDASH: elegir Remoto o Serial port (USB), y después una versión de firmware](images/7-maintenance-firmware-update.gif){width="1000"}

*El flujo de actualización de firmware — elegir un método, y después una versión.*

!!! note "¿Compilas tu propio firmware?"
    Este flujo solo instala releases oficiales publicadas en GitHub. Si eres desarrollador de firmware y trabajas con un `firmware.bin` compilado localmente que (todavía) no es una release publicada, usa en su lugar el procedimiento de flasheo manual — ver **[3. Grabado del Firmware y Carga de la Aplicación](flashing-application-upload.md)**.

## MicroPython REPL

Al pulsar **MicroPython REPL** se conecta con la consola de MicroPython en vivo del dispositivo (ver `remote_repl.py` en el firmware) para ejecutar comandos, inspeccionar el estado, o depurar. Es el mismo botón **REPL** disponible en la propia página de un dispositivo (ver [6.3.3](isurdash-devices.md#633-visualizacion-y-estado-del-dispositivo)) — este apartado describe qué hace.

Al igual que con las actualizaciones de firmware, hay dos métodos de conexión — **el REPL nunca está disponible por Bluetooth**; la conexión Bluetooth (ver [6.3.5](isurdash-devices.md#635-conexion-local-por-bluetooth)) es solo para visualización de sensores en tiempo real y configuración local, no para el REPL:

* **Remoto:** disponible en **cualquier** versión de ISURLOG, pero solo para dispositivos con módem **NB-IoT o Wi-Fi** — los dispositivos LoRa no soportan REPL remoto.
* **Serial port (USB):** disponible para **todos** los dispositivos, independientemente del módem, mediante una conexión por cable.

Algunos detalles prácticos:

* La consola **se cierra automáticamente tras 2 minutos** sin recibir ningún comando.
* **Alternativa:** una vez conectado, se puede ampliar este tiempo editando uno mismo la variable `REPL_TIMEOUT` (en milisegundos), por ejemplo:

  ```python
  REPL_TIMEOUT = 120000
  ```

* La sesión puede **exportarse como un archivo `.txt`** para consultarla más adelante.

![Sesión de MicroPython REPL en IsurDASH](images/7-maintenance-repl-session.gif){width="1000"}

*Una sesión en vivo de MicroPython REPL.*
