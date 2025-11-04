# src/modules/update_manager.py

import uos
import uhashlib
import ubinascii
import time
from machine import reset
from modules import utils
import os

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
    
def decode_base64_file(input_b64_filepath, output_bin_filepath, buffer_size=1024):
    """
    Decodes a Base64 text file (.txt/.b64) into a binary file (.bin)
    in MicroPython, processing it in chunks to save RAM.

    Args:
        input_b64_filepath (str): Path to the downloaded Base64 file.
        output_bin_filepath (str): Path where the resulting binary file will be saved.
        buffer_size (int): Size of the read/write buffer in bytes (adjust according to RAM).

    Returns:
        bool: True if decoding was successful, False otherwise.
    """
    utils.log_info(f"Starting Base64 decoding from '{input_b64_filepath}' to '{output_bin_filepath}'...")
    start_time = time.ticks_ms()

    try:
        # Delete output file if it already exists
        try:
            os.remove(output_bin_filepath)
            utils.log_info(f"Previous binary file '{output_bin_filepath}' deleted.")
        except OSError:
            pass # It didn't exist, perfect

        total_bytes_written = 0
        # Open both files
        with open(input_b64_filepath, "rb") as fin, open(output_bin_filepath, "wb") as fout:
            base64_chunk = bytearray(buffer_size * 4 // 3) # Buffer to read Base64 (approx size)
            leftover = b'' # To store fragments at the end of a chunk

            while True:
                # Read a chunk from the Base64 file
                # Using readinto for efficiency
                bytes_read = fin.readinto(base64_chunk)

                if bytes_read == 0:
                    # End of the input file
                    # Process any remaining data that didn't form a complete 4-byte block
                    if leftover:
                        try:
                            binary_data = ubinascii.a2b_base64(leftover)
                            fout.write(binary_data)
                            total_bytes_written += len(binary_data)
                            utils.log_debug(f"Decoded {len(binary_data)} final leftover bytes.")
                        except ubinascii.Error as e:
                            utils.log_error(f"Error decoding final Base64 leftover: {e!r}. Leftover: {leftover!r}")
                            raise # Re-raise to abort
                    break # Exit the while loop

                # Combine previous leftover with new data
                current_data = leftover + memoryview(base64_chunk)[:bytes_read]

                # Clean up line breaks and spaces (important!)
                current_data = current_data.replace(b'\r', b'').replace(b'\n', b'').replace(b' ', b'')

                # Ensure we only process multiples of 4 Base64 bytes
                # (except possibly at the very end)
                decode_len = (len(current_data) // 4) * 4
                if decode_len == 0 and bytes_read > 0:
                     # Not enough for a full block, save as leftover
                     leftover = bytes(current_data) # Convert memoryview to bytes
                     continue

                chunk_to_decode = current_data[:decode_len]
                leftover = bytes(current_data[decode_len:]) # Save the rest for the next iteration

                if not chunk_to_decode:
                    # If after cleaning only leftovers remain, continue
                    continue

                # Decode the Base64 chunk
                try:
                    binary_chunk = ubinascii.a2b_base64(chunk_to_decode)
                except Exception as e:
                    utils.log_error(f"Error decoding Base64: {e!r}")
                    utils.log_debug(f"Problematic chunk (start): {chunk_to_decode[:80]!r}")
                    # Could try decoding by removing the last character? Risky
                    raise # Re-raise to abort

                # Write the binary chunk
                fout.write(binary_chunk)
                total_bytes_written += len(binary_chunk)
                # Log progress periodically to avoid flooding
                if total_bytes_written % (buffer_size * 10) < buffer_size: # Approx every 10 buffers  # Corrected condition logic slightly
                    utils.log_debug(f"Decoded and written {total_bytes_written} bytes...")

        # Decoding completed
        end_time = time.ticks_ms()
        duration = time.ticks_diff(end_time, start_time) / 1000
        utils.log_info(f"Base64 decoding completed in {duration:.2f} seconds.")
        utils.log_info(f"Binary file saved to '{output_bin_filepath}' ({total_bytes_written} bytes).")

        return True

    except Exception as e:
        utils.log_error(f"FATAL error during Base64 decoding: {e!r}")
        # Ensure incomplete binary file is deleted on failure
        try:
            os.remove(output_bin_filepath)
            utils.log_warning(f"Incomplete binary file '{output_bin_filepath}' deleted.")
        except OSError:
            pass # File might not have been created or already deleted
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