# src/modules/internal_storage.py
import uos
from modules import utils

class InternalStorage:
    """
    Manages payloads stored in a SINGLE file on the ESP32's internal file system.
    Implements FIFO (First-In, First-Out) deletion of old payloads when
    the available space falls below a specified threshold, OR a maximum
    number of lines is exceeded.
    """

    def __init__(self, filename="payloads.txt", threshold_mb=1, max_lines=None):  # Changed default to 1MB
        """
        Initializes the InternalStorage manager.

        Args:
            filename: The name of the file to store payloads in (default: "payloads.txt").
            threshold_mb:  The free space threshold (in megabytes) below which
                           oldest lines will be deleted (default: 1 MB).
            max_lines:     Maximum number of lines in the file.  If None, no limit.
        """
        self.filename = filename
        self.threshold_bytes = int(threshold_mb * 1024 * 1024)  # Convert MB to bytes
        self.max_lines = max_lines

    def get_free_space(self):
        """Gets the free space on the file system in bytes."""
        try:
            stats = uos.statvfs('/')
            block_size = stats[0]
            free_blocks = stats[3]
            return block_size * free_blocks
        except Exception as e:
            utils.log_error(f"Error getting free space: {e}")
            return 0  # Assume no space on error

    def get_file_line_count(self):
        """Counts lines in the payload file."""
        try:
            with open(self.filename, 'r') as f:
                return sum(1 for _ in f)
        except OSError:
            return 0  # Return 0 if file doesn't exist yet

    def delete_oldest_lines(self, num_lines_to_delete):
        """Deletes the specified number of oldest lines from the file."""
        if num_lines_to_delete <= 0:
            return

        try:
            with open(self.filename, "r") as f:
                lines = f.readlines()

            if len(lines) <= num_lines_to_delete:
                # Delete entire file content
                with open(self.filename, "w") as f:
                    f.write("")  # Overwrite with empty string
                utils.log_info(f"Deleted all lines from {self.filename}.")
            else:
                with open(self.filename, "w") as f:
                    f.writelines(lines[num_lines_to_delete:])  # Write back newer lines
                utils.log_info(f"Deleted {num_lines_to_delete} oldest lines from {self.filename}.")

        except OSError as e:
            utils.log_error(f"Error deleting lines from {self.filename}: {e}")


    def store_payload(self, payload):
        """
        Stores a payload string in the file. Manages free space and max lines.

        Args:
            payload: The payload string to store.

        Returns:
            True on success, False on failure.
        """
        try:
            # 1. Manage space *before* appending.
            self.manage_space()

            # 2. Append the payload.
            with open(self.filename, "a") as f:
                f.write(payload + "\n")  # Append with a newline
            utils.log_info(f"Appended payload to {self.filename}")
            return True

        except OSError as e:
            utils.log_error(f"Error storing payload in {self.filename}: {e}")
            return False

    def manage_space(self):
        """Manages disk space, deleting oldest lines if necessary."""

        while True:
            free_space = self.get_free_space()
            line_count = self.get_file_line_count()

            utils.log_info(f"Free space: {free_space / (1024 * 1024):.2f} MB,  Line count: {line_count}, Max lines: {self.max_lines}, Threshold: {self.threshold_bytes/(1024*1024):.2f} MB")

            if free_space < self.threshold_bytes or (self.max_lines is not None and line_count >= self.max_lines):
                if not self.delete_oldest_lines(1):  # Delete at least one line
                    break  # Exit if can not delete lines.
            else:
                break  # Enough space, exit the loop

    def get_all_payloads(self):
        """
        Retrieves all payloads from the file.

        Returns:
            A list of payload strings, or an empty list if the file is empty
            or an error occurs.  Payloads are returned in order from oldest to newest.
        """
        payloads = []
        try:
            with open(self.filename, "r") as f:
                for line in f:  # Iterate directly over the file object
                    payloads.append(line.strip())  # Remove leading/trailing whitespace
            return payloads
        except OSError as e:
            if e.args[0] == 2:  # errno.ENOENT (file not found)
                utils.log_info(f"File {self.filename} not found (empty).")
                return []  # Return empty list if file doesn't exist yet
            else:
                utils.log_error(f"Error reading payloads from {self.filename}: {e}")
                return []  # Return empty list on other errors

    def clear_storage(self):
        """Clears all payloads from the storage file."""
        try:
            with open(self.filename, "w") as f:
                f.write("")  # Overwrite with an empty string
            utils.log_info(f"Cleared storage file: {self.filename}")
        except OSError as e:
            utils.log_error(f"Error clearing storage file {self.filename}: {e}")