"""I2C 16x2 LCD helper using RPLCD with a no-op fallback.

Provides a small `LCDDisplay` class with methods:
- show_ready(), show_unknown(), show_success(name), show_message(...), clear(), close()

This module avoids hard failure on non-RPi systems by providing a NullLCD when
RPLCD or smbus is not available.
"""
from time import sleep
try:
    from RPLCD.i2c import CharLCD
    RPLCD_AVAILABLE = True
except Exception:
    CharLCD = None
    RPLCD_AVAILABLE = False

try:
    from config.pin_config import LCD_I2C_ADDRESS
except Exception:
    LCD_I2C_ADDRESS = 0x27


class NullLCD:
    def __init__(self, *a, **k):
        pass

    def clear(self):
        pass

    def write_string(self, s):
        pass

    def cursor_pos(self, pos):
        class Ctx:
            def __enter__(self):
                return None
            def __exit__(self, *e):
                return False
        return Ctx()

    def close(self):
        pass


class LCDDisplay:
    def __init__(self, address: int = LCD_I2C_ADDRESS, cols: int = 16, rows: int = 2, i2c_expander: str = 'PCF8574'):
        self._lcd = None
        self._available = False
        if RPLCD_AVAILABLE and CharLCD is not None:
            try:
                # Typical constructor for RPLCD i2c
                self._lcd = CharLCD(i2c_expander=i2c_expander, address=address, port=1, cols=cols, rows=rows)
                self._available = True
            except Exception:
                self._lcd = NullLCD()
                self._available = False
        else:
            self._lcd = NullLCD()
            self._available = False

    def clear(self):
        try:
            self._lcd.clear()
        except Exception:
            pass

    def show_message(self, line1: str, line2: str = ''):
        try:
            self._lcd.clear()
            with self._lcd.cursor_pos((0, 0)):
                self._lcd.write_string(line1[:16])
            if line2:
                with self._lcd.cursor_pos((1, 0)):
                    self._lcd.write_string(line2[:16])
        except Exception:
            # ignore display errors
            pass

    def show_ready(self):
        self.show_message('Zeiterfassung', 'Bereit')

    def show_unknown(self):
        self.show_message('Unbekannter Tag', 'Admin melden')

    def show_success(self, name: str):
        # show name (trim) and OK
        self.show_message(name[:16], 'Erfolg')

    def close(self):
        try:
            self._lcd.close()
        except Exception:
            pass


__all__ = ['LCDDisplay']
