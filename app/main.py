import time
from machine import Pin, reset, WDT, UART, deepsleep, I2C
from modules.power_manager import pm
from modules import utils
from modules.config_manager import config_manager
from modules import downlink_manager
from lib.IsurlogLPP import IsurlogLPPEncoder
from modules.rtc_memory import RTC_Memory
from modules.eeprom_memory import EEPROM_Memory
from modules.led_manager import LEDManagerULP
from lib.ota import rollback
from lib.mcp4017 import MCP4017
from modules.accel_manager import Accelerometer
from lib.mcp23008 import MCP23008
from modules.version import VERSION
import os
import asyncio


# --- GLOBALS & COOPERATIVE SYNCHRONIZATION ---
connection_ok = asyncio.Event()  # Informational flag: there is an active connection right now
telemetry_idle = asyncio.Event()      # Set when there is no telemetry in progress (allows sleeping)
read_sensor_idle = asyncio.Event()
# --- Flag shared between the hard IRQ and the asyncio task ---
telemetry_trigger = asyncio.ThreadSafeFlag()
telemetry_idle.set()
nb_iot_module = None # Shared modem instance (UART-safe)
mqtt_client = None  # Shared MQTT instance
lorawan_module = None  # Shared LoRaWAN modem instance
rtc_memory = None
eeprom_memory = None
mcp = None  # shared MCP23008 instance (GP6/7: accelerometer interrupts, GP3/4/5: digital inputs), created once at boot
mcp_digital_input = None  # DigitalInputMCP23008 wrapping the shared mcp, set at boot if hardware is present
modem_type = None  # Set once in __main__ from static_config (doesn't change at runtime)
battery_voltage = None
modem_lock = asyncio.Lock()           # Serializes ALL modem access between concurrent tasks
encoder = IsurlogLPPEncoder()
wake_up_sources = []
AUTH_FILE = 'auth'

#Enable WDT

try:
    wdt = WDT(timeout=600000)
    wdt.feed() # Feed at boot
    print("Watchdog Timer enabled to 10 minutes.")
except Exception as e:
    print(f"Could not enable Watchdog Timer: {e}")
    wdt = None
    

def init_lorawan_module():
    """
    Centralized, single-point initialization of the LoRaWAN modem driver.
    Called both at startup (main) and defensively from any function that
    uses nb_iot_module, so as not to depend on an implicit call order.
    """
    global lorawan_module
    if lorawan_module is None:
        from modules import lorawan
        rx = Pin(4, hold=False)
        tx = Pin(2, hold=False)
        lorawan_module = lorawan.LoRaWAN(uart_id=2, tx_pin=2, rx_pin=4, baudrate=115200)
 
        # Class C devices can receive downlinks at any time; add the same
        # wake pin NB-IoT uses for eDRX, so an incoming Class C downlink can
        # wake the ESP32 from deepsleep too.
        lorawan_config = config_manager.dynamic_config["communications"].get("lorawan", {})
        if lorawan_config.get("class", 0) == 2:
            wake_up_pin = config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("esp_wake_up", 35)
            if wake_up_pin not in wake_up_sources:
                wake_up_sources.append(wake_up_pin)

def init_nb_iot_module():
    """
    Centralized, single-point initialization of the LoRaWAN modem driver,
    mirroring init_nb_iot_module(). en_com_module (created unconditionally
    in __main__) already handles the shared enable pin, so nothing extra
    is needed for that here.
    """
    global nb_iot_module
    if nb_iot_module is None:
        from modules import nb_iot
        rx = Pin(2, hold=False)
        tx = Pin(4, hold=False)
        nb_iot_module = nb_iot.NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)

        #Add wake-up source for eDRX.
        wake_up_pin = config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("esp_wake_up", 35)
        if wake_up_pin not in wake_up_sources:
            wake_up_sources.append(wake_up_pin)

def init_mqtt_client():
    """
    Centralized, single-point initialization of the WiFi MQTT client object,
    mirroring init_nb_iot_module(). Just creates the object if it doesn't
    exist yet -- actually connecting/subscribing still happens in
    establish_network_connection(), same as nb_iot_module.connect() does.
    """
    global mqtt_client
    if mqtt_client is None:
        from modules.umqttsimple import MQTTClient
        mqtt_config, _ = get_mqtt_settings()
        mqtt_client = MQTTClient(ser_num, mqtt_config.get("ip", ""), user=mqtt_config.get("user", ""), password=mqtt_config.get("passwd", ""), ssl=True)

def init_rtc_memory():
    """
    Centralized, single-point initialization of rtc_memory, mirroring
    init_nb_iot_module(). Any function that needs rtc_memory can call this
    defensively first instead of assuming it was already created elsewhere.
    """
    global rtc_memory
    if rtc_memory is None:
        rtc_memory = RTC_Memory(max_payload_size=config_manager.dynamic_config["general"].get("max_payload_size", 256))


def init_eeprom_memory():
    """
    Centralized, single-point initialization of eeprom_memory, mirroring
    init_rtc_memory(). Kept as a fully independent object: rtc_memory and
    eeprom_memory are same-level modules that don't call each other, so
    all the RTC-vs-EEPROM routing lives in the helper functions below.
    """
    global eeprom_memory
    if eeprom_memory is None:
        eeprom_memory = EEPROM_Memory(max_payload_size=config_manager.dynamic_config["general"].get("max_payload_size", 256))
        
def get_accumulator_target():
    """
    Configured accumulator size, read fresh every time (like get_mqtt_settings())
    since it can change at runtime via a config downlink.
    """
    return config_manager.dynamic_config["general"].get("register_acumulator", 5)

def _migrate_rtc_to_eeprom():
    """
    Moves everything currently queued in RTC RAM to EEPROM in one shot,
    then empties RTC RAM completely. Called when RTC RAM is full - normally
    only because of a connectivity outage lasting longer than the
    configured accumulator, since in the healthy case a transmission
    clears RTC well before it physically fills up. Frees the whole RTC
    buffer for new payloads to keep landing there (fast, no wear), while
    the already-accumulated backlog is safe in EEPROM until a transmission
    finally succeeds and drains both (see get_all_pending_payloads()).
    """
    pending = rtc_memory.get_payloads()
    migrated = 0
    for p in pending:
        if eeprom_memory.store_payload(p):
            migrated += 1
        else:
            utils.log_error("Failed to migrate an RTC payload to EEPROM, it will be lost")
    rtc_memory.clear_memory()
    utils.log_warning(f"RTC memory was full (connectivity outage?); migrated {migrated}/{len(pending)} payload(s) to EEPROM.")

def store_payload_in_queue(payload):
    """
    Stores a payload in RTC RAM or EEPROM depending on the configured
    accumulator size versus RTC RAM's physical capacity
    (rtc_memory.max_possible_payloads). If the accumulator is small enough
    to fit in RTC RAM but RTC RAM is currently full (connectivity outage),
    migrates the existing backlog to EEPROM first to free it up.
    :return: True if stored, False otherwise
    """
    if get_accumulator_target() > rtc_memory.max_possible_payloads:
        # Accumulator larger than RTC RAM can ever hold: never let
        # unconfirmed data sit only in volatile RTC memory (wiped by a
        # real power loss/brownout, unlike deep sleep). Store straight
        # to EEPROM from the very first cycle.
        return eeprom_memory.store_payload(payload)

    if rtc_memory.store_payload(payload):
        return True

    # RTC RAM full - only expected from a connectivity outage lasting
    # longer than the configured accumulator. Free it up in one shot.
    _migrate_rtc_to_eeprom()
    return rtc_memory.store_payload(payload)

def get_pending_payload_count():
    """Total payloads currently pending across both backends."""
    return eeprom_memory.get_pending_count() + rtc_memory.get_counter()

def payload_queue_should_transmit():
    """
    True once the configured accumulator has been reached, counting
    pending payloads across both RTC RAM and EEPROM - a payload doesn't
    stop counting towards the accumulator just because it was migrated to
    EEPROM during an outage.
    """
    # -1 because when this runs, the current cycle's payload is still
    # pending to be stored (mirrors the original rtc_memory.should_transmit()).
    return get_pending_payload_count() >= get_accumulator_target() - 1

def get_all_pending_payloads():
    """All pending payloads, oldest first: EEPROM backlog, then RTC RAM."""
    return eeprom_memory.get_payloads(max_count=None) + rtc_memory.get_payloads()

def remove_confirmed_payloads(n):
    """
    Removes exactly the first n payloads (oldest first) from the combined
    queue - EEPROM's backlog first, then RTC RAM - leaving anything after
    that untouched so it gets retried next cycle.

    Use this after transmitting, with n = however many publish_payload()
    calls actually returned True. Never clear the whole queue before a
    transmission is confirmed: if the connection drops mid-batch, whatever
    hasn't been removed yet stays queued instead of being lost.
    """
    if n <= 0:
        return

    eeprom_count = eeprom_memory.get_pending_count()
    eeprom_remove = min(n, eeprom_count)
    if eeprom_remove:
        eeprom_memory.remove_confirmed(eeprom_remove)

    rtc_remove = n - eeprom_remove
    if rtc_remove:
        # RTC_Memory has no native "remove first n" (it's a plain growing
        # array of slots, not a circular FIFO like EEPROM's). Simulated
        # here with existing calls only - no changes to rtc_memory.py -
        # since RTC RAM has no wear concern, a full rewrite is fine.
        remaining = rtc_memory.get_payloads()[rtc_remove:]
        rtc_memory.clear_memory()
        for p in remaining:
            rtc_memory.store_payload(p)

