# 1. Build Environment Setup

This guide details the necessary steps to set up a stable development environment for compiling the custom MicroPython firmware binary (`firmware.bin`) for the ISURLOG datalogger.

The firmware is based on **MicroPython v1.25.0** and includes custom modifications for optimized data logging applications.

!!! warning "WARNING"
    This project is derived from MicroPython v1.25.0 and includes custom modifications. While effort is made to maintain stability, it is subject to changes and and may differ from upstream MicroPython.


## 1.1 Supported Development Platforms

The ISURLOG was designed to be compatible with various development platforms, including **ESP-IDF**, **MicroPython**, and **Arduino IDE**. However, it is important to note that **ISURKI guarantees full compatibility and total support only with MicroPython**.

| Platform | Compatibility Status | Recommendation |
| :--- | :--- | :--- |
| **MicroPython** | **Fully Guaranteed and Supported** | **Highly Recommended** to maximize functionality. |
| **ESP-IDF / Arduino IDE** | Compatibility depends on specific implementation and future updates; **full functionality is not guaranteed**. | Use is not discouraged, but ISURKI focuses on maintaining compatibility and offering continuous support only on MicroPython. |

## 1.2 Recommended Environment

The recommended build environment is **Ubuntu Linux**.

For Windows users, native compilation is complex and **not recommended**. Please use the **Windows Subsystem for Linux (WSL)** and follow the Ubuntu instructions below for a more stable and straightforward setup.

## 1.3 Build Instructions (Ubuntu / WSL)

### Step 1: Install System Dependencies

Open your Ubuntu terminal and install all required packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install build-essential libffi-dev git pkg-config
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

### Step 2: Clone and Install ESP-IDF

This firmware requires ESP-IDF v5.2.x. We recommend `v5.2.6` for optimal compatibility with the MicroPython base.

```bash
# Create a directory for ESP-IDF
mkdir -p ~/esp
cd ~/esp

# Clone the correct version
git clone -b v5.4.1 --recursive [https://github.com/espressif/esp-idf.git](https://github.com/espressif/esp-idf.git)

# Install the toolchain
cd esp-idf
./install.sh esp32
```

### Step 3: Activate ESP-IDF Environment

You must "source" the export script in your terminal to set environment variables.

```bash
# Add the export command to your profile
echo -e '\n. $HOME/esp/esp-idf/export.sh' >> ~/.profile

# Source it for the current session
source $HOME/esp/esp-idf/export.sh
```

### Step 4: Clone This Repository

Clone the firmware repository to your system:

```bash
cd ~
git clone [https://github.com/isurki-tecnica/isurlog-firmware.git](https://github.com/isurki-tecnica/isurlog-firmware.git)

# Navigate into the repo
cd isurlog-firmware

# Switch to our working branch (if not already on 'main')
git checkout main

```

### Step 5: Compile the Firmware

Finally, navigate to the `esp32` port directory within the cloned repository and run the build commands:

```bash
# Navigate to the ESP32 port
cd ports/esp32

# Clean any previous builds (optional, but recommended for fresh builds)
make BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM clean

# Download MicroPython specific submodules
make submodules

# Start the build process
make BOARD=ESP32_GENERIC BOARD_VARIANT=SPIRAM
```

## 1.4 Output Files

### Firmware Binary Location

The compiled firmware `.bin` file will be generated in the following directory:

`ports/esp32/build-ESP32_GENERIC-SPIRAM/firmware.bin`

## Application Code (`app/`)

This repository also contains the `app/` folder.

IMPORTANT: The contents of this folder (`main.py`, `config/`, etc.) are NOT compiled into the firmware. These files represent the Python application logic and must be uploaded manually to the ESP32's filesystem (using tools like Thonny or rshell) after flashing the `firmware.bin`. This allows for flexible updates to the application logic without recompiling the entire firmware.