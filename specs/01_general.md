# Projektübersicht

Es soll eine Arbeitszeiterfassung in der Datei raspberry_pi_rfid_sync_service.py programmiert werden
Mit RFID Tags kann sich ein Mitarbeiter ein- und ausbuchen,
Pausen beginnen und beenden.

Dokumentation zum Projekt liegt in der Dtaei specs/

## Architektur

Das Terminal besteht aus einem Raspberry Pi mit RFID Sensor.
Das Terminal nutzt eine lokale SQlite Datenbank und synchronisiert die Daten dann mit einem Server mit CRUD Backend, wo sie in einer MySQL/MariaDB gespeichert werden.


## Hardware Terminal

- Raspberry Pi 4
- RFID Sensor, Typ PN 532, angeschlossen am GPIO des Raspi
- LEDs
    - "Bereit" (dual color, rot, grün und orange als Mischfarbe): dauer an in grün, wenn eingeschaltet und die Software läuft (wird bei beenden ausgeschaltet)
    - "Kommen" (grün): wenn eine Kommen-Zeit erkannt wurde
    - "Gehen" (rot): wenn eine Gehen-Zeit registriert wurde
- LCD 16x2 mit I2C Adapter
- Buttons
    - "Info"
    - "Kommen" zum Einbuchen
    - "Gehen" zum Ausbuchen
    - "ext Termin" zum Gehen/Kommen zu/von einem Termin ausser Haus

## Software Terminal

- Raspberry Pi OS
- Python für die Terminal-Software
- Datei: zeiterfassung.py für die Hauptanwendung
- Datei: benutzeradmin.py als interaktive CLI Anwendung
- Datei: reports.py als CLI mit Auswahl des Reports per CLI Arg
- Datei: dbmigration_client.py als CLI welches die DB Struktur anlegt

## Software Server

- Debian Linux
- Python Flask Backend
- MySQL
- Datei: zeitserver.py
- Datei: dbmigration_server.py als CLI welches die DB Struktur in der MySQL/MariaDB anlegt
- Hinweis: zeitserver.py verbindet sich mit der MySQL/MariaDB per ENV:
  - TIME_DB_HOST, TIME_DB_PORT, TIME_DB_USER, TIME_DB_PASSWORD, TIME_DB_NAME
  - dbmigration_server.py nutzt dieselben ENV-Variablen zur Initialisierung



## DB Schema

```sql
-- Korrigiertes DB-Schema für lokale SQLite-Datenbank

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    event_type VARCHAR(16) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    timestamp DATETIME NOT NULL,
    synced INTEGER DEFAULT 0,
    CHECK (event_type IN ('work', 'break', 'extern'))
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
```


## Funktionsweise

- Das Terminal wartet darauf, dass ein RFID Tag präsentiert wird.
- Die UID des Tag wird in die lokale DB geschrieben, markiert als synced=0.
- Wenn eine Internet-Verbindung besteht, dann wird überprüft, ob in der lokalen SQlite Einträge vorhanden sind, die noch nicht synchronisiert sind (also mit synced=0). Diese werden dann einzeln an den Server gesendet und lokal als synchronisiert markiert.
- eine dual Color LED (rot, grün und Mischfarbe also orange) an zwei GPIO Pins zeigt den Verarbeitungszustand an.
    - "Bereit", grün dauerleuchten, wenn das Terminal zum Einlesen eines Tags bereit ist
    - "Bereit" 3x blinken rot, wenn das Einlesen eines Tags fehlgeschlagen ist oder wenn der Tag nicht bekannt ist (nicht in der employee DB vorhanden)
    - "Bereit" 3x blinken in grün, wenn der Tag gelesen werden konnte, bekannt ist und in der lokalen DB abgespeichert wurde
    - "Bereit" rot dauerleuchten, wenn der Leser nicht bereit ist (z.B. weil eine lange laufende Synchronisation nach langer offline Phase gerade läuft, wenn das Filesystem voll ist und keine Daten geschrieben werden können, wenn die SQlite DB nicht reagiert usw.)
- wenn ein RFID Tag gezeigt wird
    - wenn dies die erste Buchung am Tag ist, also eindeutig eine Einbuchung am Morgen ist, wird eingebucht
    - wenn am gleichen Tag, vorher schon eingebucht wurde und die Einbuchen Taste gedruckt wurde, wird die zweite Einbuchen-Zeit ignoriert
    - wenn der Mitarbeiter am aktuellen Tag schon eingebucht ist, wird ausgebucht (wenn keine Taste gedrückt oder Taste "gehen")
    - wenn der Mitarbeiter am aktuellen Tag eingebucht ist und die Taste "ext Termin" drückt, dann arbeitet er weiter aber geht zu einem externen Termin, es zählt als Arbeitszeit, die Buchung ist ein "start_ext"
    - wenn der Mitarbeiter am gleichen Tag vom ext Termin zurück kommt und seinen RFID zeigt, wird "end_ext" aktualisiert
    - die "Gehen" und "Kommen" Tasten werden analog für Pausen (Start/Ende) verwendet