def clear_payload_queues():
    """
    Unconditionally wipes both backends, discarding anything pending.
    NOT for use after a transmission attempt - a partial failure would
    lose whatever wasn't actually sent. Use remove_confirmed_payloads()
    for that. This is only for an intentional full reset (e.g. a manual
    "clear queue" action).
    """
    eeprom_memory.clear_memory()
    rtc_memory.clear_memory()

def get_mqtt_settings():
    """
    Returns (mqtt_config, base_topic). Looked up fresh on every call (unlike
    modem_type) since dynamic_config can change at runtime via a config
    downlink.
    """
    mqtt_config = config_manager.get_dynamic("communications").get("mqtt")
    base_topic = mqtt_config.get("base_topic", "isurlog")
    return mqtt_config, base_topic

def should_resync_rtc():
    """
    True if the RTC should be resynced: it lost power, or it's been more
    than 'rtc_sync_int' hours since the last sync (crystal drift correction).
    """
    if pm.rtc_lost_power:
        return True
    interval_h = config_manager.dynamic_config["general"].get("rtc_sync_int", 7)*24
    if interval_h == 0:
        return False
    return rtc_memory.rtc_resync_due(pm.rtc.get_unix_time(), interval_h * 3600)

async def read_all_sensors(upload_mode, ble = False, n_loop = 1, n_seconds = 10, isurnode_enabled = False):
    
    global battery_voltage
        
    data = [[0, "addUnixTime", pm.rtc.get_unix_time()]]
    alarm_condition = False

    # Pre-check of activated sensors
    modbus_config = config_manager.get_dynamic("modbus_config")
    analog_config = config_manager.get_dynamic("analog_config")
    pt100_config = config_manager.get_dynamic("pt100_config")
    output_config = config_manager.get_dynamic("output_config")
    battery_config = config_manager.get_dynamic("battery_config")
    accel_config = config_manager.get_dynamic("accelerometer_config")
    
    num_modbus_enabled = sum(ch.get("enable", False) for ch in modbus_config.get("inputs", [])) if modbus_config else 0
    num_analog_enabled = sum(ch.get("enable", False) for ch in analog_config.get("inputs", [])) if analog_config else 0
    pt100_enabled = pt100_config and pt100_config.get("enable", False)

    # Battery measurement
    
    from lib.max1704x import max1704x
    max17048_sensor = max1704x()
    
    if max17048_sensor.sensor_exists():
        
        soc = max17048_sensor.getSoc()
        crate = max17048_sensor.getCrate()
        battery_voltage = max17048_sensor.getVCell()
        
        if crate is not None and battery_config.get("crate", False):
            utils.log_info(f"Charge rate: {crate}%/h")
            data.append([0, "addCRateInput", crate])
        else:
            utils.log_error("Error reading charge rate or charge rate is disabled.")
            
        if soc is not None and battery_config.get("soc", False):
            utils.log_info(f"State of charge: {soc}%")
            data.append([0, "addSoCInput", soc])
        else:
            utils.log_error("Error reading state of charge or state of charge is disabled.")

    else:
    
        from modules import battery_monitor
        batt_monitor = battery_monitor.BatteryMonitor()
        battery_voltage = batt_monitor.read_voltage()
        Pin(39, Pin.IN, Pin.PULL_UP, hold=False)

    if battery_voltage is not None:
        utils.log_info(f"Battery Voltage: {battery_voltage}mV")
        data.append([0, "addVoltageInput", battery_voltage])
    else:
        utils.log_error("Error reading battery voltage.")
        
    # LIS2DH12 measurement
    
    if accel_config and accel_config.get("enable", False):
        
        accel = Accelerometer(mcp)
        if accel.hardware_ready:
            accel_values  = list(accel.sensor.read_acceleration)
            utils.log_info(f"Accelerometer acceleration: x: {accel_values[0]}g, y: {accel_values[1]}g, z: {accel_values[2]}g")
            data.append([0, "addAccelerometer", accel_values[0], accel_values[1], accel_values[2]])
            
            #Check alarms for every axis acceleration
            for axis_config in accel_config["axles"]:
                
                channel = axis_config.get("channel")
                #Check alarms axis acceleration
                if (upload_mode and (axis_config.get("low_cond", False)) and (accel_values[channel] < axis_config.get("low", 0))):
                    alarm_condition = True
                if (upload_mode and (axis_config.get("high_cond", False)) and (accel_values[channel] > axis_config.get("high", 0))):
                    alarm_condition = True

    reg_on_t = time.time()
    
    if not ble:
            
        if num_modbus_enabled > 0 or num_analog_enabled > 0 or pt100_enabled:
            pm.control_vdc(1)
            await asyncio.sleep_ms(250)
            
        if num_modbus_enabled > 0 or pt100_enabled:
            pm.control_5v(1)
            
        if output_config.get("active_vdc", False):
            pm.control_digital_output(1)
        
    # Digital inputs - channel 0 is the native ESP32 pin (counter via ULP,
    # or plain state); channels 3/4/5 are GP3/GP4/GP5 on the MCP23008
    # (state only - no coprocessor there to count pulses in the background).
    digital_config = config_manager.get_dynamic("digital_config")
        
    if digital_config:
        from modules.digital_sensor import DigitalInputULP

        # Back-compat: devices still on the old flat schema (no "inputs"
        # list, just enable/counter/low/high at the top level) get wrapped
        # as a single channel-0 entry, so old and new config pushes both work.
        digital_inputs = digital_config.get("inputs")
        if digital_inputs is None:
            legacy_input = dict(digital_config)
            legacy_input["channel"] = 0
            legacy_input.setdefault("counter", True)  # matches the old flat schema's default
            digital_inputs = [legacy_input]

        for input_cfg in digital_inputs:
            if not input_cfg.get("enable", False):
                continue

            channel = input_cfg.get("channel")

            if channel == 0:
                #Digital input pulse counter mode
                if input_cfg.get("counter", False):
                    ulp_digital_input = DigitalInputULP()
                    if not ulp_digital_input.ulp_loaded(): #Init ULP coprocessor only if the magic token is not set
                        ulp_digital_input.load_ulp()
                    value = ulp_digital_input.get_pulse_count()
                    weighted_value = value * input_cfg.get("pulse_weight", 1)
                #Digital input state mode
                else:
                    digital_input = Pin(DIO0_PIN, Pin.IN)
                    value = digital_input.value()
                    weighted_value = value
                    if value == 0 and DIO0_PIN not in wake_up_sources:
                        wake_up_sources.append(DIO0_PIN)

            elif channel in (1, 2, 3):
                #MCP23008 expander input (state only), configured once at boot
                if mcp_digital_input is not None:
                    gp_num = int(channel) + 2
                    value = mcp_digital_input.read(gp_num)
                    weighted_value = value
                else:
                    utils.log_warning(f"Digital input channel {channel} configured but MCP23008/accelerometer hardware not detected - skipping.")
                    continue

            else:
                utils.log_error(f"Unknown digital input channel {channel} in configuration - skipping.")
                continue

            data.append([channel, "addDigitalInput", value])

            #Check alarms
            if (upload_mode and input_cfg.get("low_cond", False) and weighted_value < input_cfg.get("low", 0)):
                alarm_condition = True
            if (upload_mode and input_cfg.get("high_cond", False) and weighted_value > input_cfg.get("high", 0)):
                alarm_condition = True
                
    # Internal temperature and humidity sensor (BME680 or SHT30)
    int_th_config = config_manager.get_dynamic("int_th_sensor")
    # External temperature and humidity sensor (BME280 only?)
    ext_th_config = config_manager.get_dynamic("ext_th_sensor")
    
    th_configs = [int_th_config, ext_th_config]
    
    read_sensors = []
    
    for th_config in th_configs:

        if th_config and th_config.get("enable", True):
            
            utils.log_info("Reading internal temperature and humidity sensor...")
            
            i2c = I2C(scl=Pin(22), sda=Pin(21))
            devices = i2c.scan()
            sensor_data = None
            
            if (68 in devices) and (68 not in read_sensors):
                utils.log_info("SHT30 sensor found!")
                from modules import sht30_sensor
                sht_sensor = sht30_sensor.SHT30Sensor()
                sensor_data = sht_sensor.read_data()
                read_sensors.append(68)
                
            elif (118 in devices) and (118 not in read_sensors):
                utils.log_info("BME sensor found!")
                from modules import bme_sensor
                CHIP_ID = bme_sensor.BME_CHIP_ID()
                
                if CHIP_ID == 88: #Sensor is BMP280
                    utils.log_info("Sensor is BMP280!")
                    bme_sensor = bme_sensor.BME280Sensor()
                    sensor_data = bme_sensor.read_data()
                    read_sensors.append(118)
                    
                elif CHIP_ID == 96: #Sensor is BME280
                    utils.log_info("Sensor is BME280!")
                    bme_sensor = bme_sensor.BME280Sensor()
                    sensor_data = bme_sensor.read_data()
                    read_sensors.append(118)
                    
                elif CHIP_ID == 97: #Sensor is BME680
                    utils.log_info("Sensor is BME680!")
                    bme_sensor = bme_sensor.BME680Sensor(IAQ=False)  # Set IAQ=True if you want IAQ calculation
                    sensor_data = bme_sensor.read_data()
                    read_sensors.append(118)
                else:
                    utils.log_warning(f"Unkwon CHIP ID found: {CHIP_ID}")

            if sensor_data:
                utils.log_info(f"Temperature: {sensor_data['temperature']:.2f} °C, Humidity: {sensor_data['humidity']:.2f} %RH")
                data.append([len(read_sensors)-1, "addTemperatureSensor", sensor_data['temperature']])
                data.append([len(read_sensors)-1, "addHumiditySensor", sensor_data['humidity']])

                #Check temperature alarms
                if (upload_mode and (th_config.get("temperature_low_cond", False)) and (sensor_data['temperature'] < th_config.get("temperature_low", 0))):
                    alarm_condition = True
                if (upload_mode and (th_config.get("temperature_high_cond", False)) and (sensor_data['temperature'] > th_config.get("temperature_high", 0))):
                    alarm_condition = True

                #Check humidity alarms
                if (upload_mode and (th_config.get("humidity_low_cond", False)) and (sensor_data['humidity'] < th_config.get("humidity_low", 0))):
                    alarm_condition = True
                if (upload_mode and (th_config.get("humidity_high_cond", False)) and (sensor_data['humidity'] > th_config.get("humidity_high", 0))):
                    alarm_condition = True
                    
        else:
            utils.log_info("No temperature and humidity sensor configured in dymanic_config.json.")
        
        
    sum_pt100 = 0.0
    count_pt100 = 0
    sum_analog = {}
    count_analog = {}
    sum_modbus = {}
    count_modbus = {}
    sum_modbus_generic = {}
    count_modbus_generic = {}

    # Modules
    max31865_module = None
    modbus_module = None
    analog_module = None
    
    if pt100_enabled:
        from modules import max31865_sensor
        max31865_module = max31865_sensor.MAX31865Sensor()

    if num_analog_enabled > 0:
        from modules import analog_sensor
        analog_module = analog_sensor.AnalogInput()
        # Init dictionaries
        for ch_cfg in analog_config.get("inputs", []):
            if ch_cfg.get("enable", False):
                ch = ch_cfg.get("channel")
                if ch is not None:
                    sum_analog[ch] = 0.0
                    count_analog[ch] = 0
        
        # Analog preadquisition (only once)
        pre_acquisition_time = analog_config.get("pre_acquisition", 0)
        if pre_acquisition_time > 0:
            utils.log_info(f"Starting Analog pre-acquisition delay: {pre_acquisition_time} ms")
            while (time.time() - reg_on_t) * 1000 < pre_acquisition_time:
                await asyncio.sleep_ms(500)
            utils.log_info("Analog pre-acquisition delay finished.")

    if num_modbus_enabled > 0:
        from modules import modbus_sensor
        baudrate_map = {0: 9600, 1: 19200, 2: 38400, 3: 57600, 4: 115200}
        parity_map = {0: None, 1: 0, 2: 1}
        modbus_module = modbus_sensor.ModbusSensor(
            baudrate=baudrate_map[modbus_config.get("baudrate", 0)],
            data_bits=modbus_config.get("data_bits", 8),
            parity=parity_map[modbus_config.get("parity", 0)],
            stop_bits=modbus_config.get("stop_bits", 1)
        )
        # Init dictionaries
        for ch_cfg in modbus_config.get("inputs", []):
            if ch_cfg.get("enable", False):
                ch = ch_cfg.get("channel")
                if ch is not None:
                    fc = ch_cfg.get("fc")
                    if fc == 1 or fc == 2 or ch_cfg.get("long_int", False):
                        sum_modbus_generic[ch] = 0
                        count_modbus_generic[ch] = 0
                    else:
                        sum_modbus[ch] = 0.0
                        count_modbus[ch] = 0

        # Modbus preadquisition (only once)
        pre_acquisition_time = modbus_config.get("pre_acquisition", 0)
        if pre_acquisition_time > 0:
            utils.log_info(f"Starting Modbus pre-acquisition delay: {pre_acquisition_time} ms")
            while (time.time() - reg_on_t) * 1000 < pre_acquisition_time:
                await asyncio.sleep_ms(500)
            utils.log_info("Modbus pre-acquisition delay finished.")


    # --- Sampling loop ---
    start_time = time.time()
    loop_counter = 0
    
    while (time.time() - start_time < n_seconds) and (loop_counter < n_loop):
            
        # --- Temperature PT100 Input ---
        if pt100_enabled and max31865_module:
            temperature = max31865_module.read_temperature()
            if temperature is not None:
                utils.log_info(f"  Loop {loop_counter}: PT100 Temp: {temperature:.2f} °C")
                sum_pt100 += temperature
                count_pt100 += 1
                
                # Check alarms
                if (upload_mode and (pt100_config.get("low_cond", False)) and (temperature < pt100_config.get("low", 0))):
                    alarm_condition = True
                if (upload_mode and (pt100_config.get("high_cond", False)) and (temperature > pt100_config.get("high", 0))):
                    alarm_condition = True
            else:
                utils.log_info(f"  Loop {loop_counter}: Error reading PT100 temperature.")

        # --- Modbus Inputs ---
        if num_modbus_enabled > 0 and modbus_module:
            for channel_config in modbus_config["inputs"]:
                if not channel_config.get("enable", False):
                    continue # Skip disabled channels

                channel = channel_config.get("channel")
                slave_addr = channel_config.get("slave_address")
                register_addr = channel_config.get("register_address")
                fc = channel_config.get("fc")
                is_fp = channel_config.get("is_FP", False)
                byte_order = channel_config.get("byte_order", "big") # Ensure default if not specified
                number_of_decimals = 10**channel_config.get("number_of_decimals", 0)
                offset = channel_config.get("offset", 0.0)
                invert = channel_config.get("invert", False)
                long_int = channel_config.get("long_int", False)
                
                value = modbus_module.read_modbus_data(slave_addr, fc, register_addr, is_fp)
                await asyncio.sleep_ms(100)

                if value is not None:
                    if not is_fp:
                        value = value[0]
                    
                    # Apply offsets
                    if fc == 3 or fc == 4:
                        if invert:
                            value = offset - value/number_of_decimals   
                        else:
                            value = value/number_of_decimals - offset
                    
                    utils.log_info(f"  Loop {loop_counter}: Modbus Ch {channel}: {value}")

                    if fc == 1 or fc == 2 or long_int:
                        sum_modbus_generic[channel] += value
                        count_modbus_generic[channel] += 1
                    else:
                        sum_modbus[channel] += value
                        count_modbus[channel] += 1

                    # Check alarms
                    if upload_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                        alarm_condition = True
                    if upload_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0):
                        alarm_condition = True
                else:
                    utils.log_info(f"  Loop {loop_counter}: Error reading Modbus channel {channel}.")

        # --- Analog inputs ---
        if num_analog_enabled > 0 and analog_module:
            for channel_config in analog_config["inputs"]:
                if not channel_config.get("enable", False):
                    continue # Skip disabled channels

                channel = channel_config.get("channel")
                value = analog_module.read_analog(3 - channel) # Hardware-specific mapping
                value = analog_module.convert_value(value, channel_config.get("zero", 0),  channel_config.get("full_scale", 100))

                if value is not None:
                    utils.log_info(f"  Loop {loop_counter}: Analog Ch {channel}: {value}")
                    sum_analog[channel] += value
                    count_analog[channel] += 1

                    # Check alarms 
                    if upload_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                        alarm_condition = True
                    if upload_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0):
                        alarm_condition = True
                else:
                    utils.log_info(f"  Loop {loop_counter}: Error reading Analog channel {channel}.")
        
        # --- Loop end ---
        loop_counter += 1
        if wdt:
            utils.log_info("Feeding WDT from read_all_sensors task.")
            wdt.feed()
        if (loop_counter < n_loop):
            await asyncio.sleep_ms(5000)
                
                
    if (not ble) and (not isurnode_enabled):
        pm.control_vdc(0)
        pm.control_5v(0)
        if output_config.get("active_vdc", False):
            pm.control_digital_output(0)
    
    # --- CALCULATE AVERAGE VALUES & ADD TO DATA ---

    if pt100_enabled:
        if count_pt100 > 0:
            avg_pt100 = sum_pt100 / count_pt100
            utils.log_info(f"Final PT100 Avg: {avg_pt100:.2f} (from {count_pt100} readings)")
            data.append([0, "addTemperatureInput", avg_pt100])
        else:
            utils.log_info("No valid PT100 readings obtained.")
            data.append([0, "addTemperatureInput", 0]) # Add 0 for error

    if num_analog_enabled > 0:
        for channel, total_sum in sum_analog.items():
            count = count_analog[channel]
            if count > 0:
                avg_analog = total_sum / count
                utils.log_info(f"Final Analog Ch {channel} Avg: {avg_analog:.2f} (from {count} readings)")
                data.append([channel, "addAnalogInput", avg_analog])
            else:
                utils.log_info(f"No valid Analog Ch {channel} readings obtained.")
                data.append([channel, "addAnalogInput", 0.0]) # Add 0 for error

    if num_modbus_enabled > 0:
        # Average for FC 3/4 (float)
        for channel, total_sum in sum_modbus.items():
            count = count_modbus[channel]
            if count > 0:
                avg_modbus = total_sum / count
                utils.log_info(f"Final Modbus Ch {channel} Avg: {avg_modbus:.2f} (from {count} readings)")
                data.append([channel, "addModbusInput", avg_modbus])
            else:
                utils.log_info(f"No valid Modbus Ch {channel} readings obtained.")
                data.append([channel, "addModbusInput", 0.0])

        # Average for FC 1/2 (int/generic)
        for channel, total_sum in sum_modbus_generic.items():
            count = count_modbus_generic[channel]
            if count > 0:
                # El promedio de enteros debe redondearse a entero
                avg_modbus_gen = int(round(total_sum / count, 0))
                utils.log_info(f"Final Modbus-Gen Ch {channel} Avg: {avg_modbus_gen} (from {count} readings)")
                data.append([channel, "addModbusGenericInput", avg_modbus_gen])
            else:
                utils.log_info(f"No valid Modbus-Gen Ch {channel} readings obtained.")
                data.append([channel, "addModbusGenericInput", 0])
                
    
    # Digital outputs
    
    # TODO: Proccess outputs :)
    
    return data, alarm_condition

