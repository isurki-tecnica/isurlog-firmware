# freeze(path) strips `path` itself from the resulting module name and
# keeps everything after it - so freezing src/modules directly would
# produce top-level names (accel_manager, not modules.accel_manager).
# Freezing the *parent* of modules/ and lib/ in one call is what preserves
# "modules"/"lib" as the package prefix, matching the existing
# `from modules import ...` / `from lib.xxx import ...` code.
include("$(PORT_DIR)/boards/manifest.py")
freeze("$(BOARD_DIR)/../../src")
