import sqlite3
from pathlib import Path
from config.db_schema import init_db, CLIENT_SCHEMA

def test_init_db_creates_tables(tmp_path):
    db_file = tmp_path / "test_zeiter.db"
    init_db(db_file, CLIENT_SCHEMA)
    assert db_file.exists()
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names = {r[0] for r in cur.fetchall()}
    # wichtige Tabellen prüfen
    assert "events" in names
    assert "employees" in names
    assert "logs" in names
    conn.close()
