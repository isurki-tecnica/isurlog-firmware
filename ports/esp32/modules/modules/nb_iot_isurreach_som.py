from machine import UART, Pin
from modules import utils
import time
import json
from modules.config_manager import config_manager
import ubinascii

class NBIoT:
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=9600, timeout=1000):
        """
        Initializes the NB-IoT module.

        Args:
            uart_id: The ID of the UART peripheral (e.g., 0, 1, 2).
            tx_pin: The GPIO pin number for UART TX.
            rx_pin: The GPIO pin number for UART RX.
            baudrate: The baud rate for UART communication (default: 9600).
            timeout: Timeout in milliseconds for reading responses (default: 1000).
        """
        self.tx_pin = tx_pin if tx_pin is not None else config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("tx_pin", 4)
        self.rx_pin = rx_pin if rx_pin is not None else config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("rx_pin", 2)
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(self.tx_pin), rx=Pin(self.rx_pin), timeout=timeout)
        self.received_messages = []
        self.BLACKLIST = {
            'NB-IoT': ['21403'],  # Block Orange NB-IoT (MQTT downlinks not working?)
            'LTE-M':  ['21401']   # Block Vodafone LTE-M (Vodafone does not support eDRX over LTE-M)
        }

    def send_at_command(self, command, expected_response="OK", timeout=1000):
        """
        Sends an AT command to the NB-IoT module and waits for a response.

        Args:
            command: The AT command string to send.
            expected_response: The expected response string (default: "OK").
            timeout: Timeout in milliseconds for waiting for the response (default: 1000).

        Returns:
            The response string from the module, or None if a timeout occurs.
        """
        self.uart.write(command + "\r\n")
        utils.log_debug(f"Sent AT command: {command}")

        response = self._wait_for_response(expected_response, timeout, command = command)

        if response:
            utils.log_debug(f"Received response: {response}")
        else:
            utils.log_error(f"Timeout waiting for response to AT command: {command}")
        return response
    
    def send_at_command_check(self, command, expected_response="OK", timeout=2000, retries=3, retry_delay=1):
        """
        Sends an AT command and checks the response, retrying if necessary.

        Args:
            command: The AT command to send.
            expected_response: The expected response string.
            timeout: The timeout in milliseconds for each attempt.
            retries: The number of retry attempts.

        Returns:
            True if the command was successful, False otherwise.
        """
        for i in range(retries):
            response = self.send_at_command(command, expected_response, timeout)
            if response and expected_response in response:
                return True
            utils.log_warning(f"AT command failed, retrying ({i+1}/{retries})...")
            time.sleep(retry_delay)  # Wait before retrying
        utils.log_error(f"AT command '{command}' failed after {retries} retries.")
        return False
    
    def _parse_mqtt_msg_urc(self, urc_line):
        """Parses a #XXMQTTMSG URC and adds it to the queue."""
        # Expected format: <topic_received>\r\n<message>
        try:
            parts = urc_line.split('\r\n')
            topic = parts[0]
            message_raw = parts[1]
            
            utils.log_info(f"URC MQTT Message Received - Topic: {topic}, Message: {message_raw}")
            self.received_messages.append({'topic': topic, 'message': message_raw})

        except Exception as e:
            utils.log_error(f"Error parsing MQTT message URC: {e}, Line: {urc_line}")
    
    def _parse_mqtt_evt_urc(self, urc_line):
        """Parses a #XMQTTEVT URC."""
        # Expected format: #XMQTTEVT: <evt_type>,<result>
        try:
            parts = urc_line.split(':', 1)[1].strip().split(',')
            if len(parts) == 2:
                evt_type = int(parts[0])
                result = int(parts[1])
                utils.log_info(f"URC MQTT Event Received - Type: {evt_type}, Result: {result}")
                # You can add logic here to handle specific events if needed
                if result != 0:
                    utils.log_error(f"MQTT Event indicates failure (Result: {result})")
            else:
                 utils.log_warning(f"Could not parse MQTT event URC: {urc_line}")
        except Exception as e:
            utils.log_error(f"Error parsing MQTT event URC: {e}, Line: {urc_line}")

    def _wait_for_response(self, expected_response, timeout, command=None): # Added command parameter
        """
        Waits for a specific response, processing URCs in the meantime.
        Args:
            expected_response: The expected response string.
            timeout: Timeout in milliseconds.

        Returns:
            The full response string if the expected response is found, otherwise None.
            
        """
        start_time = time.ticks_ms()
        buffer = ""
        response_lines = [] # Stores lines that ARE part of the expected response

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.uart.any():
                try:
                    # Read everything available to avoid losing fast URCs
                    chunk = self.uart.read().decode('utf-8', 'ignore') # Ignore decoding errors
                    buffer += chunk
                except Exception as e:
                     utils.log_error(f"Error reading UART: {e}")
                     buffer = "" # Clear buffer in case of serious error

            # Process the buffer line by line
            while '\r\n' in buffer:
                line, buffer = buffer.split('\r\n', 1)
                line = line.strip() # Remove extra spaces

                if not line: # Ignore empty lines
                    continue

                # Check URCs FIRST
                if line.startswith("#XMQTTMSG:"):
                    utils.log_info("#XMQTTMSG detected!")
                    #topic_line = self._read_uart_until(f'isurlog/config/{config_manager.static_config.get("serial", "c-000")}' ,text_timeout=6000) # Timeout para el topic
                    self._parse_mqtt_msg_urc(buffer)
                elif line.startswith("#XMQTTEVT:"):
                    utils.log_info("#XMQTTEVT detected!")
                    self._parse_mqtt_evt_urc(line)
                else:
                    # If it's not a known URC, add it to the response lines
                    response_lines.append(line)
                    # Check if the expected response is in the LAST line or in the set
                    # (depends on how modem responds, adjust if necessary)
                    full_response_text = "\r\n".join(response_lines)
                    if expected_response in full_response_text:
                         return full_response_text

            time.sleep_ms(20)

        # Timeout: Return what was accumulated if it contains the response, otherwise None
        full_response_text = "\r\n".join(response_lines)
        if expected_response in full_response_text:
            return full_response_text
        else:
            # Log what was received if it's not the expected response
            if response_lines:
                 utils.log_warning(f"Timeout waiting for '{expected_response}'. Received: {full_response_text}")
            return None
    
    def select_SIM(self, sim="eSIM"):
        """
        Selects between the eSIM of the NB-IoT module o the physical external sim.

        Args:
            sim: eSIM or external.

        Returns:
            True if successfull.
        """
        
        if not self.send_at_command_check("AT+CFUN=0"): #Modem must be disabled before changing the SIM
            return False
        
        if not self.send_at_command_check("AT#XGPIOCFG=1,12"): #Set GPIO12 as output.
            return False
        
        if (sim == "external"):
            if not self.send_at_command_check("AT#XGPIO=0,12,0"): #Set GPIO12 low.
                return False
            
        if (sim == "eSIM"):
            if not self.send_at_command_check("AT#XGPIO=0,12,1"): #Set GPIO12 high.
                return False
            
    def _parse_cops_response(self, response):
        """
        Parses the response from AT+COPS=? to extract a list of (PLMN, AcT) tuples.
        Example input: '+COPS: (1,"","","21407",7),(1,"","","21403",7)'
        Example output: [('21407', '7'), ('21403', '7')]
        """
        networks = []
        if "+COPS:" not in response:
            return networks
        
        # Remove the '+COPS: ' part and split by '),' which separates entries
        response_part = response.split('+COPS: ')[1]
        entries = response_part.split('),(')
        
        for entry in entries:
            try:
                parts = entry.split(',')
                # The PLMN is the 4th part, AcT is the 5th
                plmn = parts[3].strip().replace('"', '')
                act = parts[4].strip().replace(')', '')
                if plmn: # Ensure PLMN is not empty
                    networks.append((plmn, act))
            except IndexError:
                continue # Ignore malformed entries
        return networks

    def connect(self, connection_preference, edrx = True, apn = None):

        """
        Connects to the NB-IoT network.

        Returns:
            True if the connection is successful, False otherwise.
        """

        if not self.send_at_command_check("AT"):
            return False

        if not self.send_at_command_check("AT#XSLMVER"):  
            return False
        
        if not self.send_at_command_check("AT+CGMR"):  
            return False
        
        response = self.send_at_command("AT%XMONITOR")
        
        if response and ("%XMONITOR: 1" in response or "%XMONITOR: 5" in response):
            utils.log_info("Device was connected to the network.")
            
        else:    

            # --- Configure System Mode (Check First) ---
            if connection_preference == "LTE-M":
                desired_mode_val = 1
            elif connection_preference == "NB-IoT":
                desired_mode_val = 2

            query_response = self.send_at_command("AT%XSYSTEMMODE?", "%XSYSTEMMODE:") # Check response starts with %XSYSTEMMODE:
            current_mode_val = -1 # Indicate unknown state
            if query_response:
                try:
                    # Example response: %XSYSTEMMODE: 1,1,0,2
                    current_mode_val = int(query_response.strip().split(',')[-1])
                except (IndexError, ValueError) as e:
                    utils.log_warning(f"Could not parse current system mode: {e}")

            if current_mode_val != desired_mode_val:
                utils.log_info(f"Setting system mode to {connection_preference} ({desired_mode_val})...")
                if not self.send_at_command_check(f"AT%XSYSTEMMODE=1,1,0,{desired_mode_val}"):
                    utils.log_error("Failed to set system mode.")
                    return False
            else:
                utils.log_info(f"System mode already set correctly ({current_mode_val}). Skipping.")
                
            # --- Configure RAI --> Release Assistance Indication (Check First) ---

            query_response = self.send_at_command("AT%RAI?", "%RAI:") # Check response starts with %XSYSTEMMODE:
            current_mode_val = -1 # Indicate unknown state
            if query_response:
                try:
                    # Example response: %XRAI: 0
                    current_mode_val = int(query_response.strip().split(": ")[-1])
                except (IndexError, ValueError) as e:
                    utils.log_warning(f"Could not parse RAI: {e}")

            if current_mode_val != 1:
                utils.log_info(f"Setting RAI to 1...")
                if not self.send_at_command_check("AT%RAI=1"):
                    utils.log_error("Failed to set RAI.")
                    return False
            else:
                utils.log_info(f"RAI already set correctly ({current_mode_val}). Skipping.")
                
            #Configure eDRX mode ---
            if edrx:

                if connection_preference == "LTE-M":
                    desired_mode_val = 4
                elif connection_preference == "NB-IoT":
                    desired_mode_val = 5

                if not self.send_at_command_check('AT%PERIODICSEARCHCONF=0,0,0,1,"0,10,40,,5","1,300,600,1800,1800,3600"'): #Ultra low power periodic cell search.
                    return False
                             
                if not self.send_at_command_check(f'AT+CEDRXS=1,{desired_mode_val},"0011"'): #Enable eDRX mode.
                    return False
                
                if not self.send_at_command_check(f'AT%XPTW={desired_mode_val},"0001"'): #Set Paging Time Window (PTW). 
                    return False

            if apn != None:
                if not self.send_at_command_check(f'AT+CGDCONT=1,"IP","{apn}"', "OK", timeout=1000): 
                    return False
            if not self.send_at_command_check("AT+CFUN=1", "OK", timeout=1000): 
                return False
            
            
            
            utils.log_info("Starting smart network selection...")
            is_connected = False

            # 1. Scan available networks (puede tardar varios minutos)
            scan_response = self.send_at_command('AT+COPS=?', timeout=300000)
            
            if scan_response and "+COPS:" in scan_response:
                available_networks = self._parse_cops_response(scan_response)
                current_blacklist = self.BLACKLIST.get(connection_preference, [])
                
                utils.log_info(f"Networks found: {[net[0] for net in available_networks]}")
                utils.log_info(f"Blacklist for {connection_preference}: {current_blacklist}")

                # 2. Connect only to allowed networks
                for plmn, act in available_networks:
                    if plmn in current_blacklist:
                        utils.log_info(f"Operator {plmn} is blacklisted, skipping.")
                        continue
                    
                    utils.log_info(f"Attempting manual connection to PLMN: {plmn}...")
                    if self.send_at_command_check(f'AT+COPS=1,2,"{plmn}"'):
                        if self.wait_for_network_connection(timeout=180000): # 3 min timeout per operator
                            utils.log_info(f"Successfully connected to {plmn}!")
                            is_connected = True
                            break
                    utils.log_warning(f"Failed to initiate connection to {plmn}.")
            
            # 3. Plan B: If manual fails, switch back to auto
            if not is_connected:
                utils.log_warning("Manual selection failed. Falling back to automatic mode.")
                self.send_at_command_check('AT+COPS=0')
                is_connected = self.wait_for_network_connection(timeout=600000)

            if not is_connected:
                utils.log_error("Failed to connect to any network.")
                return False
            
            if not self.send_at_command_check('AT+CPSMS=0'): #Disable PSM mode.
                return False            
        
            if not self.send_at_command_check("AT+CPSMS?", "OK", timeout=1000): 
                return False

            if not self.send_at_command_check("AT%XMONITOR", "OK", timeout=1000): 
                return False

        utils.log_info("Connected to NB-IoT network.")
        
        if edrx:
            
            if not self.send_at_command("AT+CEDRXRDP", expected_response = "CEDRXRDP", timeout=4000):
                utils.log_error("Failed to set eDRX mode.")
            else:
                utils.log_info("eDRX mode set.")
            
        return True
    
    def wake_up(self, max_attempts = 5):
        
        """
        Wake up NB-IoT module from sleep (AT#XSLEEP=2 or AT#XSLEEP=0)

        Returns:
            True if wake up is successful, False otherwise.
        """
        
        active = False
        attempts = 0
        
        while (not active) and (attempts < max_attempts):
        
            if not self.send_at_command_check("AT", "OK", timeout=1000, retries = 1):
                Pin(config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("nb_iot_wake_up", 18), Pin.OUT, value=0, hold=True)
                time.sleep_ms(100)
                Pin(config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("nb_iot_wake_up", 18), Pin.OUT, value=1, hold=True)
                attempts += 1
            
            else:
                utils.log_info("NB-IoT module woken up.")
                return True

        utils.log_info("Could not wake up NB-IoT module.")
        return False
    
    def sleep(self):
        
        """
        Enter Sleep. In this mode, both the SLM service and the LTE connection are maintained.

        Returns:
            True if enter sleep state was successful, False otherwise.
        """

        if not self.send_at_command_check("AT#XSLEEP=2", "OK", timeout=1000): # SLM service and the LTE connection are maintained.
            return False

        utils.log_info("NB-IoT module to sleep, SLM service and the LTE connection are maintained.")
        return True
    
    def disconnect(self):
        
        """
        Enter Idle. In this mode, both the SLM service and the LTE connection are terminated.

        Returns:
            True if disconnection was successful, False otherwise.
        """

        if not self.send_at_command_check("AT+CFUN=4", "OK", timeout=1000): # Set flight mode.
            return False

        if not self.send_at_command_check("AT#XSLEEP=0", "OK", timeout=1000): # SLM service and the LTE connection are terminated.
            return False

        utils.log_info("Disconnected from NB-IoT network.")
        return True
    
    def reset(self):
        
        """
        Performs a soft reset of the nRF91 Series SiP

        Returns:
            True if reset was successful, False otherwise.
        """

        return self.send_at_command_check("AT#XRESET", "Ready", timeout=4000)
    
    def hard_reset(self):
        
        """
        Performs a hard reset of the nRF91 Series SiP

        Returns:
            True if reset was successful, False otherwise.
        """
        
        EN_COM_MODULE = config_manager.static_config.get("pinout", {}).get("control", {}).get("en_nbiot_pin", 5)
        
        Pin(EN_COM_MODULE, Pin.OUT, Pin.PULL_UP, value=0, hold=True)
        time.sleep(1)
        Pin(EN_COM_MODULE, Pin.OUT, Pin.PULL_UP, value=1, hold=True)
        time.sleep(1)

        return self.send_at_command_check("AT", timeout=4000)

    def get_imei_ccid(self):
        """
        Gets IMEI and CCID of the eSIM.

        Returns:
            A dictionary containing the IMEI and CCID, or None if an error occurred.

        Example:
            nb_iot_module = NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)
            imei_ccid_data  = nb_iot_module.get_imei_ccid()
            if imei_ccid_data:
                imei = imei_ccid_data["imei"]
                ccid = imei_ccid_data["ccid"]
                utils.log_info(f"IMEI: {imei}")
                utils.log_info(f"CCID: {ccid}")
            else:
                utils.log_error("Failed to get IMEI and CCID.")
        """
        imei = None
        ccid = None

        # Get IMEI
        response = self.send_at_command("AT+CGSN=1", "OK")
        if response:
            lines = response.split("\r\n")
            for line in lines:
                if "+CGSN:" in line:
                    imei = line.split(":")[1].strip().replace('"', '') # Extrae el IMEI y elimina las comillas
                    break

        # Set CFUN to 41
        self.send_at_command("AT+CFUN=41")

        # Get CCID
        response = self.send_at_command("AT%XICCID", "OK", timeout=3000)
        if response:
            lines = response.split("\r\n")
            for line in lines:
                if "%XICCID:" in line:
                    ccid = line.split(":")[1].strip()
                    break

        if imei and ccid:
            return {"imei": imei, "ccid": ccid}
        else:
            utils.log_error("Failed to get IMEI and/or CCID.")
            return None

    def register_SIM(self):
        """
        Registers the SIM in the network.

        Returns:
            True if the registration is successful, False otherwise.

        Example:
            nb_iot_module = NBIoT(uart_id=2, tx_pin=4, rx_pin=2, baudrate=115200)
            if nb_iot_module.register_sim():
                utils.log_info("SIM registered successfully.")
            else:
                utils.log_error("SIM registration failed.")
        """
        # Enable the modem
        if not self.send_at_command_check("AT+CFUN=1"):
            utils.log_error("Failed to enable modem.")
            return False

        # Wait for network connection (adjust timeout as needed)
        if not self.wait_for_network_connection(timeout=600000):
            utils.log_error("Timeout waiting for network connection.")
            return False

        # Complete registration
        if not self.send_at_command_check('AT#XHTTPCCON=1,"d.actinius.io",14000,123322', timeout=5000):
            utils.log_error("Failed to execute AT#XHTTPCCON.")
            return False

        if not self.send_at_command_check('AT#XHTTPCREQ="POST","/v1/tx/reg/complete",""', timeout=5000):
            utils.log_error("Failed to execute AT#XHTTPCREQ.")
            return False

        utils.log_info("SIM registration successful.")
        return True

    def check_network_connection(self):
        """
        Checks if module is connected to the network.

        Returns:
            True if connected, False otherwise.
        """

        response = self.send_at_command("AT%XMONITOR")
        if response and ("%XMONITOR: 1" in response or "%XMONITOR: 5" in response):
            utils.log_info("NB-IoT module connected to the network.")
            return True

        return False

    def wait_for_network_connection(self, timeout=60000):
        """
        Waits for the device to connect to the network.

        Args:
            timeout: Timeout in milliseconds.

        Returns:
            True if the connection is successful, False otherwise.
        """
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            response = self.send_at_command("AT%XMONITOR")
            if response and ("%XMONITOR: 1" in response or "%XMONITOR: 5" in response):
                utils.log_info("Device connected to the network.")
                return True
            time.sleep(2)  # Check every 2 seconds
        return False

    def get_signal_quality(self):
        """
        Gets the signal quality.

        Returns:
            The signal quality (CSQ) as a string, or None if an error occurred.
        """
        response = self.send_at_command("AT+CSQ")
        if response:
            # Parse the response to extract the CSQ value
            # Example response: +CSQ: 18,99
            parts = response.split(":")
            if len(parts) == 2:
                csq_part = parts[1].split(",")[0].strip()
                return csq_part
        return None
    
    def get_ip_address(self):
        """
        Gets the IP address assigned to the module.

        Returns:
            The IP address as a string, or None if an error occurred.
        """
        response = self.send_at_command("AT+CGPADDR=1")
        if response and "+CGPADDR: 1," in response:
            # Parse the response to extract the IP address
            # Example response: +CGPADDR: 1,"10.123.45.67"
            parts = response.split(",")
            if len(parts) == 2:
                ip_address = parts[1].replace('"', "")
                return ip_address
        return None
    
    def get_network_time(self):
        """Gets the current time from the modem's RTC (using AT+CCLK?).

        Returns:
            The time as a string in the format "yy/MM/dd,hh:mm:ss+TZ",
            or None if an error occurred.  This is the format returned by the modem.
        """
        response = self.send_at_command("AT+CCLK?", "+CCLK:", timeout=2000) #Expect a response that starts by "+CCLK:"
        if response:
            try:
                # Extract time string. Response format: +CCLK: "yy/MM/dd,hh:mm:ss+TZ"
                time_str = response.split('"')[1]  # Get the part within quotes
                utils.log_info(f"Modem time: {time_str}")
                return time_str
            except (IndexError, ValueError) as e:
                utils.log_error(f"Error parsing modem time response: {e}, response: {response}")
                return None
        else:
            utils.log_error("Failed to get time from modem.")
            return None
    
    def mqtt_configure(self, client_id, keep_alive, clean_session):

        """
        Configure the MQTT client before connecting to a broker.

        Args:
            client_id: Indicates the MQTT Client ID.
            keep_alive: Indicates the maximum Keep Alive time in seconds for MQTT.
            clean_session: 0 to connect to a MQTT broker using a persistent session. 1 to connect to a MQTT broker using a clean session.

        Returns:
            True if the configuration was successful, False otherwise.

        """

        if not self.send_at_command_check(f'AT#XMQTTCFG="{client_id}",{keep_alive},{clean_session}', timeout = 2000):
            utils.log_error("Failed to configure MQTT connection.")
            return False
        
        utils.log_info("MQTT connection successfully configured.")
        return True
    
    def mqtt_connect(self, username, password, url, port):

        """
        Connect to the MQTT client.

        Args:
            username: Indicates the MQTT client username.
            password: Indicates the MQTT client password in cleartext.
            url: Indicates the MQTT broker hostname.
            port: Indicates the MQTT broker port.

        Returns:
            True if the connection was successful, False otherwise.

        """

        if not self.send_at_command_check(f'AT#XMQTTCON=1,"{username}","{password}","{url}",{port}', timeout = 2000):
            utils.log_error("Failed to configure MQTT connection.")
            return False
        
        utils.log_info("MQTT connection successfully configured.")
        return True
    
    def mqtt_check_connection(self):

        """
        Checks if the MQTT client is still connected to the broker.

        Returns:
            True if connected, False otherwise.

        """

        res = self.send_at_command("AT#XMQTTCON?", timeout = 1000)
        if res.strip("\r\nOK") == '#XMQTTCON: 0':
            utils.log_info("MQTT connection is closed.")
            return False
        else:
            utils.log_info("MQTT connection is alive.")
            return True
        
    def mqtt_publish(self, topic, msg):

        """
        Publish MQTT message.

        Args:
            topic: Indicates the topic on which data is published.
            msg: Contains the payload on the topic being published.
        Returns:
            True if message is published, False otherwise.

        """

        if not self.send_at_command_check(f'AT#XMQTTPUB="{topic}","{msg}",0,0', timeout = 2000):
            utils.log_error("Failed to configure MQTT connection.")
            return False
        
        utils.log_info(f"MQTT message successfully published to: {topic}")
        return True
    
    def mqtt_subscribe(self, topic, QoS = 1):

        """
        Susbscribe MQTT message.

        Args:
            topic: Indicates the topic to subscribe to.
        Returns:
            True if successfully susbcribed, False otherwise.

        """

        if not self.send_at_command_check(f'AT#XMQTTSUB="{topic}",{QoS}', timeout = 2000, retries = 10, retry_delay = 5):
            utils.log_error("Failed to configure MQTT connection.")
            return False
        
        utils.log_info(f'Successfully subscribe to: {topic}')
        return True
    
    def get_mqtt_messages(self):
        """
        Retrieves and clears the list of received MQTT messages.

        Returns:
            A list of dictionaries, each containing 'topic' and 'message'.
            Returns an empty list if no messages have been received.
        """
        messages = self.received_messages
        self.received_messages = [] # Clear the list after retrieving it
        return messages

    def download_file(self, ip_address, port, filename, local_filename = "update_candidate.py", chunk_size=1024):
            """
            DEBUG FUNCTION: Performs a full chunked GET transfer test and prints
            ONLY the file content from each chunk's response.
            """
            
            def extract_block(text):
                lines = text.split('\n')
                capturing = False
                block = []

                for line in lines:
                    if line.startswith('#XHTTPCRSP:') and not capturing:
                        # Primera marca: activar captura
                        capturing = True
                        # Si hay más contenido después de la marca, capturarlo
                        rest = line[len('#XHTTPCRSP:'):].strip()
                        content = line.split(None, 1)  # divide en "#XHTTPCRSP:230,1" y lo que sigue
                        if len(content) > 1:
                            block.append(content[1])  # Captura el texto tras la marca
                        continue
                    elif line.startswith('#XHTTPCRSP:') and capturing:
                        # Segunda marca: detener captura
                        break
                    elif capturing:
                        block.append(line)

                return '\n'.join(block).rstrip('\r\n')
            
            utils.log_info(f"--- Iniciando Test Inteligente de Peticiones GET por Chunks ---")

            # ----------------------------------------------------------------------
            # ETAPA 1: Pedir el primer chunk para descubrir el tamaño total del archivo
            # ----------------------------------------------------------------------
            total_size = None
            bytes_downloaded = 0
            
            print("\n" + "="*60)
            utils.log_info(f"STEP 1: Requesting first chunk (bytes 0-{chunk_size-1}) to get total size...")
            print("="*60)

            if not self.send_at_command_check(f'AT#XHTTPCCON=1,"{ip_address}",{port},54322', timeout=10000):
                utils.log_error("Failed to open HTTP connection for size discovery.")
                return

            try:
                range_header = f"Range: bytes=0-{chunk_size-1}\\r\\n"
                command = f'AT#XHTTPCREQ="GET","/{filename}","{range_header}"'
                utils.log_info(f"Sending command: {command}")
                self.uart.write(command + '\r\n')

                # Leer la respuesta completa para este primer chunk
                response_bytes = bytearray()
                last_data_time = time.ticks_ms()
                while time.ticks_diff(time.ticks_ms(), last_data_time) < 10000:
                    if self.uart.any():
                        response_bytes.extend(self.uart.read(self.uart.any()))
                        last_data_time = time.ticks_ms()
                    time.sleep_ms(20)
                
                response_str = response_bytes.decode('utf-8', 'ignore')
                                
                # Parsear la respuesta para encontrar Content-Range
                for line in response_str.split('\r\n'):
                    if line.lower().startswith("content-range:"):
                        try:
                            size_str = line.split('/')[-1]
                            total_size = int(size_str)
                            utils.log_info(f"SUCCESS: Total file size discovered: {total_size} bytes.")
                            break
                        except Exception as e:
                            utils.log_error(f"Failed to parse Content-Range: {e}")
                
                if total_size is None:
                    utils.log_error("Could not determine total file size. Aborting.")
                    return

                # <<< INICIO DEL CAMBIO SOLICITADO >>>
                
                print("\n----------- CONTENIDO DEL CHUNK #1 -----------")
                
                print(f"Preparse: {response_str}")
                
                response_str = extract_block(response_str)
                with open(local_filename, "wb") as f:
                    f.write(response_str)
                print(f"Postparse: {response_str}")
                    
                print("------------ FIN DEL CHUNK #1 ------------\n")
                # <<< FIN DEL CAMBIO SOLICITADO >>>
                    
            finally:
                self.send_at_command_check("AT#XHTTPCCON=0")
                bytes_downloaded += chunk_size

            # ----------------------------------------------------------------------
            # ETAPA 2: Bucle para pedir y mostrar los chunks restantes
            # ----------------------------------------------------------------------
            utils.log_info(f"\nSTEP 2: Looping for remaining chunks...")
            
            while bytes_downloaded < total_size:
                chunk_start = bytes_downloaded
                chunk_end = min(chunk_start + chunk_size - 1, total_size - 1)

                if chunk_start >= total_size: break

                print("\n" + "="*60)
                utils.log_info(f"Requesting Chunk: bytes {chunk_start}-{chunk_end}")
                print("="*60)

                if not self.send_at_command_check(f'AT#XHTTPCCON=1,"{ip_address}",{port}', timeout=5000):
                    break
                
                try:
                    range_header = f"Range: bytes={chunk_start}-{chunk_end}\\r\\n"
                    command = f'AT#XHTTPCREQ="GET","/{filename}","{range_header}"'
                    utils.log_info(f"Sending command: {command}")
                    self.uart.write(command + '\r\n')

                    response_bytes = bytearray()
                    chunk_receive_start_time = time.ticks_ms()
                    chunk_timeout = 10000 # Timeout general de 20s por chunk

                    while time.ticks_diff(time.ticks_ms(), chunk_receive_start_time) < chunk_timeout:
                        if self.uart.any():
                            response_bytes.extend(self.uart.read(self.uart.any()))
                            
                            # <<< LÓGICA MEJORADA: Esperar al SEGUNDO URC >>>
                            # Contamos cuántas veces aparece la señal de finalización.
                            if response_bytes.count(b'#XHTTPCRSP:') >= 2:
                                # Hemos recibido tanto el URC de la cabecera como el del cuerpo.
                                # Esperamos un instante más por si los últimos bytes llegan fragmentados.
                                time.sleep_ms(50) 
                                if self.uart.any():
                                    response_bytes.extend(self.uart.read(self.uart.any()))
                                
                                utils.log_info("Second #XHTTPCRSP URC detected. Chunk response is complete.")
                                break # Salir del bucle de lectura.

                        time.sleep_ms(20) # Ceder CPU
                    
                    response_str = response_bytes.decode('utf-8', 'ignore')

                    # <<< INICIO DEL CAMBIO SOLICITADO (REPETIDO PARA EL BUCLE) >>>
                    print(f"\n----------- CONTENIDO DEL CHUNK #{bytes_downloaded // chunk_size + 1} -----------")

                    print(f"Preparse: {response_str}")

                    response_str = extract_block(response_str)
                    print(f"Postparse: {response_str}")
                    
                    if response_str != '':
                        bytes_downloaded += chunk_size
                        with open(local_filename, "ab") as f:
                            f.write(response_str)
                    else:
                         utils.log_error(f"Error downloading chunk #{bytes_downloaded // chunk_size + 1}")
                         
                    print(f"------------ FIN DEL CHUNK ------------\n")
                    # <<< FIN DEL CAMBIO SOLICITADO >>>

                finally:
                    self.send_at_command_check("AT#XHTTPCCON=0")
                
                time.sleep(2)

            utils.log_info("--- Chunked GET Test Finished ---")





