# 1. Configuración del Entorno de Compilación

Esta guía explica cómo configurar un entorno de desarrollo y compilar el firmware de ISURLOG desde el código fuente.

El firmware se compila contra un **MicroPython original, sin modificar** (actualmente **v1.29.0**) más un único parche pequeño y versionado — no es un fork completo. Este repositorio (`isurlog-firmware`) contiene únicamente el código propio de ISURKI: la lógica de la aplicación, los drivers, la definición de la placa y las herramientas de compilación. MicroPython en sí se clona aparte, así que pasar a una versión más nueva nunca requiere tocar el historial de este repositorio.

!!! warning "Todavía en evolución"
    El código propio de ISURKI está sujeto a cambios, y puede quedarse por detrás de la última versión de MicroPython en algún momento.

## 1.1 Plataformas de Desarrollo Soportadas

El ISURLOG se diseñó para ser compatible con distintas plataformas de desarrollo, incluyendo **ESP-IDF**, **MicroPython** y **Arduino IDE**. Sin embargo, es importante señalar que **ISURKI garantiza compatibilidad total y soporte completo únicamente con MicroPython**.

| Plataforma | Estado de Compatibilidad | Recomendación |
| :--- | :--- | :--- |
| **MicroPython** | **Totalmente Garantizada y Soportada** | **Muy recomendable** para aprovechar toda la funcionalidad. |
| **ESP-IDF / Arduino IDE** | La compatibilidad depende de la implementación concreta y de futuras actualizaciones; **no se garantiza la funcionalidad completa**. | No se desaconseja su uso, pero ISURKI centra el mantenimiento de compatibilidad y el soporte continuo únicamente en MicroPython. |

## 1.2 Entorno Recomendado

El entorno de compilación recomendado es **Ubuntu Linux**.

Para usuarios de Windows, la compilación nativa es compleja y **no se recomienda**. Utilizar el **Subsistema de Windows para Linux (WSL)** y seguir las instrucciones de Ubuntu de más abajo, para una configuración más estable y sencilla.

## 1.3 Cómo Encajan las Piezas

En la compilación se juntan cuatro piezas independientes:

| Pieza | Qué es | Dónde vive |
| :--- | :--- | :--- |
| **ESP-IDF** | El SDK de Espressif: el compilador y los drivers de bajo nivel sobre los que se construye MicroPython | `~/esp/esp-idf` (Paso 2) |
| **MicroPython** | El intérprete/runtime original, sin modificar salvo un parche pequeño (ver Paso 5) | Donde lo clones — *no* dentro de este repositorio |
| **`isurlog-firmware`** (este repo) | El código propio de ISURKI: la aplicación (`app/`), los drivers (`src/`), la definición de la placa (`boards/ISURLOG_ESP32/`) y las herramientas de compilación (`tools/`) | Se clona aparte, donde prefieras |
| **El parche** (`patches/main.c.patch`) | El único cambio inevitable al código compartido de MicroPython — una comprobación de PIN/autenticación antes de llegar a la REPL | Versionado dentro de `isurlog-firmware`, se aplica sobre tu clon de MicroPython en el Paso 5 |

El script de compilación (Paso 6) las une: ESP-IDF aporta el compilador, MicroPython el intérprete, e `isurlog-firmware` todo lo específico de la placa ISURLOG.

## 1.4 Instrucciones de Compilación (Ubuntu / WSL)

### Paso 1: Instalar las Dependencias del Sistema

Abrir la terminal de Ubuntu e instalar todos los paquetes necesarios:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv \
  cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential pkg-config
```

### Paso 2: Clonar e Instalar ESP-IDF

El firmware se compila con **ESP-IDF v5.4.1**:

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4.1 --recursive https://github.com/espressif/esp-idf.git

cd esp-idf
./install.sh esp32
```

!!! note "Por qué ESP-IDF 5.4.1 y no 5.5"
    MicroPython 1.29 recomienda ESP-IDF 5.5.2, pero también soporta la 5.4.1. En el ESP32 original, al compilar MicroPython 1.29 con ESP-IDF 5.5 se queda fuera la función `esp32.gpio_deep_sleep_hold()`, que el ISURLOG necesita para mantener el estado de sus pines de control (alimentación del módem y de los sensores) durante el deep sleep. Con ESP-IDF 5.4.1 esa función sí se incluye.

