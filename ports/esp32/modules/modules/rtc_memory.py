# src/modules/rtc_memory.py (FINAL ROBUST VERSION WITH 2KB LIMIT)

from machine import RTC
from modules import utils
from modules.config_manager import config_manager

class RTC_Memory:
    def __init__(self, max_payload_size = 256):
        self.rtc = RTC()
        # --- CONFIGURATION ---
        self.COUNTER_ADDR = 0
        self.ALARM_FLAG_ADDR = 4  # <-- NEW: 1 byte for the alarm status flag
        
        self.PAYLOAD_START_ADDR = 8 # <-- MODIFIED: Payloads now start at byte 8 to leave space for counter and alarm flag (4+1+3 padding)
        self.PAYLOAD_SLOT_SIZE = max_payload_size
        
        # Documented write limit for rtc.memory() on ESP32
        self.RTC_BUFFER_LIMIT = 2048

        # Calculate the maximum number of payloads that fit in the 2KB buffer
        self.max_possible_payloads = (self.RTC_BUFFER_LIMIT - self.PAYLOAD_START_ADDR) // self.PAYLOAD_SLOT_SIZE
        
        # Read the desired accumulator value from the configuration
        self.n_cycles = config_manager.get_dynamic("general", "register_acumulator", default=5)

        # Enforce the limit if the user's configuration exceeds it
        if self.n_cycles > self.max_possible_payloads:
            utils.log_warning(f"Configured accumulator ({self.n_cycles}) exceeds 2KB RTC write limit for slot size {self.PAYLOAD_SLOT_SIZE}.")
            self.n_cycles = self.max_possible_payloads
            utils.log_warning(f"Accumulator has been limited to {self.n_cycles}.")
        
        self.TOTAL_BUFFER_SIZE = self.PAYLOAD_START_ADDR + (self.max_possible_payloads * self.PAYLOAD_SLOT_SIZE)
        
    def get_alarm_flag(self):
        """Reads the alarm status flag from the last transmission."""
        buffer = self.rtc.memory()
        if len(buffer) < 5:
            return False
        return buffer[self.ALARM_FLAG_ADDR] == 1

    def set_alarm_flag(self, status: bool):
        """Sets the alarm status flag in RTC memory."""
        buffer = self._get_buffer()
        buffer[self.ALARM_FLAG_ADDR] = 1 if status else 0
        self.rtc.memory(buffer)

    def _get_buffer(self):
        """Internal helper to get/initialize the RTC buffer."""
        buffer = self.rtc.memory()
        # If the buffer does not have the expected size (e.g., on first boot), it gets "formatted".
        if len(buffer) != self.TOTAL_BUFFER_SIZE:
            new_buffer = bytearray(self.TOTAL_BUFFER_SIZE)
            self.rtc.memory(new_buffer)
            return new_buffer
        return bytearray(buffer)

    def get_counter(self):
        """Reads the counter from the RTC buffer."""
        buffer = self.rtc.memory() 
        if len(buffer) < 4:
            return 0
        return int.from_bytes(buffer[0:4], 'little')

    def store_payload(self, payload):
        """Stores a payload in its predefined slot."""
        counter = self.get_counter()
        if counter >= self.max_possible_payloads:
            return False

        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        payload += b'\x00' # Add null terminator

        if len(payload) > self.PAYLOAD_SLOT_SIZE:
            utils.log_error(f"Payload too large: {len(payload)} bytes (max {self.PAYLOAD_SLOT_SIZE})")
            return False

        buffer = self._get_buffer()
        offset = self.PAYLOAD_START_ADDR + (counter * self.PAYLOAD_SLOT_SIZE)
        
        # Modify the buffer in RAM
        buffer[offset : offset + len(payload)] = payload
        counter += 1
        buffer[0:4] = counter.to_bytes(4, 'little')
        
        # Write the entire modified buffer back
        self.rtc.memory(buffer)
        
        utils.log_info(f"Stored payload in RTC memory. Cycle {counter} of {self.n_cycles}")
        return True

    def get_payloads(self):
        """Retrieves all stored payloads."""
        payloads = []
        counter = self.get_counter()
        buffer = self.rtc.memory() # Read the buffer once

        for i in range(counter):
            offset = self.PAYLOAD_START_ADDR + (i * self.PAYLOAD_SLOT_SIZE)
            slot_data = buffer[offset : offset + self.PAYLOAD_SLOT_SIZE]
            
            end_index = slot_data.find(b'\x00')
            if end_index != -1:
                payload_str = slot_data[:end_index].decode('utf-8')
                payloads.append(payload_str)
        return payloads

    def clear_memory(self):
        """Formats and clears the RTC memory buffer, preserving the last alarm state."""
        # We only clear the counter, not the whole buffer, to remember the alarm flag
        buffer = self._get_buffer()
        buffer[0:4] = (0).to_bytes(4, 'little')
        # Also clear the payload area for safety
        payloads_area = bytearray(self.TOTAL_BUFFER_SIZE - self.PAYLOAD_START_ADDR)
        buffer[self.PAYLOAD_START_ADDR:] = payloads_area
        self.rtc.memory(buffer)
        utils.log_info("RTC payloads cleared.")

    def should_transmit(self):
        """Checks if it is time to transmit."""
        return self.get_counter() >= self.n_cycles


