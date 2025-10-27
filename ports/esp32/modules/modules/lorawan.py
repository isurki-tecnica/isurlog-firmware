from machine import UART, Pin
from modules import utils
import time
import json
from modules.config_manager import config_manager

class LoRaWAN:
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
        self.confirmed = False #ACK enabled or disabled.
        self.connected = False

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

        response = self.wait_for_response(expected_response, timeout)

        if response:
            utils.log_debug(f"Received response: {response}")
        else:
            utils.log_error(f"Timeout waiting for response to AT command: {command}")
        return response
    
    def send_at_command_check(self, command, expected_response="OK", timeout=2000, retries=3):
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
            time.sleep_ms(1000)  # Wait before retrying
        utils.log_error(f"AT command '{command}' failed after {retries} retries.")
        return False

    def wait_for_response(self, expected_response, timeout):
        """
        Waits for a specific response from the NB-IoT module.

        Args:
            expected_response: The expected response string.
            timeout: Timeout in milliseconds.

        Returns:
            The full response string if the expected response is found, otherwise None.
        """
        start_time = time.ticks_ms()
        response = ""
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.uart.any():
                try:
                    response += self.uart.read().decode("utf-8", "ignore")
                except UnicodeError as e_decode:
                    print(f"UNICODE ERROR during check: {e_decode}, buffer: {response}")
                if expected_response in response:
                    return response
                utils.log_info(f"Not expected response: {response}")
        return None

    def set_network_mode(self, mode=1):
        """Sets the network working mode after checking the current mode.

        Args:
            mode: 0 = P2P_LORA, 1 = LoRaWAN (default), 2 = P2P_FSK.
                  (The actual meaning of these modes depends on your LoRaWAN module)

        Returns: True on success or if already set, False on failure.
        """

        query_response = self.send_at_command("AT+NWM=?", "AT+NWM=") # Expect response starting with AT+NWM=
        current_mode = -1 # Indicate unknown state
        if query_response:
            try:
                # Expected response structure from query: AT+NWM=<mode>\r\nOK\r\n (or similar)
                mode_str = query_response.split("=")[1].strip("\r\nOK")
                current_mode = int(mode_str)
                utils.log_info(f"Current network mode from modem: {current_mode}")
            except (IndexError, ValueError) as e:
                utils.log_warning(f"Could not parse current network mode from '{query_response}': {e}")
        else:
            utils.log_warning("No response received for AT+NWM=? query.")

        if current_mode == mode:
            utils.log_info(f"Network mode already set to {mode}. Skipping.")
            return True
        else:
            utils.log_info(f"Setting network mode to {mode} (current: {current_mode})...")
            return self._send_at_command_check(f"AT+NWM={mode}") # For set, expect "OK"

    def set_join_mode(self, mode=1):
        """Sets the network join mode after checking the current mode.

        Args:
            mode: 0 = ABP, 1 = OTAA (default).

        Returns: True on success or if already set, False on failure.
        """
        query_response = self.send_at_command("AT+NJM=?", "AT+NJM=") # Expect response starting with AT+NJM=
        current_mode = -1
        if query_response:
            try:
                # Expected response: AT+NJM=<mode>\r\nOK\r\n
                mode_str = query_response.split("=")[1].strip("\r\nOK")
                current_mode = int(mode_str)
                utils.log_info(f"Current join mode from modem: {current_mode}")
            except (IndexError, ValueError) as e:
                utils.log_warning(f"Could not parse current join mode from '{query_response}': {e}")
        else:
            utils.log_warning("No response received for AT+NJM=? query.")

        if current_mode == mode:
            utils.log_info(f"Join mode already set to {mode}. Skipping.")
            return True
        else:
            utils.log_info(f"Setting join mode to {mode} (current: {current_mode})...")
            return self._send_at_command_check(f"AT+NJM={mode}")

    def set_class(self, class_type='A'):
        """Sets the device class after checking the current class.

        Args:
            class_type: 'A' (default), 'B', or 'C'.

        Returns: True on success or if already set, False on failure.
        """
        if class_type.upper() not in ('A', 'B', 'C'):
            utils.log_error("Invalid LoRaWAN class. Must be A, B, or C.")
            return False

        query_response = self.send_at_command("AT+CLASS=?", "AT+CLASS=") # Expect response starting with AT+CLASS=
        current_class = "" # Default to empty string if not parsed
        if query_response:
            try:
                # Expected response: AT+CLASS=<class_type>\r\nOK\r\n
                class_str = query_response.split("=")[1].strip("\r\nOK")
                current_class = class_str.upper() # Compare in uppercase
                utils.log_info(f"Current device class from modem: {current_class}")
            except IndexError as e: # No "=" found or other parsing issue
                utils.log_warning(f"Could not parse current class from '{query_response}': {e}")
        else:
            utils.log_warning("No response received for AT+CLASS=? query.")

        if current_class == class_type.upper():
            utils.log_info(f"Device class already set to {class_type.upper()}. Skipping.")
            return True
        else:
            utils.log_info(f"Setting device class to {class_type.upper()} (current: {current_class})...")
            return self._send_at_command_check(f"AT+CLASS={class_type.upper()}")

    def set_band(self, band=4):
        """Sets the active region after checking the current band.

        Args:
            band: Region/band number (e.g., 4 for EU868).

        Returns: True on success or if already set, False on failure.
        """
        query_response = self.send_at_command("AT+BAND=?", "AT+BAND=") # Expect response starting with AT+BAND=
        current_band = -1
        if query_response:
            try:
                # Expected response: AT+BAND=<band_number>\r\nOK\r\n
                band_str = query_response.split("=")[1].strip("\r\nOK")
                current_band = int(band_str)
                utils.log_info(f"Current band from modem: {current_band}")
            except (IndexError, ValueError) as e:
                utils.log_warning(f"Could not parse current band from '{query_response}': {e}")
        else:
            utils.log_warning("No response received for AT+BAND=? query.")

        if current_band == band:
            utils.log_info(f"Band already set to {band}. Skipping.")
            return True
        else:
            utils.log_info(f"Setting band to {band} (current: {current_band})...")
            return self._send_at_command_check(f"AT+BAND={band}")
    
    def set_confirmed_mode(self, mode):
        """Sets the confirmed mode.

        Args:
            mode: This command is used to configure the uplink payload to be confirmed or unconfirmed type.

        Returns: True on success, False on failure.
        """
        
        self.confirmed = mode
        return self.send_at_command_check(f"AT+CFM={mode}")


    def set_dev_eui(self, dev_eui):
        """Sets the Device EUI.

        Args:
            dev_eui: The Device EUI string.

        Returns: True on success, False on failure.
        """
        return self.send_at_command_check(f"AT+DEVEUI={dev_eui}")

    def set_app_eui(self, app_eui):
        """Sets the Application EUI.

        Args:
            app_eui: The Application EUI string.

        Returns: True on success, False on failure.
        """
        return self.send_at_command_check(f"AT+APPEUI={app_eui}")

    def set_app_key(self, app_key):
        """Sets the Application Key.

        Args:
            app_key: The Application Key string.

        Returns: True on success, False on failure.
        """
        return self.send_at_command_check(f"AT+APPKEY={app_key}")

    def join_network(self, attempts=3, interval=8):
      """Joins the LoRaWAN network.

      Args:
          attempts: Number of join attempts.
          interval:  Join interval 

      Returns: True on success, False on failure.  Waits for +JOIN: Network joined
      """
      if not self.send_at_command_check(f"AT+JOIN=1:0:{interval}:{attempts}", "OK"):
            return False
      # Now wait for the "Network joined" indication.  This can take some time.
      response = self.wait_for_response("+EVT:JOINED", timeout=60000)  # Wait up to 60 seconds
      if response:
          utils.log_info("Successfully joined LoRaWAN network.")
          return True
      else:
          utils.log_error("Failed to join LoRaWAN network.")
          return False

    def request_time(self, ):
        """Requests the current date and time.

        Args:
            enable: 0 = Disabled, 1 = Enabled (default).

        Returns: True on success, False on failure.
        """
        return self.send_at_command_check(f"AT+TIMEREQ=1")

    def send_uplink(self, port, data):
        """Sends data over the LoRaWAN network.

        Args:
            port: The application port.
            data: The data to send (as a hexadecimal string).

        Returns:
            True on success, False on failure.  Waits for '+SEND: OK'
        """
        if self.confirmed:
            response = self.send_at_command(f"AT+SEND={port}:{data}", "+EVT:SEND_CONFIRMED_OK", timeout=10000)  # Longer timeout for sending
        else:
            response = self.send_at_command(f"AT+SEND={port}:{data}", "+EVT:TX_DONE", timeout=10000)  # Longer timeout for sending
        if response:
            utils.log_info(f"Data sent successfully on port {port}.")
            return True
        else:
            utils.log_error(f"Failed to send data on port {port}.")
            return False
        
    def get_downlink(self):
        
        """This command is used to access the last received data in hex format.

        Returns:
            Payload if data, None otherwise.  Waits for '+SEND: OK'
        """
        response = self.send_at_command("AT+RECV=?", "AT+RECV=", timeout=1000)  # Longer timeout for sending
        
        if response:
            data = response.split("=")[1]
            data = data.split("OK")[0]
            data = data.strip("\r\n")
            if data == "0:":
                utils.log_info(f"No downlink received.")
                return None
            else:
                port, data = data.split(":")
                utils.log_info(f"Data received on port {port}: {data}")
                return data
        else:
            utils.log_error(f"Failed to get response.")
            return None
        
    def get_downlink_hex(self):
        """Obtiene el último downlink como string hexadecimal."""

        response = self.send_at_command("AT+RECV=?", "AT+RECV=", timeout=1000)
        if response:
             try:
                 # '+RECV=P:xxxxxxxx'
                 if "OK" in response and ":" in response:
                     parts = response.split(':')
                     if len(parts) >= 2 and parts[0].startswith("+RECV="):
                          port_data = parts[0].split('=')[1] # Obtiene P
                          data_hex = parts[1].split('\r')[0].split('\n')[0] # Obtiene xxxxxxxx
                          if data_hex:
                              utils.log_info(f"Hex data received on port {port_data}: {data_hex}")
                              return data_hex
                          else:
                              # Puede ser un downlink vacío o solo ACK
                              utils.log_info(f"Empty downlink or ACK received.")
                              return None
                     else:
                          # No es un formato de downlink esperado o no hay datos
                           return None
                 else:
                     # No hubo respuesta o fue inesperada
                     return None
             except Exception as e:
                 utils.log_error(f"Error parsing downlink response: {e}")
                 return None
        else:
            utils.log_error(f"Failed to get downlink response.")
            return None


    def get_downlink_bytes(self):
        """Obtiene el último downlink como objeto bytes."""
        data_hex = self.get_downlink_hex()
        if data_hex:
            try:
                # Convertir hexadecimal a bytes
                return binascii.unhexlify(data_hex)
            except (ValueError, TypeError) as e:
                utils.log_error(f"Failed to convert hex to bytes: {data_hex} - {e}")
                return None
        return None
        
    def get_network_time(self):
        """Gets the local time from the module.

        Returns:
            The local time as a string (format: hhmmss on MM/DD/YYYY), or None on failure.
        """
        response = self.send_at_command("AT+LTIME=?", "AT+LTIME=", timeout=5000)
        if response:
            try:
                # Extract time string. Example response: "+LTIME: 04h36m00s on 11/27/2023"
                time_str = response.split("=")[1].strip()
                time_str = time_str.strip('\r\nOK')
                utils.log_info(f"Module local time: {time_str}")
                return time_str
            except (IndexError, ValueError) as e:
                utils.log_error(f"Error parsing time response: {e}, response: {response}")
                return None
        else:
            utils.log_error("Failed to get local time from LoRaWAN module.")
            return None

    def enable_auto_sleep(self):
        """Enable RAK3172 auto sleep.  LPM makes the device sleep automatically after sending AT commands.

        Returns: True on success, False on failure.
        """
        return self.send_at_command("AT+LPM=1")
    
    def sleep(self):
        """Puts the module into sleep mode.

        Returns: True on success, False on failure.
        """
        return self.send_at_command("AT+SLEEP")
        
    def modem_time_to_unix(self, time_str):
        """
        Converts the modem's time string (from AT+LTIME=?) to a Unix timestamp.

        Args:
            time_str: The time string in the format "hhmmss on MM/DD/YYYY".

        Returns:
            The Unix timestamp (seconds since 1970-01-01 00:00:00 UTC), or None
            if an error occurred.
        """
        try:
            # "04h36m00s on 11/27/2023"
            time_parts = time_str[:8].split("h")  # Split into hours, minutes, seconds
            hour = int(time_parts[0])
            minute = int(time_parts[1].split("m")[0]) # Correctly extract minutes
            second = int(time_parts[1].split("m")[1][:-1]) #Correctly extracts seconds

            date_parts = time_str[12:].split("/")
            
            month = int(date_parts[0])
            day = int(date_parts[1])
            year = int(date_parts[2])
            
            # Create a time tuple in *local* time (as required by mktime)
            local_time_tuple = (year, month, day, hour, minute, second, 0, 0)  # Weekday and yearday are ignored

            # Convert to seconds since epoch (local time)
            timestamp = time.mktime(local_time_tuple)
           
            return timestamp

        except (IndexError, ValueError) as e:
            utils.log_error(f"Error parsing time string from modem: {e}, string: {time_str}")
            return None

    def connect(self):
        """
        Configures and joins the LoRaWAN network using settings from config_manager.

        This is a convenience method that combines setting all the parameters and joining.
        It uses 'dynamic_config' from the config_manager for settings.

        Returns: True on success, False on failure.
        """

        # Load configuration from config_manager
        lorawan_config = config_manager.dynamic_config["communications"].get("lorawan", {})

        if not self.send_at_command_check("AT"):
            return False

        # Set Network Mode (LoRaWAN)
        if not self.set_network_mode(lorawan_config.get("network_mode", 1)):  # Default to LoRaWAN
            return False

        # Set Join Mode (OTAA or ABP)
        if not self.set_join_mode(lorawan_config.get("join_mode", 1)):  # Default to OTAA
            return False

        # Set Class (A, B, or C)
        if not self.set_class(lorawan_config.get("class", "A")):  # Default to Class A
            return False

        # Set Band
        if not self.set_band(lorawan_config.get("band", 4)):  # Default to EU868
            return False

        # Set DEVEUI, APPEUI, and APPKEY
        if not self.set_dev_eui(lorawan_config.get("dev_eui")):
            return False
        if not self.set_app_eui(lorawan_config.get("app_eui")):
            return False
        if not self.set_app_key(lorawan_config.get("app_key")):
            return False

        # Join the network
        if not self.join_network():
            return False

        return True

    def check_network_connection(self):
        """
        Checks if module is connected to the network.

        Returns:
            True if connected, False otherwise.
        """

        response = self.send_at_command("AT+NJS=?")
        if response and ("AT+NJS=1" in response):
            utils.log_info("LoRaWAN module connected to the network.")
            return True

        return False
    
    def reset(self):
        
        """
        Performs a soft reset of the nRF91 Series SiP

        Returns:
            True if reset was successful, False otherwise.
        """

        return self.send_at_command_check("ATZ", "LoRaWAN", timeout=4000)

