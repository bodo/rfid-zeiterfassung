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
    print("Mögliche Lösungen (auf dem Raspberry Pi):")
    print(" 1) Systempakete installieren:")
    print("    sudo apt update && sudo apt install -y python3-pip python3-dev build-essential python3-rpi.gpio python3-spidev")
    print(" 2) Python‑Paket installieren:")
    print("    sudo pip3 install mfrc522")
    print(" 3) SPI aktivieren (raspi-config):")
    print("    sudo raspi-config -> Interface Options -> SPI -> Enable, dann Reboot")
    print(" 4) Nutzer zur Gruppe hinzufügen (Zugriff auf /dev/spidev*):")
    print("    sudo usermod -aG spi,gpio $USER && reboot")
    print(" 5) Prüfen, ob das Gerät vorhanden ist:")
    print("    ls -l /dev/spidev*")
    print("Danach: Skript mit sudo ausführen, falls Zugriffsfehler bestehen:\n    sudo python3 terminal/test_rc522.py")
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
                msg = str(ex)
                print("Lesefehler:", msg)
                # Häufig: MIFARE Classic benötigt Auth zum Lesen von Datenblöcken.
                # Versuche als Fallback nur die UID per low-level API zu lesen.
                if "AUTH ERROR" in msg or "status2req & 0x08" in msg or "Authentication" in msg:
                    try:
                        from mfrc522 import MFRC522
                        dev = MFRC522()
                        status, TagType = dev.MFRC522_Request(dev.PICC_REQIDL)
                        if status == dev.MI_OK:
                            status, uid = dev.MFRC522_Anticoll()
                            if status == dev.MI_OK and uid:
                                uid_hex = ''.join(f"{b:02X}" for b in uid)
                                uid_dec = int(uid_hex, 16)
                                print(f"Fallback UID: {uid_dec} (HEX: {uid_hex})")
                            else:
                                print("Fallback: UID konnte nicht gelesen werden.")
                        else:
                            print("Fallback: Kein Tag im Lesebereich (low-level).")
                    except Exception as e2:
                        print("Fallback Low-level Lesefehler:", e2)
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
