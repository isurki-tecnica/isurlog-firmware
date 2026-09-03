# src/modules/ble_manager.py

# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import uasyncio as asyncio
from lib import aioble
from lib.aioble import security
from lib.aioble.core import ble
import bluetooth
from modules import utils
import struct
from modules.config_manager import config_manager

_IO_CAPABILITY_DISPLAY_ONLY = const(0)

security.load_secrets()

def _adv_payload_helper(name, services):
    adv_payload = bytearray(b'\x02\x01\x06')

    if services:
        uuid_bytes = bytes(services[0])
        uuid_len = len(uuid_bytes)

        adv_payload += struct.pack('B', uuid_len + 1)

        if uuid_len == 16:
            adv_payload += b'\x07'
        else:
            adv_payload += b'\x03'

        adv_payload += uuid_bytes

    scan_rsp = bytearray()
    if name:
        name_bytes = name.encode()
        scan_rsp += struct.pack('B', len(name_bytes) + 1)
        scan_rsp += b'\x09'
        scan_rsp += name_bytes

    return adv_payload, scan_rsp


class BLEManager:

    def __init__(self, device_name="Isurlog-Datalogger", command_callback=None):
        self.device_name = device_name
        self.command_callback = command_callback
        self._loop = asyncio.get_event_loop()
        
        ble.config(gap_name=self.device_name)
        
        pin = config_manager.static_config.get("pin", 123456)
        security.set_fixed_pin(pin)
        
        self._SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
        self._DATA_PAYLOAD_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
        self._COMMAND_CHAR_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
        self._ADV_INTERVAL_MS = 250_000

        ble_service = aioble.Service(self._SERVICE_UUID)

        self.data_characteristic = aioble.Characteristic(
            ble_service,
            self._DATA_PAYLOAD_CHAR_UUID,
            read=True,
            notify=True
        )

        self.command_characteristic = aioble.Characteristic(
            ble_service,
            self._COMMAND_CHAR_UUID,
            write=True,
            capture=True
        )

        aioble.register_services(ble_service)

        self._peripheral_task = self._loop.create_task(self._peripheral_task())
        self._command_handler_task = self._loop.create_task(self._command_handler_task())

        self.client_connected = False
        self.client_disconnected = False

        utils.log_info(f"BLEManager secure init: {self.device_name}")

    async def _peripheral_task(self):
        utils.log_info("Starting secure BLE advertising...")

        adv_payload, scan_rsp_payload = _adv_payload_helper(
            self.device_name,
            [self._SERVICE_UUID]
        )

        while True:
            try:
                async with await aioble.advertise(
                    self._ADV_INTERVAL_MS,
                    adv_data=adv_payload,
                    resp_data=scan_rsp_payload,
                ) as connection:

                    utils.log_info(f"BLE connected: {connection.device}")

                    try:
                        await security.pair(
                            connection,
                            bond=True,
                            le_secure=True,
                            mitm=True,
                            io=_IO_CAPABILITY_DISPLAY_ONLY,
                            timeout_ms=30000
                        )

                        utils.log_info("BLE paired + encrypted + bonded")

                    except Exception as e:
                        utils.log_warning(f'Pairing failed: {e} — disconnecting')
                        await connection.disconnect()
                        continue

                    self.client_connected = True

                    await connection.disconnected()

                    utils.log_info("BLE disconnected")
                    self.client_disconnected = True

            except asyncio.CancelledError:
                return
            except Exception as e:
                utils.log_error(f"BLE error: {e}")
                await asyncio.sleep_ms(1000)

    async def _command_handler_task(self):
        utils.log_info("Secure BLE command receiver started")

        while True:
            try:
                connection, data = await self.command_characteristic.written()

                if not connection.encrypted:
                    utils.log_warning("Rejected command from unencrypted link")
                    continue

                utils.log_info(f"BLE command: {data}")

                if self.command_callback:
                    self.command_callback(data)

            except asyncio.CancelledError:
                return
            except Exception as e:
                utils.log_error(f"Command error: {e}")

    def update_data_payload(self, payload):
        try:
            if isinstance(payload, str):
                payload = payload.encode()

            self.data_characteristic.write(payload, send_update=True)

        except Exception as e:
            utils.log_error(f"BLE update error: {e}")

    def stop(self):
        if self._peripheral_task:
            self._peripheral_task.cancel()
        if self._command_handler_task:
            self._command_handler_task.cancel()
        utils.log_info("BLE stopped")
