import time
from machine import Pin, reset, WDT, UART, deepsleep, I2C
from modules import power_manager
from modules import utils, battery_monitor
from modules.config_manager import config_manager
from lib.IsurlogLPP import IsurlogLPPEncoder
from modules.rtc_memory import RTC_Memory
from modules.led_manager import LEDManagerULP
from lib.ota import rollback

#Enable WDT

try:
    wdt = WDT(timeout=600000)
    wdt.feed() # Feed at boot
    print("Watchdog Timer enabled to 10 minutes.")
except Exception as e:
    print(f"Could not enable Watchdog Timer: {e}")
    wdt = None

def read_all_sensors(pm, register_mode, ble = False, n_loop = 1, n_seconds = 10):
    
    data = [[0, "addUnixTime", pm.get_unix_time()]]
    alarm_condition = False

    # Pre-check of activated sensors
    modbus_config = config_manager.get_dynamic("modbus_config")
    analog_config = config_manager.get_dynamic("analog_config")
    pt100_config = config_manager.get_dynamic("pt100_config")
    output_config = config_manager.get_dynamic("output_config")

    num_modbus_enabled = sum(ch.get("enable", False) for ch in modbus_config.get("inputs", [])) if modbus_config else 0
    num_analog_enabled = sum(ch.get("enable", False) for ch in analog_config.get("inputs", [])) if analog_config else 0
    pt100_enabled = pt100_config and pt100_config.get("enable", False)

    # Battery measurement
    batt_monitor = battery_monitor.BatteryMonitor()
    battery_voltage = batt_monitor.read_voltage()

    if battery_voltage is not None:
        print(f"Battery Voltage: {battery_voltage}mV")
        data.append([0, "addVoltageInput", battery_voltage])
    else:
        print("Error reading battery voltage.")
        
    Pin(39, Pin.IN, Pin.PULL_UP, hold=False)

    reg_on_t = time.time()
    
    if not ble:
            
        if num_modbus_enabled > 0 or num_analog_enabled > 0 or pt100_enabled:
            pm.control_vdc(1)
            time.sleep_ms(250)
            
        if num_modbus_enabled > 0 or pt100_enabled:
            pm.control_5v(1)
            
        if output_config.get("active_vdc", False):
            pm.control_digital_output(1)
        
    # Digital input
    digital_config = config_manager.get_dynamic("digital_config")

    if digital_config and digital_config.get("enable", False):
        from modules.digital_sensor import DigitalInputULP
        #Digital input pulse counter mode
        if digital_config.get("counter", True): 
            ulp_digital_input = DigitalInputULP()
            if not ulp_digital_input.ulp_loaded(): #Init ULP coprocessor only if the magic token is not set
                ulp_digital_input.load_ulp()
            pulses = ulp_digital_input.get_pulse_count()
            data.append([0, "addDigitalInput", pulses])
            
            #Check alarms
            if (register_mode and (digital_config.get("low_cond", False)) and (pulses*digital_config.get("pulse_weight", 1) < digital_config.get("low", 0))):
                alarm_condition = True
            if (register_mode and (digital_config.get("high_cond", False)) and (pulses*digital_config.get("pulse_weight", 1) > digital_config.get("high", 0))):
                alarm_condition = True
        
        #Digital input state mode
        else:
            
            digital_input = Pin(DIO0_PIN, Pin.IN)
            state = digital_input.value()
            data.append([0, "addDigitalInput", state])
            if state == 0:
                wake_up_sources.append(DIO0_PIN)
                
    # Internal temperature and humidity sensor (BME680 or SHT30)
    int_th_config = config_manager.get_dynamic("int_th_sensor")
    # External temperature and humidity sensor (BME280 only?)
    ext_th_config = config_manager.get_dynamic("ext_th_sensor")
    
    th_configs = [int_th_config, ext_th_config]
    
    read_sensors = []
    
    for th_config in th_configs:

        if th_config and th_config.get("enable", True):
            
            print("Reading internal temperature and humidity sensor...")
            
            i2c = I2C(scl=Pin(22), sda=Pin(21))
            devices = i2c.scan()
            sensor_data = None
            
            if (68 in devices) and (68 not in read_sensors):
                print("SHT30 sensor found!")
                from modules import sht30_sensor
                sht_sensor = sht30_sensor.SHT30Sensor()
                sensor_data = sht_sensor.read_data()
                read_sensors.append(68)
                
            elif (118 in devices) and (118 not in read_sensors):
                print("BME sensor found!")
                from modules import bme_sensor
                CHIP_ID = bme_sensor.BME_CHIP_ID()
                
                if CHIP_ID == 88: #Sensor is BME280
                    print("Sensor is BME280!")
                    bme_sensor = bme_sensor.BME280Sensor()
                    sensor_data = bme_sensor.read_data()
                    read_sensors.append(118)
                    
                elif CHIP_ID == 97: #Sensor is BME680
                    print("Sensor is BME680!")
                    bme_sensor = bme_sensor.BME680Sensor(IAQ=False)  # Set IAQ=True if you want IAQ calculation
                    sensor_data = bme_sensor.read_data()
                    read_sensors.append(118)
                else:
                    print(f"Unkwon CHIP ID found: {CHIP_ID}")

            if sensor_data:
                print(f"BME680 - Temperature: {sensor_data['temperature']:.2f} °C, Humidity: {sensor_data['humidity']:.2f} %RH")
                data.append([len(read_sensors)-1, "addTemperatureSensor", sensor_data['temperature']])
                data.append([len(read_sensors)-1, "addHumiditySensor", sensor_data['humidity']])

                #Check temperature alarms
                if (register_mode and (th_config.get("temperature_low_cond", False)) and (sensor_data['temperature'] < th_config.get("temperature_low", 0))):
                    alarm_condition = True
                if (register_mode and (th_config.get("temperature_high_cond", False)) and (sensor_data['temperature'] > th_config.get("temperature_high", 0))):
                    alarm_condition = True

                #Check humidity alarms
                if (register_mode and (th_config.get("humidity_low_cond", False)) and (sensor_data['humidity'] < th_config.get("humidity_low", 0))):
                    alarm_condition = True
                if (register_mode and (th_config.get("humidity_high_cond", False)) and (sensor_data['humidity'] > th_config.get("humidity_high", 0))):
                    alarm_condition = True
                    
        else:
            print("No temperature and humidity sensor configured in dymanic_config.json.")
        
        
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
                time.sleep(0.5)
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
                time.sleep(0.5)
            utils.log_info("Modbus pre-acquisition delay finished.")


    # --- Sampling loop ---
    start_time = time.time()
    loop_counter = 0
    
    while (time.time() - start_time < n_seconds) and (loop_counter < n_loop):
            
        # --- Temperature PT100 Input ---
        if pt100_enabled and max31865_module:
            temperature = max31865_module.read_temperature()
            if temperature is not None:
                print(f"  Loop {loop_counter}: PT100 Temp: {temperature:.2f} °C")
                sum_pt100 += temperature
                count_pt100 += 1
                
                # Check alarms
                if (register_mode and (pt100_config.get("low_cond", False)) and (temperature < pt100_config.get("low", 0))):
                    alarm_condition = True
                if (register_mode and (pt100_config.get("high_cond", False)) and (temperature > pt100_config.get("high", 0))):
                    alarm_condition = True
            else:
                print(f"  Loop {loop_counter}: Error reading PT100 temperature.")

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
                time.sleep_ms(100)

                if value is not None:
                    if not is_fp:
                        value = value[0]
                    
                    # Apply offsets
                    if fc == 3 or fc == 4:
                        if invert:
                            value = offset - value/number_of_decimals   
                        else:
                            value = value/number_of_decimals - offset
                    
                    print(f"  Loop {loop_counter}: Modbus Ch {channel}: {value}")

                    if fc == 1 or fc == 2 or long_int:
                        sum_modbus_generic[channel] += value
                        count_modbus_generic[channel] += 1
                    else:
                        sum_modbus[channel] += value
                        count_modbus[channel] += 1

                    # Check alarms
                    if register_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                        alarm_condition = True
                    if register_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0):
                        alarm_condition = True
                else:
                    print(f"  Loop {loop_counter}: Error reading Modbus channel {channel}.")

        # --- Analog inputs ---
        if num_analog_enabled > 0 and analog_module:
            for channel_config in analog_config["inputs"]:
                if not channel_config.get("enable", False):
                    continue # Skip disabled channels

                channel = channel_config.get("channel")
                value = analog_module.read_analog(3 - channel) # Hardware-specific mapping
                value = analog_module.convert_value(value, channel_config.get("zero", 0),  channel_config.get("full_scale", 100))

                if value is not None:
                    print(f"  Loop {loop_counter}: Analog Ch {channel}: {value}")
                    sum_analog[channel] += value
                    count_analog[channel] += 1

                    # Check alarms 
                    if register_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                        alarm_condition = True
                    if register_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0):
                        alarm_condition = True
                else:
                    print(f"  Loop {loop_counter}: Error reading Analog channel {channel}.")
        
        # --- Loop end ---
        loop_counter += 1
        if wdt:
            print("Feeding WDT from read_all_sensors task.")
            wdt.feed()
        if (loop_counter < n_loop):
            time.sleep(5)
                
                
    if not ble:
        pm.control_vdc(0)
        pm.control_5v(0)
        if output_config.get("active_vdc", False):
            pm.control_digital_output(0)
    
    # --- CALCULATE AVERAGE VALUES & ADD TO DATA ---

    if pt100_enabled:
        if count_pt100 > 0:
            avg_pt100 = sum_pt100 / count_pt100
            print(f"Final PT100 Avg: {avg_pt100:.2f} (from {count_pt100} readings)")
            data.append([0, "addTemperatureInput", avg_pt100])
        else:
            print("No valid PT100 readings obtained.")
            data.append([0, "addTemperatureInput", 0]) # Add 0 for error

    if num_analog_enabled > 0:
        for channel, total_sum in sum_analog.items():
            count = count_analog[channel]
            if count > 0:
                avg_analog = total_sum / count
                print(f"Final Analog Ch {channel} Avg: {avg_analog:.2f} (from {count} readings)")
                data.append([channel, "addAnalogInput", avg_analog])
            else:
                print(f"No valid Analog Ch {channel} readings obtained.")
                data.append([channel, "addAnalogInput", 0.0]) # Add 0 for error

    if num_modbus_enabled > 0:
        # Average for FC 3/4 (float)
        for channel, total_sum in sum_modbus.items():
            count = count_modbus[channel]
            if count > 0:
                avg_modbus = total_sum / count
                print(f"Final Modbus Ch {channel} Avg: {avg_modbus:.2f} (from {count} readings)")
                data.append([channel, "addModbusInput", avg_modbus])
            else:
                print(f"No valid Modbus Ch {channel} readings obtained.")
                data.append([channel, "addModbusInput", 0.0])

        # Average for FC 1/2 (int/generic)
        for channel, total_sum in sum_modbus_generic.items():
            count = count_modbus_generic[channel]
            if count > 0:
                # El promedio de enteros debe redondearse a entero
                avg_modbus_gen = int(round(total_sum / count, 0))
                print(f"Final Modbus-Gen Ch {channel} Avg: {avg_modbus_gen} (from {count} readings)")
                data.append([channel, "addModbusGenericInput", avg_modbus_gen])
            else:
                print(f"No valid Modbus-Gen Ch {channel} readings obtained.")
                data.append([channel, "addModbusGenericInput", 0])
                
    #Digital output
        
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
        
    do_config = config_manager.get_dynamic("output_config")
    latency_time = config_manager.dynamic_config["general"].get("latency_time", 10) * 60
    if do_config:
        if not output_config.get("active_vdc", False) and output_config.get("crontab", "inactive") != "inactive":
            from lib import crontab
                
            cron = output_config.get("crontab", "inactive")
            print(f'ON Cron job for DO is configured: {cron}')
            entry = crontab.CronTab(cron)
            
            if entry.test():
                pm.control_digital_output(1)
            else:
                pm.control_digital_output(0)
    
    return data, alarm_condition

