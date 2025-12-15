
an die AI:
jede Sektion ausfüllen, Anweisungen in runden Klammern beachten


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

# RDM6300 / serielle Leser (optional)
pyserial>=3.5

# Hilfsbibliotheken
python-dateutil>=2.8


## Archtektur

Meine Anwendung ist eine Client-Server Installation, wobei der Server-Teil für den Betrieb nicht zwingen erforderlich ist. Er agiert sozusagen für die Sicherung der Daten des Client (RFID Terminal).

Auf dem Server kommt Python, Flask und MySQL zum Einsatz.

Das Terminal verwendet Python 
