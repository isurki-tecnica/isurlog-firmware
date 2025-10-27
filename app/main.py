import time
from machine import Pin, reset, WDT, UART
from modules import power_manager, utils, battery_monitor
from modules.config_manager import config_manager
from lib.IsurlogLPP import IsurlogLPPEncoder
from modules.rtc_memory import RTC_Memory
from modules.led_manager import LEDManagerULP
import uio
import builtins

#Enable WDT

try:
    wdt = WDT(timeout=600000)
    wdt.feed() # Feed at boot
    print("Watchdog Timer enabled to 10 minutes.")
except Exception as e:
    print(f"Could not enable Watchdog Timer: {e}")
    wdt = None
    
def execute_code(code):
    buffer = uio.StringIO()
    try:
        # Override print to capture its output
        def print_override(*args, **kwargs):
            builtins.print(*args, **kwargs, file=buffer)
        builtins.print, original_print = print_override, builtins.print

        try:
            # Try to evaluate as an expression
            result = eval(code)
            if result is not None:
                buffer.write(str(result))
        except SyntaxError:
            # Otherwise execute as statements
            exec(code, globals())
    except Exception as e:
        return "{}: {}".format(type(e).__name__, str(e))
    finally:
        builtins.print = original_print

    output = buffer.getvalue()
    return output if output else None

def handle_remote_repl():
    """
    Enables REPL mode.
    """
    uart = UART(2, baudrate=115200, tx=Pin(4), rx=Pin(2), timeout=1000)
    command_topic = f"isurlog/repl_in/{ser_num}" 
    print(f"--- Remote REPL Mode Activated. Listening on {command_topic} ---")
    
    repl_active = True
    last_message_time = time.ticks_ms()

    while repl_active:
        #Read all UART buffer
        
        if (time.ticks_diff(time.ticks_ms(), last_message_time) > 120000):
            print("Disconnecting from online REPL due to timeout...")
            nb_iot_module.mqtt_publish(f"isurlog/repl_out/{ser_num}", "Disconnected")
            repl_active = False
            
        if uart.any():
            uart_bytes = uart.read()

            try:
                block_str = uart_bytes.decode('utf-8').strip()
                lines = block_str.splitlines()

                # Check is it's a MQTT message
                if lines and lines[0].startswith('#XMQTTMSG:'):
                    
                    header_line = lines[0]

                    if len(lines) >= 3:
                        parts = header_line.split(',')

                        topic_str = lines[1]
                        message_str = lines[2]
                        
                        last_message_time = time.ticks_ms()
                        
                        print(f"MQTT MSG on topic '{topic_str}': {message_str}")
                        
                        if message_str.strip() == "logout":

                            nb_iot_module.mqtt_publish(f"isurlog/repl_out/{ser_num}", "Disconnected")
                            print("Exit command received. Deactivating REPL.")
                            response = "REPL session terminated."
                            repl_active = False
                            
                        else:
                        
                            command_output = execute_code(message_str)
                            print(f"Response to received commmand: {command_output}")
                            nb_iot_module.mqtt_publish(f"isurlog/repl_out/{ser_num}", command_output)
                            wdt.feed()
                            
                    else:
                        
                        print(f"Received incomplete MQTT message block: {lines}")
                
                else:
                    print(f"Received non-MQTT data: {block_str}")
                    
            except Exception as e:
                print(f"Error while processing UART data: {e}")

