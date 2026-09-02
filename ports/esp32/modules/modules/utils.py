# src/modules/utils.py

# Copyright (C) 2026 ISURKI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import time
import json

# LOG_LEVEL used to be resolved by having utils.py load its own separate
# copy of static_config.json (and an unused copy of dynamic_config.json)
# at import time - duplicating the load that config_manager.py already
# does, which is the single source of truth for config. Instead, we
# resolve it lazily from config_manager on first use.
#
# The import is deferred (inside the function, not at module level)
# because config_manager.py itself does `from modules import utils` at
# import time - importing config_manager back at utils' module level
# would be a circular import. By the time a log call actually happens,
# config_manager has always finished initializing.
_LOG_LEVEL = None  # Opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL

def _get_log_level():
    global _LOG_LEVEL
    if _LOG_LEVEL is None:
        try:
            from modules.config_manager import config_manager
            _LOG_LEVEL = config_manager.get_static("log_level", default="INFO")
        except Exception:
            # config_manager isn't ready yet (e.g. this is being called
            # from within config_manager's own init). Don't cache the
            # fallback - retry properly on the next log call.
            return "INFO"
    return _LOG_LEVEL


def log_message(level, message):
    """
    Logs a message with a specified level.

    Args:
        level: The log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
        message: The message to log.
    """
    timestamp = time.time()
    log_level = _get_log_level()

    if level == "DEBUG" and log_level == "DEBUG":
        print(f"[{timestamp}] DEBUG: {message}")
    elif level == "INFO" and (log_level == "DEBUG" or log_level == "INFO"):
        print(f"[{timestamp}] INFO: {message}")
    elif level == "WARNING" and (log_level == "DEBUG" or log_level == "INFO" or log_level == "WARNING"):
        print(f"[{timestamp}] WARNING: {message}")
    elif level == "ERROR" and (log_level == "DEBUG" or log_level == "INFO" or log_level == "WARNING" or log_level == "ERROR"):
        print(f"[{timestamp}] ERROR: {message}")
    elif level == "CRITICAL":
        print(f"[{timestamp}] CRITICAL: {message}")


def log_error(message):
    """
    Logs an error message.

    Args:
        message: The error message to log.
    """
    log_message("ERROR", message)

def log_info(message):
    """
    Logs an info message.

    Args:
        message: The info message to log.
    """
    log_message("INFO", message)

def log_debug(message):
    """
    Logs a debug message.

    Args:
        message: The debug message to log.
    """
    log_message("DEBUG", message)
    
def log_warning(message):
    """
    Logs a warning message.

    Args:
        message: The warning message to log.
    """
    log_message("WARNING", message)

def get_datetime_string():
    """
    Returns the current date and time as a formatted string.

    Returns:
        A string representing the current date and time.
    """
    current_time = time.localtime()
    year, month, day, hour, minute, second = current_time[:6]
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

def save_data_to_file(filepath, data):
    """
    Saves data to a file.

    Args:
        filepath: The path to the file.
        data: The data to save (must be json compatible).
    """
    try:
        with open(filepath, "a") as f:
            f.write(json.dumps(data) + "\n") # Write each set of data on a new line
        log_info(f"Data saved to {filepath}")
    except Exception as e:
        log_error(f"Error saving data to file: {e}")