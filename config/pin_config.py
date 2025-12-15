# Zentrale Pin- und Secret-Konfiguration (BCM-Nummern)

LED_READY_GREEN = 17
LED_READY_RED = 27
LED_KOMMEN = 22
LED_GEHEN = 23

BTN_INFO = 5
BTN_KOMMEN = 6
BTN_GEHEN = 13
BTN_EXT_TERM = 19

I2C_SDA = 2
I2C_SCL = 3
LCD_I2C_ADDRESS = 0x27

PN532_SPI_MOSI = 10
PN532_SPI_MISO = 9
PN532_SPI_SCLK = 11
PN532_SPI_CS = 8
PN532_RSTO = 24
PN532_IRQ = 25

LED_COMMON_ANODE = False
LED_RESISTOR_OHM = 330

import os
from pathlib import Path

def load_shared_secret(env_var_name: str = "TIME_SHARED_SECRET",
                       fallback_path: str = "/etc/time_shared_secret") -> str:
    """
    Lädt das Shared Secret:
    1. Aus ENV (IHK_SHARED_SECRET)
    2. Aus Datei /etc/ihk_shared_secret (falls vorhanden)
    3. Sonst leere Zeichenkette zurückgeben (Caller soll dies prüfen)
    """
    val = os.getenv(env_var_name)
    if val:
        return val.strip()
    try:
        p = Path(fallback_path)
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    try:
        p2 = Path(__file__).parent / "secrets.example.env"
        if p2.exists():
            for line in p2.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == env_var_name:
                        return v.strip()
    except Exception:
        pass
    return ""