def read_all_sensors(pm, register_mode, ble = False):
    
    data = [[0, "addUnixTime", pm.get_unix_time()]]
    alarm_condition = False

    # Pre-check of activated sensors
    modbus_config = config_manager.get_dynamic("modbus_config")
    analog_config = config_manager.get_dynamic("analog_config")
    pt100_config = config_manager.get_dynamic("pt100_config")
    output_config = config_manager.get_dynamic("output_config")

    any_modbus_enabled = any(ch.get("enable", False) for ch in modbus_config.get("inputs", [])) if modbus_config else False
    any_analog_enabled = any(ch.get("enable", False) for ch in analog_config.get("inputs", [])) if analog_config else False
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
            
        if any_analog_enabled or any_modbus_enabled or pt100_enabled:
            pm.control_vdc(1)
            time.sleep_ms(250)
            
        if any_modbus_enabled or pt100_enabled:
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
            
    # Temperature PT100 Input
    pt100_config = config_manager.get_dynamic("pt100_config")

    if pt100_config and pt100_config.get("enable", False):
        pm.control_5v(1)
        from modules import max31865_sensor
        max31865_module = max31865_sensor.MAX31865Sensor()
        print("Reading PT100 input...")
        faults = max31865_module.read_faults()
        temperature = max31865_module.read_temperature()
        if temperature is not None:
            print(f"  PT100 Temperature: {temperature:.2f} °C")
            data.append([0, "addTemperatureInput", temperature])
            
            #Check alarms
            if (register_mode and (pt100_config.get("low_cond", False)) and (temperature < pt100_config.get("low", 0))):
                alarm_condition = True
            if (register_mode and (pt100_config.get("high_cond", False)) and (temperature > pt100_config.get("high", 0))):
                alarm_condition = True
                
        else:
            print("  Error reading PT100 temperature.")
            data.append([0, "addTemperatureInput", 0]) 

    else:
        print("No PT100 input configured in dymanic_config.json.")

    # BME680 Sensor
    bme680_config = config_manager.get_dynamic("BME680_sensor")

    if bme680_config and bme680_config.get("enable", True):
        from modules import bme680_sensor
        print("Reading BME680 sensor...")
        bme_sensor = bme680_sensor.BME680Sensor(IAQ=False)  # Set IAQ=True if you want IAQ calculation
        bme_data = bme_sensor.read_data()
        if bme_data:
            print(f"BME680 - Temperature: {bme_data['temperature']:.2f} °C, Pressure: {bme_data['pressure']:.2f} hPa, Humidity: {bme_data['humidity']:.2f} %RH")
            data.append([0, "addTemperatureSensor", bme_data['temperature']])
            data.append([0, "addHumiditySensor", bme_data['humidity']])

            #Check temperature alarms
            if (register_mode and (bme680_config.get("temperature_low_cond", False)) and (bme_data['temperature'] < bme680_config.get("temperature_low", 0))):
                alarm_condition = True
            if (register_mode and (bme680_config.get("temperature_high_cond", False)) and (bme_data['temperature'] > bme680_config.get("temperature_high", 0))):
                alarm_condition = True

            #Check humidity alarms
            if (register_mode and (bme680_config.get("humidity_low_cond", False)) and (bme_data['humidity'] < bme680_config.get("humidity_low", 0))):
                alarm_condition = True
            if (register_mode and (bme680_config.get("humidity_high_cond", False)) and (bme_data['humidity'] > bme680_config.get("humidity_high", 0))):
                alarm_condition = True
                
    else:
        print("No BME680 sensor configured in dymanic_config.json.")

    # Modbus Inputs
    if any_modbus_enabled:
        from modules import modbus_sensor
        utils.log_info("At least one Modbus input is enabled. Proceeding with acquisition.")

        # 2. Perform pre-acquisition delay ONLY if any input is enabled
        pre_acquisition_time = modbus_config.get("pre_acquisition", 0)
        if pre_acquisition_time > 0:
            utils.log_info(f"Starting Modbus pre-acquisition delay: {pre_acquisition_time} ms")
            now = time.time()
            while ((now - reg_on_t) * 1000 < pre_acquisition_time):
                remaining_ms = pre_acquisition_time - (now - reg_on_t) * 1000
                if remaining_ms > 1000:
                    print(f"Modbus pre-acquisition: waiting {remaining_ms:.0f} ms...")
                time.sleep(0.5) 
                now = time.time()
            utils.log_info("Modbus pre-acquisition delay finished.")
        else:
            utils.log_info("Modbus pre-acquisition time is 0 or not configured. Skipping delay.")

        # 3. Initialize the module and read ONLY if any input is enabled
        modbus_module = modbus_sensor.ModbusSensor() # Initialize Modbus sensor
        print("Reading Enabled Modbus inputs...")
        
        for channel_config in modbus_config["inputs"]: # Iterate over the list
            channel = channel_config.get("channel")
            if channel is None: # Check if the channel is present
                print(f"  Error: Missing channel number in Modbus config.")
                continue

            # Check if THIS specific input is enabled
            if not channel_config.get("enable", False):
                print(f"  Skipping Modbus input channel {channel} (disabled).")
                continue

            # Get necessary parameters for reading
            slave_addr = channel_config.get("slave_address")
            register_addr = channel_config.get("register_address")
            fc = channel_config.get("fc")
            is_fp = channel_config.get("is_FP", False)
            byte_order = channel_config.get("byte_order", "big") # Ensure default if not specified
            number_of_decimals = 10**channel_config.get("number_of_decimals", 0)
            offset = channel_config.get("offset", 0.0)
            invert = channel_config.get("invert", False)
            long_int = channel_config.get("long_int", False)

            if slave_addr is None or register_addr is None or fc is None:
                print(f"  Error: Missing configuration (slave, reg, or fc) for Modbus input channel {channel}.")
                continue

            # Read the value
            # Pass byte_order, needed for floating point conversion
            
            print(f"Reading modbus input. slave_addr: {slave_addr}, fc: {fc}, register_addr: {register_addr}, is_fp: {is_fp}") 
            value = modbus_module.read_modbus_data(slave_addr, fc, register_addr, is_fp)
            time.sleep_ms(100)

            if value is not None:
                if not is_fp:
                    value = value[0]
                print(f"  Channel {channel}: {value}")
                # Determine LPP type based on function code
                if fc == 1 or fc == 2:
                    data.append([channel, "addModbusGenericInput", value])
                else: # FC 3 or 4
                    if invert:
                        value = offset - value/number_of_decimals   
                    else:
                        value = value/number_of_decimals - offset
                    
                    if long_int:
                        data.append([channel, "addModbusGenericInput", value])
                    else:
                        data.append([channel, "addModbusInput", value])

                # Check alarms 

                if register_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                    alarm_condition = True
                if register_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0):
                    alarm_condition = True

            else:
                print(f"  Error reading Modbus input channel {channel}.")
                if fc == 1 or fc == 2:
                    data.append([channel, "addModbusGenericInput", 0]) 
                else:
                    data.append([channel, "addModbusInput", 0.0]) 

    else:
        # This executes if 'inputs' exists but no entry is enabled
        print("All Modbus inputs are disabled.")
        
        
    #Analog inputs
    if any_analog_enabled:
        from modules import analog_sensor
        utils.log_info("At least one analog input is enabled. Proceeding with acquisition.")

        # 2. Perform pre-acquisition delay ONLY if any input is enabled
        pre_acquisition_time = analog_config.get("pre_acquisition", 0)
        if pre_acquisition_time > 0:
            utils.log_info(f"Starting pre-acquisition delay: {pre_acquisition_time} ms")
            now = time.time()
            while((now - reg_on_t) * 1000 < pre_acquisition_time):
                 remaining_ms = pre_acquisition_time - (now - reg_on_t) * 1000
                 if remaining_ms > 1000:
                      print(f"Analog sensor pre-acquisition: waiting {remaining_ms:.0f} ms...")
                 time.sleep(0.5)
                 now = time.time()
            utils.log_info("Pre-acquisition delay finished.")
        else:
            utils.log_info("Pre-acquisition time is 0 or not configured. Skipping delay.")

        # 3. Initialize the module and read ONLY if any input is enabled
        analog_module = analog_sensor.AnalogInput()
        print("Reading Enabled Analog inputs...")
        for channel_config in analog_config["inputs"]: # Iterate over the list
            channel = channel_config.get("channel")

            if channel is None: # Check if the channel is present
                print(f"  Error: Missing channel number in analog config.")
                continue

            # Check if THIS specific input is enabled
            if not channel_config.get("enable", False):
                # We already know at least one is enabled in general,
                # but we can skip the log if this specific one is not.
                print(f"  Skipping Analog input channel {channel} (disabled).") # Optional
                continue

            # Read the value
            value = analog_module.read_analog(3-channel)
            value = analog_module.convert_value(value, channel_config.get("zero", 0),  channel_config.get("full_scale", 100))

            if value is not None:
                print(f"  Channel {channel}: {value}")
                data.append([channel, "addAnalogInput", value])

                # Check alarms (assuming register_mode and alarm_condition are defined earlier)
                if register_mode and channel_config.get("low_cond", False) and value < channel_config.get("low", 0):
                    alarm_condition = True
                if register_mode and channel_config.get("high_cond", False) and value > channel_config.get("high", 0): # Corrected 'hi' to 'high'
                    alarm_condition = True
            else:
                print(f"  Error reading Analog input channel {channel}.")
                data.append([channel, "addAnalogInput", 0.0]) # Add default value on error

    else:
        # This executes if 'inputs' exists but no entry is enabled
        print("All Analog inputs are disabled.")
        
    # --- Power down regulators ---
    if not ble:
        pm.control_vdc(0)
        pm.control_5v(0)
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

    print("\n####WELCOME TO ISURLOG OS MICROPYTHON FLAVOUR####\n")

    # --- Power Management ---
    pm = power_manager.PowerManager()
    pm.set_cpu_freq("low-power")
    ser_num = config_manager.static_config.get("serial", "c-000")
    print(f"Isurlog with serial number: {ser_num}")
    
    #Init RTC memory
    rtc_memory = RTC_Memory(max_payload_size = config_manager.dynamic_config["general"].get("max_payload_size", 256))

    # --- Initialize Variables ---

    wake_up_sources = []
    register_mode = config_manager.get_dynamic("general").get("register_mode", 0) #Register mode, 0 normal, 1 conditional

    # Declare Blinky <º)))><
    blinky = LEDManagerULP()
    if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
        
        if (pm.wakeup_reason == "Power-on reset"):
            pm.set_cpu_freq("balanced")
            blinky.load_ulp() #Load Blinky only on Power-on reset
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
        pm.set_cpu_freq("ultra-low-power") # Back to 20MHZ to save power.

        
    #Read all sensors (if activated)
    data, alarm_condition = read_all_sensors(pm, register_mode)

    # Get battery voltage from data to configure Blinky later
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
    modem_type = config_manager.static_config.get("modem", "nb-iot")

    if modem_type == "nb-iot":
        if config_manager.static_config.get("isurreach", False):
            from modules import nb_iot_isurreach_som as nb_iot
        else:
            from modules import nb_iot
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
                pm.go_to_sleep()
            
            keep_alive = ((config_manager.dynamic_config["general"].get("latency_time", 10) * 60)+20) * config_manager.dynamic_config["general"].get("register_acumulator", 1)
            nb_iot_module.mqtt_configure(ser_num, keep_alive, 0)
            if not nb_iot_module.mqtt_connect(config_manager.static_config.get("mqtt", {}).get("user", ""), config_manager.static_config.get("mqtt", {}).get("passwd", ""), config_manager.static_config.get("mqtt", {}).get("ip", "80.24.238.36"), config_manager.static_config.get("mqtt", {}).get("port", 1883)):
                print("Failed to connect to MQTT broker")
                pm.go_to_sleep()
            
            if not pm.rtc_available:
                new_time = nb_iot_module.get_network_time()
                print(f"New requested time UTC: {new_time}")
                pm.set_rtc_time(new_time)
                
            nb_iot_module.mqtt_subscribe(f"isurlog/config/{ser_num}", QoS=2)
            
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
        if modem_type == "nb-iot":
            if (config_manager.dynamic_config["general"].get("debug_led", False)) and (not(config_manager.dynamic_config["digital_config"].get("counter", False))):
                blinky.set_ulp_pattern(pulse_num=1, n_micro_pulses=250, delay_on=5, delay_off=20, inter_delay=250,  wake_up_period=5)
            nb_iot_module = nb_iot.NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)
            print("Transmitting data throught NB-IoT...")
            payloads = rtc_memory.get_payloads()
            rtc_memory.clear_memory()
            print(f"Retrieved payloads: {payloads}")

            nb_iot_module.wake_up()  # Wake up *only* when transmitting
            #nb_iot_module.mqtt_subscribe(f"isurlog/config/{ser_num}", QoS=2)
            if not nb_iot_module.mqtt_check_connection():
                if not nb_iot_module.check_network_connection():
                    nb_iot_module.reset() #Reset NB-IoT module
                    reset() #Reset ESP32
                if not nb_iot_module.mqtt_connect(config_manager.static_config.get("mqtt", {}).get("user", ""), config_manager.static_config.get("mqtt", {}).get("passwd", ""), config_manager.static_config.get("mqtt", {}).get("ip", "80.24.238.36"), config_manager.static_config.get("mqtt", {}).get("port", 1883)):
                    print("Failed to connect to MQTT broker")
                    pm.go_to_sleep()
                nb_iot_module.mqtt_subscribe(f"isurlog/config/{ser_num}", QoS=2)
                    
            for i, payload in enumerate(payloads):
                #Publish not empty payloads only.
                if payload:
                    print(f"Publishing payload {i+1}: {payload}")
                    if not nb_iot_module.mqtt_publish(f"dataloggers/datos/{ser_num}", payload):
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
                        if nb_iot_module.mqtt_publish(f"isurlog/repl_out/{ser_num}", "Connected"):
                            nb_iot_module.mqtt_subscribe(f"isurlog/repl_in/{ser_num}", QoS=2)
                            handle_remote_repl()
                            
                    elif "Update" in msg['message']: #FIRMWARE UPDATE MESSAGE
                        print("Starting OTA update process...")
                        update_instructions = msg['message'].split(" ")
                        if len(update_instructions) == 5:
                            from modules import update_manager
                            _, server, port, file, checksum = update_instructions
                            print(f"Received instructions: Server: {server} Port: {port} File: {file} Checksum: {checksum}")
                            nb_iot_module.download_file(server, port, file, chunk_size=1024)
                            if update_manager.verify_file_checksum(checksum):
                                update_manager.perform_update()
                                print("Update process finished, rebooting in 5 seconds...")
                                if not nb_iot_module.mqtt_publish(f"dataloggers/update/{ser_num}", "Update OK"):
                                    print(f"Failed to publish response")
                                time.sleep(5)
                                reset()
                        if not nb_iot_module.mqtt_publish(f"dataloggers/update/{ser_num}", "Update FAILED"):
                            print(f"Failed to publish response")
                        
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
    pm.go_to_sleep()
























