# src/modules/digital_input_ulp.py
# -*- coding: utf-8 -*-
from esp32 import ULP
from machine import mem32, Pin
from lib.esp32_ulp import src_to_binary, src_to_binary_ext
import time
from modules import utils

class LEDManagerULP:
    def __init__(self, timer_period_us= 10*1_000_000):
        """
        Initializes the LEDManagerULP module for displaying different ISURLOG states.

        Args:
            timer_period_us (int): ULP timer period in microseconds. 
        """
        
        self.ULP_MEM_BASE = 0x50000000
        self.ULP_DATA_MASK = 0xffff  # ULP data in lower 16 bits
        self.PULSES_NUM_OFFSET = 168
        self.UPULSES_NUM_OFFSET = 172
        self.CYCLES_ON_OFFSET = 176
        self.LOOPS_OFF_OFFSET = 180
        self.REMAIN_OFF_OFFSET = 184
        self.LOOPS_INTER_OFFSET = 188
        self.REMAIN_INTER_OFFSET = 192
        self.load_addr, self.entry_addr = 0, 0
        self.CYCLES_PER_US = 8
        self.CYCLES_PER_MS = 8000
        self.MAX_WAIT = 65535

        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/rtc_io_periph.c
        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/rtc_cntl_reg.h
        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/reg_base.h
        
        self.source = """\
            # --- Constantes de Registros y Hardware --- (Sin cambios)
            #define DR_REG_RTCIO_BASE           0x3ff48400
            #define RTC_IO_XTAL_32K_PAD_REG     (DR_REG_RTCIO_BASE + 0x8c)
            #define RTC_IO_X32P_MUX_SEL_M (BIT(17))
            #define RTC_GPIO_OUT_REG            (DR_REG_RTCIO_BASE + 0x0)
            #define RTC_GPIO_ENABLE_REG         (DR_REG_RTCIO_BASE + 0xc)
            #define RTC_GPIO_ENABLE_S           14
            #define RTC_GPIO_OUT_DATA_S         14
            #define RTCIO_GPIO32_CHANNEL        9

            # --- Configuración del Pin GPIO --- (Sin cambios)
            .set gpio, RTCIO_GPIO32_CHANNEL

            # --- Constantes Fijas --- (Sin cambios)
            .set max_wait, 65535

            .data
            # --- Variables Compartidas (CON .global) ---
            .global init_flag             # <--- Añadido .global
            init_flag: .long 0

            .global ulp_pulse_number      # <--- Añadido .global
            ulp_pulse_number: .long 1
            .global ulp_num_micro_pulsos  # <--- Añadido .global
            ulp_num_micro_pulsos: .long 20
            .global ulp_cycles_delay_on   # <--- Añadido .global
            ulp_cycles_delay_on: .long 40
            .global ulp_delay_off_loops   # <--- Añadido .global
            ulp_delay_off_loops: .long 2
            .global ulp_delay_off_remainder # <--- Añadido .global
            ulp_delay_off_remainder: .long 28970
            .global ulp_inter_pulse_delay_loops # <--- Añadido .global
            ulp_inter_pulse_delay_loops: .long 61
            .global ulp_inter_pulse_delay_remainder # <--- Añadido .global
            ulp_inter_pulse_delay_remainder: .long 2365

            .text
            # --- Resto del código ULP --- (Sin cambios funcionales)
            .global entry
            entry:
              # --- Bloque de Inicialización ---
              move r0, init_flag
              ld r1, r0, 0
              move r2, 1
              sub r2, r1, r2
              jump run_pulse_sequence, eq

            init:
              WRITE_RTC_REG(RTC_IO_XTAL_32K_PAD_REG, RTC_IO_X32P_MUX_SEL_M, 1, 1);
              WRITE_RTC_REG(RTC_GPIO_ENABLE_REG, RTC_GPIO_ENABLE_S + gpio, 1, 1)
              move r0, init_flag
              move r1, 1
              st r1, r0, 0

            run_pulse_sequence:
              # --- Bucle Exterior ---
              move r1, ulp_pulse_number
              ld r0, r1, 0

            outer_pulse_loop:
              # --- Inicio Ráfaga ---
              move r1, ulp_num_micro_pulsos
              ld r3, r1, 0

            burst_loop:
              # 1. ON
              WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 1)
              # 2. Wait ON
              wait ulp_cycles_delay_on
              # 3. OFF
              WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 0)
              # 4. Wait OFF
              move r1, ulp_delay_off_loops
              ld r2, r1, 0
            delay_off_inner_loop:
              wait max_wait
              sub r2, r2, 1
              jump delay_off_loop_end, eq
              jump delay_off_inner_loop
            delay_off_loop_end:
              wait ulp_delay_off_remainder
              # 5. Decremento micro-pulsos
              sub r3, r3, 1
              jump after_burst_loop, eq
              jump burst_loop

            after_burst_loop:
              # --- Retardo Condicional ---
              move r1, 1
              sub r1, r0, r1
              jump after_inter_pulse_delay, eq
              # --- Retardo Inter-Ráfaga ---
              move r1, ulp_inter_pulse_delay_loops
              ld r2, r1, 0
            inter_pulse_delay_loop:
              wait max_wait
              sub r2, r2, 1
              jump inter_pulse_delay_loop_end, eq
              jump inter_pulse_delay_loop
            inter_pulse_delay_loop_end:
              wait ulp_inter_pulse_delay_remainder
            after_inter_pulse_delay:
              # --- Decremento bucle exterior ---
              sub r0, r0, 1
              jump end_sequence, eq
              jump outer_pulse_loop

            end_sequence:
              halt
            """
        self.binary = None
        self.ulp = None
        self.timer_period_us = timer_period_us

    def load_ulp(self):
        """Loads the ULP program into the coprocessor."""
        utils.log_info("Converting source to bin...")
        self.binary = src_to_binary(self.source, cpu="esp32")
        utils.log_info("Done!")
        self.ulp = ULP()
        self.ulp.set_wakeup_period(0, self.timer_period_us)  # use timer0
        self.ulp.load_binary(self.load_addr, self.binary)
        self.ulp.run(self.entry_addr)
        utils.log_info("ULP program loaded successfully.")

    def set_ulp_pattern(self, pulse_num=1, n_micro_pulses=20, delay_on=5, delay_off=20, inter_delay=500, wake_up_period=10):
        """
        Calculates and writes the LED pattern parameters to ULP memory.
        
        """
        
        utils.log_info(f"Configurating ULP: pulses={pulse_num}, upulses={n_micro_pulses}, on={delay_on}us, off={delay_off}ms, inter={inter_delay}ms")

        cycles_on = self.CYCLES_PER_US * delay_on

        cycles_off = self.CYCLES_PER_MS * delay_off
        loops_off = cycles_off // self.MAX_WAIT
        remain_off = cycles_off % self.MAX_WAIT

        cycles_inter = self.CYCLES_PER_MS * inter_delay
        loops_inter = cycles_inter // self.MAX_WAIT
        remain_inter = cycles_inter % self.MAX_WAIT

        try:
            # Escribir valores usando las direcciones del diccionario 'addrs'
            # NOTA: Usamos ULP_MEM_BASE + addr, y escribimos un valor de 32 bits
            mem32[self.ULP_MEM_BASE + self.PULSES_NUM_OFFSET] = pulse_num
            mem32[self.ULP_MEM_BASE + self.UPULSES_NUM_OFFSET] = n_micro_pulses
            mem32[self.ULP_MEM_BASE + self.CYCLES_ON_OFFSET] = cycles_on
            mem32[self.ULP_MEM_BASE + self.LOOPS_OFF_OFFSET] = loops_off
            mem32[self.ULP_MEM_BASE + self.REMAIN_OFF_OFFSET] = remain_off
            mem32[self.ULP_MEM_BASE + self.LOOPS_INTER_OFFSET] = loops_inter
            mem32[self.ULP_MEM_BASE + self.REMAIN_INTER_OFFSET] = remain_inter
            utils.log_info("Values written in RTC SLOW MEMORY")
            
            ulp = ULP()
            ulp.set_wakeup_period(0, wake_up_period*1_000_000)

        except Exception as e:
            utils.log_error(f"Error values to RTC SLOW MEMORY: {e}")
    

