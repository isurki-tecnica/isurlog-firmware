# src/modules/config_manager.py
import json
from modules import utils

# Mapa que relaciona el nombre del tipo de configuración LPP con su ruta en el JSON.
# '{channel}' se reemplaza por el índice del canal.
CONFIG_MAP = {
    # General
    'setLatencyTime': ('general', 'latency_time'),
    'setRtcSync': ('general', 'rtc_sync', bool),
    'setRegisterMode': ('general', 'register_mode'),
    'setRegisterAccumulator': ('general', 'register_acumulator'),
    'setMagnetWakeup': ('general', 'magnet_wakeup', bool),
    'setDebugLED': ('general', 'debug_led', bool),
    # LoRaWAN
    'setLoRaWANDevEUI': ('communications', 'lorawan', 'dev_eui', lambda v: f"{v:016X}"),
    'setLoRaWANAppEUI': ('communications', 'lorawan', 'app_eui', lambda v: f"{v:016X}"),
    'setLoRaWANAppKey': ('communications', 'lorawan', 'app_key', lambda v: f"{v:032X}"),
    # NB-IoT
    'setNB_IoTeDRX': ('communications', 'nb_iot', 'edrx', bool),
    # Analog Inputs
    'setAnalogPreAcquisition': ('analog_config', 'pre_acquisition'),
    'setAnalogInputEnable': ('analog_config', 'inputs', '{channel}', 'enable', bool),
    'setAnalogInputZero': ('analog_config', 'inputs', '{channel}', 'zero'),
    'setAnalogInputFullScale': ('analog_config', 'inputs', '{channel}', 'full_scale'),
    'setAnalogInputLow': ('analog_config', 'inputs', '{channel}', 'low'),
    'setAnalogInputHigh': ('analog_config', 'inputs', '{channel}', 'high'),
    'setAnalogInputLowCond': ('analog_config', 'inputs', '{channel}', 'low_cond', bool),
    'setAnalogInputHighCond': ('analog_config', 'inputs', '{channel}', 'high_cond', bool),
    # Digital Inputs
    'setDigitalEnable': ("digital_config", "enable", bool),
    "setDigitalCounter": ("digital_config", "counter", bool),
    "setDigitalPulseWeight": ("digital_config", "pulse_weight"),
    "setDigitalWake": ("digital_config", "wake"),
    "setDigitalLow": ("digital_config", "low"),
    "setDigitalHigh": ("digital_config", "high"),
    "setDigitalLowCond": ("digital_config", "low_cond", bool),
    "setDigitalHighCond": ("digital_config", "high_cond", bool),
    # Modbus Inputs
    'setModbusPreAcquisition': ('modbus_config', 'pre_acquisition'),
    'setModbusInputEnable': ('modbus_config', 'inputs', '{channel}', 'enable', bool),
    'setModbusInputSlaveAddress': ('modbus_config', 'inputs', '{channel}', 'slave_address'),
    'setModbusInputRegisterAddress': ('modbus_config', 'inputs', '{channel}', 'register_address'),
    'setModbusInputFc': ('modbus_config', 'inputs', '{channel}', 'fc'),
    'setModbusInputNumberOfDecimals': ('modbus_config', 'inputs', '{channel}', 'number_of_decimals'),
    'setModbusInputIsFP': ('modbus_config', 'inputs', '{channel}', 'is_FP', bool),
    'setModbusInputInvert': ('modbus_config', 'inputs', '{channel}', 'invert', bool),
    'setModbusInputOffset': ('modbus_config', 'inputs', '{channel}', 'offset'),
    'setModbusInputLow': ('modbus_config', 'inputs', '{channel}', 'low'),
    'setModbusInputHigh': ('modbus_config', 'inputs', '{channel}', 'high'),
    'setModbusInputLowCond': ('modbus_config', 'inputs', '{channel}', 'low_cond', bool),
    'setModbusInputHighCond': ('modbus_config', 'inputs', '{channel}', 'high_cond', bool),
    'setModbusInputLongInt': ('modbus_config', 'inputs', '{channel}', 'long_int', bool),
    # PT100
    'setPT100Enable': ('pt100_config', 'enable', bool),
    'setPT100Wires': ('pt100_config', 'wires'),
    'setPT100Low': ('pt100_config', 'low'),
    'setPT100High': ('pt100_config', 'high'),
    'setPT100LowCond': ('pt100_config', 'low_cond', bool),
    'setPT100HighCond': ('pt100_config', 'high_cond', bool),
    # BME680
    'setBME680Enable': ('BME680_sensor', 'enable', bool),
    'setBME680TemperatureLow': ('BME680_sensor', 'temperature_low'),
    'setBME680TemperatureHigh': ('BME680_sensor', 'temperature_high'),
    'setBME680TemperatureLowCond': ('BME680_sensor', 'temperature_low_cond', bool),
    'setBME680TemperatureHighCond': ('BME680_sensor', 'temperature_high_cond', bool),
    'setBME680HumidityLow': ('BME680_sensor', 'humidity_low'),
    'setBME680HumidityHigh': ('BME680_sensor', 'humidity_high'),
    'setBME680HumidityLowCond': ('BME680_sensor', 'humidity_low_cond', bool),
    'setBME680HumidityHighCond': ('BME680_sensor', 'humidity_high_cond', bool),
    
    # --- ISURNODE CONFIG ---
    # Isurnode General
    'setIsurnodeEnable': ('isurnode_config', 'enable', bool),
    'setIsurnodeSlaveAddress': ('isurnode_config', 'slave_address'),
    # Isurnode Analog
    'setIsurnodeAnalogPreAcquisition': ('isurnode_config', 'analog_config', 'pre_acquisition'),
    'setIsurnodeAnalogTriggerAddress': ('isurnode_config', 'analog_config', 'trigger_address'),
    'setIsurnodeAnalogInputEnable': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'enable', bool),
    'setIsurnodeAnalogInputZero': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'zero'),
    'setIsurnodeAnalogInputFullScale': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'full_scale'),
    'setIsurnodeAnalogInputLow': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'low'),
    'setIsurnodeAnalogInputHigh': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'high'),
    'setIsurnodeAnalogInputLowCond': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'low_cond', bool),
    'setIsurnodeAnalogInputHighCond': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'high_cond', bool),
    'setIsurnodeAnalogInputAddress': ('isurnode_config', 'analog_config', 'inputs', '{channel}', 'address'),
    # Isurnode SHT30
    'setIsurnodeSHT30Enable': ('isurnode_config', 'SHT30_sensor', 'enable', bool),
    'setIsurnodeSHT30TriggerAddress': ('isurnode_config', 'SHT30_sensor', 'trigger_address'),
    'setIsurnodeSHT30Address': ('isurnode_config', 'SHT30_sensor', 'address'),
    'setIsurnodeSHT30TempLow': ('isurnode_config', 'SHT30_sensor', 'temperature_low'),
    'setIsurnodeSHT30TempHigh': ('isurnode_config', 'SHT30_sensor', 'temperature_high'),
    'setIsurnodeSHT30TempLowCond': ('isurnode_config', 'SHT30_sensor', 'temperature_low_cond', bool),
    'setIsurnodeSHT30TempHighCond': ('isurnode_config', 'SHT30_sensor', 'temperature_high_cond', bool),
    'setIsurnodeSHT30HumLow': ('isurnode_config', 'SHT30_sensor', 'humidity_low'),
    'setIsurnodeSHT30HumHigh': ('isurnode_config', 'SHT30_sensor', 'humidity_high'),
    'setIsurnodeSHT30HumLowCond': ('isurnode_config', 'SHT30_sensor', 'humidity_low_cond', bool),
    'setIsurnodeSHT30HumHighCond': ('isurnode_config', 'SHT30_sensor', 'humidity_high_cond', bool),
    # Isurnode Digital Outputs
    'setIsurnodeDigitalOutputEnable': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'enable', bool),
    'setIsurnodeDigitalOutputType': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'type'),
    'setIsurnodeDigitalOutputAddress': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'address'),
    'setIsurnodeDigitalOutputLogicOp': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'logic_operator'),
    'setIsurnodeDigitalOutputRetry': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'retry'),
    'setIsurnodeDigitalOutputRetrySleep': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'retry_sleep'),
    'setIsurnodeDigitalOutputOnTime': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'on_time'),
    # Isurnode Digital Outputs -> Condition 1
    'setIsurnodeDigOutCond1Sensor': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 0, 'sensor'),
    'setIsurnodeDigOutCond1Low': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 0, 'low'),
    'setIsurnodeDigOutCond1High': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 0, 'high'),
    'setIsurnodeDigOutCond1LowCond': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 0, 'low_cond', bool),
    'setIsurnodeDigOutCond1HighCond': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 0, 'high_cond', bool),
    # Isurnode Digital Outputs -> Condition 2
    'setIsurnodeDigOutCond2Sensor': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 1, 'sensor'),
    'setIsurnodeDigOutCond2Low': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 1, 'low'),
    'setIsurnodeDigOutCond2High': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 1, 'high'),
    'setIsurnodeDigOutCond2LowCond': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 1, 'low_cond', bool),
    'setIsurnodeDigOutCond2HighCond': ('isurnode_config', 'digital_outputs', 'outputs', '{channel}', 'conditions', 1, 'high_cond', bool),
}

