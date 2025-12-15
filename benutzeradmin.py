#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "data" / "zeiterfassung.db"

def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)

def list_employees(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, rfuid_uid, role, timestamp FROM employees ORDER BY id")
    for row in cur.fetchall():
        print(row)

def add_employee(conn):
    name = input("Name: ").strip()
    if not name:
        print("Name erforderlich.")
        return
    role = input("Role (employee/hr/boss/admin) [employee]: ").strip() or "employee"
    if role not in ('employee','hr','boss','admin'):
        print("Ungültige Rolle.")
        return
    print("Bitte RFID-Tag präsentieren (UID eingeben):")
    uid = input("RFID UID: ").strip()
    ts = datetime.utcnow().isoformat()
    cur = conn.cursor()
    cur.execute("INSERT INTO employees (name, rfuid_uid, role, timestamp, synced) VALUES (?,?,?,?,0)", (name, uid, role, ts))
    conn.commit()
    print("Angestellter hinzugefügt, id=", cur.lastrowid)

def delete_employee(conn):
    id_ = input("ID löschen: ").strip()
    if not id_.isdigit():
        print("Ungültige ID.")
        return
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id = ?", (int(id_),))
    conn.commit()
    print("Gelöscht.")

def edit_employee(conn):
    id_ = input("ID editieren: ").strip()
    if not id_.isdigit():
        print("Ungültige ID.")
        return
    cur = conn.cursor()
    cur.execute("SELECT id, name, rfuid_uid, role FROM employees WHERE id = ?", (int(id_),))
    row = cur.fetchone()
    if not row:
        print("Nicht gefunden.")
        return
    print("Aktuell:", row)
    name = input(f"Name [{row[1]}]: ").strip() or row[1]
    uid = input(f"RFID UID [{row[2]}]: ").strip() or row[2]
    role = input(f"Role [{row[3]}]: ").strip() or row[3]
    if role not in ('employee','hr','boss','admin'):
        print("Ungültige Rolle.")
        return
    cur.execute("UPDATE employees SET name=?, rfuid_uid=?, role=?, synced=0 WHERE id=?", (name, uid, role, int(id_)))
    conn.commit()
    print("Aktualisiert.")

def main():
    conn = connect_db()
    try:
        while True:
            print("\nBenutzer-Admin: (l)ist, (a)dd, (e)dit, (d)elete, (q)uit")
            cmd = input("Auswahl: ").strip().lower()
            if cmd == 'l':
                list_employees(conn)
            elif cmd == 'a':
                add_employee(conn)
            elif cmd == 'e':
                edit_employee(conn)
            elif cmd == 'd':
                delete_employee(conn)
            elif cmd == 'q':
                break
    finally:
        conn.close()

if __name__ == "__main__":
    main()
