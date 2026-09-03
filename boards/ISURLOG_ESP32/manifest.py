# freeze()'s resulting package name is the basename of the given directory
# (that's why our own driver library is called "src/lib" and not "lib" -
# the leaf name is what matters, not the parent). Both need to stay named
# exactly "modules" and "lib" for the existing `from modules import ...`
# and `from lib.xxx import ...` imports across the codebase to keep working.
include("$(PORT_DIR)/boards/manifest.py")
freeze("$(BOARD_DIR)/../../src/modules")
freeze("$(BOARD_DIR)/../../src/lib")
