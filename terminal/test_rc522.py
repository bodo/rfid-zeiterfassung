#!/usr/bin/env python3
"""Kleines Testskript für RC522 Leser.

Benutzung: Auf dem Raspberry Pi mit aktiviertem SPI ausführen.

- Installiere: `pip install mfrc522 spidev RPi.GPIO`
- SPI aktivieren: `sudo raspi-config` -> Interface -> SPI
"""
import time

try:
    from mfrc522 import SimpleMFRC522
except Exception as e:
    print("Fehler: mfrc522 Bibliothek nicht gefunden:", e)
    print("Installieren: pip install mfrc522 spidev RPi.GPIO (nur auf Raspberry Pi)")
    raise SystemExit(1)


def main():
    reader = SimpleMFRC522()
    print("RC522 Test: Karte/Tag halten. Ctrl+C zum Beenden.")
    try:
        while True:
            try:
                id, text = reader.read()
                print(f"Gelesene ID: {id} (HEX: {format(id, 'X')})")
                # optional: kurze Pause
                time.sleep(1)
            except Exception as ex:
                print("Lesefehler:", ex)
                time.sleep(0.5)
    except KeyboardInterrupt:
        print('\nBeende Test.')
    finally:
        try:
            reader.cleanup()
        except Exception:
            pass


if __name__ == '__main__':
    main()