async def read_isurnode_data(upload_mode, data, alarm_condition, ble = False):
    
    SENSOR_MAP = {
    0: ("addAnalogInput", 0),
    1: ("addAnalogInput", 1),
    2: ("addAnalogInput", 2),
    3: ("addAnalogInput", 3),
    4: ("addModbusInput", 0),
    5: ("addModbusInput", 1),
    6: ("addModbusInput", 2),
    7: ("addModbusInput", 3),
    8: ("addTemperatureInput", 0),

    }
    
    isurnode_config = config_manager.get_dynamic("isurnode_config")
    modbus_config = config_manager.get_dynamic("modbus_config")
    
    if not isurnode_config or not isurnode_config.get("enable"):
        utils.log_info("Isurnode is disabled.")
        return data, alarm_condition # No changes.
    
    pm.control_vdc(1)
    await asyncio.sleep_ms(250)
    pm.control_5v(1)

    from modules import modbus_sensor
    baudrate_map = {0: 9600, 1: 19200, 2: 38400, 3: 57600, 4: 115200}
    parity_map = {0: None, 1: 0, 2: 1}
    modbus_module = modbus_sensor.ModbusSensor(
        baudrate=baudrate_map[modbus_config.get("baudrate", 0)],
        data_bits=modbus_config.get("data_bits", 8),
        parity=parity_map[modbus_config.get("parity", 0)],
        stop_bits=modbus_config.get("stop_bits", 1)
    )
    
    slave_address = isurnode_config.get("slave_address")
    analog_config = isurnode_config.get("analog_config")
    any_analog_enabled = any(ch.get("enable", False) for ch in analog_config.get("inputs", [])) if analog_config else False
    
    #SHT30 sensor
    
    sht30_config = isurnode_config.get("SHT30_sensor")
    if sht30_config and sht30_config.get("enable"):
        utils.log_info("SHT30 sensor is enabled. Proceeding with acquisition.")
        try:
            trigger_addr = 101 #Fixed address
            read_addr = 8 #Fixed address
            channel = 2 #Fixed channel
            
            if modbus_module.write_register(slave_address, trigger_addr, 1):
                await asyncio.sleep_ms(1000)
            
                utils.log_info(f"SHT30: Trigger completed, reading temperature and humidity...")
                temperature = modbus_module.read_modbus_data(slave_address, 4, read_addr, False)[0]/100
                await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 is MicroPython is slow.
                humidity = modbus_module.read_modbus_data(slave_address, 4, read_addr+1, False)[0]/100
                await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 is MicroPython is slow.
                
                data.append([channel, "addTemperatureSensor", temperature])
                data.append([channel, "addHumiditySensor", humidity])
                
                utils.log_info(f"SHT30: Reading completed -> Temperature={temperature}C, Humidity={humidity}%")
                
                #Check temperature alarms
                if (upload_mode and (sht30_config.get("temperature_low_cond", False)) and (temperature < sht30_config.get("temperature_low", 0))):
                    alarm_condition = True
                if (upload_mode and (sht30_config.get("temperature_high_cond", False)) and (temperature > sht30_config.get("temperature_high", 0))):
                    alarm_condition = True

                #Check humidity alarms
                if (upload_mode and (sht30_config.get("humidity_low_cond", False)) and (humidity < sht30_config.get("humidity_low", 0))):
                    alarm_condition = True
                if (upload_mode and (sht30_config.get("humidity_high_cond", False)) and (humidity > sht30_config.get("humidity_high", 0))):
                    alarm_condition = True

            else:
                utils.log_error(f"Failed to write trigger for SHT30 sensor at address {trigger_addr}")

        except Exception as e:
            utils.log_error(f"Error reading SHT30 sensor: {e}")
            
    #Analog inputs
    
    if any_analog_enabled:
        utils.log_info("At least one analog input is enabled. Proceeding with acquisition.")
        
        from modules import analog_sensor
        analog_module = analog_sensor.AnalogInput()

        # 2. Perform pre-acquisition delay ONLY if any input is enabled
        pre_acquisition_time = analog_config.get("pre_acquisition", 0)
        if pre_acquisition_time > 0:
            utils.log_info(f"Starting pre-acquisition delay: {pre_acquisition_time} ms")
            now = time.time()
            while((now - reg_on_t) * 1000 < pre_acquisition_time):
                 remaining_ms = pre_acquisition_time - (now - reg_on_t) * 1000
                 if remaining_ms > 1000:
                      utils.log_info(f"Analog sensor pre-acquisition: waiting {remaining_ms:.0f} ms...")
                 await asyncio.sleep_ms(500)
                 now = time.time()
            utils.log_info("Pre-acquisition delay finished.")
        else:
            utils.log_info("Pre-acquisition time is 0 or not configured. Skipping delay.")
            
        try:
            
            trigger_addr = 100 #Fixed address
            
            # 1. Trigger all analog inputs acquisition at once
            if modbus_module.write_register(slave_address, trigger_addr, 1):
                
                await asyncio.sleep_ms(1000)
                utils.log_info(f"SHT30: Trigger completed, reading temperature and humidity...")
                
                # 3. Iterate and read each configured analog input
                for analog_input in analog_config.get("inputs", []):
                    if analog_input.get("enable", False):
                        read_addr = analog_input["channel"] - 4   # 0, 1, 2, 3 for channels 4, 5, 6, 7
                        channel = analog_input["channel"]
                        
                        try:
                            # Read the corresponding register value
                            # Using function 4 (Read Input Registers) as per your example
                            raw_value = modbus_module.read_modbus_data(slave_address, 4, read_addr, False)[0]/1000.0
                            value = analog_module.convert_value(raw_value, analog_input.get("zero", 0),  analog_input.get("full_scale", 100))
                            
                            # Add data to the payload
                            data.append([channel, "addAnalogInput", value])
                            utils.log_info(f"  - Read addr {read_addr}: {value}")

                            # Check alarms (assuming upload_mode and alarm_condition are defined earlier)
                            if upload_mode and analog_input.get("low_cond", False) and value < analog_input.get("low", 0):
                                alarm_condition = True
                            if upload_mode and analog_input.get("high_cond", False) and value > analog_input.get("high", 0): # Corrected 'hi' to 'high'
                                alarm_condition = True
                                
                            await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 is MicroPython is slow.
                            
                        except Exception as e:
                            utils.log_error(f"Error reading analog input at address {read_addr}: {e}")
                            
            else:
                utils.log_error(f"Failed to write trigger for analog inputs at address {trigger_addr}")

        except Exception as e:
            utils.log_error(f"Error during analog input acquisition process: {e}")

    do_config = isurnode_config.get("digital_outputs")

    if do_config and do_config.get("outputs"):
        
        utils.log_info("Processing digital outputs...")
                
        for output_channel in do_config["outputs"]:
            
            if not output_channel.get("enable", False):
                continue

            await asyncio.sleep_ms(5000) #Sleep for recharging the capacitor.
            channel_out = output_channel.get("channel")
            valve_type = output_channel.get("type") # ON/OFF: 1, Proportional: 2
            
            if valve_type == 1: #ON-OFF VALVE
                
                utils.log_info(f'ON-OFF valve found on channel {channel_out}!')

                condition_results = []
                logic_op = output_channel.get("logic_operator", 0) # 0=OR, 1=AND
                sensor1_id = output_channel.get("sensor1") #Sensor1 asociatted to the regulation.
                sensor2_id = output_channel.get("sensor2") #Sensor2 asociatted to the regulation.
                
                if (pm.wakeup_reason == "Power-on reset") and not ble: #Init all EVs as disabled.
                    utils.log_info(f'  - Setting valve to default state --> CLOSE.')
                    modbus_module.write_register(slave_address, channel_out*2+201, 1)
                    await asyncio.sleep_ms(1000)
                    rtc_memory.set_ev_state(channel_out, 0)

                # Find the LPP type and channel for the required sensor
                if sensor1_id not in SENSOR_MAP:
                    utils.log_warning(f"  - Unknown sensor ID {sensor1_id} in channel.")
                    break
                
                # Find the LPP type and channel for the required sensor
                if sensor2_id not in SENSOR_MAP:
                    utils.log_warning(f"  - Unknown sensor ID {sensor2_id} in channel.")
                    break
                
                lpp_type, sensor_channel = SENSOR_MAP[sensor1_id]
                
                # Search for the sensor's value in the main 'data' list
                sensor_value1 = None
                for item in data:
                    # item format is [channel, lpp_type_string, value]
                    if item[0] == sensor_channel and item[1] == lpp_type:
                        sensor1_value = item[2]
                        break # Found the value, no need to search further
                    
                if sensor1_value is None:
                    utils.log_warning(f"  - No value found for sensor ID {sensor1_id} ({lpp_type} ch:{sensor_channel}) in data.")
                    
                lpp_type, sensor_channel = SENSOR_MAP[sensor2_id]
                
                # Search for the sensor's value in the main 'data' list
                sensor2_value = None
                for item in data:
                    # item format is [channel, lpp_type_string, value]
                    if item[0] == sensor_channel and item[1] == lpp_type:
                        sensor2_value = item[2]
                        break # Found the value, no need to search further
                    
                if sensor2_value is None:
                    utils.log_warning(f"  - No value found for sensor ID {sensor2_id} ({lpp_type} ch:{sensor_channel}) in data. Condition will be False.")
                    
                if output_channel.get("cond1_enable", False) and sensor1_value is not None:
                    if output_channel.get("low1_cond", False):
                        if sensor1_value < output_channel.get("low1", 0):
                            utils.log_warning(f"  - Low condition 1 is TRUE.")
                            condition_results.append(True)
                        else:
                            condition_results.append(False)
                        
                    if output_channel.get("high1_cond", False):
                        if sensor1_value > output_channel.get("high1", 0):
                            utils.log_warning(f"  - High condition 1 is TRUE.")
                            condition_results.append(True)
                        else:
                            condition_results.append(False)
                        
                if output_channel.get("cond2_enable", False) and sensor2_value is not None:
                    if output_channel.get("low2_cond", False):
                        if sensor2_value < output_channel.get("low2", 0):
                            utils.log_warning(f"  - Low condition 2 is TRUE.")
                            condition_results.append(True)
                        else:
                            condition_results.append(False)
                        
                    if output_channel.get("high2_cond", False):
                        if sensor1_value > output_channel.get("high2", 0):
                            utils.log_warning(f"  - High condition 2 is TRUE.")
                            condition_results.append(True)
                        else:
                            condition_results.append(False)
                
                utils.log_info(f"  - Result for condition_results: {condition_results}")
                should_be_active = bool(condition_results) and (all(condition_results) if logic_op == 1 else any(condition_results))
                log_op_str = "AND" if logic_op == 1 else "OR"
                utils.log_info(f"  - Result for with {log_op_str} logic: {should_be_active}")
                
                if not rtc_memory.get_manual_ev_flag():
                
                    if should_be_active and not rtc_memory.get_ev_state(channel_out):
                        utils.log_info(f"  - Sending OPEN pulse.")
                        modbus_module.write_register(slave_address, channel_out*2 + 200, 1)
                        await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 with MicroPython is slow.
                        rtc_memory.set_ev_state(channel_out, 1)
                    elif not should_be_active and rtc_memory.get_ev_state(channel_out):
                        utils.log_info(f"  - Sending CLOSE pulse.")
                        modbus_module.write_register(slave_address, channel_out*2 + 201, 1)
                        await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 with MicroPython is slow.
                        rtc_memory.set_ev_state(channel_out, 0)
                        
                #Append last valve state to data (Only ON-OFF valve and if output rule is defined)
                data.append([channel_out + 3, "addDigitalOutput", rtc_memory.get_ev_state(channel_out)])
                    
            if valve_type == 2: #PROPORTIONAL VALVE
                
                utils.log_info(f'Proportional valve{output_channel.get("channel")} found!')
                
                sensor1_id = output_channel.get("sensor1") #Sensor asociatted to the regulation.
                on_time = output_channel.get("on_time", 500)
                if on_time < 150:
                    on_time = 150
                    
                if pm.wakeup_reason == "Power-on reset" and not ble:
                    
                    utils.log_info(f'Setting valve{channel_out} to default state.')
                    modbus_addr =  output_channel.get("channel")*4+200
                    close_addr = modbus_addr + 1
                    modbus_module.write_register(slave_address, close_addr, 1)
                    await asyncio.sleep_ms(1000)
                    modbus_addr =  output_channel.get("channel")*4+202
                    close_addr = modbus_addr + 1
                    modbus_module.write_register(slave_address, close_addr, 1)
                    await asyncio.sleep_ms(1000)
                    
                # Find the LPP type and channel for the required sensor
                if sensor1_id not in SENSOR_MAP:
                    utils.log_warning(f"  - Unknown sensor ID {sensor1_id} in valve{channel_out}.")
                    break
                
                lpp_type, sensor_channel = SENSOR_MAP[sensor1_id]
                
                # Search for the sensor's value in the main 'data' list
                sensor_value = None
                for item in data:
                    # item format is [channel, lpp_type_string, value]
                    if item[0] == sensor_channel and item[1] == lpp_type:
                        sensor_value = item[2]
                        break # Found the value, no need to search further
                    
                if sensor_value is None:
                    utils.log_warning(f"  - No value found for sensor ID {sensor1_id} ({lpp_type} ch:{sensor_channel}) in data. Condition will be False.")
                    break
            
                if output_channel.get("cond1_enable", False) and not rtc_memory.get_manual_ev_flag():
                    if output_channel.get("low1_cond", False) and sensor_value < output_channel.get("low1", 0):
                        
                        utils.log_info(f"Sensor ID {sensor1_id} value: {sensor_value} is low. Sending pulse to EV{channel_out*2}.")
                        modbus_addr =  output_channel.get("channel")*4+200
                        open_addr = modbus_addr
                        close_addr = open_addr + 1
                        # Send OPEN pulse
                        modbus_module.write_register(slave_address, open_addr, 1)
                        
                        # Wait for the specified duration
                        await asyncio.sleep_ms(on_time)
                        
                        # Send CLOSE pulse
                        modbus_module.write_register(slave_address, close_addr, 1)
                        await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 with MicroPython is slow.
                        
                    if output_channel.get("high1_cond", False) and sensor_value > output_channel.get("high1", 0):
                        
                        utils.log_info(f"Sensor ID {sensor1_id} value: {sensor_value} is high. Sending pulse to EV{channel_out*2+1}.")
                        modbus_addr =  output_channel.get("channel")*4+202
                        open_addr = modbus_addr
                        close_addr = open_addr + 1
                        # Send OPEN pulse
                        modbus_module.write_register(slave_address, open_addr, 1)
                        
                        # Wait for the specified duration
                        await asyncio.sleep_ms(on_time)
                        
                        # Send CLOSE pulse
                        modbus_module.write_register(slave_address, close_addr, 1)
                        await asyncio.sleep_ms(150) #Sleep 150ms, STM32L4 with MicroPython is slow.

    if (not ble):
        pm.control_vdc(0)
        pm.control_5v(0)
        if output_config.get("active_vdc", False):
            pm.control_digital_output(0)

    return data, alarm_condition


