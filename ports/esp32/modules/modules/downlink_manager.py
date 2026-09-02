"""
downlink_manager.py

Processes downlinks (incoming messages) from the three transports:
WiFi, NB-IoT, and LoRaWAN.

Each transport has its own function (process_wifi_downlinks,
process_nbiot_downlinks, process_lorawan_downlinks) that does practically
the same thing that code block in main.py used to do, except now
it lives here. There is no "magic" involved: each function explicitly
receives what it needs (the communications module, rtc_memory, wdt, ser_num,
base_topic) and runs its own if/elif logic, just like before.

The only things actually shared across the three transports are:
    - is_manual_command(text): check if a text is an SD/EV command.
    - process_sd_ev_manual_command(...): execute that manual command.
    - apply_config(...): decode an LPP hex downlink and apply it.

LoRaWAN now delivers its downlinks via lorawan_module.get_downlink_messages(),
which returns the same structure as nb_iot_module.get_mqtt_messages():
a list of dictionaries {'topic':..., 'message':...}. That is why the
LoRaWAN loop is as simple as the other two transports; all hex -> text
conversion is already handled inside lorawan.py.

Usage from main.py:

    from modules import downlink_manager

    downlink_manager.process_wifi_downlinks(mqtt_client, rtc_memory, wdt, ser_num, base_topic)
    downlink_manager.process_nbiot_downlinks(nb_iot_module, rtc_memory, wdt, ser_num, base_topic)
    downlink_manager.process_lorawan_downlinks(lorawan_module, rtc_memory)
"""

from modules import utils
from modules.config_manager import config_manager
from modules.power_manager import pm
from lib.IsurlogLPP import IsurlogLPPEncoder
from lib.ota import rollback
import asyncio
import time

encoder = IsurlogLPPEncoder()


# --------------------------------------------------------------------------
# Shared functions
# --------------------------------------------------------------------------

def is_manual_command(text):
    """An SD/EV manual command is plain text like 'SD1 ON' or 'EV1 500'."""
    return "SD" in text or "EV" in text


def apply_config(hex_text):
    """Decodes an LPP hex downlink and applies it as a new configuration.
    Return Downlink ID if present"""
    utils.log_info(f"New downlink: {hex_text}")
    decoded_downlink = encoder.decode(hex_text)
    downlink_id = next((item['value'] for item in decoded_downlink if item.get('channel') == 0 and item.get('name') == 'setDownlinkID'), None)
    if downlink_id is not None:
        decoded_downlink = [item for item in decoded_downlink if not (item.get('channel') == 0 and item.get('name') == 'setDownlinkID')]
    utils.log_info(f"Decoded downlink: {decoded_downlink}")
    config_manager.apply_conf_update(decoded_downlink)
    return downlink_id

