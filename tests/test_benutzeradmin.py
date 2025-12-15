import sqlite3
from pathlib import Path
import importlib
import config.db_schema as db_schema

def test_benutzeradmin_connect_and_list(tmp_path, capsys, monkeypatch):
    mod = importlib.import_module("benutzeradmin")
    temp_db = tmp_path / "zeiterfassung.db"
    # monkeypatch DB_PATH used by module
    monkeypatch.setattr(mod, "DB_PATH", temp_db)
    # initialize DB schema for client
    db_schema.init_db(temp_db, db_schema.CLIENT_SCHEMA)
    # connect and insert employee directly
    conn = mod.connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO employees (name, rfuid_uid, role, timestamp, synced) VALUES (?,?,?,?,0)", ("TestUser", "UID123", "employee", "2025-01-01T00:00:00"))
    conn.commit()
    # call list_employees which prints rows
    mod.list_employees(conn)
    captured = capsys.readouterr()
    assert "TestUser" in captured.out
    conn.close()
