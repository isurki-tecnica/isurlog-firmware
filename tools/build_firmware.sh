#!/usr/bin/env bash
# Builds the ISURLOG firmware and checks it, in one go. Run in WSL/Linux:
#
#   bash tools/build_firmware.sh --fw-version 2.0.6
#   bash tools/build_firmware.sh --fw-version 2.0.6 --micropython-dir ~/micropython-1.30 --idf-dir ~/esp/esp-idf-5.5.2
#
# 1. Activates ESP-IDF in a clean environment, so a different ESP-IDF that
#    ~/.profile already loaded can't get mixed into the build.
# 2. Deletes the previous MicroPython build (configured with another ESP-IDF
#    it would refuse to build anyway).
# 3. Builds the firmware (the repo's Makefile: VERSION + MICROPYTHON_DIR).
# 4. Checks that every firmware API our code uses exists in the build.
#
# Why ESP-IDF 5.4.1 by default and not 5.5.x with MicroPython 1.29: on the
# ESP32, MicroPython 1.29 + ESP-IDF 5.5 drops esp32.gpio_deep_sleep_hold(),
# which power_manager.py needs to keep the control pins held in deep sleep.

set -euo pipefail

usage() {
    cat <<EOF
Usage: bash tools/build_firmware.sh --fw-version VERSION [--micropython-dir DIR] [--idf-dir DIR]

  --fw-version VERSION    ISURLOG firmware version to build, e.g. 2.0.6 (required)
  --micropython-dir DIR   MicroPython clone to build against; the version built is
                          whatever tag is checked out there
                          (default: micropython-1.29, two folders above this repo)
  --idf-dir DIR           ESP-IDF to build with (default: ~/esp/esp-idf, ESP-IDF 5.4.1)
  -h, --help              Show this help
EOF
}

# Re-run in a clean environment (no inherited ESP-IDF Python venv or variables).
if [[ -z "${ISURLOG_CLEAN_ENV:-}" ]]; then
    exec env -i HOME="$HOME" USER="${USER:-}" TERM="${TERM:-xterm}" \
        PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
        ISURLOG_CLEAN_ENV=1 bash --noprofile --norc "${BASH_SOURCE[0]}" "$@"
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW_VERSION=""
MICROPYTHON_DIR="$(cd "$REPO/../.." && pwd)/micropython-1.29"
IDF="$HOME/esp/esp-idf"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fw-version)        FW_VERSION="${2:-}"; shift 2 ;;
        --fw-version=*)      FW_VERSION="${1#*=}"; shift ;;
        --micropython-dir)   MICROPYTHON_DIR="${2:-}"; shift 2 ;;
        --micropython-dir=*) MICROPYTHON_DIR="${1#*=}"; shift ;;
        --idf-dir)           IDF="${2:-}"; shift 2 ;;
        --idf-dir=*)         IDF="${1#*=}"; shift ;;
        -h|--help)           usage; exit 0 ;;
        *)                   echo "Unknown option: $1"; echo; usage; exit 1 ;;
    esac
done
[[ -n "$FW_VERSION" ]] || { echo "Missing --fw-version"; echo; usage; exit 1; }

BUILD_DIR="$MICROPYTHON_DIR/ports/esp32/build-ISURLOG_ESP32"
PARTITIONS="$REPO/boards/ISURLOG_ESP32/partitions-8MiB-ota.csv"

step() { echo; echo "=== [$1/4] $2"; }
fail() { echo; echo "ERROR: $*"; exit 1; }

step 1 "ESP-IDF: $IDF"
[[ -f "$IDF/export.sh" ]] || fail "ESP-IDF not found at $IDF (use --idf-dir)"
[[ -f "$MICROPYTHON_DIR/ports/esp32/main.c" ]] || fail "MicroPython not found at $MICROPYTHON_DIR (use --micropython-dir)"
# shellcheck disable=SC1091
source "$IDF/export.sh" > /dev/null
# export.sh doesn't always fail loudly, so check it really activated this ESP-IDF.
[[ "$(cd "${IDF_PATH:-/nonexistent}" 2>/dev/null && pwd)" == "$(cd "$IDF" && pwd)" ]] || fail "ESP-IDF at $IDF did not activate (run its install.sh?)"
idf.py --version
echo "MicroPython: $MICROPYTHON_DIR ($(git -C "$MICROPYTHON_DIR" describe --tags 2>/dev/null || echo 'unknown version'))"

step 2 "Cleaning the previous build: $BUILD_DIR"
rm -rf "$BUILD_DIR"

step 3 "Building firmware $FW_VERSION"
make -C "$REPO" VERSION="$FW_VERSION" MICROPYTHON_DIR="$MICROPYTHON_DIR"
# Building with an ESP-IDF other than the one MicroPython pins rewrites its
# component lockfile; put it back so the MicroPython clone stays clean.
git -C "$MICROPYTHON_DIR" checkout -q -- ports/esp32/lockfiles/dependencies.lock.esp32 2>/dev/null || true

step 4 "Checking the firmware APIs our code uses"
python3 "$REPO/tools/gen_api_check.py" --repo "$REPO" --out "$BUILD_DIR/api_check.py"
CHECK_OK=1
python3 "$REPO/tools/check_build.py" "$BUILD_DIR" || CHECK_OK=0

APP_BIN="$BUILD_DIR/micropython.bin"
APP_SIZE=$(stat -c %s "$APP_BIN")
OTA_SIZE=$(( $(awk -F, '$1 ~ /^ *ota_0/ {gsub(/ /, "", $5); print $5}' "$PARTITIONS") ))
win() { wslpath -w "$1" 2>/dev/null || echo "$1"; }

echo
echo "================================================================"
echo " ISURLOG firmware $FW_VERSION"
echo "================================================================"
echo " Full image (USB flashing at 0x1000: bootloader + partition table + app):"
echo "   $(win "$BUILD_DIR/firmware.bin")"
echo " App only (OTA updates):"
echo "   $(win "$APP_BIN")"
echo "   $APP_SIZE bytes, $(( (OTA_SIZE - APP_SIZE) * 100 / OTA_SIZE ))% of the OTA partition still free"
if [[ $CHECK_OK -eq 1 ]]; then
    echo " API check: OK"
    echo
    echo " Next:"
    echo "  1. Flash it:  cd \"$BUILD_DIR\" && python -m esptool --chip esp32 -b 460800 --before default_reset --after hard_reset write_flash 0x1000 firmware.bin"
    echo "  2. Upload to the device:  $(win "$BUILD_DIR/api_check.py")"
    echo "  3. In its REPL:  import api_check"
else
    echo " API check: MISSING APIs above - DO NOT FLASH this build, fix them first."
    exit 1
fi
