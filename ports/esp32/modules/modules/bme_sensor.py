# src/modules/bme680_sensor.py
from machine import I2C, Pin
from modules import utils
from lib.pimoroni_bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS, SLEEP_MODE
import json
import time
from modules.config_manager import config_manager
from lib.bme280_float import BME280


def BME_CHIP_ID(sda_pin=None, scl_pin=None, i2c_freq=None, address=0x76):
    
    """
    Function to get CHIP_ID of the BME sensor. CHIP_ID is 0x58 (88) for BME280 and 0x61 (97) for BME680
    """
    
    sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 18)
    scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 19)
    i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)
    
    i2c_bus = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=i2c_freq)
    result = bytearray(1)
    i2c_bus.readfrom_mem_into(address, 0xd0, result)
    
    return result[0]

class BME280Sensor:
    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, address=0x76):
        """
        Initializes the BME680 sensor.

        Args:
            sda_pin: The SDA pin for the I2C bus.
            scl_pin: The SCL pin for the I2C bus.
            i2c_freq: The frequency for the I2C bus.
            address: The I2C address of the sensor (default: 0x76).
        """
        
        # I2C configuration from config.json, or use defaults
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 18)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 19)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)

        # Initialize I2C bus
        self.i2c_bus = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)
        
        try:
            self.sensor = BME280(i2c=self.i2c_bus)
            utils.log_info("BME280 sensor initialized successfully.")
            
        except Exception as e:
            utils.log_error(f"Failed to initialize BME280 sensor: {e}")
            self.sensor = None
            
    def read_data(self):
        """
        Reads the sensor data (temperature, pressure, humidity, gas resistance).

        Returns:
            A dictionary containing the sensor data, or None if an error occurred or if data is not ready."""

        if self.sensor:
            try:
                sensor_data = self.sensor.read_compensated_data()
                
                data = {
                    "temperature": sensor_data[0],
                    "pressure": sensor_data[1]/100,
                    "humidity": sensor_data[2],
                }

                return data
            
            except Exception as e:
                utils.log_error(f"Error reading BME280 sensor data: {e}")
                return None
        else:
            utils.log_error("BME280 sensor not initialized.")
            return None
        
            