async def sensor_reading_task():
    """
    Reads all sensors periodically and stores the LPP payload in rtc_memory
    (same steps the old single-shot main.py did inline: user_script, encode,
    optional internal flash copy, store_payload).

    Manages read_sensor_idle: cleared while reading, set once stored (even on
    error) so battery_sleep_governor() and run_telemetry_cycle() know it's safe to
    sleep / grab payloads.
    """
    
    global rtc_memory

    while True:
        
        read_sensor_idle.clear()  # Block sleep/telemetry while a reading is in progress
        continuous_mode = False
        
        try:
            upload_mode = config_manager.get_dynamic("general").get("upload_mode", 0)
            continuous_mode = config_manager.get_dynamic("general").get("continuous_mode", False)
            isurnode_config = config_manager.get_dynamic("isurnode_config")
            latency_s = config_manager.dynamic_config["general"].get("latency_time", 10) * 60
            loop_seconds = pm.seconds2wakeup()
            
            if not continuous_mode:
                n_loop_cycles = config_manager.get_dynamic("general").get("loop_cycles", 1)
                
            else:
                n_loop_cycles = latency_s//5 + 1

            data, alarm_condition = await read_all_sensors(upload_mode, n_loop=n_loop_cycles, n_seconds=loop_seconds, isurnode_enabled=isurnode_config.get("enable", False))
            data, alarm_condition = await read_isurnode_data(upload_mode, data, alarm_condition)

            if alarm_condition:
                # Known as soon as this cycle's reading is done, well before
                # read_sensor_idle is set below -- run_telemetry_cycle() can start
                # waking the modem right away instead of waiting for
                # scheduled_telemetry_task's next pass (up to latency_time away).
                _trigger_send_telemetry("alarm detected this cycle")

            #----- USER SCRIPT ------
            if "user_script.py" in os.listdir():
                if config_manager.dynamic_config["general"].get("user_script", False):
                    try:
                        import sys
                        if "user_script" in sys.modules:
                            del sys.modules["user_script"]
                        import user_script
                        data = user_script.process(data)
                    except Exception as e:
                        utils.log_error("Error in user script:", e)
                else:
                    try:
                        os.remove("user_script.py")
                    except Exception as e:
                        utils.log_error("Error removing user script:", e)

            # --- Encode data to Isurlog LPP format ---
            utils.log_info(f"Data to encode: {data}")
            encoded_payload = encoder.encode(data)

            internal_register = config_manager.get_dynamic("general").get("internal_register", False)

            if encoded_payload:
                utils.log_info(f"Encoded Payload: {encoded_payload}")
                if internal_register:
                    from modules import internal_storage
                    internal_storage_module = internal_storage.InternalStorage()
                    if internal_storage_module.store_payload(encoded_payload):
                        utils.log_info(f"Payload stored in internal flash: {encoded_payload}")
                    else:
                        utils.log_error(f"Failed to store payload in internal flash: {encoded_payload}")
                else:
                    utils.log_info("Internal register is disabled.")
            else:
                utils.log_error("Encoding failed. Sending empty payload")
                encoded_payload = ""  # Send empty payload on failure

            if not store_payload_in_queue(encoded_payload):
                utils.log_error("Could not store payload in RTC memory or EEPROM.")
            else:
                utils.log_info(f"Stored payload. Cycle {get_pending_payload_count()} of {get_accumulator_target()}")

            #Update alarm flag so run_telemetry_cycle()/theft logic can see it changed this cycle.
            rtc_memory.set_alarm_flag(alarm_condition)

            if wdt:
                utils.log_info("Feeding WDT from sensor_reading_task.")
                wdt.feed()

        except Exception as e:
            utils.log_error(f"[TASK: SENSORS] Reading failed: {e}")
            latency_s = config_manager.dynamic_config["general"].get("latency_time", 10) * 60

        finally:
            read_sensor_idle.set()  # Unblock sleep/telemetry regardless of outcome


        if not continuous_mode:
            await asyncio.sleep(latency_s)