def process_sd_ev_manual_command(command, rtc_memory, ble=False):
    """Executes a digital output (SD) or valve (EV) manual command.
    Moved as-is from main.py; the only change is that rtc_memory is now a
    parameter instead of a global variable."""

    if "SD" in command:
        command = command.strip("SD")
        out_num, state = command.split(" ")
        out_num = int(out_num)

        if state == 'ON':
            pm.control_digital_output(1)
        else:
            pm.control_digital_output(0)

    else:
        if "Clear" in command:  # Clear EV manual control flag
            rtc_memory.set_manual_ev_flag(False)
            return

        pm.control_vdc(1)
        time.sleep_ms(250)
        pm.control_5v(1)
        time.sleep_ms(4000)

        isurnode_config = config_manager.get_dynamic("isurnode_config")
        slave_address = isurnode_config.get("slave_address")
        modbus_config = config_manager.get_dynamic("modbus_config")

        from modules import modbus_sensor
        baudrate_map = {0: 9600, 1: 19200, 2: 38400, 3: 57600, 4: 115200}
        parity_map = {0: None, 1: 0, 2: 1}
        modbus_module = modbus_sensor.ModbusSensor(
            baudrate=baudrate_map[modbus_config.get("baudrate", 0)],
            data_bits=modbus_config.get("data_bits", 8),
            parity=parity_map[modbus_config.get("parity", 0)],
            stop_bits=modbus_config.get("stop_bits", 1)
        )

        command = command.strip("EV")
        channel, param = command.split(" ")
        channel = int(channel)
        param = int(param)
        modbus_addr = channel * 2 + 200

        utils.log_info(f'Channel:{channel} Slave address:{slave_address} Modbus address:{modbus_addr} Param:{param}')

        if param == 1 or param == 0:  # ON/OFF valve
            rtc_memory.set_ev_state(channel, 1)
            if param == 0:
                modbus_addr += 1
                rtc_memory.set_ev_state(channel, 0)
            modbus_module.write_register(slave_address, modbus_addr, 1)

        else:  # Proportional valve
            open_addr = modbus_addr
            close_addr = modbus_addr + 1

            modbus_module.write_register(slave_address, open_addr, 1)
            time.sleep_ms(param)
            modbus_module.write_register(slave_address, close_addr, 1)
            time.sleep_ms(150)  # STM32L4 with MicroPython is slow.

        pm.control_vdc(0)
        pm.control_5v(0)

    rtc_memory.set_manual_ev_flag(True)


async def _handle_ota_update(text, nb_iot_module, wdt, ser_num, base_topic):
    """Flujo de actualizacion OTA. Solo llega aqui desde downlinks NB-IoT."""
    from machine import reset
    from modules import update_manager

    utils.log_info("Starting OTA update process...")
    update_instructions = text.split(" ")

    update_manager.clean_flash(["micropython.b64.txt", "micropython.bin", "update_candidate.py"])

    if len(update_instructions) == 7:
        _, server, port, up_file_name, up_checksum, main_file_name, main_checksum = update_instructions
        utils.log_info(
            f"Received instructions: Server: {server} Port: {port} "
            f"up_File: {up_file_name} up_Checksum: {up_checksum} "
            f"main_File: {main_file_name} main_Checksum: {main_checksum}"
        )

        if await nb_iot_module.download_file(server, port, up_file_name, "micropython.b64.txt", wdt=wdt, chunk_size=8192):
            if update_manager.decode_base64_file("micropython.b64.txt", "micropython.bin"):
                if update_manager.verify_file_checksum(up_checksum, filename="micropython.bin"):
                    utils.log_info("Decoding successful!")
                    ota_succeded = False
                    from lib.ota import update
                    try:
                        with update.OTA(verbose=True, reboot=False) as ota_updater:
                            with open("/micropython.bin", "rb") as f:
                                ota_updater.from_stream(f)
                        utils.log_info("OTA update prepared.")
                        ota_succeded = True
                    except Exception as e_ota:
                        utils.log_error(f"Error during .bin OTA update: {e_ota!r}")

                    try:
                        update_manager.clean_flash(["micropython.b64.txt", "micropython.bin", "update_candidate.py"])
                        if ota_succeded:
                            await nb_iot_module.download_file(server, port, main_file_name, "update_candidate.py", chunk_size=2048)
                            if update_manager.verify_file_checksum(main_checksum, filename="update_candidate.py"):
                                update_manager.perform_update()
                                utils.log_info("Update process finished, rebooting in 5 seconds...")
                                if await nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update OK"):
                                    utils.log_error("Failed to publish response")
                                    await asyncio.sleep_ms(5000)
                                    reset()
                    except Exception as e_ota:
                        utils.log_error(f"Error during .py OTA update: {e_ota!r}")
                else:
                    utils.log_error("Decoding failed.")

    # If code reached this point, update wasn't completed.
    rollback.cancel_force()
    update_manager.clean_flash(["micropython.b64.txt", "micropython.bin", "update_candidate.py"])
    if not await nb_iot_module.mqtt_publish(f"{base_topic}/update/{ser_num}", "Update FAILED"):
        utils.log_error("Failed to publish response")


