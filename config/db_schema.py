import sqlite3
from pathlib import Path
from typing import Union

# Schema für Client (zeiterfassung)
CLIENT_SCHEMA = """
-- Client (SQLite) schema angepasst an Spec: event_type ∈ ('work','break','ext'), end_time NOT NULL
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    event_type VARCHAR(16) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    timestamp DATETIME NOT NULL,
    synced INTEGER DEFAULT 0,
    CHECK (event_type IN ('work', 'break', 'ext'))
);
CREATE INDEX IF NOT EXISTS idx_events_synced ON events(synced);
CREATE INDEX IF NOT EXISTS idx_events_employee_id ON events(employee_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    rfuid_uid VARCHAR(32),
    role VARCHAR(16) NOT NULL,
    timestamp DATETIME NOT NULL,
    synced INTEGER DEFAULT 0,
    CHECK (role IN ('employee', 'hr', 'boss', 'admin'))
);
CREATE INDEX IF NOT EXISTS idx_employees_rfuid_uid ON employees(rfuid_uid);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(16) NOT NULL,
    message VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    CHECK (category IN ('event', 'hr', 'sync', 'error'))
);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
"""

# MySQL / MariaDB schema (angepasst an Spec)
SERVER_SCHEMA_MYSQL = """
CREATE TABLE IF NOT EXISTS server_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remote_id INT,
    employee_id INT,
    event_type VARCHAR(32) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    timestamp DATETIME,
    received_at DATETIME,
    INDEX idx_server_events_employee (employee_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS server_employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    rfuid_uid VARCHAR(32),
    role VARCHAR(16),
    created_at DATETIME
) ENGINE=InnoDB;
"""

def init_db(db_path: Union[str, Path], schema: str) -> None:
    """
    Erzeugt Verzeichnis, verbindet zur SQLite-DB und führt das Schema aus.
    Idempotent: sicher mehrfach ausführbar.
    """
    p = Path(db_path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()

def init_mysql_db(host: str, user: str, password: str, database: str, port: int = 3306) -> None:
    """
    Erstellt die erforderlichen Tabellen in einer MySQL/MariaDB-Datenbank.
    Benötigt das Paket `mysql-connector-python` (pip install mysql-connector-python).
    """
    try:
        import mysql.connector
    except Exception as exc:
        raise RuntimeError("mysql-connector-python required: pip install mysql-connector-python") from exc

    # Verbindung zur DB herstellen (DB muss existieren)
    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=database, port=port, autocommit=True
    )
    try:
        cur = conn.cursor()
        # Statements splitten und einzeln ausführen (multi=True kann je nach Connector-Version genutzt werden)
        for stmt in SERVER_SCHEMA_MYSQL.split(";"):
            s = stmt.strip()
            if not s:
                continue
            cur.execute(s)
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()
