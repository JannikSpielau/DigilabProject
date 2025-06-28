# /home/tom/lcd/cursor.py
from base import (LCD, LCD_CMD_MODE,
                      LCD_LINE_1_ADDR_BASE, LCD_LINE_2_ADDR_BASE,
                      LCD_DISPLAY_CTRL_BASE, LCD_DISPLAY_ON_BIT,
                      LCD_CURSOR_ON_BIT, LCD_BLINK_ON_BIT)
import argparse

def main():
    parser = argparse.ArgumentParser(description="Control LCD cursor position and appearance.")
    parser.add_argument("--line", type=int, choices=[1, 2], help="Set cursor line (1 or 2).")
    parser.add_argument("--col", type=int, choices=range(16), help="Set cursor column (0-15). Requires --line if used.")

    parser.add_argument("--display", choices=["on", "off"], help="Turn display ON or OFF.")
    parser.add_argument("--cursor", choices=["on", "off"], help="Turn cursor visibility ON or OFF.")
    parser.add_argument("--blink", choices=["on", "off"], help="Turn cursor blink ON or OFF.")

    args = parser.parse_args()

    if args.col is not None and args.line is None:
        parser.error("--col requires --line to be specified for positioning.")
        return

    try:
        lcd = LCD() # Assumes LCD is initialized. Manages its own backlight state.

        # --- Part 1: Set Cursor Position (if specified) ---
        if args.line is not None:
            col = args.col if args.col is not None else 0 # Default to column 0 if line is set

            if args.line == 1:
                address = LCD_LINE_1_ADDR_BASE + col
            else: # args.line == 2
                address = LCD_LINE_2_ADDR_BASE + col

            print(f"Python script (cursor): Setting DDRAM address to 0x{address:02X} (Line {args.line}, Col {col}).")
            lcd.lcd_byte(address, LCD_CMD_MODE)

        # --- Part 2: Set Display/Cursor/Blink (if any of these args are provided) ---
        if args.display is not None or args.cursor is not None or args.blink is not None:
            # If any of these are specified, we construct a new display control command.
            # For unspecified ones, we'll use a default (e.g., display on, cursor off, blink off).
            # A more advanced version might try to read current state, but that's complex.

            # Default to display ON if not specified by user when other flags are present
            display_val = LCD_DISPLAY_ON_BIT if (args.display == "on" or (args.display is None and (args.cursor is not None or args.blink is not None))) else 0x00
            if args.display == "off": display_val = 0x00 # Explicit off

            cursor_val  = LCD_CURSOR_ON_BIT  if args.cursor == "on" else 0x00
            blink_val   = LCD_BLINK_ON_BIT   if args.blink == "on" else 0x00

            final_display_cmd = LCD_DISPLAY_CTRL_BASE | display_val | cursor_val | blink_val

            print(f"Python script (cursor): Setting Display Control to 0x{final_display_cmd:02X}.")
            lcd.lcd_byte(final_display_cmd, LCD_CMD_MODE)

        print("Python script (cursor): Cursor command(s) complete.")

    except Exception as e:
        print(f"Python script (cursor) error: {e}")

if __name__ == '__main__':
    main()