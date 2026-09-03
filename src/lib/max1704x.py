"""
{Andre Peeters 2017/10/31}<https://github.com/andrethemac/max17043.py/tree/master>

Description: This is a Micropython library for the MAX17043/17044 LiPo fuel gauge.  
Creation date: 2017/10/31
Modification date:
Version: 1.0
Dependencies: binascii, machine
modified by: @Cesar
"""
from machine import Pin, I2C
import binascii
from modules import utils

class max1704x:
    REGISTER_VCELL = const(0X02)
    REGISTER_SOC = const(0X04)
    REGISTER_MODE = const(0X06)
    REGISTER_VERSION = const(0X08)
    REGISTER_CONFIG = const(0X0C)
    REGISTER_COMMAND = const(0XFE)
    REGISTER_CRATE = const(0x16)
    REGISTER_TTE = const(0x11)
    REGISTER_HIBRT = const(0x0A)

    def __init__(self, _id=0, sda_pin=21, scl_pin=22, freq=100000):
        """
        Initializes the I2C connection and checks for sensor presence.
        """
        self._id = _id
        self.freq = freq
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.i2c = I2C(0, sda=Pin(self.sda_pin), scl=Pin(self.scl_pin), freq=self.freq)
        self.max1704xAddress = 0x36  # Expected address for MAX1704X

        if not self.sensor_exists():
            utils.log_warning("MAX1704X sensor not found on I2C bus.")

    def __str__(self):
        """
        String representation of the values.
        """
        rs  = "The I2C address is {}\n".format(self.max1704xAddress)
        rs += "The I2C pins are SDA: {} and SCL: {}\n".format(self.sda_pin, self.scl_pin)
        rs += "The version is {}\n".format(self.getVersion())
        rs += "VCell is {} V\n".format(self.getVCell())
        rs += "Compensate value is {}\n".format(self.getCompensateValue())
        rs += "The alert threshold is {} %\n".format(self.getAlertThreshold())
        rs += "Is it in alert? {}\n".format(self.inAlert())
        return rs
    
    def sensor_exists(self):
        """
        Quickly checks if the sensor responds at the expected I2C address.
        Returns True if found, False otherwise.
        """
        try:
            # Attempt to read a known register to confirm the sensor is connected
            self.i2c.readfrom_mem(self.max1704xAddress, self.REGISTER_VERSION, 1)
            return True
        except OSError:
            # If there's an I2C error, assume the device is not connected
            return False
    def address(self):
        """
        Returns the I2C address.
        """
        return self.max1704xAddress

    def reset(self):
        """
        Resets the sensor.
        """
        self.__writeRegister(REGISTER_COMMAND, binascii.unhexlify('0054'))

    def getVCell(self):
        """
        Gets the actual real-time voltage of the battery cell.
        """
        buf = self.__readRegister(self.REGISTER_VCELL)
        # Combine the two bytes into a single 16-bit integer
        value = (buf[0] << 8) | buf[1]
        
        # The MAX17048 has a resolution of 78.125 microvolts per LSB
        # 78.125 µV is equal to 0.000078125 mVolts
        return value * 0.078125
    
    def getTTE(self):
        """
        Calculates the estimated time until the battery is empty.
        Returns the time in hours.
        """
        buf = self.__readRegister(self.REGISTER_TTE)
        # Combine bytes (Big Endian)
        value = (buf[0] << 8) | buf[1]
        
        # 1 LSB = 5.625 seconds
        total_seconds = value * 5.625
        
        # Return hours (seconds / 3600)
        return total_seconds / 3600.0

    def getSoc(self):
        """
        Gets the state of charge.
        """
        buf = self.__readRegister(REGISTER_SOC)
        return (buf[0] + (buf[1] / 256.0))
    
    def getCrate(self):
        """
        Gets the charge/discharge rate in %/h.
        Positive = Charging, Negative = Discharging.
        """
        buf = self.__readRegister(self.REGISTER_CRATE)
        # Combine bytes (Big Endian)
        value = (buf[0] << 8) | buf[1]
        
        # Convert to signed integer (16-bit two's complement)
        if value & 0x8000:
            value -= 1 << 16
            
        # 1 LSB = 0.208% / hour
        return value * 0.208
    
    def get_hibernation_config(self):
        """
        Reads hibernation thresholds from the HIBRT register (0x0A).
        Returns:
            tuple: (act_thr, hib_thr)
        """
        buf = self.__readRegister(self.REGISTER_HIBRT)
        # act_thr: Wakeup threshold (Active mode). 1 LSb = 1.25mV
        act_thr = buf[0] 
        # hib_thr: Sleep threshold (Hibernate mode). 1 LSb = 0.208%/hr
        hib_thr = buf[1] 
        return act_thr, hib_thr

    def set_hibernation_config(self, act_thr, hib_thr):
        """
        Sets hibernation thresholds in the HIBRT register (0x0A).
        
        Args:
            act_thr: Exit hibernate if |OCV-VCELL| > ActThr.
            hib_thr: Enter hibernate if |CRATE| < HibThr for > 6min.
                     A value of 0x00 in HibThr disables hibernate mode.
        """
        buf = bytearray([act_thr, hib_thr])
        self.__writeRegister(self.REGISTER_HIBRT, buf)

    def getVersion(self):
        """
        Gets the version of the max17043 module.
        """
        buf = self.__readRegister(REGISTER_VERSION)
        return (buf[0] << 8) | (buf[1])

    def getCompensateValue(self):
        """
        Gets the compensation value.
        """
        return self.__readConfigRegister()[0]

    def getAlertThreshold(self):
        """
        Gets the alert level.
        """
        return (32 - (self.__readConfigRegister()[1] & 0x1f))

    def setAlertThreshold(self, threshold):
        """
        Sets the alert level.
        """
        self.threshold = 32 - threshold if threshold < 32 else 32
        buf = self.__readConfigRegister()
        buf[1] = (buf[1] & 0xE0) | self.threshold
        self.__writeConfigRegister(buf)

    def inAlert(self):
        """
        Checks if the max17043 module is in alert.
        """
        return (self.__readConfigRegister())[1] & 0x20

    def clearAlert(self):
        """
        Clears the alert.
        """
        self.__readConfigRegister()

    def quickStart(self):
        """
        Performs a quick reset.
        """
        self.__writeRegister(REGISTER_MODE, binascii.unhexlify('4000'))
        
    def getRComp(self):
        """
        Reads the 8-bit RCOMP value from the CONFIG register.
        """
        # Read the 2-byte CONFIG register
        buf = self.__readRegister(REGISTER_CONFIG)
        # RCOMP is the MSB (Most Significant Byte)
        return buf[0]

    def setRComp(self, rcomp):
        """
        Updates the 8-bit RCOMP value in the CONFIG register.
        Preserves the LSB settings (Alert Threshold, Sleep bit, etc.).
        """
        if not 0 <= rcomp <= 255:
            raise ValueError("RCOMP must be an 8-bit value (0-255)")
            
        # Read current CONFIG to preserve LSB settings
        current_config = self.__readRegister(REGISTER_CONFIG)
        
        # Create new buffer: [New RCOMP (MSB), Original LSB]
        new_config = bytes([rcomp, current_config[1]])
        
        self.__writeRegister(REGISTER_CONFIG, new_config)

    def __readRegister(self, address):
        """
        Reads the register at the specified address, always returns a 2-byte bytearray.
        """
        return self.i2c.readfrom_mem(self.max1704xAddress, address, 2)

    def __readConfigRegister(self):
        """
        Reads the configuration register, always returns a 2-byte bytearray.
        """
        return self.__readRegister(REGISTER_CONFIG)

    def __writeRegister(self, address, buf):
        """
        Writes the buf to the register address.
        """
        self.i2c.writeto_mem(self.max1704xAddress, address, buf)

    def __writeConfigRegister(self, buf):
        """
        Writes the buf to the configuration register.
        """
        self.__writeRegister(REGISTER_CONFIG, buf)

    def deinit(self):
        """
        Turns off the peripheral.
        """
        self.i2c.deinit()


