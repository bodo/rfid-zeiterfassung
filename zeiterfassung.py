#!/usr/bin/env python3
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import time
import argparse
import logging
try:
    import board                 # Adafruit Blinka / CircuitPython board pins
    import busio
    import digitalio
    from adafruit_pn532.spi import PN532_SPI
except Exception:
    board = None
    busio = None
    digitalio = None
    PN532_SPI = None

from config.db_schema import CLIENT_SCHEMA, init_db as init_db_file
from config.pin_config import PN532_SPI_CS, PN532_RSTO, PN532_IRQ, LED_COMMON_ANODE

DB_PATH = Path(__file__).parent / "data" / "zeiterfassung.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Konsolen-Logging konfigurieren (nur Nachricht, Zeit wird manuell formatiert)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Mapping Event-Typ -> kurze deutsche Beschreibung (für Konsole)
# Neues Schema: event_type ∈ {'work','break','ext'}
EVENT_LABELS = {
    "work": "kommt/geht",       # je nach Kontext kann Start/Ende unterschieden werden
    "break": "Pause",
    "ext": "ext Termin",
}

def connect_db():
    # sicherstellen, dass DB-Struktur existiert
    init_db_file(DB_PATH, CLIENT_SCHEMA)
    conn = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)
    return conn

def find_employee_by_rfid(conn, uid):
    cur = conn.cursor()
    cur.execute("SELECT id, name, role FROM employees WHERE rfuid_uid = ?", (uid,))
    return cur.fetchone()

def insert_event(conn, employee_id, event_type, start_time=None, end_time=None):
    if start_time is None:
        start_time = datetime.utcnow().isoformat()
    # Schema verlangt nun end_time NOT NULL -> falls nicht gesetzt, setze end_time = start_time
    if end_time is None:
        end_time = start_time
    ts = datetime.utcnow().isoformat()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (employee_id, event_type, start_time, end_time, timestamp, synced) VALUES (?,?,?,?,?,0)",
        (employee_id, event_type, start_time, end_time, ts)
    )
    conn.commit()
    return cur.lastrowid

def log(conn, category, message):
    ts = datetime.utcnow().isoformat()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (category, message, timestamp) VALUES (?,?,?)", (category, message, ts))
    conn.commit()

def console_log_employee(emp_name: str, uid: str, event_type: str, when=None):
    """
    Ausgabe im Format: 09:00 Mitarbeiter "Karl" ("UID") kommt
    when: datetime oder None -> aktuelle lokale Zeit verwenden
    """
    if when is None:
        when = datetime.now()
    time_str = when.strftime("%H:%M")
    label = EVENT_LABELS.get(event_type, event_type)
    logging.info(f"{time_str} Mitarbeiter \"{emp_name}\" (\"{uid}\") {label}")

class PN532Reader:
    """
    Einfacher PN532 SPI Reader-Wrapper.
    Benutzt adafruit_pn532.spi.PN532_SPI.
    read_uid(timeout) -> HEX string (z.B. "04AABBCCDD")
    """
    def __init__(self, cs_pin: int = PN532_SPI_CS, rst_pin: int = None, irq_pin: int = None):
        if PN532_SPI is None or board is None or busio is None or digitalio is None:
            raise RuntimeError("Adafruit PN532 libs nicht installiert oder Blinka nicht verfügbar")
        # Board pin name versuchen (z.B. D8 für BCM8)
        try:
            spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        except Exception as e:
            raise RuntimeError("SPI Init fehlgeschlagen: " + str(e))
        # CS Pin auf board.<D{n}> abbilden
        cs_attr = f"D{cs_pin}"
        try:
            cs = digitalio.DigitalInOut(getattr(board, cs_attr))
        except Exception:
            # Fallback: CE0/CE1 Standard pins (D8 für CE0)
            cs = digitalio.DigitalInOut(board.D8)
        try:
            self.pn532 = PN532_SPI(spi, cs)
            # Initialisierung
            self.pn532.SAM_configuration()
        except Exception as e:
            raise RuntimeError("PN532 Init fehlgeschlagen: " + str(e))

    def read_uid(self, timeout: float = 0.5):
        """
        Liest passives Ziel (Card) und gibt HEX-String zurück oder None bei Timeout.
        """
        try:
            uid = self.pn532.read_passive_target(timeout=timeout)
        except Exception:
            uid = None
        if not uid:
            return None
        # NTAG UID als HEX (groß) darstellen
        return "".join(f"{b:02X}" for b in uid)

