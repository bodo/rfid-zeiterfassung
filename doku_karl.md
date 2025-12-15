Welche Teile in welche Kapitel/Anhänge

## Benutze Komponenten



gemeinsam Server/Client:
Flask >= 2.0. (Bibliothek zum Entwickeln von API/CRUD Anwendungen)
mysql-connector-python >= 8.0 (Bibliothek zum MySQL Zugriff)
python-dotenv >= 0.21.0 (Konfiguration mit ENV Variablen)
requests >= 2.26 (HTTP Protokol Bibliothek)

Server:
gunicorn >= 20.1.0  (eine HTTP Webserver Komponente)




Client:

# PN532 (Adafruit CircuitPython) [I2C/SPI]
adafruit-circuitpython-pn532 >= 2.0.0  (Bibliothek für den low-level HW-Zugriff auf den RFID Sensor)

# LCD 16x2 I2C (optional, z.B. RPLCD oder Adafruit-CharLCD)
RPLCD>=0.9

# Raspberry Pi GPIO libraries
RPi.GPIO>=0.7  # für bare-metal RPi; auf Nicht-RPi-Systemen ggf. weglassen
gpiozero>=1.6  # optional, höherer Abstraktionslayer


# Hilfsbibliotheken
python-dateutil>=2.8


## Archtektur

Meine Anwendung ist eine Client-Server Installation, wobei der Server-Teil für den Betrieb nicht zwingen erforderlich ist. Er agiert sozusagen für die Sicherung der Daten des Client (RFID Terminal).

Auf dem Server kommt Python, Flask und MySQL zum Einsatz.

Das Terminal verwendet Python und das Framework Flask.




## Dateien für Anhänge
ein paar Vorschläge im Format:
<Dateiname> - <Bildunterschrift>

### Entwickler Doku
INSTALL.md

hier muss die Formatierung von Markdown nach Word gemacht werden. Evtl. macht Word das auch autom bei Copy & Paste

### Benutzer Doku
README.md
Steffi: ggf. die Bereiche für Admins weg-kürzen?


## Code Beispiele
zeiterfassung.py — Hauptprogramm Terminal: Liest RFID, schreibt events, sync zum Server

zeitserver.py - Server, empfängt die Datensätze vom Terminal


benutzeradmin.py - CLI Programm zum Verwalten der Mitarbeiter (HR-Abteilung)


config/db_schema.py - DB Schema
plus zwei Scripte für die Ausführung auf Terminal (SQlite) und Server (MySQL):

dbmigration_client.py - Script zum Anlegen der DB auf dem Terminal
dbmigration_server.py - Script zum Anlegen der DB auf dem Server



Steffi: Start-Scripte und System Config, also für das Linux System, damit der Deamon autom beim Boot startet?

systemd/zeiterfassung.service - systemd Unit für das Terminal
systemd/zeitserver.service - systemd Unit für den Flask-Server


## Unittest Codes
Verzeichnis tests/

Vorschlag zum Übernehmen:
tests/terminal/test_benutzeradmin.py


## Screenshots
screenshot-terminal.png - SSH Screenshot der Terminal mit Konsolen-Ausgaben


## Lastenheft

## Auszug — Lastenheft (Knapp)

Zielsetzung
- Bereitstellung eines zuverlässigen Terminals zur Arbeitszeiterfassung mittels RFID (NTAG215).
- Lokale Speicherung der Ereignisse (clientseitig, SQLite) und sichere Synchronisation zu einem zentralen Server (MySQL) mit CRUD-API.
- Einfache Admin/HR-Tools zur Verwaltung von Mitarbeitern und Reporting.

Stakeholder
- Endnutzer: Mitarbeiter (Buchen Kommen/Gehen/Pausen/Externe Termine)
- HR/Admin: Verwaltung von Mitarbeiter-Tags, Reporting, Fehlerkorrektur
- Betrieb/DevOps: Installation und Betrieb auf Raspberry Pi (Terminal) und Debian-Server

Funktionale Kernanforderungen (hoch)
- Terminal liest RFID-UID (NTAG215) und erzeugt Events: work (Start/Ende), break (Start/Ende), extern (Start/Ende).
- Lokale DB mit synced-Flag; Hintergrund-Sync zu Server, Auth per Shared Secret.
- CLI-Tools: benutzeradmin zur Verwaltung (add/edit/delete/list), reports für Auswertungen.
- Server stellt Endpunkte zur Verfügung: /sync/events (POST), /employees (GET/POST), mit Validierung und Statuscodes (200/403/502).

Nicht‑funktionale Anforderungen (hoch)
- Offline-fähig: Terminal muss auch ohne Netzwerk arbeiten und später synchronisieren.
- Verfügbarkeit: Terminal startet als systemd-Service; Robustheit gegen DB/FS-Probleme.
- Sicherheit: Shared Secret (TIME_SHARED_SECRET) für API; Secrets nicht im Repo.
- Testbarkeit: Unittests für DB, CLI, Sync-Client und (mocked) Reader.