async def establish_network_connection(force_hard_reset=False, max_retry_connection_lorawan = 1):
    """
    Establishes the network connection and configures the MQTT/NTP sockets
    or the LoRaWAN join, depending on modem_type.
    Returns True if the connection was successful, False otherwise.
    Must always be called under modem_lock.

    force_hard_reset: for NB-IoT, skips the modem hard_reset by default (a
    cold-booted modem doesn't need one, and it's the slowest recovery step)
    -- only pass True once a plain connect() attempt has already failed.
    """

    mqtt_config, base_topic = get_mqtt_settings()
    if status_led.is_enabled():
        status_led.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200, wake_up_period=2)

    if modem_type == "nb-iot":
        
        global nb_iot_module
        utils.log_info("Initializing NB-IoT network registration...")

        if force_hard_reset:
            utils.log_warning("Retry escalation: hard-resetting the NB-IoT modem.")
            await nb_iot_module.hard_reset()
        
        await nb_iot_module.select_SIM(config_manager.dynamic_config["communications"]["cellular_iot"].get("external_sim", True))

        preference = config_manager.dynamic_config["communications"]["cellular_iot"].get("preference", 0)
        apn = config_manager.dynamic_config["communications"]["cellular_iot"].get("apn", None)

        if not await nb_iot_module.connect(preference, apn=apn):
            utils.log_error("Failed to connect to NB-IoT cellular cells.")
            return False

        keep_alive = ((config_manager.dynamic_config["general"].get("latency_time", 10) * 60) + 20) * config_manager.dynamic_config["general"].get("register_acumulator", 1)
        await nb_iot_module.mqtt_configure(ser_num, keep_alive, 0)

        if not await nb_iot_module.mqtt_connect(mqtt_config.get("user", ""), mqtt_config.get("passwd", ""), mqtt_config.get("ip", ""), mqtt_config.get("port", 1883)):
            utils.log_error("Failed to establish MQTT Broker connection.")
            return False

        if should_resync_rtc():
            new_time = await nb_iot_module.get_network_time()
            utils.log_info(f"New requested time UTC: {new_time}")
            pm.set_rtc_time(new_time, mode = "NB-IoT")
            rtc_memory.set_last_rtc_sync(pm.rtc.get_unix_time())

        await nb_iot_module.mqtt_subscribe(f"{base_topic}/config/{ser_num}", QoS=2)
        return True

    elif modem_type == "wifi":
        
        global mqtt_client
        from modules import wifi
        utils.log_info("Initializing Wifi connection...")

        if not wifi.is_connected():
            ssid = config_manager.dynamic_config["communications"]["wifi"].get("ssid", None)
            password = config_manager.dynamic_config["communications"]["wifi"].get("password", None)

            if ssid is not None and password is not None:
                if await wifi.do_connect(ssid, password, timeout_seconds=15):
                    if should_resync_rtc():
                        import ntptime
                        try:
                            ntptime.settime()
                            new_time = time.localtime()
                            utils.log_info(f"New requested time UTC: {new_time}")
                            pm.set_rtc_time(new_time, mode="WiFi")
                            rtc_memory.set_last_rtc_sync(pm.rtc.get_unix_time())
                        except Exception as ntp_err:
                            utils.log_error(f"NTP Synchronization failed: {ntp_err}")
                else:
                    utils.log_error("Could not establish Wifi connection!")
                    return False
            else:
                utils.log_warning("No SSID and password configured for WiFi.")
                return False
            
        try:
            mqtt_client.connect(clean_session=True)
            mqtt_client.subscribe(f"{base_topic}/config/{ser_num}", qos=1)
        except Exception as err:
            utils.log_error(f"Could not connect to the MQTT broker: {err}")
            return False
        
        return True
    
    elif modem_type == "lorawan":

        global lorawan_module
        utils.log_info("Initializing LoRaWAN network join...")
        
        if force_hard_reset:
            utils.log_warning("Retry escalation: hard-resetting the LoRaWAN modem.")
            await lorawan_module.reset()

        lorawan_config = config_manager.dynamic_config["communications"].get("lorawan", {})
        class_map = {0: "A", 1: "B", 2: "C"}

        if not await lorawan_module.connect(lorawan_class=class_map[lorawan_config.get("class", 0)], attempts = max_retry_connection_lorawan):
            utils.log_error("Failed to connect to LoRaWAN")
            return False

        await lorawan_module.set_confirmed_mode(0)  # Enable/disable send ACK (optional)
        return True
    
    return False


