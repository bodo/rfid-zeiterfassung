#!/usr/bin/env python3
"""RC522 Reader wrapper using low-level MFRC522 API (non-blocking polling).

Provides `RC522Reader` with `read_uid(timeout)` returning HEX string or None,
and `cleanup()` for symmetry with other readers.
"""
import time

try:
    from mfrc522 import MFRC522
except Exception:
    MFRC522 = None


class RC522Reader:
    def __init__(self, cs_pin: int = None, rst_pin: int = None):
        if MFRC522 is None:
            raise RuntimeError("mfrc522 library not available; install mfrc522 and spidev")
        # MFRC522() autodetects SPI pins on Raspberry Pi
        try:
            self.dev = MFRC522()
        except Exception as e:
            raise RuntimeError("RC522 init failed: " + str(e))

    def read_uid(self, timeout: float = 0.5):
        """Poll the RC522 for a passive tag. Returns HEX UID string or None on timeout."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                status, TagType = self.dev.MFRC522_Request(self.dev.PICC_REQIDL)
                if status != self.dev.MI_OK:
                    time.sleep(0.02)
                    continue
                status, uid = self.dev.MFRC522_Anticoll()
                if status == self.dev.MI_OK and uid:
                    # uid is a list of 4 bytes (or more); format as uppercase HEX
                    return "".join(f"{b:02X}" for b in uid)
            except Exception:
                # ignore transient errors and continue polling
                time.sleep(0.05)
        return None

    def cleanup(self):
        # MFRC522 has no explicit cleanup in this implementation
        return