Rahmenbedingungen
- Hardware: Raspberry Pi 4, PN532 (SPI), LCD I2C, LEDs, Taster.
- Betriebssysteme: Raspberry Pi OS (Terminal), Debian (Server).
- Datenschutz: Speicherung minimaler personenbezogener Daten (Name, Tag UID); Logs begrenzen und Zugriffsrechte beachten.

## Auszug — Pflichtenheft (Knapp, technisch)

Architektur & Komponenten
- Terminal (Client)
  - Sprache: Python 3.8+
  - Hauptskripte: zeiterfassung.py (Daemon/CLI), benutzeradmin.py, reports.py, dbmigration_client.py
  - DB: SQLite file data/zeiterfassung.db; Schema wie in specs/01_general.md
  - Reader: PN532 via SPI; gelesene NTAG215 UID als HEX-String (z. B. "04A1B2C3") verwendet als rfuid_uid
  - GPIO: config/pin_config.py enthält BCM‑Pin‑Belegung
  - Service: systemd unit zeiterfassung.service, EnvironmentFile /etc/tjp_env (TIME_SHARED_SECRET)

- Server
  - Sprache: Python (Flask)
  - API:
    - POST /sync/events
      - Auth: Header X-Shared-Secret == TIME_SHARED_SECRET
      - Payload: {"events": [ { "id": <local_id>, "employee_id": <int>, "event_type":"work|break|extern", "start_time": ISO, "end_time": ISO, "timestamp": ISO } , ... ]}
      - Responses: 200 OK {received:n}, 403 Forbidden (auth), 502 Bad Gateway (payload/DB error)
    - GET /employees
    - POST /employees (auth required)
  - DB: MySQL/MariaDB (ENV: TIME_DB_HOST/PORT/USER/PASSWORD/NAME), Schema wie config/db_schema.SERVER_SCHEMA_MYSQL
  - Service: systemd unit zeitserver.service or gunicorn behind nginx

Datenmodell / Validierung
- events.event_type ∈ {'work','break','extern'}
- events.start_time, events.timestamp ISO8601; end_time optional (Pflege: Updaten beim Ausbuchen) — in der finalen Implementierung kann end_time NULL erlauben oder initial gleich start_time setzen; Schema/Code sind konsistent zu halten.
- employees.rfuid_uid gespeichert als Großbuchstaben HEX ohne Trennzeichen; eindeutiger Lookup: SELECT id FROM employees WHERE rfuid_uid = ?

Reader / Verhalten beim Lesen
- PN532 via SPI betreiben; read_passive_target liefert Bytes → konvertiere zu HEX-String (big-endian) und normalisiere (z.B. upper()).
- Entprellung: nach erfolgreichem Lesen kurze Blockierzeit (z. B. 1s) um Doppeleinträge zu vermeiden.
- Wenn Tag unbekannt: LED/Blinkcode rot (3x), Log-Eintrag category='error', Zeigt Hinweis auf LCD: "Unbekannter Tag — Admin".

Sync‑Client (Terminal)
- Hintergrund-Job prüft periodisch (configurable) unsynced Events (synced=0) und sendet in Batches an /sync/events.
- Fehlerbehandlung:
  - 200 → markiere lokale Einträge synced=1
  - 502 → retry mit exponentiellem Backoff (konfigurierbar)
  - 403 → Log und Alarm (konfigurierbar), keine Retries bis Secret/Config geprüft
- Logging: High‑level Logs auf Konsole/Journal; detaillierte Einträge in logs‑Tabelle.

Admin/HR-CLI
- benutzeradmin.py: interaktive Eingabe, prüft Rolle ∈ {'employee','hr','boss','admin'}, registriert vorgelesene UID beim Add-Vorgang.
- reports.py: CLI mit Auswahl; generiert list, last X days, fehlerhafte Buchungen (missing end_time, overlapping, multiple starts).

Betrieb & Deployment
- Secrets: TIME_SHARED_SECRET in /etc/tjp_env (root:root, 600) oder /etc/time_shared_secret; nie im Repo.
- systemd Units müssen WorkingDirectory und ExecStart auf /opt/zeiterfassung/{terminal|server} zeigen.
- Backups: SQLite‑Snapshot vor Updates; MySQL‑Backups via regulärem Backup-Prozess.
- Monitoring/Health: zeitserver expose /health (optional) und einfache Zählung unsynced events (für Alerts).

Test & Qualität
- Unittests abdecken: DB Migration/Schema, insert/find/update flows, benutzeradmin flows (mock DB), sync-client logic (requests gemockt), PN532 Reader mittels FakeReader.
- CI: pytest in pipeline; Lint (flake8) optional; Integrationstest mit temporärer SQLite DB und Flask TestClient.

Anmerkungen / offene Punkte zur Umsetzung
- Entscheidung: end_time NULL zulassen oder sofort setzen? Empfehlung: end_time NULL beim Start, update beim Ende → bessere Modellierung. Falls Schema NOT NULL bleibt, implementiere Update‑Flow oder setze end_time=start_time als Platzhalter.
- Zeitstempel: intern UTC; für UI/Reporting in lokale Zeit konvertieren.
- Datenschutz/Retention: Frist festlegen (z. B. 2 Jahre) und in Betriebskonzept aufnehmen.


## Pflichtenheft

