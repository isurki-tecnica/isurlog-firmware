# src/modules/eeprom_memory.py

# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from modules import utils
from modules.config_manager import config_manager
from lib.EEPROM24LC1025 import eeprom24lc1025, PAGE_SIZE
from machine import I2C, Pin

# Fixed payload slot sizes exposed to the end user in the configuration
# platform. All of them evenly divide (32, 64) or are exact multiples of
# (128, 256) the EEPROM's physical page size, so slots never straddle a
# page boundary regardless of which one is chosen.
ALLOWED_PAYLOAD_SIZES = (32, 64, 128, 256)


class EEPROM_Memory:
    '''
    Persistent FIFO queue on I2C EEPROM (24AA1025/24LC1025/24FC1025), used as
    a backup buffer for payloads that could not be transmitted or that did
    not fit in RTC RAM. Unlike RTC_Memory, this data survives full power
    loss / brownouts, not just deep sleep.

    Slots are sized to exactly one EEPROM page (128 bytes: 1 length byte +
    up to 127 payload bytes). This guarantees every payload write is a
    single atomic page write, and every slot stays within one 64K block,
    which avoids torn writes and cross-boundary splits entirely.
    '''

    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, eeprom_address=0x50, base_address=0, max_payload_size=128):
        '''
        :param max_payload_size: payload slot size in bytes, as configured
                                  by the user (one of 32, 64, 128, 256).
                                  1 byte of each slot is used internally as
                                  a length prefix, leaving
                                  max_payload_size - 1 bytes for the actual
                                  payload.
        '''
        # --- CONFIGURATION ---
        
        # Load configuration from config_manager or use hardcoded defaults
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 21)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 22)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)

        # Initialize I2C bus
        self.i2c = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)

        self.eeprom = eeprom24lc1025(self.i2c, address=eeprom_address)

        self.MAGIC = b'EQ01'  # marks an initialized queue header
        self.HEADER_SIZE = PAGE_SIZE  # reserve one full page for the header

        if max_payload_size not in ALLOWED_PAYLOAD_SIZES:
            utils.log_warning(f"Invalid max_payload_size ({max_payload_size}), must be one of {ALLOWED_PAYLOAD_SIZES}. Defaulting to 128.")
            max_payload_size = 128

        self.PAYLOAD_SLOT_SIZE = max_payload_size
        self.MAX_PAYLOAD_BYTES = max_payload_size - 1

        self.HEAD_ADDR = 4    # 4 bytes, index of the oldest slot (next to read)
        self.TAIL_ADDR = 8    # 4 bytes, index of the next free slot (next to write)
        self.COUNT_ADDR = 12  # 4 bytes, number of payloads currently queued

        self.BASE_ADDR = base_address
        self.PAYLOAD_START_ADDR = self.BASE_ADDR + self.HEADER_SIZE

        self.total_slots = (self.eeprom.capacity - self.PAYLOAD_START_ADDR) // self.PAYLOAD_SLOT_SIZE

        # If a payload overflows the queue when full, overwrite the oldest
        # entry instead of rejecting the new one. Configurable, defaults to True.
        self.overwrite_oldest = config_manager.get_dynamic("general", "eeprom_overwrite_oldest", default=True)

        self._ensure_initialized()

    # ---------------- header handling ----------------

    def _read_header(self):
        '''
        Reads (head, tail, count) from the header page. Formats the queue
        on first use if the magic number is missing (blank EEPROM) or
        doesn't match (unexpected content).
        '''
        raw = self.eeprom.read(self.BASE_ADDR, self.HEADER_SIZE)
        if raw[0:4] != self.MAGIC:
            self._format()
            return 0, 0, 0
        head = int.from_bytes(raw[self.HEAD_ADDR:self.HEAD_ADDR + 4], 'little')
        tail = int.from_bytes(raw[self.TAIL_ADDR:self.TAIL_ADDR + 4], 'little')
        count = int.from_bytes(raw[self.COUNT_ADDR:self.COUNT_ADDR + 4], 'little')
        return head, tail, count

    def _write_header(self, head, tail, count):
        '''
        Writes the header fields in a single page write (all within the
        reserved header page, so this is one atomic operation).
        '''
        buf = bytearray(16)
        buf[0:4] = self.MAGIC
        buf[self.HEAD_ADDR:self.HEAD_ADDR + 4] = head.to_bytes(4, 'little')
        buf[self.TAIL_ADDR:self.TAIL_ADDR + 4] = tail.to_bytes(4, 'little')
        buf[self.COUNT_ADDR:self.COUNT_ADDR + 4] = count.to_bytes(4, 'little')
        self.eeprom.write(self.BASE_ADDR, buf)

    def _format(self):
        '''
        Initializes an empty queue. Called automatically on first boot
        (blank EEPROM) or if the header is unreadable/corrupted.
        '''
        utils.log_warning("EEPROM queue header not found or invalid, formatting.")
        self._write_header(0, 0, 0)

    def _ensure_initialized(self):
        self._read_header()  # triggers _format() internally if needed

    # ---------------- store ----------------

    def store_payload(self, payload):
        '''
        Stores a single payload in the queue. If the queue is full, either
        overwrites the oldest entry (default) or rejects the new one,
        depending on self.overwrite_oldest.
        :param payload: str or bytes (e.g. a hex-encoded Cayenne-LPP-like string)
        :return: True if stored, False otherwise
        '''
        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        if len(payload) > self.MAX_PAYLOAD_BYTES:
            utils.log_error(f"Payload too large for EEPROM queue: {len(payload)} bytes (max {self.MAX_PAYLOAD_BYTES})")
            return False

        head, tail, count = self._read_header()

        if count >= self.total_slots:
            if not self.overwrite_oldest:
                utils.log_error(f"EEPROM queue is full ({count}/{self.total_slots}), payload dropped")
                return False
            utils.log_warning(f"EEPROM queue is full ({count}/{self.total_slots}), overwriting oldest payload")
            head = (head + 1) % self.total_slots
            count -= 1

        offset = self.PAYLOAD_START_ADDR + (tail * self.PAYLOAD_SLOT_SIZE)
        slot = bytes([len(payload)]) + payload
        self.eeprom.write(offset, slot)

        tail = (tail + 1) % self.total_slots
        count += 1
        self._write_header(head, tail, count)

        utils.log_info(f"Stored payload in EEPROM queue. Pending: {count}/{self.total_slots}")
        return True

    # ---------------- status ----------------

    def get_pending_count(self):
        '''Returns the number of payloads currently queued.'''
        _, _, count = self._read_header()
        return count

    def has_pending(self):
        '''True if there is at least one payload waiting to be sent.'''
        return self.get_pending_count() > 0

    # ---------------- retrieve / drain ----------------

    def get_payloads(self, max_count=20):
        '''
        Non-destructively retrieves up to 'max_count' pending payloads,
        oldest first. Does NOT remove them from the queue - call
        remove_confirmed() after a successful send.
        :param max_count: batch limit, to bound RAM/time usage. Use None
                           to retrieve everything currently queued (careful
                           with very large backlogs).
        :return: list of decoded payload strings
        '''
        head, tail, count = self._read_header()
        n = count if max_count is None else min(count, max_count)

        payloads = []
        idx = head
        for _ in range(n):
            offset = self.PAYLOAD_START_ADDR + (idx * self.PAYLOAD_SLOT_SIZE)
            slot = self.eeprom.read(offset, self.PAYLOAD_SLOT_SIZE)
            length = slot[0]
            data = bytes(slot[1:1 + length])
            try:
                payloads.append(data.decode('utf-8'))
            except UnicodeError:
                utils.log_error("Corrupted payload found in EEPROM queue, skipping")
            idx = (idx + 1) % self.total_slots

        return payloads

    def remove_confirmed(self, n):
        '''
        Removes 'n' payloads from the front of the queue (oldest first).
        Call this after successfully transmitting the batch returned by
        get_payloads().
        :param n: number of payloads to drop
        :return: number of payloads actually removed (may be less than n
                 if the queue held fewer)
        '''
        head, tail, count = self._read_header()
        n = min(n, count)
        if n <= 0:
            return 0
        head = (head + n) % self.total_slots
        count -= n
        self._write_header(head, tail, count)
        utils.log_info(f"Removed {n} confirmed payload(s) from EEPROM queue. Pending: {count}/{self.total_slots}")
        return n

    # ---------------- reset ----------------

    def clear_memory(self, wipe_data=False):
        '''
        Empties the queue by resetting head/tail/count. This is fast and
        sufficient for normal operation, since old slot bytes are never
        read once count drops to 0.
        :param wipe_data: if True, also overwrites the whole payload area
                           with 0xFF. Slow (a few seconds for the full
                           128KB) - intended for factory reset / debugging,
                           not routine use.
        '''
        self._write_header(0, 0, 0)
        if wipe_data:
            self.eeprom.erase(self.PAYLOAD_START_ADDR)
        utils.log_info("EEPROM queue cleared.")