class BME680Sensor:
    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, address=0x76, IAQ=False):
        """
        Initializes the BME680 sensor.

        Args:
            sda_pin: The SDA pin for the I2C bus.
            scl_pin: The SCL pin for the I2C bus.
            i2c_freq: The frequency for the I2C bus.
            address: The I2C address of the sensor (default: 0x76).
            IAQ: Boolean to determine if gas resistance measurement (IAQ calculation) should be enabled.
        """

        # I2C configuration from config.json, or use defaults
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 18)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 19)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)
        self.IAQ = IAQ
        self.burn_in_data = []
        self.burn_in_time = 300  # Burn-in time in seconds
        self.gas_baseline = None
        self.hum_baseline = 40.0
        self.hum_weighting = 0.25

        # Initialize I2C bus
        self.i2c_bus = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)

        try:
            self.sensor = BME680(i2c_addr=address, i2c_device=self.i2c_bus)

            # Set up the over sampling and filters
            self.sensor.set_humidity_oversample(OS_2X)
            self.sensor.set_pressure_oversample(OS_4X)
            self.sensor.set_temperature_oversample(OS_8X)
            self.sensor.set_filter(FILTER_SIZE_3)

            # Configure the gas sensor if IAQ is enabled
            if self.IAQ:
                self.sensor.set_gas_status(ENABLE_GAS_MEAS)
                self.sensor.set_gas_heater_temperature(320)
                self.sensor.set_gas_heater_duration(150)
                self.sensor.select_gas_heater_profile(0)
            else:
                self.sensor.set_gas_status(0) # Disable gas sensor

            utils.log_info("BME680 sensor initialized successfully.")
        except Exception as e:
            utils.log_error(f"Failed to initialize BME680 sensor: {e}")
            self.sensor = None

    def _burn_in(self):
        """Performs the burn-in process for the gas sensor."""
        utils.log_info("Collecting gas resistance burn-in data for 5 minutes...")
        start_time = time.time()
        curr_time = time.time()
        burn_in_data = []

        while curr_time - start_time < self.burn_in_time:
            curr_time = time.time()
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance
                burn_in_data.append(gas)
                utils.log_info(f"Burn-in - Gas resistance: {gas} Ohms")
                time.sleep(1)

        self.gas_baseline = sum(burn_in_data[-50:]) / 50.0
        utils.log_info(f"Gas baseline: {self.gas_baseline} Ohms, humidity baseline: {self.hum_baseline} %RH")

    def calculate_iaq(self, gas, hum):
        """
        Calculates the IAQ score based on gas resistance and humidity.

        Args:
            gas: The gas resistance in Ohms.
            hum: The relative humidity in %RH.

        Returns:
            The IAQ score (0-100).
        """
        gas_offset = self.gas_baseline - gas
        hum_offset = hum - self.hum_baseline

        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = (100 - self.hum_baseline - hum_offset)
            hum_score /= (100 - self.hum_baseline)
            hum_score *= (self.hum_weighting * 100)
        else:
            hum_score = (self.hum_baseline + hum_offset)
            hum_score /= self.hum_baseline
            hum_score *= (self.hum_weighting * 100)

        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = (gas / self.gas_baseline)
            gas_score *= (100 - (self.hum_weighting * 100))
        else:
            gas_score = 100 - (self.hum_weighting * 100)

        # Calculate air_quality_score.
        iaq_score = hum_score + gas_score
        return iaq_score

    def read_data(self):
        """
        Reads the sensor data (temperature, pressure, humidity, gas resistance).

        If IAQ is enabled, it performs a burn-in if necessary and calculates the IAQ score.

        Returns:
            A dictionary containing the sensor data, or None if an error occurred or if data is not ready.

        Example for IAQ:

        for _ in range(10):
            bme_data = bme_sensor.read_data()
            if bme_data:
                utils.log_info(f"Temperature: {bme_data['temperature']:.2f} °C")
                utils.log_info(f"Pressure: {bme_data['pressure']:.2f} hPa")
                utils.log_info(f"Humidity: {bme_data['humidity']:.2f} %RH")

                if "gas_resistance" in bme_data:
                    utils.log_info(f"Gas Resistance: {bme_data['gas_resistance']:.2f} ohms")
                if "iaq_score" in bme_data:
                    utils.log_info(f"IAQ Score: {bme_data['iaq_score']:.2f}")
            else:
                utils.log_error("Failed to read BME680 sensor data.")

            time.sleep(5)

        Example for normal readings:

        """
        if self.sensor:
            try:
                # Perform burn-in if IAQ is enabled and gas baseline is not set
                if self.IAQ and self.gas_baseline is None:
                    self._burn_in()

                if self.sensor.get_sensor_data():
                    temperature = self.sensor.data.temperature
                    pressure = self.sensor.data.pressure
                    humidity = self.sensor.data.humidity

                    data = {
                        "temperature": temperature,
                        "pressure": pressure,
                        "humidity": humidity,
                    }

                    # Calculate IAQ if enabled and heater is stable
                    if self.IAQ and self.sensor.data.heat_stable:
                        gas_resistance = self.sensor.data.gas_resistance
                        iaq_score = self.calculate_iaq(gas_resistance, humidity)
                        data["gas_resistance"] = gas_resistance
                        data["iaq_score"] = iaq_score

                    # Put sensor in sleep mode. BORRAR ESTA LINEA, PRUEBA CONSUMOS
                    self.sensor.set_power_mode(SLEEP_MODE)

                    return data
                else:
                    return None
            except Exception as e:
                utils.log_error(f"Error reading BME680 sensor data: {e}")
                return None
        else:
            utils.log_error("BME680 sensor not initialized.")
            return None