def process_ble_command(received_bytes):
    """
    Processes commands received via BLE.
    It converts bytes to a hex string, decodes it, and applies the configuration.
    """
    utils.log_info(f"BLE command received (raw bytes): {repr(received_bytes)}")
    try:
        # 1. Convert the received bytes to a hexadecimal string
        hex_payload = ubinascii.hexlify(received_bytes).decode('ascii')
        utils.log_info(f"Payload converted to hex: '{hex_payload}'")
        encoder = IsurlogLPPEncoder()
        decoded_message = encoder.decode(hex_payload.upper())

        # 2. Call the function from your ConfigUpdater module to do the work
        #    This function already decodes and saves the JSON file.
        config_manager.apply_conf_update(decoded_message)
    except Exception as e:
        utils.log_error(f"Fatal error processing BLE command: {e}")

async def ble_mode_task(blinky, pm, ser_num):
    print("Magnet wakeup detected. Starting BLE mode...")
    
    # Init Bluetooh manager
    ble = ble_manager.BLEManager(device_name=f"Isurlog-{ser_num}", command_callback=process_ble_command)
    
    # Bucle de lectura y envío en tiempo real
    ble_start = time.time()
    
    if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
        blinky.set_ulp_pattern(pulse_num=5, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
    
    while (not ble.client_connected) and (time.time() - ble_start < 120):
        await asyncio.sleep(2)
        
    if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
        blinky.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
        
    if ble.client_connected:        
        while not ble.client_disconnected: # Wait until client disconnects
            # Read data from active sensors
            live_data, _ = read_all_sensors(pm, 0, ble = True)

            # Encode and send by bluetooh
            encoder = IsurlogLPPEncoder()
            live_payload = encoder.encode(live_data)
            if live_payload:
                ble.update_data_payload(live_payload)
            
            await asyncio.sleep(10)
            
            if wdt:
                print("Feeding WDT from Bluetooh task.")
                wdt.feed()
    
    print("BLE client disconnected. Continiuing with normal mode...")
    time.sleep(2)

if __name__ == "__main__":

    print("\n####WELCOME TO ISURLOG OS v.1.0.4 MICROPYTHON FLAVOUR####\n")
    ser_num = config_manager.static_config.get("serial", "c-000")
    modem_type = config_manager.static_config.get("modem", "nb-iot")
    # --- Power Management ---
    pm = power_manager.PowerManager()
    if modem_type != "wifi":
        pm.set_cpu_freq("low-power")
    print(f"Isurlog with serial number: {ser_num}")
    
    #Init RTC memory
    rtc_memory = RTC_Memory(max_payload_size = config_manager.dynamic_config["general"].get("max_payload_size", 256))

    # --- Initialize Variables ---

    wake_up_sources = []
    register_mode = config_manager.get_dynamic("general").get("register_mode", 0) #Register mode, 0 normal, 1 conditional
    continuous_mode = config_manager.get_dynamic("general").get("continuous_mode", False)
    n_loop_cycles = config_manager.get_dynamic("general").get("loop_cycles", 1)

    # Declare Blinky <º)))><
    blinky = LEDManagerULP()
    if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
        
        if (pm.wakeup_reason == "Power-on reset"):
            pm.set_cpu_freq("balanced")
            blinky.load_ulp() #Load Blinky only on Power-on reset
            if modem_type != "wifi":
                pm.set_cpu_freq("low-power")
        blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=2) #Set Blinky blinking.

    #Pin Configuration
    output_config = config_manager.get_dynamic("output_config")
    EN_COM_MODULE = config_manager.static_config.get("pinout", {}).get("control", {}).get("en_nbiot_pin", 5)
    DIO0_PIN = config_manager.static_config.get("pinout", {}).get("di0_pin", 36)    
    MAGNET_WAKEUP_PIN_NUM = config_manager.static_config.get("pinout", {}).get("magnet_pin", 35)

    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("ro_pin", 14), Pin.IN, Pin.PULL_UP, hold=False)
    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("di_pin", 23), hold=False)
    Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("re_pin", 33), hold=False)
    
    magnet_pin = Pin(MAGNET_WAKEUP_PIN_NUM, Pin.IN, Pin.PULL_UP)
    #Is the magnet still around?
    if magnet_pin.value() == 0:
        
        #Turn on both regulator (for calibration por instance)
        pm.control_vdc_soft_start(1)
        time.sleep_ms(250)
        pm.control_5v(1)
        if output_config.get("active_vdc", False):
            pm.control_digital_output(1)
        pm.set_cpu_freq("balanced") #CPU to 80 MHZ. BLE/WiFi does not work below 80MHZ
        #Import BLE libraries
        import ubinascii
        import uasyncio as asyncio
        from modules import ble_manager
        asyncio.run(ble_mode_task(blinky, pm, ser_num))
        if modem_type != "wifi":
            pm.set_cpu_freq("low-power")
        
    #Read all sensors (if activated)
    loop_seconds = pm.seconds2wakeup()
    data, alarm_condition = read_all_sensors(pm, register_mode, n_loop = n_loop_cycles, n_seconds = loop_seconds)

    #Get battery voltage from data to configure Blinky later
    found_list = None
    for sublist in data:
      if sublist[1] == 'addVoltageInput':
        found_list = sublist
        break
    battery_voltage = found_list[2]

    # --- Encode data to Isurlog LPP format ---
    encoder = IsurlogLPPEncoder()
    print(f"Data to encode: {data}")
    encoded_payload = encoder.encode(data)
    
    compact_register = config_manager.get_dynamic("general").get("compact_register", False)
    
    if compact_register:
        cycle = rtc_memory.get_counter()
        is_last_cycle = cycle >= rtc_memory.n_cycles - 1
        
        # We discard the payload (store an empty string) if:
        # - It's NOT the last cycle before a scheduled send.
        # - alarm_condition == False
        if not is_last_cycle and not alarm_condition:
            print("Compact profile enabled: Discarding non-alarm, intermediate reading.")
            encoded_payload = ""

    internal_register = config_manager.get_dynamic("general").get("internal_register", False)

    if encoded_payload:
        print(f"Encoded Payload: {encoded_payload}")
        if internal_register:
            from modules import internal_storage
            internal_storage_module = internal_storage.InternalStorage()
            if internal_storage_module.store_payload(encoded_payload): 
                print(f"Payload stored in internal flash: {encoded_payload}")
            else:
                print(f"Failed to store payload in internal flash: {encoded_payload}")
        else:
            print("Internal register is disabled.")
    else:
        print("Encoding failed. Sending empty payload")
        encoded_payload = ""  # Send empty payload on failure
        
    if not rtc_memory.store_payload(encoded_payload):
        print("Could not store payload in RTC memory.")
    else:
        print(f"Stored payload. Cycle {rtc_memory.get_counter()} of {rtc_memory.n_cycles}")

    # --- NB-IoT Setup and Logic ---
    en_com_module = Pin(EN_COM_MODULE, Pin.OUT, Pin.PULL_UP, value=1, hold=True)

    if modem_type == "wifi":
        from modules import wifi
        base_topic = config_manager.static_config.get("mqtt", {}).get("base_topic", "isurlog")
    if modem_type == "nb-iot":
        if config_manager.static_config.get("isurreach", False):
            from modules import nb_iot_isurreach_som as nb_iot
        else:
            from modules import nb_iot
        base_topic = config_manager.static_config.get("mqtt", {}).get("base_topic", "isurlog")
        wake_up_sources.append(config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("esp_wake_up", 34))
        
    if modem_type == "lorawan":
        from modules import lorawan

    #First boot, connect to NB-IoT o LoRaWAN network
    if pm.wakeup_reason == "Power-on reset":
        if modem_type == "nb-iot":
            print("Power-on reset: Initializing NB-IoT ...")
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
            nb_iot_module = nb_iot.NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)
            nb_iot_module.hard_reset()
            nb_iot_module.select_SIM(config_manager.dynamic_config["communications"]["nb_iot"].get("sim", "eSIM"))
            #nb_iot_module.get_imei_ccid()
            #nb_iot_module.register_SIM()
            if not nb_iot_module.connect(config_manager.dynamic_config["communications"]["nb_iot"].get("mode", "LTE-M"), apn = config_manager.dynamic_config["communications"]["nb_iot"].get("apn", None)):
                print("Failed to connect to NB-IoT")
                pm.configure_wakeup_sources(wake_up_sources)
                pm.go_to_sleep()
            
            keep_alive = ((config_manager.dynamic_config["general"].get("latency_time", 10) * 60)+20) * config_manager.dynamic_config["general"].get("register_acumulator", 1)
            nb_iot_module.mqtt_configure(ser_num, keep_alive, 0)
            if not nb_iot_module.mqtt_connect(config_manager.static_config.get("mqtt", {}).get("user", ""), config_manager.static_config.get("mqtt", {}).get("passwd", ""), config_manager.static_config.get("mqtt", {}).get("ip", ""), config_manager.static_config.get("mqtt", {}).get("port", 1883)):
                print("Failed to connect to MQTT broker")
                pm.configure_wakeup_sources(wake_up_sources)
                pm.go_to_sleep()
            
            if not pm.rtc_available:
                new_time = nb_iot_module.get_network_time()
                print(f"New requested time UTC: {new_time}")
                pm.set_rtc_time(new_time)
                
            nb_iot_module.mqtt_subscribe(f"{base_topic}/config/{ser_num}", QoS=2)
            
            if not rtc_memory.should_transmit():
                nb_iot_module.sleep()
            
        if modem_type == "lorawan":
            print("Power-on reset: Initializing LoRaWAN...")
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
            en_lorawan = Pin(EN_COM_MODULE, Pin.OUT, value=1, hold=True)
            lorawan_module = lorawan.LoRaWAN(uart_id=2, tx_pin=2, rx_pin=4, baudrate=115200)
            if not lorawan_module.connect():
                print("Failed to connect to LoRaWAN")
                pm.configure_wakeup_sources(wake_up_sources)
                pm.go_to_sleep()
            lorawan_module.set_confirmed_mode(0) # Enable/disable send ACK (optional)
            if not pm.rtc_available:
                lorawan_module.request_time() #Enable LoRaWAN time requests (time is available after 1st transmission)
            if not rtc_memory.should_transmit():
                lorawan_module.sleep()
            #lorawan_module.enable_auto_sleep() # Enable auto sleep.
                
    #Get previous alarm flag from rtc memory.
    previous_cycle_alarm = rtc_memory.get_alarm_flag()
    #Update rtc memory alarm_flag
    rtc_memory.set_alarm_flag(alarm_condition)
    
    print(f"Previous cycle alarm flag: {previous_cycle_alarm}. Current cycle alarm flag: {alarm_condition}")
                
    #NB-IoT or LoRaWAN connection should already be established.
    if rtc_memory.should_transmit() or alarm_condition or previous_cycle_alarm or pm.wakeup_reason == "RTC GPIO reset" or pm.wakeup_reason == "Watchdog reset": #RTC GPIO reset for magnet wakeup. Watchdog reset for NB-IoT module wakeup.
        rx = Pin(2, hold=False)
        tx = Pin(4, hold=False)
        
        if modem_type == "wifi":
            print("Power-on reset: Initializing Wifi ...")
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=3, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=200,  wake_up_period=2)
                
            if not wifi.is_connected():
            
                ssid = config_manager.dynamic_config["communications"]["wifi"].get("ssid", None)
                password = config_manager.dynamic_config["communications"]["wifi"].get("password", None)
                
                if (ssid != None and password != None):
                    if wifi.do_connect(ssid, password, timeout_seconds=15):
                        if not pm.rtc_available:
                            import ntptime
                            ntptime.settime()
                            new_time = time.localtime()
                            pm.set_rtc_time(new_time, mode = "WiFi")
                            
                        from modules.umqttsimple import MQTTClient
                        mqtt_client = MQTTClient(ser_num, config_manager.static_config.get("mqtt", {}).get("ip", ""), user=config_manager.static_config.get("mqtt", {}).get("user", ""), password=config_manager.static_config.get("mqtt", {}).get("passwd", ""))
                        try:
                            mqtt_client.connect()
                            mqtt_client.subscribe(f"{base_topic}/config/{ser_num}")
                        except Exception as err:
                            print("Could not connect to the MQTT broker!")
                            pm.configure_wakeup_sources(wake_up_sources)
                            pm.go_to_sleep()
                        
                    else:
                        print("Could not establish Wifi connection!")
                        pm.configure_wakeup_sources(wake_up_sources)
                        pm.go_to_sleep()
                else:
                    print("No SSID and password provided for WiFi.")
                
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=250, delay_on=5, delay_off=20, inter_delay=250,  wake_up_period=5)
                
            print("Transmitting data throught WiFi...")
            payloads = rtc_memory.get_payloads()
            rtc_memory.clear_memory()
            print(f"Retrieved payloads: {payloads}")
        
            for i, payload in enumerate(payloads):
                #Publish not empty payloads only.
                if payload:
                    print(f"Publishing payload {i+1}: {payload}")
                    if mqtt_client.publish(f"{base_topic}/datos/{ser_num}", payload):
                        print(f"Failed to publish payload {i+1}")
                    time.sleep(1)
                else:
                    print(f"Skipping empty payload at index {i+1}")
                    
            received_mqtt_messages = mqtt_client.check_msg()
            print(f"Received MQTT messages: {received_mqtt_messages}")
            if received_mqtt_messages:
                print(f"Received {len(received_mqtt_messages)} MQTT message(s).")
                for topic, msg in received_mqtt_messages:
                    msg = msg.decode('utf-8')
                    if msg == "Wake": #WAKE UP MESSAGE
                        pass
                    elif msg == "REPL": #ENABLE REMOTE REPL
                        if not mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Connected"):
                            mqtt_client.subscribe(f"{base_topic}/repl_in/{ser_num}")
                            from modules.remote_repl import handle_remote_repl_wifi
                            handle_remote_repl_wifi(ser_num, base_topic, wdt, mqtt_client)
                            
                    elif "update" in msg: #FIRMWARE UPDATE MESSAGE
                        print("Starting OTA update process...")
                        update_instructions = msg.split(" ")
                        if len(update_instructions) == 5:
                            from modules import update_manager
                            update_type, server, port, file_name, checksum = update_instructions
                            print(f"Received instructions: Update_type: {update_type} Server: {server} Port: {port} File: {file_name} Checksum: {checksum}")
                            
                            if update_type == "main_update":
                                if nb_iot_module.download_file(server, port, file_name, file_name, chunk_size=2048):
                                    if update_manager.verify_file_checksum(checksum, filename = file_name):
                                        update_manager.perform_update()
                                        print("Update process finished, rebooting in 5 seconds...")
                                        if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update OK"):
                                            print(f"Failed to publish response")
                                        time.sleep(5)
                                        reset()

                            if update_type == "upython_update":
                                if nb_iot_module.download_file(server, port, file_name, file_name, wdt = wdt, chunk_size=8192):
                                    if(update_manager.decode_base64_file(file_name, "/micropython_decoded.bin")):
                                        if update_manager.verify_file_checksum(checksum, filename = "/micropython_decoded.bin"):
                                            print("Decoding successful!")
                                            ota_succeded = False
                                            from lib.ota import update
                                            try:
                                                with update.OTA(verbose=True, reboot=False) as ota_updater:
                                                    with open("/micropython_decoded.bin", "rb") as f:
                                                        ota_updater.from_stream(f)
                                                print("OTA update prepared.")
                                                ota_succeded = True
                                            except Exception as e_ota:
                                                print(f"Error during OTA: {e_ota!r}")

                                            # Delete the b64 file after use to free space.
                                            try:
                                                import os
                                                os.remove(file_name)
                                                print(f"Temporary file '{file_name}' deleted.")
                                                if ota_succeded:
                                                    print("Update process finished, rebooting in 5 seconds...")
                                                    if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update OK"):
                                                        print(f"Failed to publish response")
                                                    time.sleep(5)
                                                    reset()
                                            except OSError:
                                                 pass
                                        else:
                                            print("Decoding failed.")
                        
                        #If code reaches this point the update was unsuccessful
                        if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update FAILED"):
                            print(f"Failed to publish response")
                            
                    elif "cron" in msg: #New cron syntax.
                        print("Received new cron configuration.")
                        cron_config = msg.split(":")
                        print(cron_config)
                        if len(cron_config) == 2:
                            cron_syntax = cron_config[1]
                            config_manager.dynamic_config['output_config']['crontab'] = cron_syntax
                            config_manager.save_dynamic_config()
                            print(f"Crontab successfully updated to: {cron_syntax}")
                        
                    else: #NEW CONFIGURATION MESSAGE
                        print(f"Processing message on topic: {topic}")
                        print(f"Message content: {msg}")
                        decoded_message = encoder.decode(msg)
                        print(f"New MQTT downlink: {decoded_message}")
                        config_manager.apply_conf_update(decoded_message) #Save new downlink configuration.
                    
        if modem_type == "nb-iot":
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=250, delay_on=5, delay_off=20, inter_delay=250,  wake_up_period=5)
            nb_iot_module = nb_iot.NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)
            print("Transmitting data throught NB-IoT...")
            payloads = rtc_memory.get_payloads()
            rtc_memory.clear_memory()
            print(f"Retrieved payloads: {payloads}")

            nb_iot_module.wake_up()  # Wake up *only* when transmitting
            if not nb_iot_module.mqtt_check_connection():
                if not nb_iot_module.check_network_connection():
                    nb_iot_module.reset() #Reset NB-IoT module
                    time.sleep(5)
                    reset() #Reset ESP32
                if not nb_iot_module.mqtt_connect(config_manager.static_config.get("mqtt", {}).get("user", ""), config_manager.static_config.get("mqtt", {}).get("passwd", ""), config_manager.static_config.get("mqtt", {}).get("ip", "80.24.238.36"), config_manager.static_config.get("mqtt", {}).get("port", 1883)):
                    print("Failed to connect to MQTT broker")
                    pm.configure_wakeup_sources(wake_up_sources)
                    pm.go_to_sleep()
                nb_iot_module.mqtt_subscribe(f"{base_topic}/config/{ser_num}", QoS=2)
                    
            for i, payload in enumerate(payloads):
                #Publish not empty payloads only.
                if payload:
                    print(f"Publishing payload {i+1}: {payload}")
                    if not nb_iot_module.mqtt_publish(f"{base_topic}/datos/{ser_num}", payload):
                        print(f"Failed to publish payload {i+1}")
                    time.sleep(1)
                else:
                    print(f"Skipping empty payload at index {i+1}")
                
            received_mqtt_messages = nb_iot_module.get_mqtt_messages()

            if received_mqtt_messages:
                print(f"Received {len(received_mqtt_messages)} MQTT message(s).")
                for msg in received_mqtt_messages:
                    if msg['message'] == "Wake": #WAKE UP MESSAGE
                        pass
                    
                    elif msg['message'] == "REPL": #ENABLE REMOTE REPL
                        if nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Connected"):
                            nb_iot_module.mqtt_subscribe(f"{base_topic}/repl_in/{ser_num}", QoS=2)
                            from modules.remote_repl import handle_remote_repl_nb_iot
                            handle_remote_repl_nb_iot(ser_num, base_topic, wdt, nb_iot_module)
                            
                    elif "update" in msg['message']: #FIRMWARE UPDATE MESSAGE
                        print("Starting OTA update process...")
                        update_instructions = msg['message'].split(" ")
                        if len(update_instructions) == 5:
                            from modules import update_manager
                            update_type, server, port, file_name, checksum = update_instructions
                            print(f"Received instructions: Update_type: {update_type} Server: {server} Port: {port} File: {file_name} Checksum: {checksum}")
                            
                            if update_type == "main_update":
                                if nb_iot_module.download_file(server, port, file_name, file_name, chunk_size=2048):
                                    if update_manager.verify_file_checksum(checksum, filename = file_name):
                                        update_manager.perform_update()
                                        print("Update process finished, rebooting in 5 seconds...")
                                        if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update OK"):
                                            print(f"Failed to publish response")
                                        time.sleep(5)
                                        reset()

                            if update_type == "upython_update":
                                if nb_iot_module.download_file(server, port, file_name, file_name, wdt = wdt, chunk_size=8192):
                                    if(update_manager.decode_base64_file(file_name, "/micropython_decoded.bin")):
                                        if update_manager.verify_file_checksum(checksum, filename = "/micropython_decoded.bin"):
                                            print("Decoding successful!")
                                            ota_succeded = False
                                            from lib.ota import update
                                            try:
                                                with update.OTA(verbose=True, reboot=False) as ota_updater:
                                                    with open("/micropython_decoded.bin", "rb") as f:
                                                        ota_updater.from_stream(f)
                                                print("OTA update prepared.")
                                                ota_succeded = True
                                            except Exception as e_ota:
                                                print(f"Error during OTA: {e_ota!r}")

                                            # Delete the b64 file after use to free space.
                                            try:
                                                import os
                                                os.remove(file_name)
                                                print(f"Temporary file '{file_name}' deleted.")
                                                if ota_succeded:
                                                    print("Update process finished, rebooting in 5 seconds...")
                                                    if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update OK"):
                                                        print(f"Failed to publish response")
                                                    time.sleep(5)
                                                    reset()
                                            except OSError:
                                                 pass
                                        else:
                                            print("Decoding failed.")
                        
                        #If code reaches this point the update was unsuccessful
                        if not nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update FAILED"):
                            print(f"Failed to publish response")
                            
                    elif "cron" in msg['message']: #New cron syntax.
                        print("Received new cron configuration.")
                        cron_config = msg['message'].split(":")
                        print(cron_config)
                        if len(cron_config) == 2:
                            cron_syntax = cron_config[1]
                            config_manager.dynamic_config['output_config']['crontab'] = cron_syntax
                            config_manager.save_dynamic_config()
                            print(f"Crontab successfully updated to: {cron_syntax}")
                        
                    else: #NEW CONFIGURATION MESSAGE
                        print(f"Processing message on topic: {msg['topic']}")
                        print(f"Message content: {msg['message']}")
                        decoded_message = encoder.decode(msg['message'])
                        print(f"New MQTT downlink: {decoded_message}")
                        config_manager.apply_conf_update(decoded_message) #Save new downlink configuration.
            nb_iot_module.sleep()
            
        if modem_type == "lorawan":
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=250, delay_on=5, delay_off=20, inter_delay=250,  wake_up_period=5)
            lorawan_module = lorawan.LoRaWAN(uart_id=2, tx_pin=2, rx_pin=4, baudrate=115200)
            if not lorawan_module.check_network_connection():
                    lorawan_module.reset() #Reset LoRaWAN module
                    reset() #Reset ESP32
            print("Transmitting data throught LoRaWAN...")
            payloads = rtc_memory.get_payloads()
            rtc_memory.clear_memory()
            print(f"Retrieved payloads: {payloads}")
                
            for i, payload in enumerate(payloads):
                #Publish not empty payloads only.
                if payload:
                    print(f"Publishing payload {i+1}: {payload}")
                    if not lorawan_module.send_uplink(2, payload):
                        print(f"Failed to publish payload {i+1}")
                    time.sleep(1)
                else:
                    print(f"Skipping empty payload at index {i+1}")
                    
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=2)
            if not pm.rtc_available: #Time should be available now.
                new_time = lorawan_module.get_network_time()
                print(f"New requested time UTC: {new_time}")
                pm.set_rtc_time(new_time, mode = "LoRaWAN")
                
            downlink = lorawan_module.get_downlink()
            if downlink != None:
                decoded_downlink = encoder.decode(downlink)
                print(f"New downlink: {decoded_downlink}")
                config_manager.apply_conf_update(decoded_downlink) #Save new downlink configuration.
            lorawan_module.sleep()
            
    if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
        
        if (battery_voltage < 3600):
            
            blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=20)
            
        else:
            
            blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500,  wake_up_period=10)

    pm.configure_wakeup_sources(wake_up_sources)
    rollback.cancel() #We can cancel rollback protection if program reaches this point.
    if continuous_mode:
        deepsleep(1000)
    pm.go_to_sleep()


























