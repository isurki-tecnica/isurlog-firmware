# 1. Configuración del Entorno de Compilación

Esta guía explica cómo configurar un entorno de desarrollo y compilar el firmware de ISURLOG desde el código fuente.

El firmware se compila contra un **MicroPython original, sin modificar** (fijado actualmente a **v1.25.0**) más un único parche pequeño y versionado — no es un fork completo. Este repositorio (`isurlog-firmware`) contiene únicamente el código propio de ISURKI: la lógica de la aplicación, los drivers, y la definición de la placa. MicroPython en sí se clona aparte, así que subir de versión nunca requiere tocar el historial de este repositorio.

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

Antes de entrar en comandos, ayuda saber qué se está montando exactamente — tres cosas separadas, clonadas de forma independiente, que solo se juntan en el momento de compilar:

| Pieza | Qué es | Dónde vive |
| :--- | :--- | :--- |
| **MicroPython** | El intérprete/runtime original, sin modificar salvo un parche pequeño (ver Paso 6 más abajo) | Donde lo clones — *no* dentro de este repositorio |
| **`isurlog-firmware`** (este repo) | El código propio de ISURKI: la aplicación (`app/`), los drivers (`src/`), y la definición de la placa (`boards/ISURLOG_ESP32/`) | Se clona aparte, donde prefieras |
| **El parche** (`patches/main.c.patch`) | El único cambio inevitable al código compartido de MicroPython — una comprobación de PIN/autenticación antes de llegar a la REPL | Versionado dentro de `isurlog-firmware`, se aplica sobre tu clon de MicroPython en el Paso 6 |

El comando de compilación (Paso 7) apunta a las dos ubicaciones a la vez — MicroPython aporta el compilador y el propio intérprete, `isurlog-firmware` aporta todo lo específico de la placa ISURLOG.

## 1.4 Instrucciones de Compilación (Ubuntu / WSL)

### Paso 1: Instalar las Dependencias del Sistema

Abrir la terminal de Ubuntu e instalar todos los paquetes necesarios:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv \
  cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential pkg-config
```

### Paso 2: Clonar e Instalar ESP-IDF

Este firmware se compila actualmente contra **ESP-IDF v5.4.1**.

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4.1 --recursive https://github.com/espressif/esp-idf.git

cd esp-idf
./install.sh esp32
```

### Paso 3: Activar el Entorno de ESP-IDF

Cada nueva sesión de terminal necesita esto "ejecutado" (`source`) antes de compilar, ya que configura el compilador y las variables de entorno:

```bash
# Hazlo una vez, para que ocurra automáticamente en futuras terminales:
echo -e '\n. $HOME/esp/esp-idf/export.sh' >> ~/.profile

# Para tu terminal actual:
source $HOME/esp/esp-idf/export.sh
```

### Paso 4: Clonar MicroPython

Clona MicroPython original, sin modificar, en la versión que este proyecto usa actualmente — **donde prefieras, fuera de este repositorio**:

```bash
cd ~
git clone --branch v1.25.0 --depth 1 https://github.com/micropython/micropython.git
```

### Paso 5: Clonar Este Repositorio

```bash
cd ~
git clone https://github.com/isurki-tecnica/isurlog-firmware.git
cd isurlog-firmware
```

### Paso 6: Aplicar el Parche y Descargar los Submódulos de MicroPython

Ahora que ambos están clonados, aplica el único parche de `isurlog-firmware` sobre el clon de MicroPython del Paso 4:

```bash
cd ~/micropython
git apply ~/isurlog-firmware/patches/main.c.patch
```

!!! note "Qué hace este parche, y por qué no se puede evitar"
    Añade una comprobación de PIN/autenticación que se ejecuta justo antes de que el dispositivo entraría en la REPL — cerrando el acceso serie/USB sin autenticar en una unidad ya desplegada. Tiene que vivir aquí, en el propio `main.c` de MicroPython, y no en un simple `boot.py`: una comprobación a nivel de `boot.py` se puede saltar enviando Ctrl-C en el momento justo (la secuencia de arranque de MicroPython simplemente pasa al siguiente paso, no falla de forma dura), lo cual anularía todo el sentido de la comprobación. Ponerla aquí, después de que ya se hayan ejecutado todos los demás scripts de arranque, cierra ese hueco.

Después, descarga las propias dependencias de MicroPython (esto baja `lib/berkeley-db-1.xx`, `lib/tinyusb`, `lib/micropython-lib`, sin relación con el parche anterior):

```bash
cd ports/esp32
make submodules
```

### Paso 7: Compilar el Firmware

Desde la raíz de `isurlog-firmware` (no desde dentro del clon de MicroPython), apuntando `MICROPYTHON_DIR` a donde lo clonaste en el Paso 4:

```bash
cd ~/isurlog-firmware
make VERSION=2.0.2 MICROPYTHON_DIR=~/micropython
```

`VERSION` es obligatorio — se escribe dentro del propio firmware (`src/modules/version.py`) para que un dispositivo en marcha pueda indicar en qué versión está. Usa la versión que realmente estés compilando.

Si `MICROPYTHON_DIR` falta o apunta a algo que no es un clon de MicroPython, la compilación falla inmediatamente con un mensaje claro, en vez de un error confuso más adelante.

## 1.5 Archivos Generados y Grabado

La compilación genera su salida dentro del **clon de MicroPython**, no dentro de `isurlog-firmware` — en concreto en `$MICROPYTHON_DIR/ports/esp32/build-ISURLOG_ESP32/`. Al terminar una compilación correcta, el propio sistema de build imprime el comando exacto de grabado para tu configuración, por ejemplo:

```bash
cd ~/micropython/ports/esp32/build-ISURLOG_ESP32
python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"
```

`idf.py flash` (ejecutado desde ese mismo directorio `build-ISURLOG_ESP32`) también funciona, si prefieres no lidiar directamente con `esptool`.

## 1.6 Código de la Aplicación (`app/`)

Este repositorio también contiene la carpeta `app/`.

!!! note "app/ no forma parte del firmware"
    El contenido de esta carpeta (`main.py`, `config/`, etc.) **no** se compila ni se congela dentro del binario del firmware — a diferencia de `src/modules/` y `src/lib/`, que sí. Estos archivos son la lógica de la aplicación en Python, y se despliegan en el sistema de archivos del dispositivo por separado, después de grabar el firmware: bien mediante el **propio actualizador guiado de IsurDASH** (la vía recomendada — ver [6.8. Mantenimiento de Dispositivos](isurdash-maintenance.es.md#actualizacion-de-firmware)), bien manualmente con una herramienta como Thonny o rshell. Esta separación es lo que permite actualizar la lógica de la aplicación en campo sin necesidad de regrabar nunca el firmware.
