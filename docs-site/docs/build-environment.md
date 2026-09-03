# 1. Build Environment Setup

This guide walks through setting up a development environment and compiling the ISURLOG firmware from source.

The firmware builds against a **plain, unmodified MicroPython checkout** (currently pinned to **v1.25.0**) plus one small, tracked patch — it is not a full fork. This repository (`isurlog-firmware`) only contains ISURKI's own code: the application logic, the drivers, and the board definition. MicroPython itself is cloned separately, so upgrading to a newer MicroPython version never requires touching this repository's history.

!!! warning "Still evolving"
    ISURKI's own code is subject to change, and may occasionally lag behind the very latest upstream MicroPython release.

## 1.1 Supported Development Platforms

The ISURLOG was designed to be compatible with various development platforms, including **ESP-IDF**, **MicroPython**, and **Arduino IDE**. However, it is important to note that **ISURKI guarantees full compatibility and total support only with MicroPython**.

| Platform | Compatibility Status | Recommendation |
| :--- | :--- | :--- |
| **MicroPython** | **Fully Guaranteed and Supported** | **Highly Recommended** to maximize functionality. |
| **ESP-IDF / Arduino IDE** | Compatibility depends on specific implementation and future updates; **full functionality is not guaranteed**. | Use is not discouraged, but ISURKI focuses on maintaining compatibility and offering continuous support only on MicroPython. |

## 1.2 Recommended Environment

The recommended build environment is **Ubuntu Linux**.

For Windows users, native compilation is complex and **not recommended**. Please use the **Windows Subsystem for Linux (WSL)** and follow the Ubuntu instructions below for a more stable and straightforward setup.

## 1.3 How the Pieces Fit Together

Before diving into commands, it helps to know what you're actually assembling — three separate things, cloned independently, that only come together at build time:

| Piece | What it is | Where it lives |
| :--- | :--- | :--- |
| **MicroPython** | The upstream interpreter/runtime, unmodified except for one tiny patch (see Step 6 below) | Wherever you clone it — *not* inside this repository |
| **`isurlog-firmware`** (this repo) | ISURKI's own code: the application (`app/`), the drivers (`src/`), and the board definition (`boards/ISURLOG_ESP32/`) | Cloned separately, anywhere you like |
| **The patch** (`patches/main.c.patch`) | The one unavoidable change to MicroPython's own shared code — a PIN/authentication check before the REPL is reached | Tracked inside `isurlog-firmware`, applied to your MicroPython clone in Step 6 |

The build command (Step 7) points at both locations at once — MicroPython supplies the compiler toolchain and the interpreter itself, `isurlog-firmware` supplies everything specific to the ISURLOG board.

## 1.4 Build Instructions (Ubuntu / WSL)

### Step 1: Install System Dependencies

Open your Ubuntu terminal and install all required packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv \
  cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential pkg-config
```

### Step 2: Clone and Install ESP-IDF

This firmware currently builds against **ESP-IDF v5.4.1**.

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4.1 --recursive https://github.com/espressif/esp-idf.git

cd esp-idf
./install.sh esp32
```

### Step 3: Activate the ESP-IDF Environment

Every new terminal session needs this "sourced" before building, since it sets up the compiler toolchain and environment variables:

```bash
# Do this once, so it happens automatically in future terminals:
echo -e '\n. $HOME/esp/esp-idf/export.sh' >> ~/.profile

# For your current terminal:
source $HOME/esp/esp-idf/export.sh
```

### Step 4: Clone MicroPython

Clone plain, upstream MicroPython at the version this project currently targets — **anywhere you like, outside this repository**:

```bash
cd ~
git clone --branch v1.25.0 --depth 1 https://github.com/micropython/micropython.git
```

### Step 5: Clone This Repository

```bash
cd ~
git clone https://github.com/isurki-tecnica/isurlog-firmware.git
cd isurlog-firmware
```

### Step 6: Apply the Patch and Fetch MicroPython's Own Submodules

Now that both are cloned, apply `isurlog-firmware`'s one patch to the MicroPython checkout from Step 4:

```bash
cd ~/micropython
git apply ~/isurlog-firmware/patches/main.c.patch
```

!!! note "What this patch does, and why it can't be avoided"
    It adds a PIN/authentication check that runs right before the device would otherwise drop into a REPL prompt — closing off unauthenticated serial/USB access to a deployed unit. It has to live here, in MicroPython's own `main.c`, rather than in a plain `boot.py`: a `boot.py`-level check can be skipped by sending Ctrl-C at the right moment (MicroPython's boot sequence just moves on to the next step, it doesn't hard-fail), which would defeat the whole point. Placing it here, after every other startup script has already run, closes that gap.

Then fetch MicroPython's own dependencies (this downloads `lib/berkeley-db-1.xx`, `lib/tinyusb`, `lib/micropython-lib`, unrelated to the patch above):

```bash
cd ports/esp32
make submodules
```

### Step 7: Compile the Firmware

From the root of `isurlog-firmware` (not from inside the MicroPython clone), pointing `MICROPYTHON_DIR` at wherever you cloned it in Step 4:

```bash
cd ~/isurlog-firmware
make VERSION=2.0.2 MICROPYTHON_DIR=~/micropython
```

`VERSION` is required — it gets written into the firmware itself (`src/modules/version.py`) so a running device can report which version it's on. Use whatever version you're actually building.

If `MICROPYTHON_DIR` is missing or points somewhere that isn't a MicroPython checkout, the build fails immediately with a clear message rather than a confusing error further down the line.

## 1.5 Output Files and Flashing

The build produces its output inside the **MicroPython clone**, not inside `isurlog-firmware` — specifically in `$MICROPYTHON_DIR/ports/esp32/build-ISURLOG_ESP32/`. At the end of a successful build, the build system itself prints the exact flashing command for your setup, for example:

```bash
cd ~/micropython/ports/esp32/build-ISURLOG_ESP32
python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"
```

`idf.py flash` (run from that same `build-ISURLOG_ESP32` directory) works too, if you'd rather not deal with `esptool` directly.

## 1.6 Application Code (`app/`)

This repository also contains the `app/` folder.

!!! note "app/ is not part of the firmware"
    The contents of this folder (`main.py`, `config/`, etc.) are **not** compiled or frozen into the firmware binary — unlike `src/modules/` and `src/lib/`, which are. These files are the Python application logic, and get deployed onto the device's filesystem separately, after flashing the firmware: either through **IsurDASH's own guided updater** (the recommended path — see [6.8 Device Maintenance](isurdash-maintenance.md#firmware-update)), or manually with a tool like Thonny or rshell. This split is what lets the application logic be updated in the field without ever needing to reflash the firmware itself.
