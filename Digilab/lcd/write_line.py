import os
import signal
import sys
import time
import subprocess
from base import (LCD, LCD_CHR_MODE, LCD_CMD_MODE,
                  LCD_LINE_1_ADDR_BASE, LCD_LINE_2_ADDR_BASE)
import argparse

DISPLAY_WIDTH = 16  # Max characters per line

LINE_ADDRS = {
    0: LCD_LINE_1_ADDR_BASE,
    1: LCD_LINE_2_ADDR_BASE
}

PID_FILE = "/tmp/i2c_lcd_scroller.pid"

def write_line(lcd, line, text):
    lcd.lcd_byte(LINE_ADDRS[line], LCD_CMD_MODE)
    for char in text:
        lcd.lcd_byte(ord(char), LCD_CHR_MODE)

def kill_old_instance():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, signal.SIGTERM)
            print(f"Killed old instance with PID {old_pid}")
            time.sleep(1)
        except ProcessLookupError:
            pass
        except Exception as e:
            print(f"Error killing old instance: {e}")

def write_pid():
    pid = os.getpid()
    with open(PID_FILE, "w") as f:
        f.write(str(pid))

def remove_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def run_init_py():
    # Run init.py in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    init_path = os.path.join(script_dir, "init.py")
    if os.path.exists(init_path):
        print("Running init.py...")
        subprocess.run([sys.executable, init_path])
    else:
        print("init.py not found, skipping.")

def main():
    parser = argparse.ArgumentParser(description="Write or scroll text on an I2C LCD.")
    parser.add_argument("--line", action='append', type=int, choices=[0, 1], required=True,
                        help="Line number (0 or 1). Can be used multiple times.")
    parser.add_argument("--message", action='append', type=str, required=True,
                        help="Message for the corresponding line. Must match the number of --line arguments.")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Delay in seconds between scroll steps.")
    args = parser.parse_args()

    if len(args.line) != len(args.message):
        print("Error: Each --line must have a corresponding --message.")
        return

    kill_old_instance()
    write_pid()
    run_init_py()
    lines = [" " * DISPLAY_WIDTH, " " * DISPLAY_WIDTH]
    for line_num, msg in zip(args.line, args.message):
        lines[line_num] = msg

    try:
        lcd = LCD()
        scroll_needed = any(len(line) > DISPLAY_WIDTH for line in lines)

        if not scroll_needed:
            for i, line_text in enumerate(lines):
                padded = line_text.ljust(DISPLAY_WIDTH)
                write_line(lcd, i, padded)
            print("Display complete. No scrolling needed.")
            while True:
                time.sleep(1)
        else:
            scroll_lines = [
                lines[0] + " " * DISPLAY_WIDTH,
                lines[1] + " " * DISPLAY_WIDTH
            ]
            max_len = max(len(scroll_lines[0]), len(scroll_lines[1]))

            print("Starting infinite scroll... Press Ctrl+C to stop.")
            while True:
                for i in range(max_len - DISPLAY_WIDTH + 1):
                    window0 = scroll_lines[0][i:i + DISPLAY_WIDTH].ljust(DISPLAY_WIDTH)
                    window1 = scroll_lines[1][i:i + DISPLAY_WIDTH].ljust(DISPLAY_WIDTH)

                    write_line(lcd, 0, window0)
                    write_line(lcd, 1, window1)

                    time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\nScrolling stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        remove_pid_file()

if __name__ == '__main__':
    main()
