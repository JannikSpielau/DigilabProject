# /home/tom/lcd/base.py

import smbus
import time

# I2C address of the LCD (e.g., 0x27, 0x3F, or 0x38)
LCD_ADDR = 0x38 # <<< MAKE SURE THIS IS CORRECT

# Modes for lcd_byte function (determines RS pin state)
LCD_CMD_MODE = 0  # Register Select = 0 (instruction)
LCD_CHR_MODE = 1  # Register Select = 1 (data)

# Common LCD Command Bytes (can be used by other scripts)
LCD_CLEAR_DISPLAY = 0x01
LCD_RETURN_HOME = 0x02
# Display Control Command Base (00001xxx)
LCD_DISPLAY_CTRL_BASE = 0x08
LCD_DISPLAY_ON_BIT = 0x04
LCD_CURSOR_ON_BIT = 0x02
LCD_BLINK_ON_BIT = 0x01

# Line Addresses (for Set DDRAM Address command)
LCD_LINE_1_ADDR_BASE = 0x80  # To set cursor to line 1, position 0
LCD_LINE_2_ADDR_BASE = 0xC0  # To set cursor to line 2, position 0

# PCF8574 Pin Mappings (typical for many I2C LCD backpacks)
# P0: RS (Register Select)
# P1: R/W (Read/Write - usually tied to GND for write-only)
# P2: E (Enable)
# P3: Backlight Control
# P4: D4
# P5: D5
# P6: D6
# P7: D7

# Constants for PCF8574 pin values
RS_PIN_VAL = 0x01  # P0 for RS
EN_PIN_VAL = 0x04  # P2 for Enable
BACKLIGHT_PIN_VAL = 0x08 # P3 for Backlight

# Timing constants
E_PULSE = 0.0005  # Pulse width for Enable pin
E_DELAY = 0.0005  # Delay after Enable pin toggle

class LCD:
    def __init__(self, initial_backlight_on=True):
        self.bus = smbus.SMBus(1) # For Raspberry Pi Rev 2 and later
        self.current_backlight_val = BACKLIGHT_PIN_VAL if initial_backlight_on else 0x00
        # Stores the last written PCF8574 prefix for (RS, D4-D7), with E low.
        # Initialize to a safe state: RS low (command), Data 0, E low.
        self.last_expander_prefix_state = 0x00

    def _write_to_expander(self, pcf_data_rs_prefix, enable_pin_active):
        """
        Internal method to write to PCF8574.
        pcf_data_rs_prefix: The bits for RS and Data (D4-D7).
        enable_pin_active: Boolean, True if Enable pin should be high.
        """
        expander_byte = pcf_data_rs_prefix
        if enable_pin_active:
            expander_byte |= EN_PIN_VAL

        expander_byte |= self.current_backlight_val # Add current backlight state
        self.bus.write_byte(LCD_ADDR, expander_byte)

        # If E is low, this is a stable state for RS/Data, so store it
        if not enable_pin_active:
            self.last_expander_prefix_state = pcf_data_rs_prefix

    def set_backlight(self, turn_on):
        """Controls the LCD backlight."""
        if turn_on:
            self.current_backlight_val = BACKLIGHT_PIN_VAL
        else:
            self.current_backlight_val = 0x00
        # Re-send the last known state of RS/Data pins with the new backlight state and E low.
        # This ensures other LCD control/data pins are not inadvertently changed.
        self._write_to_expander(self.last_expander_prefix_state, False) # False for E low

    def lcd_byte(self, lcd_instruction_byte, mode):
        """
        Sends a byte to the LCD.
        lcd_instruction_byte: The 8-bit command or character data for the LCD.
        mode: LCD_CMD_MODE (for instructions) or LCD_CHR_MODE (for characters).
        """
        rs_val = RS_PIN_VAL if mode == LCD_CHR_MODE else 0x00

        # High nibble (D7-D4)
        # Data bits D7-D4 from lcd_instruction_byte are already in the high 4 bits of PCF8574's P7-P4
        pcf_prefix_high_nibble = rs_val | (lcd_instruction_byte & 0xF0)
        self._write_to_expander(pcf_prefix_high_nibble, False) # Send with E low
        self._toggle_enable_pin(pcf_prefix_high_nibble)

        # Low nibble (D3-D0)
        # Shift D3-D0 of lcd_instruction_byte to occupy D7-D4 positions for PCF8574's P7-P4
        pcf_prefix_low_nibble = rs_val | ((lcd_instruction_byte << 4) & 0xF0)
        self._write_to_expander(pcf_prefix_low_nibble, False) # Send with E low
        self._toggle_enable_pin(pcf_prefix_low_nibble)

    def _toggle_enable_pin(self, pcf_data_rs_prefix):
        """Pulses the Enable pin for the given RS/Data prefix."""
        time.sleep(E_DELAY)
        self._write_to_expander(pcf_data_rs_prefix, True)  # E high
        time.sleep(E_PULSE)
        self._write_to_expander(pcf_data_rs_prefix, False) # E low (also updates last_expander_prefix_state)
        time.sleep(E_DELAY)