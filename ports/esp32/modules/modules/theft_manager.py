# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from machine import I2C, Pin, wake_reason
from lib.mcp23008 import MCP23008
from lib.LIS2DH12 import lis2dh12
import esp32
import time
import math
from modules import utils
from modules.config_manager import config_manager

class TheftManager:
    """
    Manages security and anti-tamper logic using the LIS2DH12 accelerometer 
    and MCP23008 port expander to trigger ESP32 wakeups.
    """

    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, mcp_addr=0x20, lis2dh_addr=0x18, mcp_int_pin=None):
        """
        Initializes the TheftManager module.

        Args:
            sda_pin: The I2C SDA pin.
            scl_pin: The I2C SCL pin.
            i2c_freq: The I2C frequency.
            mcp_addr: The I2C address of the MCP23008.
            lis2dh_addr: The I2C address of the LIS2DH12.
            mcp_int_pin: RTC GPIO connected to MCP23008 INT.
        """
        # Load configuration from config_manager or use hardcoded defaults
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 21)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 22)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)
        self.lis2dh_addr = lis2dh_addr
        self.mcp_addr = mcp_addr
        self.hardware_ready = False
        
        self.mcp_int_pin_num = mcp_int_pin if mcp_int_pin is not None else config_manager.static_config.get("pinout", {}).get("mcp_int_pin", 34)
        # Initialize I2C bus
        self.i2c = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)
        
        self.devices = self.i2c.scan()
        
        if 0x18 in self.devices and 0x20 in self.devices:

            # Initialize sensor instances
            # start_init=False prevents resetting the MCP registers during a wakeup read
            self.sensor = lis2dh12(self.i2c, int_pin=None, slave_address=self.lis2dh_addr)
            self.mcp = MCP23008(self.i2c, address=self.mcp_addr, start_init=False)
            
            # Internal Detection Thresholds
            self.THRESHOLD_MIN = 0.85
            self.THRESHOLD_MAX = 1.15
            self.SAMPLES_FOR_ALERT = 3
            self.hardware_ready = True
            
            utils.log_info("Compatible hardware for theft manager.")
        
        else:
            
            utils.log_error("Incompatible hardware for theft manager.")
            

    def check_wakeup(self, on_theft_confirmed=None):
        """
        Evaluates the cause of the ESP32 reset and handles security logic.

        Args:
            on_theft_confirmed: Callback function to execute if a real theft is detected.
        """
        if wake_reason() == 3:  # DEEPSLEEP_RESET
            utils.log_info("Waking up from Deep Sleep...")
            
            mcp_int_pin = Pin(self.mcp_int_pin_num, Pin.IN)
            
            if mcp_int_pin.value() == 1:
                utils.log_info("MCP23008 interrupt signal detected.")
                
                # Verify which MCP pin triggered the event
                mcp_flags = self.mcp.interrupt_flag
                _ = self.mcp.interrupt_captured  # Clears MCP internal interrupt
                
                if mcp_flags & (1 << 6):
                    utils.log_warning("Potential tamper on GP6 (Accelerometer).")
                    if self._verify_theft():
                        utils.log_warning("THEFT ALERT CONFIRMED.")
                    else:
                        utils.log_warning("False alarm. Re-arming system...")
                        self.arm()
                else:
                    utils.log_warning("Wakeup from MCP but GP6 flag is clear.")
            
            elif other_int_pin.value() == 0:
                utils.log_info("Wakeup triggered by secondary pin.")
        else:
            utils.log_info("Cold boot or manual reset. Initializing sensors...")
            # Perform full MCP initialization on power-on
            self.mcp = MCP23008(self.i2c, address=self.mcp_addr, start_init=True)
            self.arm()

    def _verify_theft(self):
        """
        Monitors accelerometer data in real-time to filter false positives.

        Returns:
            bool: True if motion exceeds thresholds for the required number of samples.
        """
        utils.log_info("Starting real-time monitoring (10s window)...")
        self.sensor.set_mode(0) # 100Hz / 12-bit
        
        confirmations = 0
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
            x, y, z = self.sensor.read_acceleration
            magnitude = math.sqrt(x**2 + y**2 + z**2)
            
            if magnitude < self.THRESHOLD_MIN or magnitude > self.THRESHOLD_MAX:
                confirmations += 1
                utils.log_warning("(!) Movement: {:.2f}G (Conf: {}/{})".format(
                    magnitude, confirmations, self.SAMPLES_FOR_ALERT))
            else:
                if confirmations > 0: confirmations -= 1

            if confirmations >= self.SAMPLES_FOR_ALERT:
                return True
                
            self.sensor._read_data(0x31, 1) # Clear LIS2DH12 INT1_SRC register
            time.sleep(0.1)
            
        return False

    def arm(self):
        """
        Configures the hardware for low-power surveillance and enters Deep Sleep.
        """
        utils.log_info("Arming Tamper Protection system...")
        
        try:
            # 1. Accelerometer: Shake/Motion detection setup
            self.sensor.sensor_reset()
            self.sensor.configure_interrupts(move=True, click=False, move_ths=0x14)
            
            # 2. MCP23008: Pin 6 as input with interrupt enabled
            self.mcp.pin(6, mode=1, pullup=1, interrupt_enable=1)
            self.mcp.config(interrupt_polarity=1) # Active High for EXT1 compatibility
            
            utils.log_info("System Armed.")
            
        except Exception as e:
            utils.log_error("Critical failure during arming: {}".format(e))
            
    def disarm(self):
        """
        Puts the LIS2DH12 into Power-Down mode (0.5µA) and disables 
        MCP23008 interrupts to achieve minimum power consumption.
        """
        utils.log_info("[SEC] Disarming system and entering Power-Down mode...")
        try:
            # 1. LIS2DH12: Set ODR to 0 to enter Power-Down (IddPdn = 0.5µA)
            self.sensor.set_mode(3)
            
            # 2. MCP23008: Disable interrupt on GP6
            self.mcp.pin(6, mode=1, pullup=1, interrupt_enable=0)
            
            # 3. MCP23008: Force Push-Pull and Active High polarity.
            self.mcp.config(interrupt_polarity=1, interrupt_open_drain=False)
            
            utils.log_info("System disarmed. Hardware in ultra-low power state.")
        except Exception as e:
            utils.log_error("Failed to disarm hardware: {}".format(e))