class ConfigManager:
    """
    Manages configuration settings from static and dynamic JSON files.
    Provides methods for accessing and updating configuration values.
    """
    def __init__(self, static_config_path="config/static_config.json", dynamic_config_path="config/dynamic_config.json"):
        self.static_config = self._load_config(static_config_path)
        self.dynamic_config = self._load_config(dynamic_config_path)
        self.dynamic_config_path = dynamic_config_path

    def _load_config(self, config_path):
        """Loads configuration from a JSON file."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (OSError, ValueError) as e: # ValueError for JSONDecodeError in MicroPython
            utils.log_error(f"Error loading configuration from {config_path}: {e}")
            return {}

    def get_static(self, *keys, default=None):
        """Retrieves a value from the static configuration."""
        return self._get_config_value(self.static_config, *keys, default=default)

    def get_dynamic(self, *keys, default=None):
        """Retrieves a value from the dynamic configuration."""
        return self._get_config_value(self.dynamic_config, *keys, default=default)

    def _get_config_value(self, config_dict, *keys, default=None):
        """Helper function to traverse the configuration dictionary."""
        value = config_dict
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _set_nested_value(self, config, path, value, channel):
        """
        Navigates a nested dictionary and list structure to set a value.
        """
        current_level = config
        for i, key in enumerate(path):
            # Substitute {channel} placeholder with the actual channel index
            if key == '{channel}':
                key = channel
            
            # If we are at the last key, set the value
            if i == len(path) - 1:
                if isinstance(current_level, dict):
                    current_level[key] = value
                elif isinstance(current_level, list) and isinstance(key, int) and 0 <= key < len(current_level):
                    current_level[key] = value # This case is less common for the last element
                else:
                    utils.log_error(f"Invalid path: cannot set value at key '{key}'")
                    return False
            else:
                # Navigate deeper
                if isinstance(current_level, dict):
                    current_level = current_level.setdefault(key, {})
                elif isinstance(current_level, list) and isinstance(key, int) and 0 <= key < len(current_level):
                    current_level = current_level[key]
                else:
                    utils.log_error(f"Invalid path or index: key '{key}' not found or out of bounds.")
                    return False
        return True

    def apply_single_update(self, channel, config_type, value):
        """
        Applies a single configuration update using the CONFIG_MAP.
        """
        if config_type not in CONFIG_MAP:
            utils.log_error(f"Unknown config type: {config_type}")
            return None

        path_info = CONFIG_MAP[config_type]
        
        # Check if there is a type converter at the end of the tuple
        converter = None
        if callable(path_info[-1]):
            converter = path_info[-1]
            path = path_info[:-1]
        else:
            path = path_info

        # Apply the converter to the value if it exists
        final_value = converter(value) if converter else value

        # Use a copy to avoid modifying the config directly before success
        # Note: deepcopy is not standard in MicroPython, so we serialize/deserialize
        config_copy = json.loads(json.dumps(self.dynamic_config))

        if self._set_nested_value(config_copy, path, final_value, channel):
            return config_copy
        else:
            utils.log_error(f"Failed to apply update for {config_type}")
            return None

    def apply_conf_update(self, decoded_data):
        """
        Applies a full configuration update from decoded LPP data.
        """
        temp_config = self.dynamic_config
        
        for entry in decoded_data:
            utils.log_info(f"Applying entry: {entry}")
            
            # Apply update to the temporary config object
            updated_config = self.apply_single_update(entry['channel'], entry['name'], entry['value'])
            
            if updated_config is None:
                utils.log_error(f"Failed to apply decoded data to config: {entry}")
                # Optional: Decide if you want to stop on first error or continue
                # return # Stop on first error
                continue # Continue with next entry
            
            # Update the main dynamic config with the successful change
            self.dynamic_config = updated_config
            utils.log_info(f"Configuration updated successfully for {entry['name']}")
            
        # Save the final configuration only once after all updates are applied
        utils.log_info(f"Final dynamic config to be saved: {self.get_dynamic()}")
        self.save_dynamic_config()

    def save_dynamic_config(self):
        """Saves the current dynamic configuration to its file."""
        try:
            with open(self.dynamic_config_path, "w") as f:
                json.dump(self.dynamic_config, f) # Use indent for readability
            utils.log_info(f"Dynamic configuration saved to {self.dynamic_config_path}")
        except OSError as e:
            utils.log_error(f"Error saving dynamic configuration to {self.dynamic_config_path}: {e}")

# Create a single, global instance of the ConfigManager
config_manager = ConfigManager()