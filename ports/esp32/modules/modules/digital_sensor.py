# src/modules/digital_input_ulp.py
from esp32 import ULP
from machine import mem32, Pin
from lib.esp32_ulp import src_to_binary
from modules import utils
from modules.config_manager import config_manager  # Import the config_manager


class DigitalInputULP:
    def __init__(self, io_number=None, debounce_max_count=None, edge_count_to_wake_up=None, timer_period_us=None):
        """
        Initializes the DigitalInputULP module for reading digital pulses using the ULP coprocessor.

        Args:
            io_number (int): The GPIO pin number to monitor.  Defaults to config.json.
            debounce_max_count (int): Debounce counter maximum value. Defaults to config.json.
            edge_count_to_wake_up (int): Number of edges to detect before waking up the main CPU. Defaults to config.json.
            timer_period_us (int): ULP timer period in microseconds. Defaults to config.json.
        """
        self.ULP_MEM_BASE = 0x50000000
        self.ULP_DATA_MASK = 0xffff  # ULP data in lower 16 bits
        self.MAGIC_TOKEN = 0xABCD
        self.MAGIC_TOKEN_OFFSET = 224
        self.NEXT_EDGE_OFFSET = 228
        self.DEBOUNCE_COUNTER_OFFSET = 232
        self.DEBOUNCE_MAX_COUNT_OFFSET = 236
        self.EDGE_COUNT_OFFSET = 240
        self.EDGE_COUNT_TO_WAKE_UP_OFFSET = 244
        self.IO_NUMBER_OFFSET = 248
        self.load_addr, self.entry_addr = 0, 0

        # Load configuration, use defaults or config file.
        self.io_number = io_number if io_number is not None else 0
        self.debounce_max_count = debounce_max_count if debounce_max_count is not None else 3
        self.edge_count_to_wake_up = edge_count_to_wake_up if edge_count_to_wake_up is not None else config_manager.dynamic_config.get("digital_config", {}).get("wake", 10)
        self.timer_period_us = timer_period_us if timer_period_us is not None else 50000

        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/rtc_io_periph.c
        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/rtc_cntl_reg.h
        #https://github.com/espressif/esp-idf/blob/v5.0.2/components/soc/esp32/include/soc/reg_base.h
        
        self.source = """
            #define DR_REG_RTCIO_BASE 0x3ff48400
            #define RTC_IO_TOUCH_PAD0_REG (DR_REG_RTCIO_BASE + 0x7c)
            #define RTC_IO_TOUCH_PAD0_MUX_SEL_M (BIT(27))
            #define RTC_IO_TOUCH_PAD0_FUN_IE_M (BIT(19))
            #define RTC_GPIO_IN_REG (DR_REG_RTCIO_BASE + 0x24)
            #define RTC_GPIO_IN_NEXT_S 14
            #define RTC_CNTL_LOW_POWER_ST_REG         (DR_REG_RTCIO_BASE + 0xc0)
            #define RTC_CNTL_RDY_FOR_WAKEUP  (BIT(19))

            /* --- INICIO DE LA MODIFICACIÓN: Añadir Magic Token --- */
            .set token, 0xABCD

            .bss
                .global magic
            magic:
                .long 0
            /* --- FIN DE LA MODIFICACIÓN --- */

                .global next_edge
            next_edge:
                .long 0

                .global debounce_counter
            debounce_counter:
                .long 0

                .global debounce_max_count
            debounce_max_count:
                .long 0

                .global edge_count
            edge_count:
                .long 0

                .global edge_count_to_wake_up
            edge_count_to_wake_up:
                .long 0

                .global io_number
            io_number:
                .long 0

                /* Code goes into .text section */
                .text
                .global entry
            entry:
                /* --- INICIO DE LA MODIFICACIÓN: Comprobar Magic Token --- */
                /* Comprobar si ya hemos inicializado */
                move r3, magic
                ld r0, r3, 0
                jumpr start_counting, token, eq

            init:
                /* Esto solo se ejecuta la primera vez */
                /* connect GPIO to the RTC subsystem */
                WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)
                /* switch the GPIO into input mode */
                WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_FUN_IE_M, 1, 1)

                /* Guardar el token para indicar que hemos terminado la inicialización */
                move r0, token
                st r0, r3, 0 /* r3 todavía contiene la dirección de 'magic' */

            start_counting:
                /* El resto del programa original empieza aquí */
                /* --- FIN DE LA MODIFICACIÓN --- */

                /* Load io_number */
                move r3, io_number
                ld r3, r3, 0

                /* Lower 16 IOs and higher need to be handled separately,
                 * because r0-r3 registers are 16 bit wide.
                 * Check which IO this is.
                 */
                move r0, r3
                jumpr read_io_high, 16, ge

                /* Read the value of lower 16 RTC IOs into R0 */
                READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S, 16)
                rsh r0, r0, r3
                jump read_done

                /* Read the value of RTC IOs 16-17, into R0 */
            read_io_high:
                READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + 16, 2)
                sub r3, r3, 16
                rsh r0, r0, r3

            read_done:
                and r0, r0, 1
                /* State of input changed? */
                move r3, next_edge
                ld r3, r3, 0
                add r3, r0, r3
                and r3, r3, 1
                jump changed, eq
                /* Not changed */
                /* Reset debounce_counter to debounce_max_count */
                move r3, debounce_max_count
                move r2, debounce_counter
                ld r3, r3, 0
                st r3, r2, 0
                /* End program */
                halt

                .global changed
            changed:
                /* Input state changed */
                /* Has debounce_counter reached zero? */
                move r3, debounce_counter
                ld r2, r3, 0
                add r2, r2, 0 /* dummy ADD to use "jump if ALU result is zero" */
                jump edge_detected, eq
                /* Not yet. Decrement debounce_counter */
                sub r2, r2, 1
                st r2, r3, 0
                /* End program */
                halt

                .global edge_detected
            edge_detected:
                /* Reset debounce_counter to debounce_max_count */
                move r3, debounce_max_count
                move r2, debounce_counter
                ld r3, r3, 0
                st r3, r2, 0
                /* Flip next_edge */
                move r3, next_edge
                ld r2, r3, 0
                add r2, r2, 1
                and r2, r2, 1
                st r2, r3, 0
                /* Increment edge_count */
                move r3, edge_count
                ld r2, r3, 0
                add r2, r2, 1
                st r2, r3, 0
                /* Compare edge_count to edge_count_to_wake_up */
                move r3, edge_count_to_wake_up
                ld r3, r3, 0
                sub r3, r3, r2
                jump wake_up, eq
                /* Not yet. End program */
                halt

                .global wake_up
            wake_up:
                /* Wake up the SoC, end program */
                wake
                halt
        """
        self.binary = None
        self.addrs_syms = None
        self.ulp = None
        
    def ulp_loaded(self):
        """Checks if the ULP code has been loaded."""
        token = mem32[self.ULP_MEM_BASE + self.MAGIC_TOKEN_OFFSET] & self.ULP_DATA_MASK
        
        if token == self.MAGIC_TOKEN:
            utils.log_info("ULP program loaded.")
            return True
        else:
            utils.log_info("ULP program not loaded.")
            return False

    def load_ulp(self):
        """Loads the ULP program into the coprocessor."""
        utils.log_info("Converting source to bin...")
        self.binary = src_to_binary(self.source, cpu="esp32")
        utils.log_info("Done!")
        self.ulp = ULP()
        self.ulp.set_wakeup_period(0, self.timer_period_us)  # use timer0
        self.ulp.load_binary(self.load_addr, self.binary)

        # Initialize ULP memory with configuration values.
        mem32[self.ULP_MEM_BASE + self.NEXT_EDGE_OFFSET] = 0
        mem32[self.ULP_MEM_BASE + self.DEBOUNCE_COUNTER_OFFSET] = self.debounce_max_count
        mem32[self.ULP_MEM_BASE + self.DEBOUNCE_MAX_COUNT_OFFSET] = self.debounce_max_count
        mem32[self.ULP_MEM_BASE + self.EDGE_COUNT_OFFSET] = 0
        mem32[self.ULP_MEM_BASE + self.EDGE_COUNT_TO_WAKE_UP_OFFSET] = self.edge_count_to_wake_up
        mem32[self.ULP_MEM_BASE + self.IO_NUMBER_OFFSET] = self.io_number

        self.ulp.run(self.entry_addr)
        utils.log_info("ULP program loaded successfully.")


    def get_pulse_count(self):
        """
        Retrieves the current pulse count (edge_count // 2).
        Sets remainder to mem32[self.ULP_MEM_BASE + self.EDGE_COUNT_OFFSET]
        
        Returns:
        
            Pulse count for each cycle."""
        
        edge_count = mem32[self.ULP_MEM_BASE + self.EDGE_COUNT_OFFSET] & self.ULP_DATA_MASK
        pulse_count = (edge_count // 2 )
        pulse_count_remainder = (edge_count % 2 )
        mem32[self.ULP_MEM_BASE + self.EDGE_COUNT_OFFSET] = pulse_count_remainder
        utils.log_info(f"Last cycles pulse counter: {pulse_count}, remainder: {pulse_count_remainder}.")
        return pulse_count
    
