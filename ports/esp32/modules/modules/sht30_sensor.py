# src/modules/sht30_sensor.py
from machine import I2C, Pin
from modules import utils
from lib.SHT30 import SHT30, SHT30Error
import time
from modules.config_manager import config_manager

class SHT30Sensor:
    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, address=0x44):
        """
        Initializes the SHT30 sensor wrapper.

        Args:
            i2c_bus: An already initialized I2C bus object. If None, it will be created.
            address: The I2C address of the sensor (default: 0x44).
        """
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 18)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 19)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)
        
        self.i2c_bus = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)
        self.sensor = None

        try:

            # Initialize the low-level SHT30 driver
            self.sensor = SHT30(i2c_addr=address, i2c_device=self.i2c_bus)

            # Check if the sensor is present on the bus
            if self.sensor.is_present():
                utils.log_info("SHT30 sensor initialized successfully.")
            else:
                utils.log_error("SHT30 sensor not found on the I2C bus.")
                self.sensor = None

        except Exception as e:
            utils.log_error(f"Failed to initialize SHT30 sensor: {e}")
            self.sensor = None
    
    def read_data(self):
        """
        Reads the sensor data (temperature and humidity).

        Returns:
            A dictionary containing the sensor data, or None if an error occurred.
        
        Example Usage:
        
        sht_sensor = SHT30Sensor() # Assumes I2C bus is configured in config.json
        for _ in range(10):
            sht_data = sht_sensor.read_data()
            if sht_data:
                utils.log_info(f"Temperature: {sht_data['temperature']:.2f} C")
                utils.log_info(f"Humidity: {sht_data['humidity']:.2f} %RH")
            else:
                utils.log_error("Failed to read SHT30 sensor data.")
            time.sleep(2)
        """
        if self.sensor:
            try:
                # The measure() method from the low-level library returns a tuple
                temperature, humidity = self.sensor.measure()
                
                data = {
                    "temperature": temperature,
                    "humidity": humidity,
                }
                return data
            
            except SHT30Error as e:
                # Handle specific errors from the low-level library
                utils.log_error(f"SHT30 sensor error: {e}")
                return None
            except Exception as e:
                # Handle other potential errors (e.g., general OSError)
                utils.log_error(f"Error reading SHT30 sensor data: {e}")
                return None
        else:
            utils.log_error("SHT30 sensor not initialized.")
            return None
