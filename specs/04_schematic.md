# Schaltplan (übersichtlich) — gesamter Aufbau

Dieses Dokument enthält einen einfachen, überprüfbaren Schaltplan als Block‑/ASCII‑Diagramm, eine Signal‑/Verdrahtungstabelle sowie eine kurze Testcheckliste für Inbetriebnahme. Ziel ist, Elektroniker und Mechaniker eine klare Anschlussübersicht bereitzustellen.

Hinweis: Außen = GND an der Hohlbuchse; Innen = +Vin (Center positive). Externer Eingang: 6–12 V DC.

----

ASCII/Block‑Diagramm

  [Externes Netzteil 6-12V]
               |
        (Barrel jack: Außen=GND, Innen=+Vin)
               |
             +Vin
               |
         +------------+
         | Step-Down  |  <-- Einstellbarer Buck (z. B. LM2596 Modul)
         | 6-12V -> 5V|
         +---+-----+--+
             |     |
         +5V |     | GND
             |     |
  +-------------------------------+  <-- 5V Schiene (Lochraster)
  |  +-------+   +---------+      |
  |  | Raspberry Pi (5V->Pi)    |  |
  |  | - 5V Pin (phys. Pin 2/4)  |  |
  |  | - GND                     |  |
  |  +-------+   +---------+      |
  |      |           |            |
  |      | I2C/SPI   |            |
  |  +---+----+  +---+---+        |
  |  | LCD I2C |  | PN532 |-------+
  |  | VCC=5V  |  | SPI   | MOSI/MISO/SCLK/CS/RST/IRQ
  |  | SDA/SCL |  | VCC   |
  |  +--------+  +-------+
  |   |LEDs/Taster/Peripherie    |
  +-------------------------------+

Wichtig: Falls ein Modul 3.3 V benötigt, speise es vom Pi‑3.3 V Pin ab oder verwende einen eigenen 3.3 V Regler; verbinde GND gemeinsam.

----

Verdrahtungstabelle (Kurzreferenz)

- Hohlbuchse: Außen = GND, Innen = +Vin (6–12 V)
- Step‑Down IN: +Vin / GND ← Hohlbuchse
- Step‑Down OUT: +5V / GND → 5V‑Schiene auf Perfboard
- Pi 5V: 5V (phys. Pin 2/4) ← 5V‑Schiene; GND ← GND‑Schiene
- I2C LCD:
  - VCC ← 5V‑Schiene (oder 3.3 V falls nötig)
  - GND ← GND‑Schiene
  - SDA ← BCM2 (Pi SDA)
  - SCL ← BCM3 (Pi SCL)
- PN532 (SPI):
  - VCC ← 5V‑Schiene (oder 3.3 V nach Datenblatt)
  - GND ← GND‑Schiene
  - MOSI ← BCM10
  - MISO ← BCM9
  - SCLK ← BCM11
  - CS   ← BCM8
  - RSTO ← BCM24 (Output vom Pi)
  - IRQ  ← BCM25 (Input zum Pi)
- LEDs (je): GPIO (z. B. BCM17) → Serie 330 Ω → LED Anode; Kathode → GND
- Taster (je): Taster zwischen GPIO und GND; in Software PullUp aktivieren

Konnektoren empfohlen:
- 2×20 Buchsenleiste auf Perfboard für Pi‑Steckbarkeit oder 2×20 Dupont Kabelbündel
- JST‑4 für I2C‑Kabel (optional)
- Schraubklemme für externen 5 V Ein-/Ausgang (optional)

----

Sicherheits‑und Prüfhinweise (Checklist)

1. Vor Anschließen: Step‑Down ohne Last auf 5.00 V einstellen und messen (Multimeter). Niemals Pi anschließen, wenn Ausgang nicht 5 V ±0.05 V ist.
2. Vor dem Einstecken: Kurzschlussprüfung zwischen 5V und GND durchführen.
3. Erst Pi anschließen, dann Software starten; prüfe mit `zeiterfassung.py` im Simulationsmodus:
   - LCD zeigt "Zeiterfassung / Bereit"
   - LED Testscript schaltet LEDs
   - Taster reagieren in Konsole
4. PN532 prüfen: Tag lesen, UID erscheint in Konsole, Event in SQLite DB.
5. Wenn Module 3.3 V benötigen: vorher Spannungspfad prüfen; niemals 5 V an 3.3 V‑Only Modul legen.

----

Hinweis für CAD/Mechanik: Zeichne auf der Platine kleine Testpads für 5V, GND, SDA, SCL, MOSI, MISO, SCLK, CS, IRQ und markiere sie im CAD (z. B. silkscreen), damit Messungen und Debugging schnell möglich sind.

Dateien: Schaltplan‑Bitmap/Vector (optional)

Wenn Du eine grafische Version (SVG/PNG) des Schaltplans wünschst, kann ich eine einfache PNG/SVG‑Datei mit den oben genannten Verbindungen erstellen — sag mir, ob du eine Vektor‑SVG bevorzugst oder ein PNG für Druck/Einbau‑Dokumentation.
