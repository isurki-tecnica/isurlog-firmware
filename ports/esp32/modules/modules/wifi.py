# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import network
import time

# CRA 4.5 Requirement: Minimum security level (WPA2)
# 0: Open, 1: WEP, 2: WPA-PSK, 3: WPA2-PSK, 4: WPA/WPA2-PSK, 5: WPA2/WPA3-PSK, 6: WPA3-PSK
MIN_SAFE_AUTH_MODE = 3

def is_connected():
    """
    Checks if the device is currently connected to a Wi-Fi network.
    
    Returns:
        bool: True if connected, False otherwise.
    """
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.isconnected()

def do_connect(ssid, password, timeout_seconds=15):
    """
    Connects to a Wi-Fi network ensuring CRA 4.5 security compliance.
    Only allows connections to WPA2 or WPA3 networks.
    """
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if not sta_if.isconnected():
        print(f'Scanning for {ssid} to verify security compliance...')
        
        # 1. Scan available networks
        networks = sta_if.scan()
        target_network = None
        
        for n in networks:
            # n[0] is SSID, n[4] is authmode
            if n[0].decode() == ssid:
                target_network = n
                break
        
        # 2. Security Validation (CRA 4.5 Check)
        if target_network:
            auth_mode = target_network[4]
            if auth_mode < MIN_SAFE_AUTH_MODE:
                print(f'SECURITY ALERT: Network {ssid} uses outdated encryption (Mode {auth_mode}).')
                print('Connection rejected to comply with CRA 4.5 (WPA2/WPA3 Mandatory).')
                return False
        else:
            print(f'Network {ssid} not found during scan.')
            return False

        # 3. Proceed with secure connection
        print(f'Security verified. Connecting to {ssid}...')
        sta_if.connect(ssid, password)
        
        start_time = time.time()
        while not sta_if.isconnected():
            if time.time() - start_time > timeout_seconds:
                print('Connection timed out!')
                return False
            time.sleep(0.5)
            
    if sta_if.isconnected():
        print('Secure connection established:', sta_if.ifconfig())
        return True
    
    return False

def do_disconnect():
    """
    Disconnects from the Wi-Fi network and safely turns off the radio.
    """
    sta_if = network.WLAN(network.STA_IF)
    
    if sta_if.active():
        print('Disconnecting from network...')
        
        # 1. Terminate connection with the AP
        if sta_if.isconnected():
            sta_if.disconnect()
            
        # 2. Turn off the radio (This prevents the WDT reset)
        sta_if.active(False)
        
        # 3. Brief wait for the ESP32 driver to finish internal cleanup
        time.sleep(0.2)
        
    print('Wi-Fi deactivated.')
    return True