# src/modules/max31865_sensor.py
import time
from machine import Pin, SPI
from modules import utils
import json
from lib.adafruit_max31865 import MAX31865
from modules.config_manager import config_manager

class MAX31865Sensor:
    def __init__(self, cs_pin=None, rtd_nominal=None, ref_resistor=None, wires=None, filter_frequency=None, polarity=None, phase=None):
        """
        Initializes the MAX31865 sensor.

        Args:
            cs_pin: The chip select pin.
            rtd_nominal: RTD nominal value.
            ref_resistor: Reference resistance value.
            wires: Number of wires (2, 3, or 4).
            filter_frequency: Filter frequency (50 or 60).
            polarity: SPI Polarity
            phase: SPI phase
        """

        # Use the provided parameters or load from static_config if not provided
        self.cs_pin = cs_pin if cs_pin is not None else config_manager.static_config.get("pinout", {}).get(
            "spi", {}).get("nss_pin", 15)
        self.rtd_nominal = rtd_nominal if rtd_nominal is not None else config_manager.static_config.get("rtd_nominal", 100)
        self.ref_resistor = ref_resistor if ref_resistor is not None else config_manager.static_config.get("ref_resistor", 430.0)
        self.wires = wires if wires is not None else config_manager.static_config.get("wires", 4)
        self.filter_frequency = filter_frequency if filter_frequency is not None else config_manager.static_config.get(
            "filter_frequency", 60)
        self.polarity = polarity if polarity is not None else config_manager.static_config.get("polarity", 0)
        self.phase = phase if phase is not None else config_manager.static_config.get("phase", 1)

        # Initialize SPI bus
        self.spi_bus = self.create_default_spi()

        # Initialize the CS pin as output
        self.cs = Pin(self.cs_pin, Pin.OUT)

        try:
            self.sensor = MAX31865(self.spi_bus, self.cs, rtd_nominal=self.rtd_nominal,
                                   ref_resistor=self.ref_resistor, wires=self.wires,
                                   filter_frequency=self.filter_frequency)
            utils.log_info("MAX31865 sensor initialized successfully.")

        except Exception as e:
            utils.log_error(f"Failed to initialize MAX31865 sensor: {e}")
            self.sensor = None

    def create_default_spi(self):
        """
        Creates a default SPI bus instance based on configuration or defaults.
        """
        sck_pin = config_manager.static_config.get("pinout", {}).get("spi", {}).get("sck_pin", 12)
        mosi_pin = config_manager.static_config.get("pinout", {}).get("spi", {}).get("mosi_pin", 27)
        miso_pin = config_manager.static_config.get("pinout", {}).get("spi", {}).get("miso_pin", 19)

        return SPI(1, baudrate=500000, polarity=self.polarity, phase=self.phase, sck=Pin(sck_pin), mosi=Pin(mosi_pin), miso=Pin(miso_pin))

    def read_temperature(self):
        """
        Reads the temperature from the MAX31865 sensor.

        Returns:
            The temperature in degrees Celsius, or None if an error occurred.
        """

        if self.sensor:
            try:
                temperature = self.sensor.temperature
                utils.log_info(f"Temperature: {temperature:.2f} °C")
                return temperature
            except Exception as e:
                utils.log_error(f"Error reading temperature from MAX31865: {e}")
                return None
        else:
            utils.log_error("MAX31865 sensor not initialized.")
            return None
        
    def read_resistance(self):
        """
        Reads the resistance from the MAX31865 sensor.

        Returns:
            The resistance in Ohms, or None if an error occurred.
        """
        if self.sensor:
            try:
                resistance = self.sensor.resistance
                utils.log_info(f"Resistance: {resistance:.2f} Ohms")
                return resistance
            except Exception as e:
                utils.log_error(f"Error reading resistance from MAX31865: {e}")
                return None
        else:
            utils.log_error("MAX31865 sensor not initialized.")
            return None
        
    def read_faults(self):
        """
        Reads the fault status from the MAX31865 sensor.

        Returns:
            A dictionary containing the fault status, or None if an error occurred.
        """
        if self.sensor:
            try:
                faults = self.sensor.fault
                # Convert the fault tuple to a dictionary with meaningful keys
                fault_dict = {
                    "high_threshold": faults[0],
                    "low_threshold": faults[1],
                    "ref_in_low": faults[2],
                    "ref_in_high": faults[3],
                    "rtd_in_low": faults[4],
                    "over_under_voltage": faults[5]
                }

                utils.log_info(f"Fault status: {fault_dict}")
                return fault_dict
            except Exception as e:
                utils.log_error(f"Error reading fault status from MAX31865: {e}")
                return None
        else:
            utils.log_error("MAX31865 sensor not initialized.")
            return None

