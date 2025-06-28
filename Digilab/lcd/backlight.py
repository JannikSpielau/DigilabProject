# /home/tom/lcd/backlight.py
from base import LCD
import argparse

def main():
    parser = argparse.ArgumentParser(description="Control LCD backlight.")
    parser.add_argument("state", choices=["on", "off"], help="Desired backlight state: 'on' or 'off'.")
    args = parser.parse_args()

    try:
        # LCD class now manages its backlight state.
        # We instantiate it (defaulting to its last known state or initial_backlight_on if first time)
        # then explicitly set the backlight.
        lcd = LCD()

        if args.state == "on":
            print("Python script (backlight): Turning backlight ON.")
            lcd.set_backlight(True)
        else: # args.state == "off"
            print("Python script (backlight): Turning backlight OFF.")
            lcd.set_backlight(False)

        print(f"Python script (backlight): Backlight set to {args.state}.")
    except Exception as e:
        print(f"Python script (backlight) error: {e}")

if __name__ == '__main__':
    main()