#!/usr/bin/env python3
from flask import Flask, request, jsonify, abort
import os
try:
    import mysql.connector as mysql_connector
except Exception:
    mysql_connector = None
from datetime import datetime
from config.pin_config import load_shared_secret
from config.db_schema import init_mysql_db

SHARED_SECRET = load_shared_secret()

# MariaDB Verbindungskonfiguration (ENV)
DB_HOST = os.getenv("TIME_DB_HOST", "localhost")
DB_PORT = int(os.getenv("TIME_DB_PORT", "3306"))
DB_USER = os.getenv("TIME_DB_USER")
DB_PASSWORD = os.getenv("TIME_DB_PASSWORD")
DB_NAME = os.getenv("TIME_DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("Bitte TIME_DB_USER, TIME_DB_PASSWORD und TIME_DB_NAME als ENV setzen (MariaDB).")

if mysql_connector is None:
    raise RuntimeError("mysql-connector-python fehlt. Installieren: pip install mysql-connector-python")

# sicherstellen, dass Server-DB Tabellen vorhanden sind (MySQL)
init_mysql_db(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)

def get_conn():
    return mysql_connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)

app = Flask(__name__)

def check_secret(req):
    if not SHARED_SECRET:
        # development: accept if secret not set
        return True
    hdr = req.headers.get("X-Shared-Secret", "")
    return hdr == SHARED_SECRET

@app.route("/sync/events", methods=["POST"])
def sync_events():
    # Auth prüfen => 403 wenn ungültig
    if not check_secret(request):
        return jsonify({"error": "forbidden"}), 403

    # JSON-Body prüfen
    if not request.is_json:
        return jsonify({"error": "invalid payload, expected application/json"}), 502

    data = request.get_json() or {}
    events = data.get("events")
    if events is None or not isinstance(events, list):
        return jsonify({"error": "invalid payload, 'events' must be a list"}), 502

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        for ev in events:
            # einfache Validierung: Pflichtfelder prüfen
            if not isinstance(ev, dict):
                raise ValueError("each event must be an object")
            required = ("employee_id", "event_type", "timestamp")
            missing = [f for f in required if f not in ev]
            if missing:
                raise ValueError(f"missing fields in event: {missing}")

            cur.execute(
                "INSERT INTO server_events (remote_id, employee_id, event_type, start_time, end_time, timestamp, received_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (
                    ev.get("id"),
                    ev.get("employee_id"),
                    ev.get("event_type"),
                    ev.get("start_time"),
                    ev.get("end_time"),
                    ev.get("timestamp"),
                    datetime.utcnow().isoformat()
                )
            )
            inserted += 1
        conn.commit()
    except Exception as exc:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        # 502 wenn Auth ok, aber fehlerhafte Daten oder Speichern fehlgeschlagen
        return jsonify({"error": "failed to store events", "details": str(exc)}), 502
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    # 200 bei Erfolg
    return jsonify({"received": inserted}), 200

@app.route("/employees", methods=["GET","POST"])
def employees():
    if request.method == "GET":
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, rfuid_uid, role FROM server_employees")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "name": r[1], "rfuid_uid": r[2], "role": r[3]} for r in rows])

    # POST: require auth
    if not check_secret(request):
        abort(403)
    data = request.get_json() or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO server_employees (name, rfuid_uid, role, created_at) VALUES (%s,%s,%s,%s)",
        (data.get("name"), data.get("rfuid_uid"), data.get("role"), datetime.utcnow().isoformat())
    )
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    return jsonify({"id": nid}), 201

# Für Produktion: Set SHARED SECRET via ENV TIME_SHARED_SECRET or /etc/time_shared_secret.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
