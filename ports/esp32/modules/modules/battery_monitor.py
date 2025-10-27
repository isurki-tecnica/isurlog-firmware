# src/modules/battery_monitor.py
from machine import ADC, Pin
from modules import utils

class BatteryMonitor:
    """
    Monitors the battery voltage connected to a specified ADC pin on the ESP32.
    """
    def __init__(self, adc_pin=39, attenuation=ADC.ATTN_6DB):
        """
        Initializes the BatteryMonitor.

        Args:
            adc_pin: The ADC pin number connected to the battery voltage divider.  Defaults to 39.
            attenuation: The ADC attenuation.  Defaults to ADC.ATTN_6DB.  Valid values are:
                         ADC.ATTN_0DB (0dB attenuation, 0-1.1V input range)
                         ADC.ATTN_2_5DB (2.5dB attenuation, 0-1.5V input range)
                         ADC.ATTN_6DB (6dB attenuation, 0-2.2V input range)
                         ADC.ATTN_11DB (11dB attenuation, 0-3.9V input range)
        """
        try:
            # ADC pin initialization and attenuation setting
            self.adc = ADC(Pin(adc_pin))
            self.adc.atten(attenuation)  # Set attenuation
            self.adc.width(ADC.WIDTH_11BIT) # 11-bit resolution
            utils.log_info(f"Battery monitor initialized on pin {adc_pin} with {attenuation} attenuation.")

        except Exception as e:
            utils.log_error(f"Failed to initialize BatteryMonitor: {e}")
            self.adc = None #Set adc object to none if fails

    def read_voltage(self):
        """
        Reads and returns the battery voltage.

        Returns:
            The battery voltage in volts, or None if an error occurred.
        """

        if self.adc is None: #If there was an error on initialization.
            utils.log_error("Battery monitor not initialized. Check the pin and attenuation settings.")
            return None

        try:
            adc_value = self.adc.read_uv()  # This method uses the known characteristics of the ADC and per-package eFuse value
            #Voltage Calculation with a 6dB attenuation, 
            #taking in consideration a voltage divider made by 2 resistors 5.9M and 3.6M
            voltage = int(adc_value * (9.5 / 3600) )

            utils.log_info(f"Raw ADC value: {adc_value}, Calculated voltage: {voltage}mV")

            return voltage

        except Exception as e:
            utils.log_error(f"Error reading battery voltage: {e}")
            return None  # Return None on error