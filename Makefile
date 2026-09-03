# ISURLOG build wrapper.
#
# Lives outside the MicroPython tree on purpose (see the decoupling plan) -
# it injects the firmware version into modules/version.py and then invokes
# the real build against a plain, unpatched MicroPython checkout, pointed
# at our own board directory via BOARD_DIR. No changes to MicroPython's own
# Makefile are needed for this.
#
# Usage: make VERSION=2.0.2
#
# NOTE: MICROPYTHON_DIR/VERSION_PY still reflect Phase 1's in-place layout
# (board dir under ports/esp32/boards/, modules under ports/esp32/modules/).
# Once modules/lib move into this repo's own top level (Phase 2), update
# these two paths accordingly.

.DEFAULT_GOAL := all

MICROPYTHON_DIR ?= .
BOARD_DIR := $(CURDIR)/ports/esp32/boards/ISURLOG_ESP32
VERSION_PY := $(CURDIR)/ports/esp32/modules/modules/version.py

VERSION ?=

.PHONY: all check-version genversion

check-version:
ifeq ($(VERSION),)
	$(error Debes indicar VERSION. Ejemplo: make VERSION=2.0.2)
endif

genversion: check-version
	@echo "VERSION = \"$(VERSION)\"" > $(VERSION_PY)
	@echo "Version de firmware: $(VERSION) -> $(VERSION_PY)"

all: genversion
	$(MAKE) -C $(MICROPYTHON_DIR)/ports/esp32 BOARD_DIR=$(BOARD_DIR)
