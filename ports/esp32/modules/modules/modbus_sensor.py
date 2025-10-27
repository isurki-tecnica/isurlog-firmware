# src/modules/modbus_sensor.py
from machine import UART, Pin
from modules import utils
import time
from lib.umodbus.serial import Serial as ModbusRTUMaster
import json
from modules.config_manager import config_manager
import struct

class ModbusSensor:
    def __init__(self, uart_id = 2, tx_pin = None, rx_pin = None, en_pin= None, baudrate=9600, data_bits=8, parity=None, stop_bits=1):
        """
        Initializes the Modbus sensor module.

        Args:
            uart_id: The UART interface ID (e.g., 1 or 2).
            tx_pin: The UART TX pin number.
            rx_pin: The UART RX pin number.
            en_pin: The RS485 enable pin number.
            baudrate: The baud rate of the UART communication (default: 9600).
            data_bits: The number of data bits (default: 8).
            parity: The parity (None, machine.UART.EVEN, or machine.UART.ODD) (default: None).
            stop_bits: The number of stop bits (default: 1).
        """

        self.tx_pin = tx_pin if tx_pin is not None else config_manager.static_config.get("pinout", {}).get("rs485", {}).get("di_pin", 23)
        self.rx_pin = rx_pin if rx_pin is not None else config_manager.static_config.get("pinout", {}).get("rs485", {}).get("ro_pin", 14)
        self.en_pin = en_pin if en_pin is not None else config_manager.static_config.get("pinout", {}).get("rs485", {}).get("re_pin", 33)

        utils.log_warning(f"Pin configuration: en_pin: {self.en_pin} rx_pin: {self.rx_pin} tx_pin: {self.tx_pin}")

        self.master = ModbusRTUMaster(
            pins=(self.tx_pin, self.rx_pin),      # given as tuple (TX, RX), check MicroPython port specific syntax
            baudrate=baudrate,    # optional, default 9600
            data_bits=data_bits,      # optional, default 8
            stop_bits=stop_bits,      # optional, default 1
            parity=parity,      # optional, default None
            ctrl_pin=self.en_pin,      # optional, control DE/RE
            uart_id=uart_id         # optional, see port specific documentation
        )

    def read_holding_registers(self, slave_addr, starting_addr, quantity):
        """
        Reads Modbus holding registers from a slave device.

        Args:
            slave_addr: The address of the Modbus slave device.
            starting_addr: The starting address of the registers to read.
            quantity: The number of registers to read.

        Returns:
            A list of register values, or None if an error occurred.

        Example:
            modbus_module = modbus_sensor.ModbusSensor()

            slave_address = 1  # Replace with your slave device address
            starting_register = 1  # Replace with the starting register address
            num_registers = 1  # Replace with the number of registers to read

            modbus_data = modbus_module.read_holding_registers(slave_address, starting_register, num_registers)

            if modbus_data:
                utils.log_info(f"Modbus data: {modbus_data}")
            else:
                utils.log_error("Failed to read Modbus data.")

        """
        try:
            response = self.master.read_holding_registers(slave_addr, starting_addr, quantity, signed = False)
            utils.log_info(f"Modbus response: {response}")
            return response
        except Exception as e:
            utils.log_error(f"Error reading Modbus input registers: {e}")
            return None

    def read_input_registers(self, slave_addr, starting_addr, quantity):
        """
        Reads Modbus input registers from a slave device.

        Args:
            slave_addr: The address of the Modbus slave device.
            starting_addr: The starting address of the registers to read.
            quantity: The number of registers to read.

        Returns:
            A list of register values, or None if an error occurred.
        """
        try:
            response = self.master.read_input_registers(slave_addr, starting_addr, quantity)
            utils.log_info(f"Modbus response: {response}")
            return response
        except Exception as e:
            utils.log_error(f"Error reading Modbus input registers: {e}")
            return None

    def write_register(self, slave_addr, register_addr, value):
        """
        Writes a single Modbus register on a slave device.

        Args:
            slave_addr: The address of the Modbus slave device.
            register_addr: The address of the register to write.
            value: The value to write.

        Returns:
            True if successful, False otherwise.
        """

        try:
            self.master.write_single_register(slave_addr, register_addr, value)
            utils.log_info(f"Successfully wrote {value} to register {register_addr} on slave {slave_addr}")
            return True
        except Exception as e:
            utils.log_error(f"Error writing to Modbus register: {e}")
            return False
        
    def _bool_list_to_int(self, bool_list):
        """Converts a list of booleans to an integer (bit representation)."""
        int_value = 0
        for bit in bool_list:
            int_value = (int_value << 1) | bit
        return int_value-1

    def read_coils(self, slave_addr, starting_addr, quantity):
        """
        Reads Modbus coils from a slave device.

        Returns:
            A binary string representing the coil values, or None if an error occurred.
        """
        try:
            response = self.master.read_coils(slave_addr, starting_addr, quantity)
            utils.log_info(f"Modbus coils response: {response}")
            if response:
                return self._bool_list_to_int(response) # Convert to binary string
            else:
                return None
        except Exception as e:
            utils.log_error(f"Error reading Modbus coils: {e}")
            return None

    def read_discrete_inputs(self, slave_addr, starting_addr, quantity):
        """
        Reads Modbus discrete inputs from a slave device.

        Returns:
            A binary string representing the input values, or None if an error occurred.
        """
        try:
            response = self.master.read_discrete_inputs(slave_addr, starting_addr, quantity)
            utils.log_info(f"Modbus discrete inputs response: {response}")
            if response:
                return self._bool_list_to_int(response) # Convert to binary string
            else:
                return None

        except Exception as e:
            utils.log_error(f"Error reading Modbus discrete inputs: {e}")
            return None
        
    def _registers_to_float(self, registers, byte_order="big"):
        """
        Converts two Modbus registers (16-bit) to a 32-bit float (IEEE 754).

        Args:
            registers: A list or tuple containing two 16-bit register values.
            byte_order:  'big' (default) or 'little' endian.

        Returns:
            The converted float value.
        Raises:
            ValueError: if registers list does not contains two values
        """
        if len(registers) != 2:
            raise ValueError("Exactly two registers are required to convert to a float.")

        # Determine the byte order for packing
        if byte_order == "big":
            # Big-endian:  Most Significant Byte (MSB) first
            byte_string = registers[0].to_bytes(2, 'big') + registers[1].to_bytes(2, 'big')
        elif byte_order == "little":
            # Little-endian: Least Significant Byte (LSB) first
             byte_string = registers[1].to_bytes(2, 'little') + registers[0].to_bytes(2, 'little')
        else:
             raise ValueError("byte_order must be 'big' or 'little'")

        # Unpack the bytes as a float
        return struct.unpack('f', byte_string)[0]


    def read_modbus_data(self, slave_addr, function_code, starting_addr, is_fp=False, byte_order="little"):
        """
        Reads Modbus data from a slave device based on the function code.

        Args:
            slave_addr: The address of the Modbus slave device.
            function_code: The Modbus function code (1, 2, 3, or 4).
            starting_addr: The starting address of the registers/coils/inputs to read.
            quantity: The number of registers/coils/inputs to read.
            is_fp: True if the data should be interpreted as a 32-bit float, False otherwise.
            byte_order: 'big' (default) or 'little' endian.  Only used if is_fp is True.

        Returns:
            A list of values (integers or booleans), a single float (if is_fp is True),
            or None if an error occurred.
        """
        try:
            if function_code == 1:
                return self.read_coils(slave_addr, starting_addr, 16)
            elif function_code == 2:
                return self.read_discrete_inputs(slave_addr, starting_addr, 16)
            elif function_code == 3:
                if is_fp:
                    # Read two registers for a float
                    registers = self.read_holding_registers(slave_addr, starting_addr, 2)
                    if registers:
                         return self._registers_to_float(registers, byte_order)
                    else:
                        return None
                else:
                    return self.read_holding_registers(slave_addr, starting_addr, 1)

            elif function_code == 4:
                if is_fp:
                    registers = self.read_input_registers(slave_addr, starting_addr, 2)
                    if registers:
                        return self._registers_to_float(registers, byte_order)
                    else:
                        return None
                else:
                    return self.read_input_registers(slave_addr, starting_addr, 1)
            else:
                utils.log_error(f"Invalid Modbus function code: {function_code}")
                return None
        except Exception as e:
            utils.log_error(f"Error reading Modbus data (function code {function_code}): {e}")
            return None

