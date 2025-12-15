# INSTALLATION (Admin)

Wichtig: Secrets nicht ins Repo committen. Alle Befehle als Nutzer mit passenden Rechten ausführen.

## 1. Voraussetzungen (Raspberry Pi)
- Raspberry Pi OS (aktuell)
- Python 3.8+
- Optional: I2C, SPI aktivieren (raspi-config)
- Pakete:
  - sudo apt update && sudo apt install -y python3 python3-venv python3-pip git i2c-tools

## 2. Projekt auschecken
cd /opt
sudo git clone <repo-url> zeiterfassung
cd zeiterfassung

## 3. Virtuelle Umgebung und Abhängigkeiten
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Abhängigkeiten (Laufzeit)
pip install -r requirements.txt

# Dev-Abhängigkeiten (Tests / Lint)
# optional: pip install -r requirements-dev.txt

# Hinweise zu Hardware‑Paketen:
# - Für PN532 per I2C/SPI: `adafruit-circuitpython-pn532` (in requirements.txt als optional markiert)
# - Für RPi GPIO auf dem Pi: `RPi.GPIO` oder `gpiozero` (nur auf dem Pi installieren)
# - Bei Bedarf für serielle Schnittstellen: `pyserial` (nur falls ein serieller Leser verwendet wird; im Projekt ist PN532 vorgesehen)
# Wenn Du auf einem Nicht‑RPi entwickelst, kannst Du die optionalen Pakete weglassen oder in einer separaten Umgebung installieren)

## 4. Shared Secret konfigurieren
Produktion: lege `/etc/time_shared_secret` an (nur root lesbar)
sudo sh -c 'echo "MEIN_SECURE_SECRET" > /etc/time_shared_secret'
sudo chmod 600 /etc/time_shared_secret

Entwicklung: oder setze ENV:
export TIME_SHARED_SECRET="MEIN_SECURE_SECRET"

## 5. DB Migration (Client & Server)
# Client-DB erstellen
python3 dbmigration_client.py
# Server-DB erstellen (lokal oder remote DB-Setup)
python3 dbmigration_server.py

Dateien:
- data/zeiterfassung.db  (Client)
- data/zeitserver.db     (Testserver)

## 6. Dienste / Start

# Systemd (Beispiel für zeiterfassung daemon auf Pi)
sudo tee /etc/systemd/system/zeiterfassung.service > /dev/null <<'EOF'
[Unit]
Description=TJP Zeiterfassung Daemon
After=network.target

[Service]
User=pi
WorkingDirectory=/opt/zeiterfassung/terminal
EnvironmentFile=/etc/tjp_env
ExecStart=/opt/zeiterfassung/terminal/.venv/bin/python3 /opt/zeiterfassung/terminal/zeiterfassung_launcher.py --real-reader
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now zeiterfassung.service

## 6.1 Systemd Unit-Files aus dem Projekt installieren
Im Projekt sind Beispiel-Unit-Files unter `systemd/` abgelegt:

1. Kopieren der Unit-Files nach /etc/systemd/system (als root):
   sudo cp systemd/zeiterfassung.service /etc/systemd/system/
   sudo cp systemd/zeitserver.service /etc/systemd/system/

2. Optional: EnvironmentFile verwenden (empfohlen für Secrets)
   Erstelle `/etc/tjp_env` mit:
     TJP_SHARED_SECRET=MEIN_SECURE_SECRET
   Setze in der Unit `EnvironmentFile=/etc/tjp_env` (oder verwende /etc/time_shared_secret wie weiter oben beschrieben).

3. Systemd neu laden und Dienste aktivieren:
   sudo systemctl daemon-reload
   sudo systemctl enable --now zeiterfassung.service
   sudo systemctl enable --now zeitserver.service

4. Logs ansehen:
   sudo journalctl -u zeiterfassung.service -f
   sudo journalctl -u zeitserver.service -f

Hinweis: Passe `User` und `ExecStart` in den Unit-Files an Deine Umgebung an (z.B. Pfad zur venv).

## 7. Server Deployment (Debian)

Die Server-Komponente läuft unter Debian/Linux und verwendet MySQL/MariaDB. Kurzanleitung für einen Debian-Host:

1) Systempakete & MariaDB installieren
```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mariadb-server
```

2) MariaDB absichern (interaktiv)
```sh
sudo mysql_secure_installation
```

