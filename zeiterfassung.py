#!/usr/bin/env python3
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import time
import argparse
import logging
try:
    # RC522 reader wrapper (uses `mfrc522` low-level API)
    from hw.rc522_reader import RC522Reader
except Exception:
    RC522Reader = None

from config.db_schema import CLIENT_SCHEMA, init_db as init_db_file
from config.pin_config import LED_COMMON_ANODE
try:
    from hw.lcd_i2c import LCDDisplay
except Exception:
    LCDDisplay = None
try:
    from hw.leds import LEDController
except Exception:
    LEDController = None

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

# RC522Reader provided in hw/rc522_reader.py; if unavailable, real-reader mode will fail with helpful message

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
    lcd = None
    leds = None
    if LCDDisplay is not None:
        try:
            lcd = LCDDisplay()
            lcd.show_ready()
        except Exception as e:
            logging.warning("LCD initialisierung fehlgeschlagen: %s", e)
    if LEDController is not None:
        try:
            leds = LEDController()
        except Exception:
            leds = None
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
                    try:
                        if lcd:
                            lcd.show_unknown()
                    except Exception:
                        pass
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
                try:
                    if lcd:
                        lcd.show_success(emp[1])
                    if leds:
                        if ev == 'work':
                            leds.flash('kommen')
                        elif ev == 'break':
                            leds.flash('break')
                        elif ev == 'ext':
                            leds.flash('ext')
                except Exception:
                    pass
            else:
                # Echte Reader-Schleife mit PN532 (SPI)
                try:
                    if RC522Reader is None:
                        raise RuntimeError("RC522Reader implementation not available (mfrc522 missing)")
                    reader = RC522Reader()
                    logging.info("RC522-Reader initialisiert, Warte auf Tags...")
                except Exception as exc:
                    logging.error("RC522-Reader konnte nicht initialisiert werden: %s", exc)
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
                            try:
                                if lcd:
                                    lcd.show_unknown()
                            except Exception:
                                pass
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
                        try:
                            if lcd:
                                lcd.show_success(emp[1])
                            if leds:
                                if ev == 'work':
                                    leds.flash('kommen')
                                elif ev == 'break':
                                    leds.flash('break')
                                elif ev == 'ext':
                                    leds.flash('ext')
                        except Exception:
                            pass
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
