# Zeiterfassung Terminal — Kurzanleitung

Dieses Projekt implementiert ein Raspberry Pi Terminal zur Arbeitszeiterfassung mit RFID.

## Für Endnutzer (Mitarbeiter)
- Terminal einschalten: Dual-Color LED "Bereit" leuchtet grün.
- RFID präsentieren: UID vor den Leser halten.
  - Bei erfolgreichem Erkennen: "Bereit" blinkt grün (3x) und "Kommen"/"Gehen" LED zeigt jeweilige Aktion.
  - Bei unbekanntem Tag: "Bereit" blinkt rot (3x).
- Tasten:
  - Info: Kurzinformation auf LCD (optional).
  - Kommen: Verwenden, um eine Einbuchung zu erzwingen/adjustieren.
  - Gehen: Verwenden zum Ausbuchen.
  - ext Termin: Start/Ende eines externen Termins (start_ext / end_ext).
- Verhalten:
  - Erste Buchung des Tages => Einbuchung (start_work).
  - Wenn bereits eingebucht => Ausbuchung (end_work).
  - Pausen analog mit Kommen/Gehen-Tasten (start_break/end_break).
  - Externe Termine bleiben Arbeitszeit, werden als start_ext/end_ext markiert.

## Admin / HR (Kurz)
- Mitarbeiter verwalten:
  - `python3 benutzeradmin.py` — interaktive CLI: add/edit/delete/list.
- Reports:
  - `python3 reports.py` — interaktiv: Mitarbeiterliste, letzte X Tage Events.
- DB-Migration:
  - `python3 dbmigration_client.py` (auf Pi)
  - `python3 dbmigration_server.py` (Server / Testserver)
- Synchronisation:
  - Das Terminal schreibt lokal in data/zeiterfassung.db (synced=0).
  - Ein Sync an den Server sendet events; Server antwortet:
    - 200 = Erfolg
    - 403 = Auth fehlgeschlagen
    - 502 = Auth ok aber fehlerhafte Daten oder Speichern fehlgeschlagen
- Shared Secret:
  - Wird über ENV TIME_SHARED_SECRET oder Datei `/etc/time_shared_secret` geladen.

### Systemd Services
Das Projekt enthält Beispiel-Units unter `systemd/`:

- `systemd/zeiterfassung.service` — Unit für das Pi‑Daemon (zeiterfassung.py)
- `systemd/zeitserver.service` — Unit für den Flask‑Demo‑Server (zeitserver.py)

Installation:
1. Kopiere die Units nach `/etc/systemd/system/`
2. Passe `User` und `ExecStart` an (Pfad zur virtualenv)
3. `sudo systemctl daemon-reload && sudo systemctl enable --now zeiterfassung.service`
4. Logs: `sudo journalctl -u zeiterfassung.service -f`

Hinweis: Secrets nicht in Unit-Files einbetten — verwende `EnvironmentFile` oder `/etc/ihk_shared_secret`.

### Konsolen-Logging / Beispiele
zeiterfassung.py gibt High-Level-Logs auf die Konsole / ins Journal aus (Beispiele):

09:00 Mitarbeiter "Karl" ("RFID_UID_123") kommt
12:00 Mitarbeiter "Karl" ("RFID_UID_123") Pause Start
12:15 Mitarbeiter "Max" ("RFID_UID_456") ext Termin Start
13:00 Mitarbeiter "Karl" ("RFID_UID_123") Pause Ende
15:15 Mitarbeiter "Max" ("RFID_UID_456") ext Termin Ende
16:30 Mitarbeiter "Karl" ("RFID_UID_123") geht
17:00 Mitarbeiter "Karl" ("RFID_UID_123") geht korrigiert

Diese Meldungen erleichtern das Monitoring per `journalctl` oder in der Konsole.

## Dateien Überblick
- zeiterfassung.py — Hauptprogramm (Daemon/CLI). Liest RFID, schreibt events.
- benutzeradmin.py — CLI zur Verwaltung von employees.
- reports.py — CLI für Reports.
- dbmigration_client.py / dbmigration_server.py — DB initialisieren.
- zeitserver.py — einfacher Flask-Demo-Server (Test/Integration).
- config/pin_config.py — zentrale Pin-Definitionen und Secret-Loader.
- data/*.db — SQLite DB-Dateien (lokal/test).

## Troubleshooting / FAQ
- LED bleibt rot (dauer): lange Sync/DB-Fehler oder Reader nicht bereit — prüfen Logs in data/ oder systemd journal.
- Tag wird nicht erkannt: UID prüfen, Reader-Verkabelung und SPI/I2C Einstellung prüfen.
- Server-Antwort 403: Shared Secret stimmt nicht.
- Server-Antwort 502: Prüfe Payload, Zeitstempel-Formate und Server-Logs.

## Kontakt / Weiteres
Für Anpassungen (andere Pinbelegung, MySQL-Backend) siehe `config/pin_config.py` und `config/db_schema.py`.

## Installation / Schnellstart
Kopiere das Repo nach /opt/zeiterfassung, dann installiere die Abhängigkeiten pro Komponente:

- Terminal:
  cd /opt/zeiterfassung/terminal
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python3 zeiterfassung_launcher.py

- Server:
  cd /opt/zeiterfassung/server
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python3 zeitserver_launcher.py
