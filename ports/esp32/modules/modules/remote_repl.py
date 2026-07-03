# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import uio
import builtins
from machine import UART, Pin
import time
from modules import utils

REPL_TIMEOUT = 120000  # ms, configurable using remote console via "REPL_TIMEOUT = <valor>"

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


def handle_remote_repl_wifi(ser_num, base_topic, wdt, mqtt_client):
    """
    Enables REPL mode WiFi.
    """
    command_topic = f"{base_topic}/repl_in/{ser_num}" 
    utils.log_info(f"--- Remote REPL Mode Activated. Listening on {command_topic} ---")
    
    repl_active = True
    last_message_time = time.ticks_ms()
    
    while repl_active:
        
        time.sleep(1)
        
        #Feed Watchdog  
        if wdt:
            wdt.feed()
            
        #Check timeout  
        if (time.ticks_diff(time.ticks_ms(), last_message_time) > REPL_TIMEOUT):
            utils.log_info("Disconnecting from online REPL due to timeout...")
            mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
            repl_active = False
        
        received_mqtt_messages = mqtt_client.check_msg()
        if received_mqtt_messages:
            for topic, msg in received_mqtt_messages:
                msg = msg.decode('utf-8')
                
                if msg == "logout":

                    mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
                    utils.log_info("Exit command received. Deactivating REPL.")
                    response = "REPL session terminated."
                    repl_active = False
                    
                else:
                
                    command_output = str(execute_code(msg))
                    utils.log_info(f"Response to received commmand: {command_output}")
                    mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", command_output)
    
def handle_remote_repl_nb_iot(ser_num, base_topic, wdt, nb_iot_module, connection_preference, mqtt_config):
    """
    Enables REPL mode NB-IoT.
    """
    if connection_preference == 1:
        desired_mode_val = 4
    elif connection_preference == 2:
        desired_mode_val = 5
    
    utils.log_info("Reconfiguring NB-IoT parameters for faster REPL response...")
    nb_iot_module.send_at_command_check("AT+CFUN=4")
    nb_iot_module.send_at_command_check(f'AT+CEDRXS=1,{desired_mode_val},"0000"')
    nb_iot_module.send_at_command_check("AT+CFUN=1")
    nb_iot_module.wait_for_network_connection(timeout=180000)
    utils.log_info("NB-IoT parameters configured.")
    
    if nb_iot_module.mqtt_connect(mqtt_config.get("user", ""), mqtt_config.get("passwd", ""), mqtt_config.get("ip", ""), mqtt_config.get("port", 1883)):
        utils.log_info("MQTT connection restablished.")
        
        if nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Connected"):
            nb_iot_module.mqtt_subscribe(f"{base_topic}/repl_in/{ser_num}", QoS=2)
    
            uart = UART(2, baudrate=115200, tx=Pin(4), rx=Pin(2), timeout=1000)
            command_topic = f"{base_topic}/repl_in/{ser_num}" 
            utils.log_info(f"--- Remote REPL Mode Activated. Listening on {command_topic} ---")
            
            repl_active = True
            last_message_time = time.ticks_ms()

            while repl_active:
                
                time.sleep(1)
                
                #Feed Watchdog  
                if wdt:
                    wdt.feed()

                #Check timeout  
                if (time.ticks_diff(time.ticks_ms(), last_message_time) > REPL_TIMEOUT):
                    utils.log_info("Disconnecting from online REPL due to timeout...")
                    nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
                    repl_active = False
                    
                #Read all UART buffer   
                if uart.any():
                    uart_bytes = uart.read()

                    try:
                        block_str = uart_bytes.decode('utf-8').strip()
                        lines = block_str.splitlines()

                        # Check is it's a MQTT message
                        if lines and lines[0].startswith('#XMQTTMSG:'):
                            
                            header_line = lines[0]

                            if len(lines) >= 3:

                                topic_str = lines[1]
                                message_str = lines[2]
                                
                                last_message_time = time.ticks_ms()
                                
                                utils.log_info(f"MQTT MSG on topic '{topic_str}': {message_str}")
                                
                                if message_str.strip() == "logout":

                                    nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
                                    utils.log_info("Exit command received. Deactivating REPL.")
                                    response = "REPL session terminated."
                                    repl_active = False
                                    
                                else:
                                
                                    command_output = execute_code(message_str)
                                    utils.log_info(f"Response to received commmand: {command_output}")
                                    nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", command_output)
                                    
                            else:
                                
                                utils.log_info(f"Received incomplete MQTT message block: {lines}")
                        
                        else:
                            utils.log_info(f"Received non-MQTT data: {block_str}")
                            
                    except Exception as e:
                        utils.log_error(f"Error while processing UART data: {e}")
                        
    else:
        utils.log_error(f"Error while reconnecting to MQTT server.")
        
    utils.log_info("Reconfiguring NB-IoT parameters for low power consumption...")
    nb_iot_module.send_at_command_check("AT+CFUN=4")
    nb_iot_module.send_at_command_check(f'AT+CEDRXS=1,{desired_mode_val},"0011"')
    nb_iot_module.send_at_command_check("AT+CFUN=1")
    nb_iot_module.wait_for_network_connection(timeout=180000)
    utils.log_info("NB-IoT parameters configured.")
    
    if nb_iot_module.mqtt_connect(mqtt_config.get("user", ""), mqtt_config.get("passwd", ""), mqtt_config.get("ip", ""), mqtt_config.get("port", 1883)):
        utils.log_info("MQTT connection restablished.")
    else:
        utils.log_error(f"Error while reconnecting to MQTT server.")
