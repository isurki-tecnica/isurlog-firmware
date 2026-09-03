'''
@Description: Generic MicroPython driver for the I2C EEPROM series
              24AA1025 / 24LC1025 / 24FC1025 (1024-Kbit, 128KB)

Reference: Microchip DS20001941M
'''

import utime

# --- Device constants -------------------------------------------
PAGE_SIZE = 128          # bytes per write page (Section 6.2)
BLOCK_SIZE = 0x10000     # 64K bytes per block (the chip has 2 blocks)
TOTAL_SIZE = 0x20000     # 128K bytes total (1024 Kbit)
WRITE_CYCLE_TIMEOUT_MS = 20   # margin over the max TWC of 5ms (Table 1-2)


class eeprom24lc1025(object):
    '''
    Generic driver for 24AA1025/24LC1025/24FC1025 EEPROM.
    API: write(address,data), read(address,length), erase(address,length,pattern),
         write_byte(address,data), read_byte(address), write_protect(enable),
         is_ready(), capacity

    Addressing note: the chip organizes its memory in TWO 64KB blocks,
    selected by the B0 bit of the control byte (Section 5.0). In MicroPython
    this translates into TWO distinct 7-bit I2C addresses, 0x04 apart on the
    bus (B0 sits on bit 2 of the 7-bit address). That's why scanning the bus
    shows two addresses (e.g. 0x50 and 0x54) for a single physical chip.
    This class abstracts that away: the caller only ever deals with a linear
    address from 0 to 131071 (0x1FFFF).
    '''

    def __init__(self, i2c_dev, address=0x50, wp_pin=None):
        '''
        :param i2c_dev: already initialized I2C object
        :param address: 7-bit address of BLOCK 0 (B0=0), matching the
                         A1/A0 wiring on your PCB. Defaults to 0x50
                         (A1=A0=0, A2=VCC per datasheet). Block 1 is
                         derived automatically as (address | 0x04).
        :param wp_pin: Pin object connected to WP (optional). If given,
                        write_protect() drives the pin directly.
        '''
        self._i2c = i2c_dev
        self._addr_block0 = address
        self._addr_block1 = address | 0x04
        self._wp_pin = wp_pin
        if self._wp_pin is not None:
            self._wp_pin.init(self._wp_pin.OUT, value=0)  # WP=0 -> write enabled

    # ---------------- internal helpers ----------------

    def _block_addr(self, block):
        return self._addr_block1 if block else self._addr_block0

    def _split_address(self, address):
        '''
        Converts a linear address (0..0x1FFFF) into (i2c_address, 16-bit offset)
        '''
        if address < 0 or address >= TOTAL_SIZE:
            raise ValueError('address out of range (0-{})'.format(TOTAL_SIZE - 1))
        block = (address >> 16) & 0x01
        offset = address & 0xFFFF
        return self._block_addr(block), offset

    def _wait_write_complete(self, i2c_addr, timeout_ms=WRITE_CYCLE_TIMEOUT_MS):
        '''
        ACK polling (Section 7.0): the chip won't acknowledge while its
        internal write cycle is in progress (max 5ms). We poll until it
        acknowledges again, instead of always waiting a fixed sleep.
        :return: True if the device responded within the timeout
        '''
        start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
            try:
                self._i2c.writeto(i2c_addr, b'')
                return True
            except OSError:
                pass
        return False

    # ---------------- write ----------------

    def write_byte(self, address, data):
        '''
        Writes a single byte (Byte Write, Section 6.1).
        :param address: linear address 0..0x1FFFF
        :param data: integer 0-255
        '''
        i2c_addr, offset = self._split_address(address)
        buf = bytes([offset >> 8, offset & 0xFF, data & 0xFF])
        self._i2c.writeto(i2c_addr, buf)
        if not self._wait_write_complete(i2c_addr):
            raise OSError('EEPROM did not respond after write_byte (internal cycle timeout)')

    def write(self, address, data):
        '''
        Writes a byte sequence of any length, automatically splitting it
        to respect the physical page limit (128 bytes, Section 6.2) and
        the block limit (64KB) of the chip. Without page splitting, the
        chip would overwrite the start of the page instead of advancing
        (see the "Note" in Section 6.2 of the datasheet).
        :param address: starting linear address 0..0x1FFFF
        :param data: bytes/bytearray to write
        '''
        data = bytes(data)
        remaining = len(data)
        pos = 0
        addr = address

        if addr + remaining > TOTAL_SIZE:
            raise ValueError('write exceeds memory size')

        while remaining > 0:
            i2c_addr, offset = self._split_address(addr)

            bytes_to_page_end = PAGE_SIZE - (offset % PAGE_SIZE)
            bytes_to_block_end = BLOCK_SIZE - offset
            chunk_len = min(remaining, bytes_to_page_end, bytes_to_block_end)
            chunk = data[pos:pos + chunk_len]

            buf = bytes([offset >> 8, offset & 0xFF]) + chunk
            self._i2c.writeto(i2c_addr, buf)
            if not self._wait_write_complete(i2c_addr):
                raise OSError('EEPROM did not respond after write() (internal cycle timeout)')

            pos += chunk_len
            addr += chunk_len
            remaining -= chunk_len

    # ---------------- read ----------------

    def read_byte(self, address):
        '''
        Reads a single byte.
        '''
        return self.read(address, 1)[0]

    def read(self, address, length):
        '''
        Reads 'length' bytes starting at 'address' (Random/Sequential Read,
        Section 8.2/8.3), automatically splitting the transfer if it crosses
        the 64KB block boundary (the chip doesn't support sequential reads
        across that boundary, Section 8.3).
        :return: bytearray with the data read
        '''
        if address < 0 or address + length > TOTAL_SIZE:
            raise ValueError('read exceeds memory size')

        result = bytearray()
        remaining = length
        addr = address

        while remaining > 0:
            i2c_addr, offset = self._split_address(addr)
            bytes_to_block_end = BLOCK_SIZE - offset
            chunk_len = min(remaining, bytes_to_block_end)

            # Random read: set the address pointer with a write (no STOP,
            # repeated start), then read. Done manually with writeto/readfrom
            # so we don't rely on addrsize=16 support in readfrom_mem.
            addr_buf = bytes([offset >> 8, offset & 0xFF])
            self._i2c.writeto(i2c_addr, addr_buf, False)
            result += self._i2c.readfrom(i2c_addr, chunk_len)

            addr += chunk_len
            remaining -= chunk_len

        return result

    # ---------------- erase ----------------

    def erase(self, address=0, length=None, pattern=0xFF):
        '''
        'Erases' a range by writing a fixed pattern. This chip has no
        hardware erase command, only writes (0xFF is the typical blank
        state of an EEPROM).
        :param address: start of the range (default 0)
        :param length: number of bytes (default: up to the end of memory)
        :param pattern: fill byte
        '''
        if length is None:
            length = TOTAL_SIZE - address

        fill_chunk = bytes([pattern & 0xFF]) * PAGE_SIZE
        remaining = length
        addr = address

        while remaining > 0:
            chunk_len = min(remaining, PAGE_SIZE)
            self.write(addr, fill_chunk[:chunk_len])
            addr += chunk_len
            remaining -= chunk_len

    # ---------------- write protection ----------------

    def write_protect(self, enable):
        '''
        Enables/disables write protection via the WP pin, if one was
        provided in the constructor. WP=VCC protects the ENTIRE memory
        (Section 6.3); partial protection is not possible.
        '''
        if self._wp_pin is None:
            raise RuntimeError('wp_pin not configured in constructor')
        self._wp_pin.value(1 if enable else 0)

    # ---------------- utilities ----------------

    def is_ready(self):
        '''
        Checks that both blocks of the chip respond on the I2C bus.
        '''
        try:
            self._i2c.writeto(self._addr_block0, b'')
            self._i2c.writeto(self._addr_block1, b'')
            return True
        except OSError:
            return False

    @property
    def capacity(self):
        '''
        Total memory size in bytes.
        '''
        return TOTAL_SIZE