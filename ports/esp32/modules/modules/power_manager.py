# src/modules/deep_sleep.py
from machine import Pin, deepsleep, I2C, freq, wake_reason, PWM
import esp32
import time
from modules import utils
import json
from lib.uds3231 import DS3231
from modules.config_manager import config_manager

class PowerManager:
    def __init__(self, sda_pin=None, scl_pin=None, i2c_freq=None, rtc_address=0x68):
        """
        Initializes the PowerManager.

        Args:
            sda_pin: The SDA pin for the I2C bus.
            scl_pin: The SCL pin for the I2C bus.
            i2c_freq: The frequency for the I2C bus.
            rtc_address: I2C address of the DS3231 RTC (default: 0x68).
        """

        self.uEPOCH = 946684800
        self.wakeup_reason = self.get_wakeup_reason()
        utils.log_info(f"ESP32 Wakeup reason: {self.wakeup_reason}")

        # I2C configuration from config.json, or use defaults
        self.sda_pin = sda_pin if sda_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("sda_pin", 21)
        self.scl_pin = scl_pin if scl_pin is not None else config_manager.static_config.get("pinout", {}).get("i2c", {}).get("scl_pin", 22)
        self.en_5v_pin = config_manager.static_config.get("pinout", {}).get("i2c", {}).get("control", 22)
        self.i2c_freq = i2c_freq if i2c_freq is not None else config_manager.static_config.get("i2c_freq", 100000)

        # Initialize I2C bus here
        self.rtc_address = rtc_address
        self.i2c_bus = I2C(0, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin), freq=self.i2c_freq)
        self.rtc = DS3231(self.i2c_bus, self.rtc_address)
        self.check_rtc_status()

        # Define the pins to be held during deep sleep
        self.pins_to_hold = [
            config_manager.static_config.get("pinout", {}).get("rs485", {}).get("ro_pin", 14),
            config_manager.static_config.get("pinout", {}).get("rs485", {}).get("di_pin", 23),
            config_manager.static_config.get("pinout", {}).get("control", {}).get("en_nbiot_pin", 5),
            config_manager.static_config.get("pinout", {}).get("control", {}).get("en_5v_pin", 13),
            config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25)
        ]

    def check_rtc_status(self):
        """
        Checks the status of the DS3231 RTC.

        Returns:
            True if the RTC is present and time is valid, False otherwise.
        """
        try:
            self.i2c_bus.readfrom_mem(self.rtc_address, 0x00, 1)  # Check if RTC is present
            if self.rtc.lost_power():  # Check if RTC lost power (and thus time)
                utils.log_error("DS3231 RTC lost power! Time is invalid.")
                self.rtc_available = False
            else:
                if (self.get_unix_time() < 1763628870): #Time can`t be earlier to the time I'm programming this :) 
                    self.rtc_available = False
                    utils.log_info(f"DS3231 RTC is present and time is not valid: {self.rtc.datetime()}")
                else:
                    self.rtc_available = True
                    utils.log_info(f"DS3231 RTC is present and time is valid: {self.rtc.datetime()}")
        except OSError:
            utils.log_error("DS3231 RTC not detected on I2C bus.")
            self.rtc_available = False

    def set_rtc_time(self, time_str, mode = "NB-IoT"):
        """
        Sets the time on the DS3231 RTC.

        Args:
            timestamp:  Time string from NB-IoT module of LoRaWAN module.
            format: NB-IoT or LoRaWAN.
        """
        
        if (mode == "NB-IoT"):
            try:
                # "yy/MM/dd,hh:mm:ss+TZ"  TZ is quarter-hours offset from GMT
                parts = time_str.split(",")
                date_parts = parts[0].split("/")
                time_parts = parts[1].split(":")
                tz_part = time_parts[2][-3:] # +02 or -02 etc
                tz_sign = 1 if tz_part[0] == "+" else -1
                tz_hours = int(tz_part[1:]) * 15 # Transform quarters of our in minutes

                year = int(date_parts[0]) + 2000  # Assuming 21st century
                month = int(date_parts[1])
                day = int(date_parts[2])
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2][:2])  # Only the first two digits are seconds

                # Create a time tuple in *local* time (as required by mktime)
                local_time_tuple = (year, month, day, 1, hour, minute, second, 0)  # Weekday and yearday are ignored
                utils.log_info(f"Local time tuple: {local_time_tuple}")
                
                self.rtc.datetime(local_time_tuple)
                self.rtc_available = True
                utils.log_info(f"Local time tuple: {self.rtc.datetime()}")


            except (IndexError, ValueError) as e:
                utils.log_error(f"Error parsing time string from modem: {e}, string: {time_str}")
                
        if (mode == "LoRaWAN"):
            try:
                # "04h36m00s on 11/27/2023"
                parts = time_str.split(" on ")
                date_parts = parts[1].split("/")
                time_parts = parts[0]

                year = int(date_parts[2]) 
                day = int(date_parts[1])
                month = int(date_parts[0])
                hour = int(time_parts[0:2])
                minute = int(time_parts[3:5])
                second = int(time_parts[6:8])  # Only the first two digits are seconds
                
                utils.log_error(f"From PM Day: {day} Month: {month}")

                # Create a time tuple in *local* time (as required by mktime)
                local_time_tuple = (year, month, day, 1, hour, minute, second, 0)  # Weekday and yearday are ignored
                utils.log_info(f"Local time tuple: {local_time_tuple}")
                
                self.rtc.datetime(local_time_tuple)
                self.rtc_available = True
                utils.log_info(f"Local time tuple: {self.rtc.datetime()}")


            except (IndexError, ValueError) as e:
                utils.log_error(f"Error parsing time string from modem: {e}, string: {time_str}")
                
    def get_unix_time(self):
        """
        Gets the time from the DS3231 RTC using a Unix timestamp.

        Return:
            Unix datetime.
        """
        time_tuple = self.rtc.datetime()
        time_tuple_for_mktime = (
            time_tuple.year,
            time_tuple.month,
            time_tuple.day,
            time_tuple.hour,
            time_tuple.minute,
            time_tuple.second,
            time_tuple.weekday, # Usamos el weekday del objeto
            1  # yearday calculado (1 para el 1 de enero)
        )
        unix_timestamp = time.mktime(time_tuple_for_mktime)
        
        return unix_timestamp + self.uEPOCH
        
    def seconds2wakeup(self):
        """
        Calculates the number of seconds until the next wakeup time,
        based on the latency_time and the current time from the RTC.

        Returns:
            The number of seconds until the next wakeup time.
        """
        if config_manager.dynamic_config["general"].get("rtc_sync", False) and self.rtc_available:

            if not self.rtc_available:
                utils.log_error("RTC not available for time synchronization.")
                return config_manager.dynamic_config["general"].get("latency_time", 10) * 60 # Default to latency_time if RTC is not available
            
            now_tuple = self.rtc.datetime()
            utils.log_info(f"Current RTC time: {now_tuple}")  # Log the current time
            now = now_tuple[4], now_tuple[5], now_tuple[6] # Get (hour, minute, second) from the tuple
            seconds_remaining = 0

            latency_time = int(config_manager.dynamic_config["general"].get("latency_time", 60)) # Default to 60 minutes if not set
            
            # Calculate the next multiple of latency_time
            if latency_time < 60:
                next_multiple = ((now[1] // latency_time) + 1) * latency_time
                if next_multiple > 60:
                    next_multiple = 0  # Reset to 0 if it exceeds 59 minutes
                seconds_remaining = (next_multiple - now[1]) * 60 - now[2]
            else:
                hours_to_next_multiple = ((now[0] // (latency_time // 60)) + 1) * (latency_time // 60)
                seconds_remaining = ((hours_to_next_multiple - now[0]) * 60 - now[1]) * 60 - now[2]

            if seconds_remaining < 60:
                seconds_remaining += latency_time * 60

            return seconds_remaining
        
        else:
            
            return int(config_manager.dynamic_config["general"].get("latency_time", 10)) * 60

    def configure_pins_for_sleep(self):
        """
        Configures the GPIO pins for deep sleep to minimize power consumption.
        """     
        Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("ro_pin", 14), Pin.OUT, Pin.PULL_DOWN,  value=0, hold=True)
        Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("di_pin", 23), Pin.OUT,  value=0, hold=True)
        Pin(config_manager.static_config.get("pinout", {}).get("rs485", {}).get("re_pin", 33), Pin.OUT,  value=0, hold=True)
        
        Pin(config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("rx_pin", 2), Pin.OUT, Pin.PULL_UP, value=1, hold=True)
        Pin(config_manager.static_config.get("pinout", {}).get("nb-iot", {}).get("tx_pin", 4), Pin.OUT, Pin.PULL_UP, value=1, hold=True)
        
        #Not necesarry to pull down via software, as they have physical pull down resistors.

        #Pin(32, Pin.OUT,  value=0, hold=True)
        #Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_5v_pin", 13), Pin.OUT,  value=0, hold=True)
        #Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=0, hold=True)

        utils.log_info("GPIO pins configured for sleep.")

    def set_cpu_freq(self, mode):
        """
        Sets the CPU frequency based on the given mode.

        Args:
            mode: The desired CPU frequency mode ("high-performance", "performance", "balanced", "low-power", "ultra-low-power").
        """
        if mode == "high-performance":
            freq(240000000)
            utils.log_info("CPU frequency set to 240 MHz (high-performance).")
        elif mode == "performance":
            freq(160000000)
            utils.log_info("CPU frequency set to 160 MHz (performance).")
        elif mode == "balanced":
            freq(80000000)
            utils.log_info("CPU frequency set to 80 MHz (balanced).")
        elif mode == "low-power":
            freq(40000000)
            utils.log_info("CPU frequency set to 40 MHz (low-power).")
        elif mode == "ultra-low-power":
            freq(20000000)
            utils.log_info("CPU frequency set to 20 MHz (ultra-low-power).")
        else:
            utils.log_error(f"Invalid CPU frequency mode: {mode}")

    def get_wakeup_reason(self):
        """
        Gets the reason for the ESP32's wakeup from deep sleep.

        Returns:
            A string describing the wakeup reason.
        """
        
        wake_reason_esp = wake_reason()
        
        if wake_reason_esp == 0:
            return "Power-on reset"
        if wake_reason_esp == 2:
            return "RTC GPIO reset"
        elif wake_reason_esp == 3:
            return "Watchdog reset"
        elif wake_reason_esp == 4:
            return "Deep sleep reset"
        elif wake_reason_esp == 5:
            return "Soft reset"
        else:
            return "Unknown wake up reason"

    def control_5v(self, state, reset = False):
        """
        Control 5V regulator (5V for MAX485 and 3v3 for MAX31865, both regulator are connected to the same ESP32 pin)
        """
        
        if reset:
            
            Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_5v_pin", 13), Pin.OUT,  value=(not state))
            time.sleep_ms(500)
        
        Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_5v_pin", 13), Pin.OUT,  value=state)
        
    def control_digital_output(self, state):
        """
        Control VO14642 solid state relay.
        """
        
        Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("do0_pin", 26), Pin.OUT,  value=state, hold=True)
        
    def control_vdc(self, state, reset = False):
        """
        Control 12V regulator.
        """
        
        if reset:
            
            Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=(not state))
            time.sleep_ms(500)
        
        Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=state)
        
    def control_vdc_soft_start(self, state, duration_ms=20):
        """
        Control 12V regulator.
        """
        if state:
            print("Starting soft start by PWM...")
            try:
                pwm = PWM(Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25)), freq=20000, duty=0)

                for i in range(101):
                    duty_cycle = int(i * 10.23) # Map 0-100 to 0-1023
                    pwm.duty(duty_cycle)
                    time.sleep_ms(duration_ms // 100)

                Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=1)
                print("Regulator ON.")

            except Exception as e:
                print(f"Error during PWM soft start: {e}")
                Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=1)
        else:
            Pin(config_manager.static_config.get("pinout", {}).get("control", {}).get("en_vdc_pin", 25), Pin.OUT,  value=0)
            print("Regulator OFF.")
        
    def configure_wakeup_sources(self, wake_up_sources):
    
        """
        Adds different pins for wakeup from deepsleep.
        """
        if config_manager.dynamic_config["general"].get("magnet_wakeup", False): #Check if magnetic wakeup is enabled.
            magnet_pin = Pin(config_manager.static_config.get("pinout", {}).get("magnet_pin", 35), Pin.IN)
            esp32.wake_on_ext0(pin = magnet_pin, level = esp32.WAKEUP_ALL_LOW)
            utils.log_info(f"Magnetic wake-up is enabled.")
        
        else:
            digital_config = config_manager.get_dynamic("digital_config")
            if digital_config.get("enable", False) and digital_config.get("counter", True):
                esp32.wake_on_ulp(True) #Enable the option to the ULP to wake up the ESP32
        
        if wake_up_sources == []:
            utils.log_info(f"No wake-up sources provided.")
            return
        
        wakeup_pins = []
        for pin in wake_up_sources:
            wakeup_pins.append(Pin(pin, Pin.IN))
            
        esp32.wake_on_ext1(pins = wakeup_pins, level = esp32.WAKEUP_ANY_HIGH)
        utils.log_info(f"Configured wake-up sources: {wake_up_sources} --> WAKEUP_ANY_HIGH.")
        
    def go_to_sleep(self):
        """
        Puts the ESP32 into deep sleep mode.
        """
        
        self.configure_pins_for_sleep()
        seconds_until_wakeup = self.seconds2wakeup()

        utils.log_info(f"Next wake-up in {seconds_until_wakeup} seconds")
        esp32.gpio_deep_sleep_hold(True)
        utils.log_info("Entering deep sleep now.")

        deepsleep(seconds_until_wakeup*1000)