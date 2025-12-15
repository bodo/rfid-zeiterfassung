#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "data" / "zeiterfassung.db"

def connect_db():
    return sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)

def list_employees(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, role, rfuid_uid FROM employees ORDER BY id")
    rows = cur.fetchall()
    for r in rows:
        print(r)

def events_last_days(conn, emp_id, days=7):
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    cur = conn.cursor()
    cur.execute("SELECT id, event_type, start_time, end_time, timestamp, synced FROM events WHERE employee_id=? AND timestamp>=? ORDER BY timestamp DESC", (emp_id, since))
    rows = cur.fetchall()
    if not rows:
        print("Keine Events.")
    for r in rows:
        print(r)

def main():
    conn = connect_db()
    try:
        while True:
            print("\nReports: (l)ist employees, (e)vents last days, (q)uit")
            cmd = input("Auswahl: ").strip().lower()
            if cmd == 'l':
                list_employees(conn)
            elif cmd == 'e':
                emp = input("Employee ID: ").strip()
                if not emp.isdigit():
                    print("Ungültige ID.")
                    continue
                days = input("Tage (default 7): ").strip()
                days = int(days) if days.isdigit() else 7
                events_last_days(conn, int(emp), days)
            elif cmd == 'q':
                break
    finally:
        conn.close()

if __name__ == "__main__":
    main()
