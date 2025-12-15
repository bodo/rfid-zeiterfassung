from pathlib import Path
import importlib
import sqlite3
import config.db_schema as db_schema

def test_dbmigration_client_main_creates_db(tmp_path, monkeypatch):
    # Import module and monkeypatch its DB_PATH to temp file
    mod = importlib.import_module("dbmigration_client")
    temp_db = tmp_path / "zeiterfassung.db"
    monkeypatch.setattr(mod, "DB_PATH", temp_db)
    # call main which uses init_db
    mod.main()
    assert temp_db.exists()
    # quick sanity check for a table
    conn = sqlite3.connect(str(temp_db))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    assert cur.fetchone() is not None
    conn.close()
