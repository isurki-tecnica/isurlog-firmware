# NOTE: these paths point at ports/esp32/modules/{modules,lib} because this
# board directory still lives inside the full MicroPython fork (Phase 1 of
# the decoupling plan). Once modules/lib move into their own standalone
# repo (Phase 2), these become $(BOARD_DIR)-relative paths instead.
include("$(PORT_DIR)/boards/manifest.py")
freeze("$(PORT_DIR)/modules/modules")
freeze("$(PORT_DIR)/modules/lib")
