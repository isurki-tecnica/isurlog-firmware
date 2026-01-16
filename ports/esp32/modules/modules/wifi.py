import network
import time

def is_connected():
    """
    Checks if the device is currently connected to a Wi-Fi network.
    
    Returns:
        bool: True if connected, False otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.isconnected()

def do_connect(ssid, password, timeout_seconds=10):
    """
    Connects to a Wi-Fi network with a specified timeout.
    
    Args:
        ssid (str): The network name.
        password (str): The network password.
        timeout_seconds (int): Maximum time to wait for connection in seconds.
        
    Returns:
        bool: True if connected successfully, False if timed out.
    """
    
    # Initialize the station interface
    sta_if = network.WLAN(network.STA_IF)
    
    # Check if already connected
    if not sta_if.isconnected():
        print(f'Connecting to network {ssid}...')
        
        # Activate the interface
        sta_if.active(True)
        
        # Connect to the access point
        # Note: We use the variables passed to the function, not hardcoded strings
        sta_if.connect(ssid, password)
        
        # Get the starting time
        start_time = time.time()
        
        # Loop until connected or timeout is reached
        while not sta_if.isconnected():
            if time.time() - start_time > timeout_seconds:
                print('Connection timed out!')
                sta_if.active(False) # Optional: Turn off interface to save power on failure
                return False
            
            time.sleep(0.5) # Wait a bit before checking again
            
    # Print network configuration if successful
    if sta_if.isconnected():
        print('Network configuration (IP/Netmask/Gateway/DNS):', sta_if.ifconfig())
        return True
    
    return False