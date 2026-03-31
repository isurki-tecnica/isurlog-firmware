# src/modules/analog.py
# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from machine import I2C, Pin
from modules.config_manager import config_manager

class MCP4017:
    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, address=0x2F, r_total=50000):
        """
        Initialize the MCP4017.
        r_total: Total resistance of the device (e.g., 5000, 10000, 50000, 100000)
        """
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 21)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 22)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)
        
        self.i2c = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)
        self.address = address
        self.r_total = r_total
        self.r_wiper = 75  # Typical wiper resistance in ohms
        
    def exists(self):
        """
        Checks if the MCP4017 is connected to the I2C bus.
        Returns True if found, False otherwise.
        """
        try:
            # Try to read 1 byte from the device address (0x2F)
            self.i2c.readfrom(self.address, 1)
            return True
        except OSError:
            # If the device does not respond (NACK), an OSError is raised
            return False

    def set_step(self, step):
        """
        Sets the wiper position (0 to 127).
        """
        if not 0 <= step <= 127:
            raise ValueError("Step must be between 0 and 127")
        
        # The MCP4017 expects a single data byte to set the wiper
        self.i2c.writeto(self.address, bytes([step]))

    def set_resistance(self, ohms):
        """
        Sets the resistance (Wiper to B terminal).
        Formula: Rwb = (Rab * step / 127) + Rw
        """
        if ohms < self.r_wiper:
            step = 0
        elif ohms >= self.r_total + self.r_wiper:
            step = 127
        else:
            step = int(((ohms - self.r_wiper) * 127) / self.r_total)
        
        self.set_step(step)

    def read_step(self):
        """
        Reads the current wiper position.
        """
        return self.i2c.readfrom(self.address, 1)[0]
    
    def set_mt3608_voltage(self, target_voltage):
        """
        Adjusts the MCP4017 to set the MT3608 output voltage.
        R1 = 1100k (fixed upper resistor)
        R2 = R_pot + 28k (potentiometer + fixed series resistor)
        """
        v_ref = 0.6  # MT3608 internal feedback reference voltage
        r1 = 1100000 # 1100k ohms
        r2_fixed_series = 28000 # 28k ohms
        
        # Security check: MT3608 cannot output less than its reference (0.6V)
        # or less than the input voltage (V_IN)
        if target_voltage <= v_ref:
            self.set_step(127) # Max resistance = Minimum possible voltage
            return

        # 1. Calculate the total R2 required for the target voltage
        # Formula: R2 = R1 / ((Vout / Vref) - 1)
        r2_total_required = r1 / ((target_voltage / v_ref) - 1)
        
        # 2. Subtract the 28k fixed resistor to find the required R_pot
        r_pot_required = r2_total_required - r2_fixed_series
        
        # 3. Set the digital pot step
        # The set_resistance method already accounts for the 128 steps (0-127)
        self.set_resistance(r_pot_required)