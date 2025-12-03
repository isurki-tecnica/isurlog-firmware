import paho.mqtt.client as mqtt
import json
import base64
import IsurlogLPP 

# --- Connection Parameters ---
BROKER_URL = "mqttisurdash.isurki.com"
BROKER_PORT = 8883
USERNAME = "YOUR_UNIQUE_USERNAME_HERE"
PASSWORD = "YOUR_UNIQUE_PASSWORD_HERE"
# Topics for both NB-IoT and LoRaWAN devices
TOPIC_NB_IOT = "dataloggers/datos/+"
APLICATION_ID = "YOUR_APPLICATION_ID_HERE"
TOPIC_LORAWAN = f"application/+/device/+/event/up"

# --- MQTT Callback Functions ---

def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the broker."""
    if rc == 0:
        print("Successfully connected to MQTT Broker!")
        # Subscribe to both topics upon connection
        client.subscribe([(TOPIC_LORAWAN, 0), (TOPIC_NB_IOT, 0)])
        print(f"Subscribed to NB-IoT topic: {TOPIC_NB_IOT}")
        print(f"Subscribed to LoRaWAN topic: {TOPIC_LORAWAN}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback function for when a message is received."""
    print(f"\n--- Message received on topic: {msg.topic} ---")
    
    # Check if the message is from a LoRaWAN device via ChirpStack
    if msg.topic.startswith("application/"):
        try:
            # 1. Decode the main JSON payload from ChirpStack
            chirpstack_data = json.loads(msg.payload.decode('utf-8'))
            print(chirpstack_data)
            device_name = chirpstack_data.get('deviceInfo', {}).get('deviceName', 'unknown')
            
            # 2. Extract the already decoded 'object'
            decoded_object = chirpstack_data.get('object')
            
            print(f"LoRaWAN device Name: {device_name}")
            if decoded_object:
                print(f"Decoded data (from ChirpStack 'object'): {decoded_object}")
                # You can also access other useful info, e.g., RSSI
                rssi = chirpstack_data.get('rxInfo', [{}])[0].get('rssi', 'N/A')
                print(f"Network Info: RSSI = {rssi}")
            else:
                print("Message contains no decoded 'object'.")

        except Exception as e:
            print(f"An error occurred processing LoRaWAN message: {e}")

    # Otherwise, assume it's a direct payload from an NB-IoT device
    else:
        try:
            device_id = msg.topic.split('/')[-1]
            # The payload is already the hex string
            hex_payload = msg.payload.decode()

            print(f"NB-IoT device ID: {device_id}")
            print(f"Raw payload (hex): {hex_payload}")

            # Use your IsurlogLPP library to decode the hex payload
            decoded_data = IsurlogLPP.decodeIsurlogLPP(hex_payload)
            print(f"Decoded data: {decoded_data}")

        except Exception as e:
            print(f"An error occurred processing NB-IoT message: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"Connecting to broker at {BROKER_URL}...")
        client.connect(BROKER_URL, BROKER_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Could not connect to broker: {e}")