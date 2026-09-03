# ISURLOG build wrapper.
#
# Lives outside the MicroPython tree on purpose (see the decoupling plan) -
# it injects the firmware version into src/modules/version.py and then
# invokes the real build against a plain, unpatched MicroPython checkout,
# pointed at our own board directory via BOARD_DIR. No changes to
# MicroPython's own Makefile are needed for this.
#
# Usage: make VERSION=2.0.2 MICROPYTHON_DIR=/path/to/micropython
#
# MICROPYTHON_DIR must point at a clone of micropython/micropython at the
# tag this project currently targets (see patches/main.c.patch for which
# tag it was verified against). Not tracked/pinned by git on purpose -
# see the decoupling plan for why (no submodule).

.DEFAULT_GOAL := all

MICROPYTHON_DIR ?= ../micropython
BOARD_DIR := $(CURDIR)/boards/ISURLOG_ESP32
VERSION_PY := $(CURDIR)/src/modules/version.py

VERSION ?=

.PHONY: all check-version genversion check-micropython-dir

check-version:
ifeq ($(VERSION),)
	$(error Debes indicar VERSION. Ejemplo: make VERSION=2.0.2)
endif

check-micropython-dir:
	@test -f "$(MICROPYTHON_DIR)/ports/esp32/main.c" || \
		(echo "MICROPYTHON_DIR ($(MICROPYTHON_DIR)) no parece un clon de micropython/micropython. Indica la ruta correcta: make MICROPYTHON_DIR=/ruta/a/micropython VERSION=$(VERSION)"; false)

genversion: check-version
	@echo "VERSION = \"$(VERSION)\"" > $(VERSION_PY)
	@echo "Version de firmware: $(VERSION) -> $(VERSION_PY)"

all: check-micropython-dir genversion
	$(MAKE) -C $(MICROPYTHON_DIR)/ports/esp32 BOARD_DIR=$(BOARD_DIR)
