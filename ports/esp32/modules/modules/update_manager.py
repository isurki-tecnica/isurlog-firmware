# src/modules/update_manager.py

import uos
import uhashlib
import ubinascii
import time
from machine import reset
from modules import utils

def verify_file_checksum(expected_hash, filename = "update_candidate.py"):
    """
    Calculates the SHA-256 hash of a local file and compares it with an expected hash.

    Args:
        filename (str): The path to the downloaded file (e.g., 'update_candidate.py').
        expected_hash (str): The expected SHA-256 hash string.

    Returns:
        bool: True if the hashes match, False otherwise.
    """
    utils.log_info(f"Verifying checksum for file '{filename}'...")
    
    sha256 = uhashlib.sha256()
    try:
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(1024) # Read in 1KB chunks
                if not chunk:
                    break
                sha256.update(chunk)

        calculated_hash_bytes = sha256.digest()
        calculated_hash_hex = ubinascii.hexlify(calculated_hash_bytes).decode()

        print(f"  - Expected Hash: {expected_hash}")
        print(f"  - Calculated Hash: {calculated_hash_hex}")

        if calculated_hash_hex.lower() == expected_hash.lower():
            utils.log_info("SUCCESS: Hash matches. File is intact.")
            return True
        else:
            utils.log_error("ERROR: Hash MISMATCH. File is corrupt or incorrect.")
            return False

    except OSError as e:
        utils.log_error(f"File not found or error reading file for checksum: {e}")
        return False
    except Exception as e:
        utils.log_error(f"An error occurred during checksum verification: {e}")
        return False

def perform_update(candidate_file='update_candidate.py', target_file='main.py'):
    """
    Performs the update by replacing the target file with the candidate file.
    Includes a backup and reboots the device upon completion.

    Args:
        candidate_file (str): The name of the new verified file.
        target_file (str): The name of the file that will be replaced (main.py).
    
    Returns:
        Does not return, as it reboots the device on success.
        Raises an exception on failure.
    """
    utils.log_info(f"Checksum verified. Proceeding to replace '{target_file}' with '{candidate_file}'.")
    backup_file = target_file + '.bak'

    try:
        # Step 1: Check if the candidate file exists
        uos.stat(candidate_file)
    except OSError:
        utils.log_error(f"Update failed: Candidate file '{candidate_file}' not found.")
        return False

    try:
        # Step 2: Create a backup of the current file (if it exists)
        try:
            uos.rename(target_file, backup_file)
            utils.log_info(f"Backup of '{target_file}' created as '{backup_file}'.")
        except OSError:
            utils.log_info(f"No previous '{target_file}' found to back up. Proceeding.")

        # Step 3: Rename the new file to be the main one
        uos.rename(candidate_file, target_file)
        utils.log_info(f"SUCCESS: '{candidate_file}' has been renamed to '{target_file}'.")
        
        # Step 4: Delete the backup if everything went well
        try:
            uos.remove(backup_file)
            utils.log_info("Backup file removed.")
        except OSError:
            # It's okay if there was no backup to delete
            pass

    except Exception as e:
        utils.log_error(f"CRITICAL ERROR during file replacement: {e}")
        utils.log_error("Attempting to restore from backup...")
        try:
            # Try to restore the backup in case of failure
            uos.rename(backup_file, target_file)
            utils.log_info("Backup restored successfully.")
        except Exception as restore_e:
            utils.log_error(f"Could not restore backup: {restore_e}. System may be unstable.")
        return False