3) Datenbank und Benutzer anlegen (ersetze PASS/DB/USER)
```sh
sudo mysql -e "CREATE DATABASE time_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
sudo mysql -e "CREATE USER 'time_user'@'localhost' IDENTIFIED BY 'secure_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON time_db.* TO 'time_user'@'localhost'; FLUSH PRIVILEGES;"
```
Hinweis: Falls der Server remote erreichbar sein soll, passe Host‑Angaben und GRANT entsprechend an.

4) Python MySQL‑Connector installieren (im virtualenv)
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install flask requests mysql-connector-python
```

5) ENV‑Variablen setzen (empfohlen: EnvironmentFile `/etc/tjp_env`)
Erstelle `/etc/tjp_env` (root, chmod 600) mit:
```
TIME_DB_HOST=localhost
TIME_DB_PORT=3306
TIME_DB_USER=time_user
TIME_DB_PASSWORD=secure_password
TIME_DB_NAME=time_db
TIME_SHARED_SECRET=ÄNDERE_DAS_SECRET
```
Setze Dateirechte:
```sh
sudo chown root:root /etc/tjp_env
sudo chmod 600 /etc/tjp_env
```

6) DB‑Migration ausführen (legt Tabellen in MariaDB an)
```sh
source .venv/bin/activate
python3 dbmigration_server.py
```

7) Systemd Unit für zeitserver (Beispiel) — EnvironmentFile nutzen
Kopiere `systemd/zeitserver.service` nach `/etc/systemd/system/` und passe an oder erstelle folgende Unit (als root):
```ini
[Unit]
Description=TJP Zeitserver
After=network.target

[Service]
WorkingDirectory=/opt/zeiterfassung/server
User=www-data
EnvironmentFile=/etc/tjp_env
ExecStart=/opt/zeiterfassung/server/.venv/bin/python3 /opt/zeiterfassung/server/zeitserver_launcher.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
Dann:
```sh
sudo systemctl daemon-reload
sudo systemctl enable --now zeitserver.service
sudo journalctl -u zeitserver.service -f
```

8) Firewall (optional)
Wenn UFW verwendet wird, Port 5000 (oder WSGI/HTTP-Proxy) erlauben:
```sh
sudo ufw allow 5000/tcp
sudo ufw enable
```

9) Produktionsempfehlung
- Verwende für Produktion einen WSGI‑Server (gunicorn) + Reverse‑Proxy (nginx) vor Flask.
- Setze TIME_SHARED_SECRET sicher (EnvironmentFile oder Secret-Manager) und niemals im Repo.
- Sorgfältige Backups / Monitoring der MariaDB.

## 8. Troubleshooting
- Fehler: Keine RFID-UID erkannt -> Prüfe PN532-Verkabelung und SPI/I2C-Settings.
- DB: Schema fehlt -> dbmigration_client.py ausführen.
- Sync Probleme -> Prüfe Netzwerk, Shared Secret, server-Logs (zeitserver.py).
- Filesystem-Volles -> Überprüfe `df -h` und Berechtigungen.

## 9. Weiteres
- Unittests: Tests in tests/ (noch nicht enthalten) ausführen mit pytest.
- Produktion: Secrets in Vault/Ansible hinterlegen, systemd Service unit mit Restart/Logging, Rotations für Logs.

## 10. Pinout / Verdrahtung (BCM)

Hinweis: Alle GPIO‑Nummern unten sind im BCM‑Layout angegeben. Vor dem Löten oder Verdrahten bitte Pinbelegung des konkreten Raspi‑Modells prüfen.

- Strom / GND
  - 3.3V: Pin 1 (oder Pin 17)
  - GND: z.B. Pin 6

- PN532 (empfohlen: SPI, damit I2C für LCD frei bleibt)
  - VCC -> 3.3V
  - GND -> GND
  - MOSI -> GPIO10 (BCM 10, SPI0 MOSI)
  - MISO -> GPIO9  (BCM 9, SPI0 MISO)
  - SCLK -> GPIO11 (BCM 11, SPI0 SCLK)
  - SS/CE -> GPIO8 (BCM 8, SPI0 CE0)
  - RSTO (optional) -> GPIO24 (BCM 24)
  - IRQ (optional) -> GPIO25 (BCM 25)

- LCD 16x2 mit I2C‑Adapter
  - SDA -> GPIO2 (BCM 2, SDA1)
  - SCL -> GPIO3 (BCM 3, SCL1)
  - I2C‑Adresse: meist 0x27 (prüfen)