# --------------------------------------------------------------------------
# Transport functions, each with different conditions.
# --------------------------------------------------------------------------

async def process_wifi_downlinks(mqtt_client, rtc_memory, wdt, ser_num, base_topic):
    """
    Commands supported by WiFi: Wake, REPL, SD/EV, or config (hex LPP).
    """
    
    downlink_IDs = []
    
    received_mqtt_messages = mqtt_client.check_msg()
    utils.log_info(f"Received MQTT messages: {received_mqtt_messages}")
    if not received_mqtt_messages:
        return

    utils.log_info(f"Received {len(received_mqtt_messages)} MQTT message(s).")
    for topic, msg in received_mqtt_messages:
        msg = msg.decode('utf-8')
        utils.log_info(f"Processing message on topic: {topic}")
        utils.log_info(f"Message content: {msg}")

        if msg == "Wake":
            pass

        elif msg == "REPL":
            if not mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Connected"):
                mqtt_client.subscribe(f"{base_topic}/repl_in/{ser_num}")
                from modules.remote_repl import handle_remote_repl_wifi
                handle_remote_repl_wifi(ser_num, base_topic, wdt, mqtt_client)

        elif is_manual_command(msg):
            utils.log_info("Processing manual command...")
            process_sd_ev_manual_command(msg, rtc_memory)

        else:
            downlink_IDs.append(apply_config(msg))
            
    for downlink_ID in downlink_IDs:
        if not mqtt_client.publish(f"{base_topic}/config_ack/{ser_num}", f"{downlink_ID}:OK"):
            utils.log_error("Failed to publish payload through cellular MQTT client.")
        await asyncio.sleep_ms(250)

    mqtt_client.publish(f"{base_topic}/config/{ser_num}", b"", retain=True, qos=1)  # Delete retained message!
    

async def process_nbiot_downlinks(nb_iot_module, rtc_memory, wdt, ser_num, base_topic):
    """
    Commands supported by NB-IoT: Wake, REPL, SD/EV, update (OTA), or
    config (hex LPP).
    """
    
    downlink_IDs = []
    
    received_mqtt_messages = nb_iot_module.get_mqtt_messages()
    if not received_mqtt_messages:
        return

    utils.log_info(f"Received {len(received_mqtt_messages)} MQTT message(s).")
    for msg_dict in received_mqtt_messages:
        msg = msg_dict['message']

        if msg == "Wake":
            pass

        elif msg == "REPL":
            from modules.remote_repl import handle_remote_repl_nb_iot
            await handle_remote_repl_nb_iot(
                ser_num, base_topic, wdt, nb_iot_module,
                config_manager.dynamic_config["communications"]["cellular_iot"].get("preference", 0),
                config_manager.get_dynamic("communications").get("mqtt")
            )

        elif is_manual_command(msg):
            utils.log_info("Processing manual command...")
            process_sd_ev_manual_command(msg, rtc_memory)

        elif "update" in msg:
            await _handle_ota_update(msg, nb_iot_module, wdt, ser_num, base_topic)

        else:
            downlink_IDs.append(apply_config(msg))
            
    for downlink_ID in downlink_IDs:
        if not nb_iot_module.mqtt_publish(f"{base_topic}/config_ack/{ser_num}", f"{downlink_ID}:OK"):
            utils.log_error("Failed to publish payload through cellular MQTT client.")
        await asyncio.sleep_ms(250)
        
async def process_lorawan_downlinks(lorawan_module, rtc_memory):
    """
    Commands supported by LoRaWAN: only SD/EV or config (hex LPP).
    There is no Wake/REPL/update: LoRaWAN's airtime and payload size limits
    aren't enough for that.
    """
    for msg_dict in await lorawan_module.get_downlink_messages():
        msg = msg_dict['message']

        if is_manual_command(msg):
            utils.log_info("Processing manual command...")
            process_sd_ev_manual_command(msg, rtc_memory)
        else:
            apply_config(msg)