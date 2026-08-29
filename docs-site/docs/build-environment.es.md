# 1. Configuración del Entorno de Compilación

Esta guía detalla los pasos necesarios para configurar un entorno de desarrollo estable con el que compilar el binario de firmware MicroPython personalizado (`firmware.bin`) para el datalogger ISURLOG.

El firmware se basa en **MicroPython v1.25.0** e incluye modificaciones propias orientadas a aplicaciones de registro de datos optimizadas.

!!! warning "ADVERTENCIA"
    Este proyecto deriva de MicroPython v1.25.0 e incluye modificaciones propias. Aunque se procura mantener la estabilidad, está sujeto a cambios y puede diferir del MicroPython original (upstream).


## 1.1 Plataformas de Desarrollo Soportadas

El ISURLOG se diseñó para ser compatible con distintas plataformas de desarrollo, incluyendo **ESP-IDF**, **MicroPython** y **Arduino IDE**. Sin embargo, es importante señalar que **ISURKI garantiza compatibilidad total y soporte completo únicamente con MicroPython**.

| Plataforma | Estado de Compatibilidad | Recomendación |
| :--- | :--- | :--- |
| **MicroPython** | **Totalmente Garantizada y Soportada** | **Muy recomendable** para aprovechar toda la funcionalidad. |
| **ESP-IDF / Arduino IDE** | La compatibilidad depende de la implementación concreta y de futuras actualizaciones; **no se garantiza la funcionalidad completa**. | No se desaconseja su uso, pero ISURKI centra el mantenimiento de compatibilidad y el soporte continuo únicamente en MicroPython. |

## 1.2 Entorno Recomendado

El entorno de compilación recomendado es **Ubuntu Linux**.

Para usuarios de Windows, la compilación nativa es compleja y **no se recomienda**. Utilizar el **Subsistema de Windows para Linux (WSL)** y seguir las instrucciones de Ubuntu de más abajo, para una configuración más estable y sencilla.

## 1.3 Instrucciones de Compilación (Ubuntu / WSL)

### Paso 1: Instalar las Dependencias del Sistema

Abrir la terminal de Ubuntu e instalar todos los paquetes necesarios:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install build-essential libffi-dev git pkg-config
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

### Paso 2: Clonar e Instalar ESP-IDF

Este firmware requiere ESP-IDF v5.2.x. Se recomienda la versión `v5.2.6` para una compatibilidad óptima con la base de MicroPython.

```bash
# Crear un directorio para ESP-IDF
mkdir -p ~/esp
cd ~/esp

# Clonar la versión correcta
git clone -b v5.4.1 --recursive [https://github.com/espressif/esp-idf.git](https://github.com/espressif/esp-idf.git)

# Instalar la toolchain
cd esp-idf
./install.sh esp32
```

### Paso 3: Activar el Entorno de ESP-IDF

Es necesario ejecutar ("source") el script de exportación en la terminal para configurar las variables de entorno.

```bash
# Añadir el comando de exportación al perfil
echo -e '\n. $HOME/esp/esp-idf/export.sh' >> ~/.profile

# Ejecutarlo para la sesión actual
source $HOME/esp/esp-idf/export.sh
```

### Paso 4: Clonar Este Repositorio

Clonar el repositorio del firmware en el sistema:

```bash
cd ~
git clone [https://github.com/isurki-tecnica/isurlog-firmware.git](https://github.com/isurki-tecnica/isurlog-firmware.git)

# Entrar en el repositorio
cd isurlog-firmware

# Cambiar a la rama de trabajo (si no se está ya en 'main')
git checkout main

```

### Paso 5: Compilar el Firmware

Por último, navegar hasta el directorio del puerto `esp32` dentro del repositorio clonado y ejecutar los comandos de compilación:

```bash
# Navegar al puerto ESP32
cd ports/esp32

# Limpiar compilaciones anteriores (opcional, pero recomendable para una compilación limpia)
make BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM clean

# Descargar los submódulos específicos de MicroPython
make submodules

# Iniciar el proceso de compilación
make BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM
```

## 1.4 Archivos Generados

### Ubicación del Binario de Firmware

El archivo `.bin` de firmware compilado se generará en el siguiente directorio:

`ports/esp32/build-ESP32_GENERIC-SPIRAM/firmware.bin`

## Código de la Aplicación (`app/`)

Este repositorio también contiene la carpeta `app/`.

!!! note "app/ no forma parte del firmware"
    El contenido de esta carpeta (`main.py`, `config/`, etc.) NO se compila dentro del firmware. Estos archivos representan la lógica de la aplicación en Python y deben subirse manualmente al sistema de archivos del ESP32 (usando herramientas como Thonny o rshell) después de grabar el `firmware.bin`. Esto permite actualizar la lógica de la aplicación con flexibilidad, sin necesidad de recompilar todo el firmware.
