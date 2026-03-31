# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import machine
import cryptolib
import json
import time
from os import stat, remove
from modules.config_manager import config_manager
import uselect

# Constants
AUTH_FILE = 'auth'
BLOCK_SIZE = 16
NULL_BYTE = b'\x00'

def pad_data(data, padding_byte):
    """Pads data to be a multiple of 16 bytes for AES."""
    return data + padding_byte * ((BLOCK_SIZE - len(data) % BLOCK_SIZE) % BLOCK_SIZE)

# Key derivation (Original logic kept for compatibility)
KEY_SOURCE = b'bkjask\xd1jddye\x03987rjh\x08da\xfawdkj3e\x0aencwdj\x23hwqwek\xf1lDDJW\x98QEQ122'
KEY_OFFSET = 7
KEY_LENGTH = 32
derived_key = pad_data(KEY_SOURCE[KEY_OFFSET : KEY_OFFSET + KEY_LENGTH], b'\xaa')
cipher = cryptolib.aes(derived_key, 1) # Mode 1: ECB

def clear_serial_buffer():
    """Flushes sys.stdin buffer using select to avoid blocking or attribute errors."""
    try:
        # Check if there is data waiting in stdin (timeout 0)
        while uselect.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.read(1)
    except:
        pass
    
def get_encrypted_pin_secret():
    """Reads PIN from JSON and returns its AES encrypted version for comparison."""
    try:
        raw_pin = config_manager.static_config.get("pin", 123456)
        
        # Format integer to 6-digit string with leading zeros
        # Ensure existing string format is preserved
        if isinstance(raw_pin, int):
            pin = "{:06d}".format(raw_pin)
        else:
            pin = str(raw_pin)
            
        return cipher.encrypt(pad_data(f">>{pin}<<".encode(), NULL_BYTE))
    except Exception:
        return None
    
ENCRYPTED_SECRET = get_encrypted_pin_secret()

def run_authentication():
    if ENCRYPTED_SECRET is None:
        print("Error: Config PIN not defined.")
        machine.reset()

    # Try to restore existing session
    try:
        stat(AUTH_FILE)
        with open(AUTH_FILE, 'rb') as f:
            stored_token = f.read()
        
        # We compare encrypted bytes directly. 
        # No decryption needed = No "can't encrypt & decrypt" error.
        if stored_token == ENCRYPTED_SECRET:
            print("\r\n[ISURLOG] Session restored. Welcome back.")
            return True
        
        remove(AUTH_FILE)
    except:
        pass

    attempts = 0
    while attempts < 3:
        try:
            # Active wait instead of time.sleep() to avoid C-level interrupt triggers
            start = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), start) < 1000:
                pass 
            
            clear_serial_buffer()
            print("\r\n--- ISURLOG ACCESS CONTROL ---")
            
            # Request PIN
            sys.stdout.write("Enter PIN: ")
            # Reading from stdin directly
            pwd = sys.stdin.readline().strip()
            
            if not pwd: 
                continue 
            
            input_enc = cipher.encrypt(pad_data(f">>{pwd}<<".encode(), NULL_BYTE))
            
            if input_enc == ENCRYPTED_SECRET:
                with open(AUTH_FILE, 'wb') as f:
                    f.write(ENCRYPTED_SECRET)
                print('REPL login authorized.')
                return 
            else:
                attempts += 1
                print('Wrong PIN. Attempt %d/3' % attempts)

        except KeyboardInterrupt:
            # Catch and ignore Ctrl+C during the login process
            print("\n[!] Keyboard interrupt blocked. Please enter the PIN.")
            continue 
        except Exception as e:
            # Safety reset on unexpected errors
            print(e)
            machine.reset()
            
    # Final lockdown if all attempts fail
    print("Too many attempts. System lockdown.")
    time.sleep(1)
    machine.reset()

# Start the process
run_authentication()