## CLI Befehle am Terminal

Wir brauchen ausserdem eine CLI Anwendung für den Pi um neue Admin/HR/Boss Tags in die DB zu verwalten.
Dazu wird interaktiv um den Namen, die Auswahl der Rolle als Auswahl (siehe DB-Schema oben) gebeten. Danach soll ein RFID Tag am Sensor präsentiert werden, der dann mit den eingegeben Daten in der DB Tabelle abgelegt wird.
Die Eingabe soll eine einfache Überprüfung falscher Eingaben bieten.

Auch das Löschen und Editieren von Angestellten muss möglich sein.

Ein weiteres CLI Programm dient zum Reporting, also Auflisten bestimmter Datensätze:
- alle Angestellten
- die letzten x Arbeitstage inkl. Pausen eines Angestellten, inkl. Summe pro Woche/Monat/Jahr (und Abweichung von den Soll-Stunden)
- Fehlerhafte Buchungen, z.B.
    - Wenn Mitarbeiter an Arbeitstagen vergessen haben sich auszubuchen
    - Wenn Mitarbeiter vergessen haben sich einzubuchen (beim Ausbuchen)
    - Wenn Mitarbeiter vergessen haben sich auszubuchen (beim Einbuchen am nächsten Morgen)
    - Wenn Mitarbeiter keine Pause an einem Arbeitstag gebucht haben. (mehrere Pausen sind OK, z.B. gewissenhafte Mitarbeiter die oft rauchen gehen)



## weitere Anforderungen

schreibe in diese Datei Informationen zur Verdrahtung am GPIO des Raspi (LEDs, Taster, RFID Reader Sensor), Widerstände usw.
Wähle passende Pins mit entsprechender Funktion. Lege die Pin-Belegung in einer extra Config Datei ab, die von den diversen Programmen geteilt wird.
Verwende ein shared Secret für den Zugriff auf die API.

Die Anwendung voll mit Unittest abgedeckt sein.

Versuche Code zwischen dbmigration_client.py und dbmigration_server.py zu teilen, ggf. ein separates Modul, dass von beiden eingebunden wird.

Die Synchronisierung der Einträge über die API sollte einen Status Code zurück senden:
- 200 wenn Auth stimmt und Eintrag übernommen und gespeichert wurde
- 403 wenn Auth fehlerhaft
- 502 wenn Auth ok aber fehlerhafte Daten oder Fehler beim Speichern


Schreibe und aktualisiere Dokumentationen:
INSTALL.md für den Admin
README.md für den Endnutzer, also wie man das Terminal benutzt, ein Extra Kapitel für Admins und HR

erstelle zwei systemd Scripte, je eines für zeiterfassung.py und zeitserver.py. 

Die Anwendung zeiterfassung.py soll auf der Konsole high-level Log Meldungen ausgeben. In der Art:
09:00 Mitarbeiter "Karl" ("RFID UID") kommt
12:00 Mitarbeiter "Karl" ("RFID UID") Pause Start
12:15 Mitarbeiter "Max" ("RFID UID") ext Termin Start
13:00 Mitarbeiter "Karl" ("RFID UID") Pause Start
15:15 Mitarbeiter "Max" ("RFID UID") ext Termin Ende
16:30 Mitarbeiter "Karl" ("RFID UID") geht
17:00 Mitarbeiter "Karl" ("RFID UID") geht korrigiert

## Projektstruktur (neues Layout)

Das Projekt ist in zwei Hauptkomponenten strukturiert:

- terminal/
  - zeiterfassung_launcher.py  # Launcher für die Terminal‑Anwendung (importiert Hauptlogik aus Root)
  - benutzeradmin.py           # CLI (kann auch im Root liegen, Launcher importiert)
  - reports.py
  - dbmigration_client.py
  - requirements.txt           # Laufzeit-Abhängigkeiten für die Terminal-Komponente

- server/
  - zeitserver_launcher.py     # Launcher für den Flask‑Server (importiert Hauptlogik aus Root)
  - dbmigration_server.py
  - requirements.txt           # Laufzeit-Abhängigkeiten für die Server-Komponente

- config/
- data/
- specs/
- tests/
  - server/
  - terminal/

Hinweis: Shared-Code (z.B. config/db_schema.py, config/pin_config.py) bleibt im Projekt‑Root und wird von beiden Komponenten verwendet. Die Launchers erleichtern das Starten/Deployment und behalten die Module zentral.

## Verdrahtung / GPIO (Empfehlung, BCM-Nummern)

Hinweis: Alle angegebenen GPIO-Nummern sind im BCM-Layout.