def has_start_work_today(conn, employee_id):
    """
    Prüft, ob für employee_id bereits ein 'work' Eintrag heute (UTC) existiert.
    """
    cur = conn.cursor()
    cur.execute("SELECT start_time, timestamp FROM events WHERE employee_id=? AND event_type='work'", (employee_id,))
    rows = cur.fetchall()
    today = datetime.utcnow().date()
    for r in rows:
        for ts in (r[0], r[1]):
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            if dt.date() == today:
                return True
    return False

def main_loop(simulate_input=True):
    conn = connect_db()
    print("Zeiterfassung gestartet. 'q' zum Beenden.")
    try:
        while True:
            if simulate_input:
                uid = input("RFID (UID) präsentieren (oder 'q'): ").strip()
                if uid.lower() == 'q':
                    break
                # Option: ask for event type for testing
                ev = input("Event type (work,break,ext) [work]: ").strip() or "work"
                emp = find_employee_by_rfid(conn, uid)
                if not emp:
                    print("Unbekannter Tag. Bitte Admin-Tag registrieren.")
                    log(conn, "error", f"Unknown RFID {uid}")
                    # konsistente Konsolenmeldung für unbekannten Tag
                    logging.error(f"{datetime.now().strftime('%H:%M')} Unbekannter RFID \"{uid}\" - bitte Admin-Tag registrieren")
                    continue
                emp_id = emp[0]
                # Vermeide doppelte Einbuchungen (work) am selben Tag
                if ev == "work" and has_start_work_today(conn, emp_id):
                    logging.warning(f"{datetime.now().strftime('%H:%M')} Mitarbeiter \"{emp[1]}\" (\"{uid}\") work-Eintrag ignoriert (bereits vorhanden)")
                    log(conn, "error", f"Ignored duplicate work for emp {emp_id} uid={uid}")
                    continue
                eid = insert_event(conn, emp_id, ev)
                # High-level Konsolen-Log gemäß Spec
                console_log_employee(emp[1], uid, ev)
                log(conn, "event", f"Inserted {ev} for emp {emp_id} (event id {eid})")
            else:
                # Echte Reader-Schleife mit PN532 (SPI)
                try:
                    reader = PN532Reader()
                    logging.info("PN532-Reader initialisiert, Warte auf Tags...")
                except Exception as exc:
                    logging.error("PN532-Reader konnte nicht initialisiert werden: %s", exc)
                    time.sleep(5)
                    break
                # Endlosschleife: bei Tag lesen verarbeiten (nicht blockierend)
                while True:
                    try:
                        uid_hex = reader.read_uid(timeout=0.5)
                        if not uid_hex:
                            # kein Tag gefunden: kurz warten
                            time.sleep(0.2)
                            continue
                        # Gefunden: UID ist HEX string
                        uid = uid_hex
                        emp = find_employee_by_rfid(conn, uid)
                        if not emp:
                            logging.error(f"{datetime.now().strftime('%H:%M')} Unbekannter RFID \"{uid}\" - bitte Admin-Tag registrieren")
                            log(conn, "error", f"Unknown RFID {uid}")
                            continue
                        emp_id = emp[0]
                        # Default-Verhalten: bei erstem Tag/Tag des Tages => work, sonst (falls duplicate) ignorieren
                        ev = "work"
                        if ev == "work" and has_start_work_today(conn, emp_id):
                            logging.warning(f"{datetime.now().strftime('%H:%M')} Mitarbeiter \"{emp[1]}\" (\"{uid}\") work-Eintrag ignoriert (bereits vorhanden)")
                            log(conn, "error", f"Ignored duplicate work for emp {emp_id} uid={uid}")
                            continue
                        eid = insert_event(conn, emp_id, ev)
                        console_log_employee(emp[1], uid, ev)
                        log(conn, "event", f"Inserted {ev} for emp {emp_id} (event id {eid})")
                        # kleine Pause, damit Karte nicht mehrfach gelesen wird
                        time.sleep(1.0)
                    except KeyboardInterrupt:
                        raise
                    except Exception as exc:
                        logging.error("Fehler in Reader-Loop: %s", exc)
                        time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        conn.close()
        print("Beende Zeiterfassung.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zeiterfassung Hauptprogramm (einfaches CLI-Loop).")
    parser.add_argument("--real-reader", action="store_true", help="Platzhalter: echten Reader benutzen (nicht implementiert).")
    args = parser.parse_args()
    main_loop(simulate_input=not args.real_reader)
