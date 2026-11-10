# 1. Build Environment Setup

This guide walks through setting up a development environment and compiling the ISURLOG firmware from source.

The firmware builds against a **plain, unmodified MicroPython checkout** (currently **v1.29.0**) plus one small, tracked patch — it is not a full fork. This repository (`isurlog-firmware`) only contains ISURKI's own code: the application logic, the drivers, the board definition, and the build tools. MicroPython itself is cloned separately, so moving to a newer MicroPython version never requires touching this repository's history.

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

Four separate pieces come together at build time:

| Piece | What it is | Where it lives |
| :--- | :--- | :--- |
| **ESP-IDF** | Espressif's SDK: the compiler toolchain and the low-level drivers MicroPython is built on | `~/esp/esp-idf` (Step 2) |
| **MicroPython** | The upstream interpreter/runtime, unmodified except for one small patch (see Step 5) | Wherever you clone it — *not* inside this repository |
| **`isurlog-firmware`** (this repo) | ISURKI's own code: the application (`app/`), the drivers (`src/`), the board definition (`boards/ISURLOG_ESP32/`), and the build tools (`tools/`) | Cloned separately, anywhere you like |
| **The patch** (`patches/main.c.patch`) | The one unavoidable change to MicroPython's own shared code — a PIN/authentication check before the REPL is reached | Tracked inside `isurlog-firmware`, applied to your MicroPython clone in Step 5 |

The build script (Step 6) brings them together: ESP-IDF supplies the toolchain, MicroPython the interpreter, and `isurlog-firmware` everything specific to the ISURLOG board.

## 1.4 Build Instructions (Ubuntu / WSL)

### Step 1: Install System Dependencies

Open your Ubuntu terminal and install all required packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl flex bison gperf python3 python3-pip python3-venv \
  cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential pkg-config
```

### Step 2: Clone and Install ESP-IDF

The firmware builds against **ESP-IDF v5.4.1**:

```bash
mkdir -p ~/esp
cd ~/esp
git clone -b v5.4.1 --recursive https://github.com/espressif/esp-idf.git