- Strom/GND
  - 3.3V: Pin 1 (oder Pin 17) -> alle 3.3V-Versorgungen
  - GND: z.B. Pin 6 -> gemeinsamer Masseanschluss

- RFID Reader PN532 (SPI, empfohlen, damit I2C für das LCD verfügbar bleibt)
  - VCC -> 3.3V
  - GND -> GND
  - MOSI -> GPIO10 (BCM 10, SPI0 MOSI)
  - MISO -> GPIO9  (BCM 9, SPI0 MISO)
  - SCLK -> GPIO11 (BCM 11, SPI0 SCLK)
  - SS/CE -> GPIO8 (BCM 8, SPI0 CE0)
  - RSTO (falls vorhanden) -> GPIO24 (BCM 24)
  - IRQ (optional) -> GPIO25 (BCM 25)

- LCD 16x2 mit I2C-Adapter
  - SDA -> GPIO2 (BCM 2, SDA1)
  - SCL -> GPIO3 (BCM 3, SCL1)
  - I2C-Adresse: üblicherweise 0x27 (prüfen)

- LEDs (mit Vorwiderständen 220–330 Ω)
  - "Bereit" (Dual-Color, Grün/Rot)
    - GRÜN -> GPIO17 (BCM 17)
    - ROT   -> GPIO27 (BCM 27)
    - Hinweis: Wenn Dual-Color als common-anode ausgeführt ist, invertierte Logik verwenden (siehe config)
  - "Kommen" (grün) -> GPIO22 (BCM 22)
  - "Gehen"   (rot) -> GPIO23 (BCM 23)

- Taster (mit internen Pull-Down, Taster gegen 3.3V schalten)
  - INFO       -> GPIO5  (BCM 5)
  - KOMMEN     -> GPIO6  (BCM 6)
  - GEHEN      -> GPIO13 (BCM 13)
  - EXT_TERMIN -> GPIO19 (BCM 19)
  - Hinweis: Taster an 3.3V, auf GPIO internen pull_down=True verwenden, entprellen softwareseitig

- Widerstände / Schutz
  - LED-Vorwiderstände: 220–330 Ω für jede LED-Farbe
  - Keine Pegelwandler nötig (alles 3.3V)
  - Für lange Leitungen Abschirmung und ggf. RC-Entprellung erwägen

## Konfigurationsdatei / gemeinsame Pin-Definition

Alle Programme (RFID-Daemon, CLI-Tools, Tests) sollen die gemeinsame Datei
config/pin_config.py verwenden, damit Pinbelegung zentral verwaltet wird.
Diese Datei lädt auch das Shared Secret (aus ENV oder Datei) für API-Zugriffe.

Pfad: config/pin_config.py

## Shared Secret / API Zugriff

- Produktion: Das Shared Secret darf nicht im Repo liegen. Entweder als System-ENV (z.B. IHK_SHARED_SECRET) oder als Datei mit restriktiven Rechten (/etc/ihk_shared_secret) hinterlegen.
- Lokale Entwicklung: config/secrets.example.env liegt bei und zeigt das Format.

## Dependencies / Requirements

Das Projekt verwendet komponentenspezifische requirements-Dateien:

- terminal/requirements.txt
  - Laufzeit (Terminal/Pi): requests, python-dateutil
  - Hardware-spezifisch (nur auf Raspberry Pi): RPi.GPIO oder gpiozero, adafruit-circuitpython-pn532 (PN532), RPLCD (I2C LCD), pyserial (serielle Leser)
  - Installation (auf Pi):
    - python3 -m venv .venv && source .venv/bin/activate
    - pip install -r terminal/requirements.txt
  - Systempakete (via apt) ggf. vorher installieren: i2c-tools, libgpiod, build-essential, python3-dev

- server/requirements.txt
  - Laufzeit (Server): Flask, mysql-connector-python, python-dotenv, requests, gunicorn
  - Optional: prometheus-client für Monitoring
  - Installation (Debian):
    - python3 -m venv .venv && source .venv/bin/activate
    - pip install -r server/requirements.txt
  - Systempakete: mariadb-server (oder MySQL), libmysqlclient-dev falls nötig

- requirements-dev.txt (Projekt-Root)
  - Dev/CI: pytest, coverage, flake8, mypy
  - Installation:
    - pip install -r requirements-dev.txt

Hinweise:
- Auf getrennter Hardware (Pi vs. Server) nur die jeweils relevanten Pakete installieren.
- Für Produktionsdeployments empfehlen wir, Versionen zu pinnen und ein Lockfile (pip‑freeze / pip‑compile) zu verwenden.
- Die Launchers (terminal/zeiterfassung_launcher.py und server/zeitserver_launcher.py) verwenden die shared modules im Projektroot; pip-Install im jeweiligen Component-Ordner installieren, damit .venv Pfade konsistent sind.