def _trigger_send_telemetry(reason):
    """
    Kicks off run_telemetry_cycle() as its own task if none is already in flight.
    Shared by every trigger source (IRQ pin, alarm detected mid-reading,
    scheduled accumulator check) so there's exactly one place that decides
    whether a send is already running.
    """
    if telemetry_idle.is_set():
        utils.log_info(f"[TASK: TELEMETRY] Triggered by {reason}.")
        telemetry_idle.clear()  # Blocks deepsleep until this finishes
        asyncio.create_task(run_telemetry_cycle())
    else:
        utils.log_info(f"[TASK: TELEMETRY] Trigger ({reason}) ignored, telemetry already in progress.")


def _telemetry_pin_isr(pin):
    """
    Runs in hard interrupt context: must be minimal (no allocations, no I2C/UART,
    no asyncio calls). Just signals the flag; the real work happens in
    telemetry_trigger_task() below.
    """
    telemetry_trigger.set()


async def telemetry_trigger_task():
    """
    Waits for the IO35 rising-edge signal and forces a telemetry upload,
    regardless of the normal scheduled cycle (seconds_until_next_telemetry_cycle)
    and regardless of whether a telemetry task is already in flight.
    """
    wake_up_pin = config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("esp_wake_up", 35)
    while True:
        await telemetry_trigger.wait()
        _trigger_send_telemetry(f"external IRQ on IO{wake_up_pin}")

async def publish_payload(payload):
    """Publishes a single, already-built payload. Connection, wake_up() and
    signal_data handling are run_telemetry_cycle()'s job, not this function's --
    this just puts the payload on the wire."""

    global nb_iot_module
    mqtt_config, base_topic = get_mqtt_settings()
    
    if status_led.is_enabled():
        status_led.set_ulp_pattern(pulse_num=1, n_micro_pulses=250, delay_on=5, delay_off=20, inter_delay=250, wake_up_period=5)

    if modem_type == "nb-iot":

        utils.log_info("Transmitting data through NB-IoT...")
        utils.log_info(f"Publishing payload: {payload}")

        if not await nb_iot_module.mqtt_publish(f"{base_topic}/datos/{ser_num}", payload):
            utils.log_error("Failed to publish payload through cellular MQTT client.")
            return False

    elif modem_type == "wifi":

        utils.log_info("Transmitting data through WiFi...")
        utils.log_info(f"Publishing payload: {payload}")

        if not mqtt_client.publish(f"{base_topic}/datos/{ser_num}", payload):
            utils.log_error("Failed to publish payload on WiFi broker.")
            return False
            
    elif modem_type == "lorawan":

        utils.log_info("Transmitting data through LoRaWAN...")
        utils.log_info(f"Publishing payload: {payload}")

        if not await lorawan_module.send_uplink(2, payload):
            utils.log_error("Failed to publish payload through LoRaWAN.")
            return False
    
    return True
            