No hace falta tener ESP-IDF activado en la terminal para compilar: el script del Paso 6 lo activa por sí mismo. Solo hay que activarlo a mano para descargar los submódulos de MicroPython (Paso 5) y para grabar el firmware (ver [1.5](#15-archivos-generados-y-grabado)).

### Paso 3: Clonar MicroPython

Clona MicroPython original, sin modificar, en la versión que este proyecto usa actualmente — **donde prefieras, fuera de este repositorio**:

```bash
cd ~
git clone --branch v1.29.0 --depth 1 https://github.com/micropython/micropython.git
```

El firmware se compila contra la versión que haya descargada en este clon. El nombre de la carpeta no importa.

### Paso 4: Clonar Este Repositorio

```bash
cd ~
git clone https://github.com/isurki-tecnica/isurlog-firmware.git
```

### Paso 5: Aplicar el Parche y Descargar los Submódulos de MicroPython

Aplica el único parche de `isurlog-firmware` sobre el clon de MicroPython del Paso 3:

```bash
cd ~/micropython
git apply ~/isurlog-firmware/patches/main.c.patch
```

!!! note "Qué hace este parche, y por qué no se puede evitar"
    Añade una comprobación de PIN/autenticación que se ejecuta justo antes de que el dispositivo entraría en la REPL — cerrando el acceso serie/USB sin autenticar en una unidad ya desplegada. Tiene que vivir aquí, en el propio `main.c` de MicroPython, y no en un simple `boot.py`: una comprobación a nivel de `boot.py` se puede saltar enviando Ctrl-C en el momento justo (la secuencia de arranque de MicroPython simplemente pasa al siguiente paso, no falla de forma dura), lo cual anularía todo el sentido de la comprobación. Ponerla aquí, después de que ya se hayan ejecutado todos los demás scripts de arranque, cierra ese hueco.

Después, descarga las propias dependencias de MicroPython (`lib/berkeley-db-1.xx`, `lib/tinyusb`, `lib/micropython-lib`, sin relación con el parche anterior). Este paso usa las herramientas de ESP-IDF, así que actívalo antes:

```bash
source ~/esp/esp-idf/export.sh
cd ~/micropython/ports/esp32
make submodules
```

Los pasos 1 a 5 solo se hacen una vez. A partir de ahí, compilar una versión nueva es solo el Paso 6.

### Paso 6: Compilar el Firmware

Desde la raíz de `isurlog-firmware`, ejecuta el script de compilación con la versión que vas a compilar y la ruta de tu clon de MicroPython:

```bash
cd ~/isurlog-firmware
bash tools/build_firmware.sh --fw-version 2.0.6 --micropython-dir ~/micropython
```

| Opción | Descripción |
| :--- | :--- |
| `--fw-version` | Versión del firmware a compilar, por ejemplo `2.0.6`. **Obligatoria.** Se escribe dentro del firmware (`src/modules/version.py`), para que un dispositivo en marcha pueda indicar en qué versión está. |
| `--micropython-dir` | Ruta del clon de MicroPython del Paso 3. |
| `--idf-dir` | ESP-IDF con la que compilar. Por defecto `~/esp/esp-idf`, la instalada en el Paso 2. |
| `-h`, `--help` | Muestra las opciones disponibles. |

El script hace cuatro pasos y se detiene en el primero que falle:

1. **Activa ESP-IDF** en un entorno limpio. Así no se mezcla en la compilación la ESP-IDF que tuviera cargada tu terminal o tu `~/.profile`, que es el error más habitual cuando hay más de una versión instalada.
2. **Borra la compilación anterior.** ESP-IDF se niega a reutilizar una compilación configurada con otra versión, y empezar de cero evita restos de compilaciones anteriores.
3. **Compila el firmware**, mediante el `Makefile` del repositorio.
4. **Comprueba las APIs del firmware.** Saca la lista de todas las funciones del firmware que usa el código del ISURLOG (de `machine`, `esp32`, `os` y el resto) y comprueba que cada una existe en esta compilación concreta. Algunas dependen de cómo se compilaron MicroPython y ESP-IDF, así que pueden desaparecer al actualizar cualquiera de los dos. Si falta alguna, el script la indica, muestra dónde la usa el código y avisa de que no se debe grabar esa compilación. Esta comprobación es la que detectaría un problema como el descrito en la nota de ESP-IDF de más arriba.

Al terminar, muestra un resumen con los archivos generados, el espacio libre en la partición OTA, el comando para grabarlo y el archivo para la comprobación en el dispositivo.

!!! note "Compilar sin el script"
    Por debajo, el script ejecuta `make VERSION=<versión> MICROPYTHON_DIR=<ruta>`. Ese comando sigue funcionando por sí solo si prefieres activar ESP-IDF tú mismo, pero entonces no se hace la comprobación de APIs.

## 1.5 Archivos Generados y Grabado

La compilación genera su salida dentro del **clon de MicroPython**, no dentro de `isurlog-firmware`: `<micropython-dir>/ports/esp32/build-ISURLOG_ESP32/`. Los archivos que importan son:

| Archivo | Qué es |
| :--- | :--- |
| `firmware.bin` | La imagen completa (bootloader, tabla de particiones y aplicación) para grabar por USB. |
| `micropython.bin` | Solo la aplicación. Es el archivo que se usa en las actualizaciones OTA. |
| `api_check.py` | El script para la comprobación en el dispositivo descrita en [1.6](#16-verificar-el-firmware-en-el-dispositivo). |

Para grabar por USB, activa ESP-IDF en la terminal (aporta `esptool`) y escribe `firmware.bin` en la dirección `0x1000`:

```bash
source ~/esp/esp-idf/export.sh
cd ~/micropython/ports/esp32/build-ISURLOG_ESP32
python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash 0x1000 firmware.bin
```

Desde Windows, cualquier herramienta basada en `esptool` funciona igual: grabar `firmware.bin` en `0x1000`.

!!! note "Qué reinicia grabar `firmware.bin`"
    Además del firmware, borra la zona NVS y la selección de partición OTA, así que después el dispositivo arranca siempre desde la primera partición OTA. El sistema de archivos del dispositivo (`main.py`, configuración) no se toca.

## 1.6 Verificar el Firmware en el Dispositivo

Este paso es opcional, pero recomendable cada vez que se compila el firmware contra una versión nueva de MicroPython o de ESP-IDF.

La comprobación del Paso 6 se hace sobre los archivos de la compilación. Cubre las funciones escritas en C, que es donde suelen estar los cambios entre versiones, pero no las de los módulos de Python incluidos en el firmware (como `asyncio`). Ejecutar `api_check.py` en el dispositivo comprueba todas las funciones que usa el código, en el firmware que de verdad está funcionando.

1. Graba el firmware nuevo.
2. Copia `api_check.py` desde la carpeta de la compilación a la raíz del sistema de archivos del dispositivo, con Thonny, rshell o una herramienta similar.
3. Detén el programa con Ctrl-C e introduce el PIN para llegar a la REPL.
4. Ejecuta:
    ```python
    import api_check
    ```

El resultado termina con un resumen:

- **`All firmware APIs used by the code exist in this firmware.`** — Todo lo que necesita el código está presente.
- **`FAIL`** — Falta en este firmware algo que usa el código. Cada línea indica qué es y dónde lo usa el código. Hay que corregirlo antes de desplegar este firmware.
- **`WARN`** — Imports opcionales que el código ya gestiona si faltan. Normalmente no son un problema.

Al terminar, se puede borrar `api_check.py` del dispositivo. No se usa durante el funcionamiento normal.

## 1.7 Código de la Aplicación (`app/`)

Este repositorio también contiene la carpeta `app/`.

!!! note "app/ no forma parte del firmware"
    El contenido de esta carpeta (`main.py`, `config/`, etc.) **no** se compila ni se congela dentro del binario del firmware — a diferencia de `src/modules/` y `src/lib/`, que sí. Estos archivos son la lógica de la aplicación en Python, y se despliegan en el sistema de archivos del dispositivo por separado, después de grabar el firmware: bien mediante el **propio actualizador guiado de IsurDASH** (la vía recomendada — ver [6.9. Mantenimiento de Dispositivos](isurdash-maintenance.es.md#actualizacion-de-firmware)), bien manualmente con una herramienta como Thonny o rshell. Esta separación es lo que permite actualizar la lógica de la aplicación en campo sin necesidad de regrabar nunca el firmware.
