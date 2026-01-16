import uio
import builtins
from machine import UART, Pin
import time

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
    print(f"--- Remote REPL Mode Activated. Listening on {command_topic} ---")
    
    repl_active = True
    last_message_time = time.ticks_ms()
    
    while repl_active:
        #Read all UART buffer
        
        if (time.ticks_diff(time.ticks_ms(), last_message_time) > 120000):
            print("Disconnecting from online REPL due to timeout...")
            mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
            repl_active = False
            
        received_mqtt_messages = mqtt_client.check_msg()
        if received_mqtt_messages:
            for topic, msg in received_mqtt_messages:
                msg = msg.decode('utf-8')
                
                if msg == "logout":

                    mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
                    print("Exit command received. Deactivating REPL.")
                    response = "REPL session terminated."
                    repl_active = False
                    
                else:
                
                    command_output = str(execute_code(msg))
                    print(f"Response to received commmand: {command_output}")
                    mqtt_client.publish(f"{base_topic}/repl_out/{ser_num}", command_output)
                    if wdt:
                        print("Feeding WDT from REPL task.")
                        wdt.feed()
        
        time.sleep(1)
    
def handle_remote_repl_nb_iot(ser_num, base_topic, wdt, nb_iot_module):
    """
    Enables REPL mode NB-IoT.
    """
    uart = UART(2, baudrate=115200, tx=Pin(4), rx=Pin(2), timeout=1000)
    command_topic = f"{base_topic}/repl_in/{ser_num}" 
    print(f"--- Remote REPL Mode Activated. Listening on {command_topic} ---")
    
    repl_active = True
    last_message_time = time.ticks_ms()

    while repl_active:
        #Read all UART buffer
        
        if (time.ticks_diff(time.ticks_ms(), last_message_time) > 120000):
            print("Disconnecting from online REPL due to timeout...")
            nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
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

                            nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", "Disconnected")
                            print("Exit command received. Deactivating REPL.")
                            response = "REPL session terminated."
                            repl_active = False
                            
                        else:
                        
                            command_output = execute_code(message_str)
                            print(f"Response to received commmand: {command_output}")
                            nb_iot_module.mqtt_publish(f"{base_topic}/repl_out/{ser_num}", command_output)
                            if wdt:
                                print("Feeding WDT from REPL task.")
                                wdt.feed()
                            
                    else:
                        
                        print(f"Received incomplete MQTT message block: {lines}")
                
                else:
                    print(f"Received non-MQTT data: {block_str}")
                    
            except Exception as e:
                print(f"Error while processing UART data: {e}")