async def run_telemetry_cycle():
    """
    Connects (or verifies the connection) and processes downlinks. Whether
    payloads actually get published depends on rtc_memory.should_transmit(),
    checked after read_sensor_idle so it reflects this cycle's data.
    Retries the connection for up to max_retry_connection attempts,
    then gives up until the next wake-up rather than draining the
    battery on a lost cause.
    """
    
    global rtc_memory

    mqtt_config, base_topic = get_mqtt_settings()
    print("[TASK: TELEMETRY] Sending telemetry for this wake-up.")
    
    max_retry_connection = config_manager.dynamic_config["general"].get("max_retry_connection", 2) 

    try:
        if modem_type == "nb-iot":
            
            global nb_iot_module

            async with modem_lock:
                await nb_iot_module.wake_up()
                cellular_connected = await nb_iot_module.check_network_connection()

                retry_attempt = 0
                while not cellular_connected and retry_attempt < max_retry_connection:
                    await establish_network_connection(force_hard_reset=(retry_attempt > 0))
                    cellular_connected = await nb_iot_module.check_network_connection()
                    retry_attempt += 1
                    if not cellular_connected:
                        await asyncio.sleep(5)
                        
                if cellular_connected:
                    
                    mqtt_connected = await nb_iot_module.mqtt_check_connection()
                    
                    retry_attempt = 0
                    while not mqtt_connected and retry_attempt < max_retry_connection:
                        await nb_iot_module.mqtt_connect(mqtt_config.get("user", ""), mqtt_config.get("passwd", ""), mqtt_config.get("ip", ""), mqtt_config.get("port", 1883))
                        mqtt_connected = await nb_iot_module.mqtt_check_connection()
                        retry_attempt += 1
                        if not mqtt_connected:
                            await asyncio.sleep(15)

                    if mqtt_connected:
                        connection_ok.set()
                        print("[TASK: TELEMETRY] Connected. Processing downlink and uploading telemetry...")
                        await downlink_manager.process_nbiot_downlinks(nb_iot_module, rtc_memory, wdt, ser_num, base_topic)
                        
                        print("[TASK: TELEMETRY] Downlinks processed.")
                        
                        await read_sensor_idle.wait()
                        payloads = get_all_pending_payloads()
                        utils.log_info(f"Retrieved payloads: {payloads}")
                        
                        total_payloads = len(payloads)
                        confirmed = 0
                        for i, payload in enumerate(payloads):
                            if (i == total_payloads - 1) and (config_manager.dynamic_config["communications"]["cellular_iot"].get("signal_data", False)):
                                signal_data = await nb_iot_module.get_signal_data()
                                extra_data = []
                                extra_data.append([0, "addModemData", signal_data[0]])
                                extra_data.append([1, "addModemData", signal_data[1]])
                                encoded_extra_payload = encoder.encode(extra_data)
                                payload += encoded_extra_payload
                            utils.log_info(f"Publishing payload {i+1}: {payload}")
                        
                            if await publish_payload(payload):
                                confirmed += 1
                            else:
                                utils.log_error(f"Publish failed for payload {i+1}/{total_payloads}; stopping this batch, {total_payloads - confirmed} payload(s) will be retried next cycle.")
                                break

                        remove_confirmed_payloads(confirmed)
                    
                    else:
                        connection_ok.clear()
                        utils.log_error(f"[TASK: TELEMETRY] No MQTT connection after {max_retry_connection} retries. Will retry on the next wake-up.")                    

                else:
                    connection_ok.clear()
                    utils.log_error(f"[TASK: TELEMETRY] No cellular connection after {max_retry_connection} retries. Will retry on the next wake-up.")
                    
                await nb_iot_module.sleep()

        elif modem_type == "wifi":
            
            global mqtt_client
            from modules import wifi

            wifi_connected = wifi.is_connected()
            retry_attempt = 0
            while not wifi_connected and retry_attempt < max_retry_connection:
                wifi_connected = await establish_network_connection()
                retry_attempt += 1
                if not wifi_connected:
                    await asyncio.sleep(5)

            if wifi_connected:
                connection_ok.set()

                print("[TASK: TELEMETRY] Connected. Processing downlink and uploading telemetry...")
                await downlink_manager.process_wifi_downlinks(mqtt_client, rtc_memory, wdt, ser_num, base_topic)
                
                print("[TASK: TELEMETRY] Downlinks processed.")

                await read_sensor_idle.wait()
                payloads = get_all_pending_payloads()
                utils.log_info(f"Retrieved payloads: {payloads}")

                total_payloads = len(payloads)
                confirmed = 0
                for i, payload in enumerate(payloads):
                    utils.log_info(f"Publishing payload {i+1}: {payload}")
                    if await publish_payload(payload):
                        confirmed += 1
                    else:
                        utils.log_error(f"Publish failed for payload {i+1}/{total_payloads}; stopping this batch, {total_payloads - confirmed} payload(s) will be retried next cycle.")
                        break

                remove_confirmed_payloads(confirmed)

                try:
                    mqtt_client.disconnect()
                    await wifi.do_disconnect()
                except Exception as err:
                    utils.log_error(f"Error while disconnecting from the MQTT broker and turning off WiFi: {err}")
                
            else:
                connection_ok.clear()
                utils.log_error(f"[TASK: TELEMETRY] No connection after {retry_attempt} attempt(s). Will retry on the next wake-up.")

        elif modem_type == "lorawan":

            global lorawan_module

            async with modem_lock:
                lorawan_connected = await lorawan_module.check_network_connection()

                retry_attempt = 0
                while not lorawan_connected and retry_attempt < max_retry_connection:
                    await establish_network_connection(force_hard_reset=(retry_attempt > 0), max_retry_connection_lorawan = max_retry_connection)
                    lorawan_connected = await lorawan_module.check_network_connection()
                    retry_attempt += 1
                    if not lorawan_connected:
                        await asyncio.sleep(5)

                if lorawan_connected:
                    connection_ok.set()
                    print("[TASK: TELEMETRY] Connected. Uploading telemetry...")

                    # request_time()/get_network_time() are tied to the uplink itself
                    # (the module only returns the network time in response to a
                    # transmission), not to the connection phase like NB-IoT/WiFi.
                    resync_requested = should_resync_rtc()
                    if resync_requested:
                        await lorawan_module.request_time()  # Enable time request on this uplink

                    await read_sensor_idle.wait()
                    payloads = get_all_pending_payloads()
                    utils.log_info(f"Retrieved payloads: {payloads}")

                    total_payloads = len(payloads)
                    confirmed = 0
                    for i, payload in enumerate(payloads):
                        utils.log_info(f"Publishing payload {i+1}: {payload}")
                        if await publish_payload(payload):
                            confirmed += 1
                        else:
                            utils.log_error(f"Publish failed for payload {i+1}/{total_payloads}; stopping this batch, {total_payloads - confirmed} payload(s) will be retried next cycle.")
                            break

                    remove_confirmed_payloads(confirmed)

                    if resync_requested:  # Time should be available now, since it was requested on the uplink above
                        new_time = await lorawan_module.get_network_time()
                        utils.log_info(f"New requested time UTC: {new_time}")
                        pm.set_rtc_time(new_time, mode="LoRaWAN")
                        rtc_memory.set_last_rtc_sync(pm.rtc.get_unix_time())

                    await downlink_manager.process_lorawan_downlinks(lorawan_module, rtc_memory)

                else:
                    connection_ok.clear()
                    utils.log_error(f"[TASK: TELEMETRY] No connection after {retry_attempt} attempt(s). Will retry on the next wake-up.")
                    
                await lorawan_module.sleep()

    except Exception as e:
        utils.log_error(f"[TASK: TELEMETRY] Upload failed: {e}")

    finally:
        telemetry_idle.set()  # Unblocks deepsleep, whether or not the send succeeded


async def scheduled_telemetry_task():
    """
    Perpetual task deciding, once per cycle, whether it's worth waking the
    modem at all: should_transmit() (accumulator due), previous_cycle_alarm
    (confirm recovery right after an alarm), or a boot reason (checked only
    on the first iteration, since pm.wakeup_reason never changes otherwise).

    This cycle's own alarm isn't known yet at this point (only after
    read_all_sensors() inside sensor_reading_task()), which is why that task
    triggers run_telemetry_cycle() itself when it finds one instead of waiting
    for this loop's next pass. Both funnel through _trigger_send_telemetry().

    Doesn't wait on read_sensor_idle: the point is for run_telemetry_cycle()'s
    connection work to overlap with sensor_reading_task(), not wait for it.
    """
    
    boot_wakeup_reasons = ("RTC GPIO reset", "Watchdog reset", "Power-on reset")  # RTC GPIO reset: magnet wakeup. Watchdog reset: NB-IoT module wakeup.
    first_iteration = True

    while True:
        previous_cycle_alarm = rtc_memory.get_alarm_flag()
        boot_requires_telemetry = first_iteration and pm.wakeup_reason in boot_wakeup_reasons
        first_iteration = False

        if payload_queue_should_transmit():
            _trigger_send_telemetry("accumulator due")
        elif previous_cycle_alarm:
            _trigger_send_telemetry("previous-cycle alarm")
        elif boot_requires_telemetry:
            _trigger_send_telemetry(f"boot ({pm.wakeup_reason})")
        else:
            utils.log_info(f"[TASK: SCHEDULE] Not due yet (cycle {get_pending_payload_count()} of {get_accumulator_target()}). Skipping modem wake-up.")

        latency_s = config_manager.dynamic_config["general"].get("latency_time", 10) * 60
        await asyncio.sleep(latency_s)

async def battery_sleep_governor():
    """
    Single decision point for deepsleep: sleeps once sensor reading and
    telemetry are both idle and the modem isn't in use, unless
    continuous_mode keeps it always on.
    """
    while True:

        if read_sensor_idle.is_set() and telemetry_idle.is_set() and not modem_lock.locked():
            rollback.cancel() #We can cancel rollback protection if program reaches this point.
            continuous_mode = config_manager.get_dynamic("general").get("continuous_mode", False)
            if not continuous_mode:
                
                if status_led.is_enabled():
                    if (battery_voltage < 3600):
                        status_led.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=20)
                    else:
                        status_led.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500,  wake_up_period=10)
            
                pm.configure_wakeup_sources(wake_up_sources)
                pm.go_to_sleep()

        await asyncio.sleep_ms(500)

