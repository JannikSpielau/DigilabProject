# /home/tom/lcd/init.py
from base import (LCD, LCD_CMD_MODE, LCD_CLEAR_DISPLAY,
                      LCD_RETURN_HOME) # Add other commands if needed
import time

# Define LCD command values if not all are in lcd_base.py or for clarity
CMD_INIT_1 = 0x33  # Initialize
CMD_INIT_2 = 0x32  # Initialize
CMD_FUNCTION_SET_4BIT_2LINE = 0x28 # Function Set: 4-bit, 2 lines, 5x8 dots
CMD_DISPLAY_CONTROL_ON_CURSOR_OFF = 0x0C # Display ON, Cursor OFF, Blink OFF
CMD_ENTRY_MODE_SET = 0x06 # Entry Mode Set: Increment cursor, no shift

def main():
    try:
        lcd = LCD(initial_backlight_on=True) # Default is True, but explicit is fine
        print("Python script (init_clear): Initializing and clearing display.")

        lcd.lcd_byte(CMD_INIT_1, LCD_CMD_MODE)
        lcd.lcd_byte(CMD_INIT_2, LCD_CMD_MODE)
        lcd.lcd_byte(CMD_FUNCTION_SET_4BIT_2LINE, LCD_CMD_MODE)
        lcd.lcd_byte(CMD_DISPLAY_CONTROL_ON_CURSOR_OFF, LCD_CMD_MODE)
        lcd.lcd_byte(CMD_ENTRY_MODE_SET, LCD_CMD_MODE)
        lcd.lcd_byte(LCD_CLEAR_DISPLAY, LCD_CMD_MODE)
        time.sleep(0.0025) # Extra delay after clear display

        print("Python script (init_clear): Initialization and clear complete.")
    except Exception as e:
        print(f"Python script (init_clear) error: {e}")

if __name__ == '__main__':
    main()