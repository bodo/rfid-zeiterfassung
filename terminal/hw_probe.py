#!/usr/bin/env python3
"""
Minimaler Hardware-Test für LCD + READY-LED.
Auf dem Raspberry Pi ausführen.
"""
import time

from hw.lcd_i2c import LCDDisplay
from hw.leds import LEDController


def main():
    lcd = LCDDisplay()
    leds = LEDController()

    try:
        lcd.show_message("LCD Test", "Hallo Pi")
    except Exception as exc:
        print(f"LCD Fehler: {exc}")

    try:
        print("READY-LED an")
        leds.ready_on()
        time.sleep(2.0)
        print("READY-LED aus")
        leds.ready_off()
    except Exception as exc:
        print(f"LED Fehler: {exc}")

    time.sleep(1.0)
    try:
        lcd.clear()
    except Exception:
        pass


if __name__ == "__main__":
    main()