async def _theft_alert_nbiot(nb_iot_module, ser_num):
    """Sends a one-off GPS alarm over NB-IoT when the accelerometer confirms
    tampering. Independent of the main gather; not worth parallelizing."""
    await nb_iot_module.wake_up()
    gps_data = await nb_iot_module.get_gps_coords()

    if await nb_iot_module.send_at_command_check(f'AT%XSYSTEMMODE=1,1,0,{config_manager.dynamic_config["communications"]["cellular_iot"].get("preference", 0)}'):
        await nb_iot_module.send_at_command_check("AT+CFUN=1")
        await nb_iot_module.wait_for_network_connection(timeout=180000)
        keep_alive = ((config_manager.dynamic_config["general"].get("latency_time", 10) * 60) + 20) * config_manager.dynamic_config["general"].get("register_acumulator", 1)
        await nb_iot_module.mqtt_configure(ser_num, keep_alive, 0)
        mqtt_config = config_manager.get_dynamic("communications").get("mqtt")
        if await nb_iot_module.mqtt_connect(mqtt_config.get("user", ""), mqtt_config.get("passwd", ""), mqtt_config.get("ip", ""), mqtt_config.get("port", 1883)):
            base_topic = mqtt_config.get("base_topic", "isurlog")
            if gps_data != []:
                lat = gps_data[0]
                lon = gps_data[1]
                elev = gps_data[2]
                await nb_iot_module.mqtt_publish(f"{base_topic}/alarms/{ser_num}", f"{lat, lon, elev}")


def process_ble_command(received_bytes):
    """
    Processes commands received via BLE.
    It converts bytes to a hex string, decodes it, and applies the configuration.
    """
    utils.log_info(f"BLE command received (raw bytes): {repr(received_bytes)}")
    
    
    if b"SD" in received_bytes or b"EV" in received_bytes: #DIGITAL OUTPUT CONTROL  (SSR or LATCHING VALVE)
        received_bytes = received_bytes.decode('ascii')
        utils.log_info("Processing manual command...")
        downlink_manager.process_sd_ev_manual_command(received_bytes, rtc_memory, ble=True)
        
    else:
                            
        try:
            # 1. Convert the received bytes to a hexadecimal string
            hex_payload = binascii.hexlify(received_bytes).decode('ascii')
            utils.log_info(f"Payload converted to hex: '{hex_payload}'")
            decoded_message = encoder.decode(hex_payload.upper())

            # 2. Call the function from your ConfigUpdater module to do the work
            #    This function already decodes and saves the JSON file.
            config_manager.apply_conf_update(decoded_message)
        except Exception as e:
            utils.log_error(f"Fatal error processing BLE command: {e}")

async def ble_mode_task():
    utils.log_info("Magnet wakeup detected. Starting BLE mode...")
    
    # Init Bluetooh manager
    ble = ble_manager.BLEManager(device_name=f"Isurlog-{ser_num}", command_callback=process_ble_command)
    ble_start = time.time()
    
    if status_led.is_enabled():
        status_led.set_ulp_pattern(pulse_num=5, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
    
    while (not ble.client_connected) and (time.time() - ble_start < 120):
        await asyncio.sleep(2)
        
    if status_led.is_enabled():
        status_led.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
        
    if ble.client_connected:        
        while not ble.client_disconnected: # Wait until client disconnects
            # Read data from active sensors
            live_data, _ = await read_all_sensors(0, ble = True)
            live_data, _ = await read_isurnode_data(0, live_data, False, ble = True)
            
            print(live_data)

            # Encode and send by bluetooh
            live_payload = encoder.encode(live_data)
            if live_payload:
                ble.update_data_payload(live_payload)
            
            await asyncio.sleep(10)
            
            if wdt:
                utils.log_info("Feeding WDT from Bluetooh task.")
                wdt.feed()
    
    utils.log_info("BLE client disconnected. Continiuing with normal mode...")
    await asyncio.sleep_ms(1000)
    
async def main():
    
    if modem_type == "nb-iot":
        init_nb_iot_module()

    if modem_type == "wifi":
        init_mqtt_client()
        
    if modem_type == "lorawan":
        init_lorawan_module()
        
    wake_up_pin = config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("esp_wake_up", 35)
    telemetry_pin = Pin(wake_up_pin, Pin.IN)
    telemetry_pin.irq(trigger=Pin.IRQ_RISING, handler=_telemetry_pin_isr)        

    tasks = [
        scheduled_telemetry_task(),
        sensor_reading_task(),
        battery_sleep_governor(),
        telemetry_trigger_task(),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":

    print("\n####WELCOME TO ISURLOG OS v.{} MICROPYTHON FLAVOUR####\n".format(VERSION))
    
    if AUTH_FILE in os.listdir():
        os.remove(AUTH_FILE)
        #pass
    
    ser_num = config_manager.static_config.get("serial", "c-000")
    modem_type = config_manager.static_config.get("modem", "nb-iot")
    
    # --- Initialize Variables ---

    vdc_voltage = config_manager.get_dynamic("general").get("vdc_voltage", 12)
    
    #Pin Configuration
    output_config = config_manager.get_dynamic("output_config")
    EN_COM_MODULE = config_manager.static_config.get("pinout", {}).get("control", {}).get("en_nbiot_pin", 5)
    DIO0_PIN = config_manager.static_config.get("pinout", {}).get("di0_pin", 36)    
    MAGNET_WAKEUP_PIN_NUM = config_manager.static_config.get("pinout", {}).get("magnet_pin", 35)
    MCP_WAKEUP_PIN_NUM = config_manager.static_config.get("pinout", {}).get("mcp_int_pin", 35)

    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("ro_pin", 14), Pin.IN, Pin.PULL_UP, hold=False)
    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("di_pin", 23), hold=False)
    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("re_pin", 33), hold=False)
    
    if modem_type != "wifi":
        pm.set_cpu_freq("low-power")
    utils.log_info(f"Isurlog with serial number: {ser_num}")
    
    #Init RTC memory and EEPROM backup queue
    init_rtc_memory()
    init_eeprom_memory()

    # Declare status_led <º)))><
    status_led = LEDManagerULP()
    if status_led.is_enabled():
        
        if (pm.wakeup_reason == "Power-on reset"):
            status_led.load_ulp() #Load status_led only on Power-on reset
            
        status_led.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=2) #Set status_led blinking.
        
        
    #Shared MCP23008: GP6/GP7 are the accelerometer's interrupt pins
    #(owned/configured by accel_manager.py), GP3/GP4/GP5 are plain digital
    #inputs (owned/configured here). One instance, injected into both
    #consumers, so there is a single source of truth for this chip instead
    #of main.py reaching into another module's internals to get it.
    mcp_i2c_sda = config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 21)
    mcp_i2c_scl = config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 22)
    mcp_i2c_freq = config_manager.static_config.get("i2c_freq", 100000)
    mcp_i2c = I2C(0, scl=Pin(mcp_i2c_scl), sda=Pin(mcp_i2c_sda), freq=mcp_i2c_freq)
    if 0x20 in mcp_i2c.scan():
        mcp = MCP23008(mcp_i2c, address=0x20, start_init=False)

    #Check/Enable anti theft system
    accel = Accelerometer(mcp)
    if accel.hardware_ready:
        if config_manager.dynamic_config["general"].get("theft_alert", False):
            theft_confirmed = accel.check_wakeup()
            wake_up_sources.append(MCP_WAKEUP_PIN_NUM)
            if theft_confirmed and modem_type == "nb-iot" and config_manager.static_config.get("isurreach", False):
                
                if status_led.is_enabled():
                    status_led.set_ulp_pattern(pulse_num=0, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=5000, wake_up_period=10) #Disable status LED.
                    
                init_nb_iot_module()
                asyncio.run(_theft_alert_nbiot(nb_iot_module, ser_num))
                
        else:
            accel.disarm()

    if mcp is not None:
        # GP3/GP4/GP5 are unused by the accelerometer (GP6/GP7 are its
        # dedicated interrupt pins) - configure them once here as plain
        # digital inputs for read_all_sensors(), independent of
        # theft_alert and independent of accel.hardware_ready (the MCP
        # can be present even if the LIS2DH12 isn't). External active
        # signal on these pins -> no internal pull-up.
        from modules.digital_sensor import DigitalInputMCP23008
        mcp_digital_input = DigitalInputMCP23008(mcp)
        for _pin in (3, 4, 5):
            mcp_digital_input.configure_input(_pin, pullup=False)
    
    #Set VDC voltage via I2C
    pot = MCP4017()
    if pot.exists():
        pot.set_mt3608_voltage(vdc_voltage)
    
    magnet_pin = Pin(MAGNET_WAKEUP_PIN_NUM, Pin.IN, Pin.PULL_UP)
    #Is the magnet still around?
    if magnet_pin.value() == 0:
        
        #Turn on both regulator (for calibration por instance)
        pm.control_vdc(1)
        time.sleep_ms(250)
        pm.control_5v(1)
        if output_config.get("active_vdc", False):
            pm.control_digital_output(1)
        pm.set_cpu_freq("balanced") #CPU to 80 MHZ. BLE/WiFi does not work below 80MHZ
        #Import BLE libraries
        import binascii
        from modules import ble_manager
        asyncio.run(ble_mode_task())
        if modem_type != "wifi":
            pm.set_cpu_freq("low-power")
        
    # --- NB-IoT/WiFi/LoRaWAN Setup and Logic ---
    en_com_module = Pin(EN_COM_MODULE, Pin.OUT, Pin.PULL_UP, value=1, hold=True)

    # --- EVENT LOOP START ---
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("ESP32 execution stopped by user.")