cd esp-idf
./install.sh esp32
```

!!! note "Why ESP-IDF 5.4.1 and not 5.5"
    MicroPython 1.29 recommends ESP-IDF 5.5.2, but also supports 5.4.1. On the original ESP32, building MicroPython 1.29 with ESP-IDF 5.5 leaves out `esp32.gpio_deep_sleep_hold()`, which the ISURLOG needs to keep its control pins (modem power, sensor supplies) in their state during deep sleep. With ESP-IDF 5.4.1 that function is included.

There is no need to keep ESP-IDF activated in your terminal to build: the build script in Step 6 activates it by itself. You only need to activate it by hand to fetch MicroPython's submodules (Step 5) and to flash the firmware (see [1.5](#15-output-files-and-flashing)).

### Step 3: Clone MicroPython

Clone plain, upstream MicroPython at the version this project currently targets — **anywhere you like, outside this repository**:

```bash
cd ~
git clone --branch v1.29.0 --depth 1 https://github.com/micropython/micropython.git
```

The firmware is built against whatever version is checked out in this clone. The name of the folder doesn't matter.

### Step 4: Clone This Repository

```bash
cd ~
git clone https://github.com/isurki-tecnica/isurlog-firmware.git
```

### Step 5: Apply the Patch and Fetch MicroPython's Own Submodules

Apply `isurlog-firmware`'s one patch to the MicroPython clone from Step 3:

```bash
cd ~/micropython
git apply ~/isurlog-firmware/patches/main.c.patch
```

!!! note "What this patch does, and why it can't be avoided"
    It adds a PIN/authentication check that runs right before the device would otherwise drop into a REPL prompt — closing off unauthenticated serial/USB access to a deployed unit. It has to live here, in MicroPython's own `main.c`, rather than in a plain `boot.py`: a `boot.py`-level check can be skipped by sending Ctrl-C at the right moment (MicroPython's boot sequence just moves on to the next step, it doesn't hard-fail), which would defeat the whole point. Placing it here, after every other startup script has already run, closes that gap.

Then fetch MicroPython's own dependencies (`lib/berkeley-db-1.xx`, `lib/tinyusb`, `lib/micropython-lib`, unrelated to the patch above). This step uses ESP-IDF's tools, so activate it first:

```bash
source ~/esp/esp-idf/export.sh
cd ~/micropython/ports/esp32
make submodules
```

Steps 1 to 5 only need to be done once. From then on, building a new version is just Step 6.

### Step 6: Build the Firmware

From the root of `isurlog-firmware`, run the build script with the version you are building and the path to your MicroPython clone:

```bash
cd ~/isurlog-firmware
bash tools/build_firmware.sh --fw-version 2.0.6 --micropython-dir ~/micropython
```

| Option | Description |
| :--- | :--- |
| `--fw-version` | Firmware version to build, for example `2.0.6`. **Required.** It is written into the firmware (`src/modules/version.py`), so a running device can report which version it's on. |
| `--micropython-dir` | Path to the MicroPython clone from Step 3. |
| `--idf-dir` | ESP-IDF to build with. Defaults to `~/esp/esp-idf`, the one installed in Step 2. |
| `-h`, `--help` | Shows the available options. |

The script runs four steps and stops at the first one that fails:

1. **Activates ESP-IDF** in a clean environment. Whatever ESP-IDF your terminal or `~/.profile` already loaded can't get mixed into the build, which avoids the most common error when more than one ESP-IDF version is installed.
2. **Deletes the previous build.** ESP-IDF refuses to reuse a build configured with a different version, and a clean build rules out leftovers.
3. **Builds the firmware**, through the repository's `Makefile`.
4. **Checks the firmware APIs.** It lists every function of the firmware that the ISURLOG code uses (from `machine`, `esp32`, `os` and the rest) and checks that each one exists in this particular build. Some depend on how MicroPython and ESP-IDF were compiled, so they can disappear when either is updated. If anything is missing, the script names it, shows where the code uses it, and tells you not to flash that build. This check is what would catch a problem like the one described in the ESP-IDF note above.

When it finishes, it shows a summary with the generated files, the space left in the OTA partition, the command to flash it, and the file to use for the on-device check.

!!! note "Building without the script"
    The script calls `make VERSION=<version> MICROPYTHON_DIR=<path>` under the hood. That command still works on its own if you prefer to activate ESP-IDF yourself, but then the API check doesn't run.

## 1.5 Output Files and Flashing

The build output goes into the **MicroPython clone**, not into `isurlog-firmware`: `<micropython-dir>/ports/esp32/build-ISURLOG_ESP32/`. The relevant files are:

| File | What it is |
| :--- | :--- |
| `firmware.bin` | The complete image (bootloader, partition table and application) for flashing over USB. |
| `micropython.bin` | The application alone. This is the file used for over-the-air (OTA) updates. |
| `api_check.py` | The script for the on-device check described in [1.6](#16-verifying-the-firmware-on-the-device). |

To flash over USB, activate ESP-IDF in your terminal (it provides `esptool`) and write `firmware.bin` at offset `0x1000`:

```bash
source ~/esp/esp-idf/export.sh
cd ~/micropython/ports/esp32/build-ISURLOG_ESP32
python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash 0x1000 firmware.bin
```

From Windows, any `esptool`-based tool works the same way: write `firmware.bin` at `0x1000`.

!!! note "What flashing `firmware.bin` resets"
    Besides the firmware, it erases the NVS area and the OTA selection, so the device always boots from the first OTA partition afterwards. The device's filesystem (`main.py`, configuration) is not touched.

## 1.6 Verifying the Firmware on the Device

This step is optional, but recommended every time the firmware is built against a new MicroPython or ESP-IDF version.

The check in Step 6 looks at the build files. It covers the functions written in C, which is where changes between versions usually happen, but not those of the Python modules frozen into the firmware (such as `asyncio`). Running `api_check.py` on the device checks every function the code uses, on the firmware that is actually running.

1. Flash the new firmware.
2. Copy `api_check.py` from the build folder to the root of the device's filesystem, with Thonny, rshell or a similar tool.
3. Stop the running program with Ctrl-C and enter the PIN to reach the REPL.
4. Run:
    ```python
    import api_check
    ```

The result ends with a summary:

- **`All firmware APIs used by the code exist in this firmware.`** — Everything the code needs is present.
- **`FAIL`** — Something the code uses is missing from this firmware. Each line names it and shows where the code uses it. Fix it before deploying this firmware.
- **`WARN`** — Optional imports that the code already handles if they are missing. These are usually not a problem.

When you are done, `api_check.py` can be deleted from the device. It isn't used during normal operation.

## 1.7 Application Code (`app/`)

This repository also contains the `app/` folder.

!!! note "app/ is not part of the firmware"
    The contents of this folder (`main.py`, `config/`, etc.) are **not** compiled or frozen into the firmware binary — unlike `src/modules/` and `src/lib/`, which are. These files are the Python application logic, and get deployed onto the device's filesystem separately, after flashing the firmware: either through **IsurDASH's own guided updater** (the recommended path — see [6.9 Device Maintenance](isurdash-maintenance.md#firmware-update)), or manually with a tool like Thonny or rshell. This split is what lets the application logic be updated in the field without ever needing to reflash the firmware itself.
