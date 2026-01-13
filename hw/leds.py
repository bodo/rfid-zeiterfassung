#!/usr/bin/env python3
"""LED helper with safe fallbacks.

Provides `LEDController` with `flash(event)` where event in {'work','break','ext'}.
Uses `gpiozero` if available, falls back to `RPi.GPIO`, otherwise Null (no-op).
"""
import time
from typing import Optional

try:
    from gpiozero import LED
    _GPIO_BACKEND = 'gpiozero'
except Exception:
    try:
        import RPi.GPIO as GPIO
        _GPIO_BACKEND = 'rpi'
    except Exception:
        _GPIO_BACKEND = None

from config.pin_config import LED_READY_GREEN, LED_READY_RED, LED_KOMMEN, LED_GEHEN, LED_EXTERN, LED_COMMON_ANODE


class _NullLED:
    def on(self):
        pass

    def off(self):
        pass


class LEDController:
    def __init__(self):
        self._ready = None
        self._ready_red = None
        self._kommen = None
        self._gehen = None
        self._extern = None
        self._common_anode = bool(LED_COMMON_ANODE)
        if _GPIO_BACKEND == 'gpiozero':
            active_high = not self._common_anode
            self._ready = LED(LED_READY_GREEN, active_high=active_high)
            self._ready_red = LED(LED_READY_RED, active_high=active_high)
            self._kommen = LED(LED_KOMMEN, active_high=active_high)
            self._gehen = LED(LED_GEHEN, active_high=active_high)
            self._extern = LED(LED_EXTERN, active_high=active_high)
        elif _GPIO_BACKEND == 'rpi':
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(LED_READY_GREEN, GPIO.OUT)
            GPIO.setup(LED_READY_RED, GPIO.OUT)
            GPIO.setup(LED_KOMMEN, GPIO.OUT)
            GPIO.setup(LED_GEHEN, GPIO.OUT)
            GPIO.setup(LED_EXTERN, GPIO.OUT)
            self._ready = ('rpi', LED_READY_GREEN)
            self._ready_red = ('rpi', LED_READY_RED)
            self._kommen = ('rpi', LED_KOMMEN)
            self._gehen = ('rpi', LED_GEHEN)
            self._extern = ('rpi', LED_EXTERN)
        else:
            # Null fallback for non-Pi environments
            self._ready = _NullLED()
            self._ready_red = _NullLED()
            self._kommen = _NullLED()
            self._gehen = _NullLED()
            self._extern = _NullLED()

    def _on(self, led):
        if _GPIO_BACKEND == 'gpiozero':
            led.on()
        elif _GPIO_BACKEND == 'rpi':
            _, pin = led
            GPIO.output(pin, GPIO.LOW if self._common_anode else GPIO.HIGH)
        else:
            pass

    def _off(self, led):
        if _GPIO_BACKEND == 'gpiozero':
            led.off()
        elif _GPIO_BACKEND == 'rpi':
            _, pin = led
            GPIO.output(pin, GPIO.HIGH if self._common_anode else GPIO.LOW)
        else:
            pass

    def ready_on(self):
        try:
            self._on(self._ready)
        except Exception:
            pass

    def ready_off(self):
        try:
            self._off(self._ready)
        except Exception:
            pass

    def flash(self, event: str, duration: float = 0.8):
        """Flash the LED corresponding to event: 'work' -> kommen/gehen mapping used by caller."""
        try:
            if event == 'work':
                # Caller decides whether it's a come or go; treat as green kurz flash
                self._on(self._ready)
                time.sleep(duration)
                self._off(self._ready)
            elif event == 'break':
                # use red as generic indicator for break
                self._on(self._ready_red)
                time.sleep(duration)
                self._off(self._ready_red)
            elif event == 'ext':
                # yellow LED for external appointment
                self._on(self._extern)
                time.sleep(duration)
                self._off(self._extern)
            elif event == 'kommen':
                self._on(self._kommen)
                time.sleep(duration)
                self._off(self._kommen)
            elif event == 'gehen':
                self._on(self._gehen)
                time.sleep(duration)
                self._off(self._gehen)
        except Exception:
            # be tolerant to GPIO errors
            pass

    def cleanup(self):
        if _GPIO_BACKEND == 'rpi':
            GPIO.cleanup()
