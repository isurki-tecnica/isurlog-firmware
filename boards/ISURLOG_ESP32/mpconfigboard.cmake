# boards/sdkconfig.base, boards/sdkconfig.ble and boards/sdkconfig.spiram
# are genuine MicroPython files - those relative paths correctly resolve
# against ports/esp32 (where MicroPython actually lives), same as for any
# other board.
#
# Our own sdkconfig.isurlog can't be referenced the same way: this board
# directory lives outside the MicroPython tree (see the decoupling plan),
# so a bare relative path would also be resolved against ports/esp32 and
# never be found there. CMAKE_CURRENT_LIST_DIR always points at wherever
# this mpconfigboard.cmake file itself lives (i.e. BOARD_DIR), regardless
# of where that is, so we use it to build an absolute path instead - and
# to also inject the partition table's own path as an absolute one, since
# CONFIG_PARTITION_TABLE_CUSTOM_FILENAME has the exact same problem.

set(ISURLOG_PARTITIONS_ABS "${CMAKE_CURRENT_LIST_DIR}/partitions-8MiB-ota.csv")
set(ISURLOG_SDKCONFIG_GEN "${CMAKE_BINARY_DIR}/sdkconfig.isurlog.generated")
file(WRITE ${ISURLOG_SDKCONFIG_GEN}
"# CONFIG_ESPTOOLPY_FLASHSIZE_4MB is not set\nCONFIG_ESPTOOLPY_FLASHSIZE_8MB=y\nCONFIG_PARTITION_TABLE_CUSTOM=y\nCONFIG_PARTITION_TABLE_CUSTOM_FILENAME=\"${ISURLOG_PARTITIONS_ABS}\"\n")

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.ble
    boards/sdkconfig.spiram
    ${ISURLOG_SDKCONFIG_GEN}
)

# Without this, MICROPY_FROZEN_MANIFEST stays unset and ports/esp32's own
# CMakeLists.txt falls back to the generic boards/manifest.py - which is
# exactly what was silently happening (build succeeded, but froze nothing
# of ours: no 'modules'/'lib' packages, ImportError at runtime). Custom
# boards with their own manifest.py must set this explicitly; it's not
# auto-detected from the file just existing in BOARD_DIR.
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