- LEDs (mit Vorwiderständen 220–330 Ω)
  - "Bereit" (Dual‑Color)
    - GRÜN -> GPIO17 (BCM 17)
    - ROT   -> GPIO27 (BCM 27)
    - Hinweis: bei common‑anode invertierte Logik beachten
  - "Kommen" (grün) -> GPIO22 (BCM 22)
  - "Gehen"   (rot) -> GPIO23 (BCM 23)

- Taster (Taster gegen 3.3V, interne Pull‑Down empfohlen, entprellen softwareseitig)
  - INFO       -> GPIO5  (BCM 5)
  - KOMMEN     -> GPIO6  (BCM 6)
  - GEHEN      -> GPIO13 (BCM 13)
  - EXT_TERMIN -> GPIO19 (BCM 19)

- Hinweise / Schutz
  - LED‑Vorwiderstände: 220–330 Ω
  - Keine Pegelwandler nötig (3.3V)
  - Lange Leitungen: Abschirmung / RC‑Entprellung erwägen
  - Beim Einsatz von I2C/SPI: Interfaces in raspi‑config aktivieren

# INSTALLATION (Komponenten)

## Projektstruktur (neu)
Das Projekt ist in zwei Komponenten aufgeteilt:
- server/ — alle serverseitigen Skripte (Flask + MySQL)
- terminal/ — alle Terminal‑/Pi‑Skripte (RFID Reader, CLI)
Geteilter Code (config/, specs/, data/, tests/ Konfig) bleibt im Projekt‑Root.

## Installation: Abhängigkeiten pro Komponente
Wir empfehlen für Entwicklung/Deployment pro Komponente eine eigene virtuelle Umgebung oder eine gemeinsame Umgebung mit den kombinierten requirements.

### Terminal (Raspberry Pi)
Im Terminal‑Verzeichnis sind die laufzeitrelevanten Abhängigkeiten:
```sh
cd /opt/zeiterfassung/terminal
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
Starten (zum Testen / Entwicklung):
```sh
python3 zeiterfassung_launcher.py
```

### Server (Debian)
Im Server‑Verzeichnis sind die serverseitigen Abhängigkeiten:
```sh
cd /opt/zeiterfassung/server
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
DB‑Migration und Start:
```sh
python3 dbmigration_server.py
python3 zeitserver_launcher.py
```

## Schnell-Install: Befehle (Terminal & Server)

# Terminal (Raspberry Pi) — aus dem geklonten Projekt root ausführen
```sh
# filepath: /opt/zeiterfassung/terminal-install.sh
# Annahme: Repo wurde nach /opt/zeiterfassung geklont und wir arbeiten im Projekt-Root
cd /opt/zeiterfassung

# 1) Kopiere Terminal‑Komponenten in das finale Terminal‑Verzeichnis
sudo mkdir -p /opt/zeiterfassung/terminal
sudo rsync -a --delete terminal/ /opt/zeiterfassung/terminal/

# 2) Erstelle Virtualenv und installiere Laufzeit‑Abhängigkeiten
cd /opt/zeiterfassung/terminal
python3 -m venv .venv
# shellcheck disable=SC1090
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3) Installiere systemd‑Unit (falls gewünscht) und starte Dienst
sudo cp systemd/zeiterfassung.service /etc/systemd/system/zeiterfassung.service
sudo systemctl daemon-reload
sudo systemctl enable --now zeiterfassung.service

# Hinweis: Passe /etc/tjp_env oder /etc/time_shared_secret vor dem Start an.
```

# Server (Debian) — aus dem geklonten Projekt root ausführen
```sh
# filepath: /opt/zeiterfassung/server-install.sh
# Annahme: Repo wurde nach /opt/zeiterfassung geklont und wir arbeiten im Projekt-Root
cd /opt/zeiterfassung

# 1) Kopiere Server‑Komponenten in das finale Server‑Verzeichnis
sudo mkdir -p /opt/zeiterfassung/server
sudo rsync -a --delete server/ /opt/zeiterfassung/server/

# 2) Erstelle Virtualenv und installiere Laufzeit‑Abhängigkeiten
cd /opt/zeiterfassung/server
python3 -m venv .venv
# shellcheck disable=SC1090
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3) Bereite ENV/Secrets vor (z.B. /etc/tjp_env), dann systemd Unit installieren
# Erstelle /etc/tjp_env mit TIME_DB_* und TIME_SHARED_SECRET (root, chmod 600)
sudo cp systemd/zeitserver.service /etc/systemd/system/zeitserver.service
sudo systemctl daemon-reload
sudo systemctl enable --now zeitserver.service

# Hinweis: Für Produktion gunicorn + nginx vorziehen; prüfe Logs via journalctl.
```
