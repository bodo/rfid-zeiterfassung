



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