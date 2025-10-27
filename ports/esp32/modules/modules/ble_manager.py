# src/modules/ble_manager.py

import uasyncio as asyncio
from lib import aioble
import bluetooth
import json
from modules import utils # For logging
import struct


def _adv_payload_helper(name, services):
    # Main advertisement: just flags and the service UUID
    adv_payload = bytearray(b'\x02\x01\x06') # Flags (General Discoverable, BR/EDR Not Supported)

    if services:
        # 1. Convert the UUID to bytes FIRST
        uuid_bytes = bytes(services[0])
        # 2. Now, get the length of the bytes
        uuid_len = len(uuid_bytes)

        adv_payload += struct.pack('B', uuid_len + 1) # Correct length of the UUID field
        
        # The advertising type depends on the UUID length (in this case, 128 bits = 16 bytes)
        if uuid_len == 16:
            adv_payload += b'\x07' # Type: Complete List of 128-bit Service Class UUIDs
        else: # For 16-bit UUIDs
            adv_payload += b'\x03' # Type: Complete List of 16-bit Service Class UUIDs

        adv_payload += uuid_bytes # Add the UUID bytes

    # Scan response: with the full name
    scan_rsp = bytearray()
    if name:
        name_bytes = name.encode()
        scan_rsp += struct.pack('B', len(name_bytes) + 1)
        scan_rsp += b'\x09' # Type: Complete Local Name
        scan_rsp += name_bytes

    return adv_payload, scan_rsp


class BLEManager:
    """
    Manages BLE communication (advertising, services, characteristics) using aioble.
    Handles real-time data notifications and command reception.
    """

    def __init__(self, device_name="Isurlog-Datalogger", command_callback=None):
        """
        Initializes the BLE manager.

        Args:
            device_name (str): The name the device will use for BLE advertising.
            command_callback (function): The function to be called when a command is received.
                                         This function will receive one argument: the received data (bytes).
        """
        self.device_name = device_name
        self.command_callback = command_callback # Save the callback function
        self._loop = asyncio.get_event_loop()

        # Define UUIDs
        self._SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
        self._DATA_PAYLOAD_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
        self._COMMAND_CHAR_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
        self._ADV_INTERVAL_MS = 250_000

        # Create service and characteristics
        ble_service = aioble.Service(self._SERVICE_UUID)
        self.data_characteristic = aioble.Characteristic(ble_service, self._DATA_PAYLOAD_CHAR_UUID, read=True, notify=True)
        self.command_characteristic = aioble.Characteristic(ble_service, self._COMMAND_CHAR_UUID, write=True, capture=True)
        aioble.register_services(ble_service)

        # Start BLE background tasks
        self._peripheral_task = self._loop.create_task(self._peripheral_task())
        self._command_handler_task = self._loop.create_task(self._command_handler_task())
        
        #Connection state
        self.client_connected = False
        self.client_disconnected = False

        utils.log_info(f"BLEManager initializated with name '{self.device_name}'")

    async def _peripheral_task(self):
        """Task to handle advertising and connections."""
        utils.log_info("Starting advertising...")
        # This call will now use the corrected function
        adv_payload, scan_rsp_payload = _adv_payload_helper(self.device_name, [self._SERVICE_UUID])
        
        while True:
            try:
                async with await aioble.advertise(
                    self._ADV_INTERVAL_MS,
                    adv_data=adv_payload,
                    resp_data=scan_rsp_payload, # Using the scan response
                ) as connection:
                    utils.log_info(f"Connection from {connection.device}")
                    self.client_connected = True
                    await connection.disconnected()
                    utils.log_info(f"Device {connection.device} disconnected.")
                    self.client_disconnected = True
            except asyncio.CancelledError:
                utils.log_info("Advertising end.")
                return
            except Exception as e:
                # This log is crucial for seeing errors like the one you had
                utils.log_error(f"Error advertising: {e}")
                await asyncio.sleep_ms(1000)

    async def _command_handler_task(self):
        """Task to wait for writes on the command characteristic and call the callback."""
        utils.log_info("Starting BLE command receiver...")
        while True:
            try:
                connection, data = await self.command_characteristic.written()
                utils.log_info(f"BLE command received from {connection.device}: {data}")

                # If a callback function has been provided, call it
                if self.command_callback:
                    self.command_callback(data) # Call the function directly

            except asyncio.CancelledError:
                utils.log_info("Command receiver stopped.")
                return
            except Exception as e:
                utils.log_error(f"Error while receiving BLE data: {e}")

    def update_data_payload(self, payload):
        """
        Updates the data characteristic (with your IsurlogLPP or JSON payload)
        and notifies subscribed clients.
        This method is NOT 'async', it can be called from synchronous code.

        Args:
            payload (str or bytes): The data payload to send.
        """
        try:
            # Ensure the payload is in bytes
            if isinstance(payload, str):
                payload = payload.encode('utf-8')

            self.data_characteristic.write(payload, send_update=True)
            utils.log_debug(f"BLE: Payload updated.")
        except Exception as e:
            utils.log_error(f"Error updating data: {e}")

    def stop(self):
        """Stops the BLE background tasks."""
        if self._peripheral_task:
            self._peripheral_task.cancel()
        if self._command_handler_task:
            self._command_handler_task.cancel()
        utils.log_info("BLE stopped.")