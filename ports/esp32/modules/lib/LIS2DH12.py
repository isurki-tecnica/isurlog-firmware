# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
@Author: Stephen.Gao
@Date: 2023-03-22
@Description: LIS2DH12 sensor driver

Copyright 2022 - 2023 quectel
'''

import utime

LIS2DH12_OUT_X_L = 0x28
LIS2DH12_OUT_X_H = 0x29
LIS2DH12_OUT_Y_L = 0x2A
LIS2DH12_OUT_Y_H = 0x2B
LIS2DH12_OUT_Z_L = 0x2C
LIS2DH12_OUT_Z_H = 0x2D
LIS2DH12_FIFO_CTRL_REG = 0x2E

# control register
LIS2DH12_CTRL_REG1 = 0x20
LIS2DH12_CTRL_REG2 = 0x21
LIS2DH12_CTRL_REG3 = 0x22
LIS2DH12_CTRL_REG4 = 0x23
LIS2DH12_CTRL_REG5 = 0x24
LIS2DH12_CTRL_REG6 = 0x25
LIS2DH12_REFERENCE_REG = 0x26
LIS2DH12_STATUS_REG = 0x27

# status register
LIS2DH12_STATUS_REG_AUX = 0x7

# interrupt register
LIS2DH12_INT1_CFG = 0x30
LIS2DH12_INT1_SRC = 0x31
LIS2DH12_INT1_THS = 0x32
LIS2DH12_INT1_DURATION = 0x33

LIS2DH12_INT2_CFG = 0x34
LIS2DH12_INT2_SRC = 0x35
LIS2DH12_INT2_THS = 0x36
LIS2DH12_INT2_DURATION = 0x37

LIS2DH12_WHO_AM_I = 0x0F

LIS2DH12_CLICK_CFG = 0x38
LIS2DH12_CLICK_SRC = 0x39
LIS2DH12_CLICK_THS = 0x3A
LIS2DH12_TIME_LIMIT = 0x3B
LIS2DH12_TIME_LATENCY = 0x3C
LIS2DH12_TIME_WINDOW = 0x3D

STANDARD_GRAVITY = 9.806

# types of interrupt
# single click
X_SINGLE_CLICK_INT = 0x01
Y_SINGLE_CLICK_INT = 0x04
Z_SINGLE_CLICK_INT = 0x10
XYZ_SINGLE_CLICK_INT = 0x15
# double click
X_DOUBLE_CLICK_INT = 0x02
Y_DOUBLE_CLICK_INT = 0x08
Z_DOUBLE_CLICK_INT = 0x20
XYZ_DOUBLE_CLICK_INT = 0x2A
# move int
POSI_CHANGE_RECOGNIZE = 0xFF
X_POSI_CHANGE_RECOGNIZE = 0x83
Y_POSI_CHANGE_RECOGNIZE = 0x8C
Z_POSI_CHANGE_RECOGNIZE = 0xB0
MOVE_RECOGNIZE = 0x7F
X_MOVE_RECOGNIZE = 0x03
Y_MOVE_RECOGNIZE = 0x0C
Z_MOVE_RECOGNIZE = 0x30
# free fall int
FF_RECOGNIZE = 0x95  #and zl yl xl


class lis2dh12(object):
    '''
    lis2dh12 class
    API：sensor_reset(),process_xyz(),int_processing_data(),resolution,
    int_enable(int_type,int_ths,time_limit,time_latency,duration),read_acceleration
    '''
    def __init__(self, i2c_dev, int_pin, slave_address=0x19):
        '''
        :param i2c_dev: i2c object
        :param int_pin: gpio of pin which is connected with int1_pin
        :param slave_address: device address
        '''
        self._address = slave_address
        self._i2c_dev = i2c_dev
        self._int_pin = int_pin
        self._extint = None
        self._sensor_init()

    def _read_data(self, regaddr, datalen):
        # Modified for ESP32: readfrom_mem(address, register, nbytes)
        return list(self._i2c_dev.readfrom_mem(self._address, regaddr, datalen))

    def _write_data(self, regaddr, data):
        # Modified for ESP32: writeto_mem(address, register, buffer)
        self._i2c_dev.writeto_mem(self._address, regaddr, bytes([data]))

    def sensor_reset(self):
        '''
        reset the sensor
        '''
        # 重置chip
        self._write_data(LIS2DH12_CTRL_REG5, 0x80)

        print('reboot already. {}'.format(self._read_data(LIS2DH12_CTRL_REG5,1)))
        utime.sleep_ms(100)
        r_data = self._read_data(LIS2DH12_WHO_AM_I, 1)
        while r_data[0] != 0x33:
            r_data = self._read_data(LIS2DH12_WHO_AM_I, 1)
            utime.sleep_ms(5)

    def _sensor_init(self):
        '''
        initialize the sensor
        '''
        #self.sensor_reset()

        self._write_data(LIS2DH12_CTRL_REG1, 0x77)  # set ODR 400HZ ,enable XYZ.
        utime.sleep_ms(20)  # (7/ODR) = 18ms
        self._write_data(LIS2DH12_CTRL_REG4, 0x08)  # ±2g

        self._write_data(LIS2DH12_CLICK_CFG, 0)  # clear click_cfg
        self._write_data(LIS2DH12_INT1_CFG, 0)  # clear int1_cfg
        self._write_data(LIS2DH12_INT2_CFG, 0)  # clear int2_cfg
        
    def configure_interrupts(self, move=False, click=False, move_ths=0x14, click_ths=0x35):
        '''
        Modular interrupt configuration for security monitoring.
        Movement (IA1) routed to INT1 (GP6).
        Click (Impact) routed to INT2 (GP7).
        '''
        # 1. Reset routing and logic configuration registers
        self._write_data(LIS2DH12_CTRL_REG3, 0x00)
        self._write_data(LIS2DH12_CTRL_REG6, 0x00)
        self._write_data(LIS2DH12_INT1_CFG, 0x00)
        self._write_data(LIS2DH12_CLICK_CFG, 0x00)

        # 2. Configure SHAKE/THEFT detection on INT1 (GP6)
        if move:
            # Enable High-pass filter for IA1 to ignore static gravity
            self._write_data(LIS2DH12_CTRL_REG2, 0x01) 
            # Route IA1 interrupt to physical INT1 pin
            self._write_data(LIS2DH12_CTRL_REG3, 0x40) 
            # Enable OR logic for X, Y, Z high events (Wake-up mode)
            self._write_data(LIS2DH12_INT1_CFG, 0x2A)  
            # Set movement threshold
            self._write_data(LIS2DH12_INT1_THS, move_ths)
            # Require 2 samples above threshold to trigger (20ms @ 100Hz)
            # This filters out single-peak mechanical noise
            self._write_data(LIS2DH12_INT1_DURATION, 0x02) 

        # 3. Configure IMPACT/VANDALISM detection on INT2 (GP7)
        if click:
            # Route Click engine to physical INT2 pin
            self._write_data(LIS2DH12_CTRL_REG6, 0x80) 
            # Enable single-click detection on all axes
            self._write_data(LIS2DH12_CLICK_CFG, 0x15) 
            # Set impact force threshold
            self._write_data(LIS2DH12_CLICK_THS, click_ths)
            # Set max pulse duration to be considered a click (50ms @ 100Hz)
            self._write_data(LIS2DH12_TIME_LIMIT, 0x05)

        # 4. Global latch configuration (LIR1 and LIR2)
        # Keeps the interrupt active until the SRC registers are read
        # Vital for MCP23008 and ESP32 Deep Sleep startup time
        self._write_data(LIS2DH12_CTRL_REG5, 0x0A)

    def start_sensor(self):
        '''
        start the sensor
        '''
        self._write_data(LIS2DH12_CTRL_REG1, 0x77)  # ODR 100HZ ,enable XYZ.
        utime.sleep_ms(20)  # (7/ODR) = 18ms

    def process_xyz(self):
        # Read 6 bytes in a single burst (0x28 corresponds to OUT_X_L)
        # The 0x80 bit (MSB) is typically used to enable I2C address auto-increment on this sensor
        data = self._i2c_dev.readfrom_mem(self._address, LIS2DH12_OUT_X_L | 0x80, 6)
        
        # MicroPython handles byte-to-integer conversion efficiently
        import struct
        # 'h' represents a signed short (16 bits) in little-endian format '<'
        # Note: LIS2DH12 data alignment varies (left/right justified) based on the operating mode
        # We will use your original logic for reconstruction, but in a cleaner implementation:
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        return (x, y, z)

    def int_processing_data(self):
        '''
        handle int_processing
        :return: x,y,z-axis acceleration
        '''
        acc = self.read_acceleration
        int_src = self._read_data(LIS2DH12_INT1_SRC,1)  # read INT1_SRC，clear interrupt request
        return acc

    @property
    def _resolution(self):
        """
        resolution range.
        :return: range_2_G, range_4_G, range_8_G,, range_16_G.
        """
        ctl4 = self._read_data(LIS2DH12_CTRL_REG4,1)[0]
        return (ctl4 >> 4) & 0x03

    @property
    def _acceleration(self):
        """
        x,y,z-axis acceleration
        :return: x,y,z-axis acceleration
        """
        divider = 1
        accel_range = self._resolution
        if accel_range == 3:        # range_16_G
            divider = 2048
        elif accel_range == 2:      # range_8_G
            divider = 4096
        elif accel_range == 1:      # range_4_G
            divider = 8192
        elif accel_range == 0:      # range_2_G
            divider = 16384

        x, y, z = self.process_xyz()

        x = x / divider
        y = y / divider
        z = z / divider

        if accel_range == 3:        # range_16_G
            x = x if x <= 16 else x - 32
            y = y if y <= 16 else y - 32
            z = z if z <= 16 else z - 32
        elif accel_range == 2:      # range_8_G
            x = x if x <= 8 else x - 16
            y = y if y <= 8 else y - 16
            z = z if z <= 8 else z - 16
        elif accel_range == 1:      # range_4_G
            x = x if x <= 4 else x - 8
            y = y if y <= 4 else y - 8
            z = z if z <= 4 else z - 8
        elif accel_range == 0:      # range_2_G
            x = x if x <= 2 else x - 4
            y = y if y <= 2 else y - 4
            z = z if z <= 2 else z - 4

        return (x, y, z)

    @property
    def read_acceleration(self):
        '''
        read acceleration
        :return: x,y,z-axis acceleration
        '''

        while 1:
            status = self._read_data(LIS2DH12_STATUS_REG,1)[0]
            xyzda = status & 0x08   # if xyz data exists, set 1
            xyzor = status & 0x80
            if not xyzda:
                continue
            else:
                x,y,z = self._acceleration
                return (x, y, z)

    def set_mode(self, mode):
        '''
        Sets the sensor operating mode using predefined constants.
        :param mode: 0: High Resolution (12-bit) @ 400Hz
                     1: Normal/HR (12-bit) @ 100Hz
                     2: Ultra-Low Power (8-bit) @ 10Hz (Ideal for Deep Sleep)
        '''
        if mode == 0:
            # ODR 400Hz (0111), LPen disabled (0), XYZ enabled (111) -> 0x77
            self._write_data(LIS2DH12_CTRL_REG1, 0x77)
            # HR bit enabled (1), FS +/- 2g (00) -> 0x08
            self._write_data(LIS2DH12_CTRL_REG4, 0x08)
        elif mode == 1:
            # ODR 100Hz (0101), LPen disabled (0), XYZ enabled (111) -> 0x57
            self._write_data(LIS2DH12_CTRL_REG1, 0x57)
            # HR bit enabled (1), FS +/- 2g (00) -> 0x08
            self._write_data(LIS2DH12_CTRL_REG4, 0x08)
        elif mode == 2:
            # ODR 10Hz (0010), Low-power mode LPen enabled (1), XYZ enabled (111) -> 0x2F
            self._write_data(LIS2DH12_CTRL_REG1, 0x2F)
            # HR bit disabled (0) for minimum power consumption -> 0x00
            self._write_data(LIS2DH12_CTRL_REG4, 0x00)
        elif mode == 3:
                # ODR Power-down (0000), LPen disabled (0), XYZ enabled (111) -> 0x07
                # Esto apaga el acelerómetro por completo según el datasheet
                self._write_data(LIS2DH12_CTRL_REG1, 0x07)
                self._write_data(LIS2DH12_CTRL_REG4, 0x00)
        else:
            print("Unknown mode.")
