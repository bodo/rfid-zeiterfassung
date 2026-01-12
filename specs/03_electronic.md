# Elektronik: Verdrahtung auf Lochrasterplatte (Perfboard)

Zweck: Konkrete Schritt‑für‑Schritt‑Anweisungen für einen Elektroniker, wie die Komponenten des Terminals auf einer Lochrasterplatte aufgebaut und mit dem Raspberry Pi verbunden werden.

Hinweis zur Nummerierung: In der Software werden GPIOs mit BCM‑Nummern verwendet (siehe `config/pin_config.py`). In der Praxis wird empfohlen, die Verdrahtung nach BCM‑Belegung zu planen; bei Unsicherheit Messung/Pinout des konkreten Pi‑Boards prüfen.

## Komponentenliste (Beispiel)
- Raspberry Pi 4 (montiert im Gehäuse)
- Lochrasterplatte (z. B. 100×70 mm) oder maßgeschneiderte Leiterplatte
- 2×20 Stiftleiste (female) / Buchsenleisten, um GPIO‑Signale zum Pi zu führen
- PN532 Modul (SPI)
- LCD 16×2 mit I2C Backpack
- LEDs (5 mm): grün/rot/weitere
- Widerstände für LEDs: 330 Ω (konfiguriert: `LED_RESISTOR_OHM = 330`)
- Taster (z. B. 6×6 mm mini tactile) oder Panel‑Taster
- 10 kΩ Pull‑up Widerstände für Taster (alternativ interne Pull‑ups in Software)
- Kondensatoren: 100 µF Elektrolyt (Power‑Decoupling), 0.1 µF Keramik (Entstörung)
- Schraubklemmen (2‑polig) für 5 V / GND Eingang (optional)

## Relevante GPIO‑Zuordnung (aus `config/pin_config.py`)
- `LED_READY_GREEN` = BCM17 (physical pin 11)
- `LED_READY_RED`   = BCM27 (physical pin 13)
- `LED_KOMMEN`      = BCM22 (physical pin 15)
- `LED_GEHEN`       = BCM23 (physical pin 16)
- `LED_EXTERN`      = BCM26 (physical pin 37) #Gelbe LED für "Extern Termin"
- `BTN_INFO`        = BCM5  (physical pin 29)
- `BTN_KOMMEN`      = BCM6  (physical pin 31)
- `BTN_GEHEN`       = BCM13 (physical pin 33)
- `BTN_EXT_TERM`    = BCM19 (physical pin 35)
- `I2C_SDA`         = BCM2  (physical pin 3, SDA)
- `I2C_SCL`         = BCM3  (physical pin 5, SCL)
- `PN532_SPI_MOSI`  = BCM10 (physical pin 19)
- `PN532_SPI_MISO`  = BCM9  (physical pin 21)
- `PN532_SPI_SCLK`  = BCM11 (physical pin 23)
- `PN532_SPI_CS`    = BCM8  (physical pin 24)
- `PN532_RSTO`      = BCM24 (physical pin 18)
- `PN532_IRQ`       = BCM25 (physical pin 22)

- `SHUTDOWN_BTN`   = BCM4  (physical pin 7)   # Taster: Sauberer Shutdown (gegen GND, langer Druck)

 - `LED_READY_GREEN` = BCM17 (physical pin 11)  # Status: Gerät bereit (grün)
 - `LED_READY_RED`   = BCM27 (physical pin 13)  # Status: Fehler/Alarm (rot)
 - `LED_KOMMEN`      = BCM22 (physical pin 15)  # Aktion: Kommen (kurzes Blink/Anzeigen)
 - `LED_GEHEN`       = BCM23 (physical pin 16)  # Aktion: Gehen (kurzes Blink/Anzeigen)
 - `LED_EXTERN`      = BCM26 (physical pin 37)  # Gelbe LED für "Extern Termin"
 - `BTN_INFO`        = BCM5  (physical pin 29)  # Taste: Info/Menu anzeigen
 - `BTN_KOMMEN`      = BCM6  (physical pin 31)  # Taste: Manuelle Kommen‑Eingabe
 - `BTN_GEHEN`       = BCM13 (physical pin 33)  # Taste: Manuelle Gehen‑Eingabe
 - `BTN_EXT_TERM`    = BCM19 (physical pin 35)  # Taste: Externer Termin / Extern‑Modus
 - `I2C_SDA`         = BCM2  (physical pin 3, SDA)
 - `I2C_SCL`         = BCM3  (physical pin 5, SCL)
 - `PN532_SPI_MOSI`  = BCM10 (physical pin 19)
 - `PN532_SPI_MISO`  = BCM9  (physical pin 21)
 - `PN532_SPI_SCLK`  = BCM11 (physical pin 23)
 - `PN532_SPI_CS`    = BCM8  (physical pin 24)
 - `PN532_RSTO`      = BCM24 (physical pin 18)
 - `PN532_IRQ`       = BCM25 (physical pin 22)

### Raspberry Pi 3 Unterstützung
- Die Verdrahtung und das Layout unterstützen alternativ einen Raspberry Pi 3 (Model B/B+). In den meisten Fällen sind die Montagebohrungen und der 40‑Pin Header kompatibel mit Pi 4, prüfe aber die Abstände vor dem finalen Gehäusedruck.
- Wenn ein Pi 3 verwendet wird, gelten die gleichen BCM‑Pins. Achte auf die Spannungspegel (3.3 V) und gleiche Anschlusslogik.

### Raspberry Pi Zero (Alternative)

- Der Raspberry Pi Zero (z. B. Zero W) ist eine platzsparende Alternative. Hinweise:
   - Mechanik: Pi Zero hat keine standardisierten Befestigungsbohrungen; plane im Gehäuse entweder:
      * eine kleine Adapterplatte mit Bohrungen für Zier‑Standoffs, oder
      * Clip‑/Klemmpunkte oder doppelseitige Klemmleisten im CAD.
   - Header: Pi Zero wird häufig ohne 40‑Pin Header geliefert — der Header muss ggf. eingelötet werden. Wenn Du auf Steckbarkeit angewiesen bist, löte eine 2×20 Buchsenleiste auf die Lochrasterplatte und verwende kurze Dupont‑Kabel.
   - Stromversorgung: Pi Zero wird über Micro‑USB (5 V) betrieben; bei integriertem Netzteil/Ausschnitt im Gehäuse darauf achten.
   - Performance: Pi Zero ist für einfache Logging‑Aufgaben ausreichend, für Netzwerk‑intensive Syncs oder Heavy‑Workloads lieber Pi 3/4 verwenden.
   - Pins und Logik: BCM‑Nummern sind dieselben; prüfe, dass alle benötigten Pins (SPI/I2C) am gelöteten Header verfügbar sind.

Praktischer Tipp: Füge im CAD eine optionale Ausnehmung für einen Pi‑Zero‑Adapter (kleine Platte) ein, die per 2–4 Schrauben fixiert werden kann. So bleibt das Gehäuse für Pi 3/4 oder Pi Zero verwendbar.

Verwende beim Verdrahten primär die BCM‑Bezeichnungen; zur Sicherheit kann zusätzlich die physische Pinbelegung (40‑pin Header) geprüft werden.

## Schaltungsprinzip
1. Power: Verwende die 5 V und GND des Raspberry Pi (physische Pins 2/4 für 5 V, mehrere GND Pins vorhanden). Stelle sicher, dass die Gesamtstromaufnahme aller Module die Versorgung nicht überschreitet.

**Externe Versorgung über Hohlbuchse + Step‑Down Wandler (empfohlen)**

- Verwende eine einzelne Hohlbuchse (Barrel jack) für den externen Eingang (geeignete Eingangs‑Spannung: 6–12 V DC). **Polung:** Außen = GND, Innen = +Vin (also Center‑positive wird verwendet, äußere Schale ist GND). Markiere dies klar auf dem Gehäuse und in der Dokumentation.
- Empfohlenes Modul: ein standardmäßiger DC‑DC Step‑Down (Buck) Wandler (z. B. LM2596S‑basiertes Modul oder ähnlicher einstellbarer Buck). Stelle den Wandler auf exakt 5.00 V ein, bevor Du Pi oder andere Elektronik verbindest.
- Verdrahtung:
   - Externer Adapter (6–12 V) → Hohlbuchse VIN (Innen +, Außen GND) → Eingang Step‑Down IN (+ / GND)
   - Step‑Down OUT (5 V / GND) → 5 V‑Schiene auf der Lochrasterplatte (dies ist die 5 V Versorgung für Pi, LCD, PN532 falls 5 V tolerant)
   - Immer zuerst mit Multimeter die 5 V am Step‑Down Ausgang prüfen (kein Gerät angeschlossen), erst dann den Pi anschließen.
- Sicherungen: Empfohlen ist eine Sicherung auf der Eingangsseite (z. B. 2 A langsam oder 2 A Polyswitch) oder auf der 5 V‑Ausgangsseite je nach Gesamtlast.
- Masse: Verbinde GND des Step‑Down, Hohlbuchse, Pi und alle Module (gemeinsame Masse).
- Montage: Der Step‑Down sollte sicher am Unterteil montiert werden (Schrauben/Standoffs oder Klemmungen). Achte auf Platz für Kühlkörper/Heatsink und belasse 10–15 mm Abstand zu brennbaren Materialien.

Hinweis: Viele Breakout‑Module für PN532 oder LCD können 3.3 V oder 5 V benötigen — prüfe Datenblatt. Falls ein Modul ausschließlich 3.3 V benötigt, speise es von der 3.3 V‑Leitung des Pi (nicht vom Step‑Down 5 V), oder verwende einen zusätzlichen LDO/Regler.
2. I2C LCD: Verbinde SDA → BCM2, SCL → BCM3, VCC → 5 V (oder 3.3 V prüfen beim Modul), GND → GND. Viele I2C‑Backpacks laufen mit 5 V und logisch mit 3.3 V via Pull‑ups; prüfe Datenblatt.
3. PN532 (SPI): Verbinde MOSI → BCM10, MISO → BCM9, SCLK → BCM11, CS → BCM8, RSTO → BCM24 (Output vom Pi), IRQ → BCM25 (Input zum Pi). VCC → 3.3 V oder 5 V je nach Breakout (prüfen!) und GND → GND.
4. LEDs: Jede LED über 330 Ω Serie an den jeweiligen GPIO; andere Seite der LED an GND (bei `LED_COMMON_ANODE = False`). Beispiel: GPIO (BCM17) → 330 Ω → Anode LED → Kathode → GND.
5. Taster: Taster zwischen GPIO und GND, Software‑PullUp aktivieren (oder externe 10 kΩ PullUp an 3.3 V). Alternativ Taster zwischen 3.3 V und GPIO mit PullDown. Standard: Taster gegen GND + interne PullUp.

Shutdown‑Taster (empfohlen):
- Verkabelung: Ein Taster zwischen `SHUTDOWN_BTN` (BCM4, physical pin 7) und GND.
- Software: In `zeiterfassung.py` wird der Taster mit internem PullUp konfiguriert. Ein langes Drücken (≥2 s) löst einen sauberen `sudo shutdown -h now` aus.
- Mechanik: Platziere den Taster an der Gehäusefront, ggf. mit Schutzabdeckung, um unbeabsichtigte Betätigungen zu vermeiden.

## Aufbau auf Lochrasterplatte (empfohlene Reihenfolge)
1. Markiere die Position der 2×20 Stiftleiste (GPIO‑Header). Lötbuchsen/Leiste so setzen, dass beim Einbau die Verbindung zum Pi ohne Zug möglich ist.
2. Lege Power‑Rails an: eine durchgehende 5 V Schiene und GND‑Schiene auf der Platine (verwende mehrere Durchkontaktierungen bzw. Leiterbahnen aus Draht). Platziere Kondensatoren (100 µF nahe Versorgungseingang, 0.1 µF nahe IC‑Pins).
3. Montiere Widerstände für LEDs nahe den LEDs; verlöte kurze Leiterstrecken.
4. Montiere Taster an der Frontkante und verbinde eine Seite des Tasters mit GND‑Schiene, die andere Seite an das entsprechende GPIO‑Pad.
5. Platziere PN532 Modul (wenn möglich flach) und führe die 4 SPI‑Signale + CS + RST + IRQ zur Stiftleiste. Achte auf kurze Signalwege.
6. Führe I2C‑Leitungen zum LCD‑Backpack (SDA/SCL) und beschrifte sie.
7. Testpunkte: Richte kleine Stiftleisten für Messpunkte (3.3 V, 5 V, GND, SPI CS, IRQ) ein.

## Mechanische Verbindung: LCD & Raspberry verschrauben, Platine unter dem LCD

- Konzept: LCD wird an der Front verschraubt; die Lochrasterplatte montiert unmittelbar darunter. Der Raspberry Pi wird auf eigenen Standoffs im Unterteil verschraubt und über steckbare Kabel (Kurzbündel) mit der Lochrasterplatte verbunden. Dadurch kann Frontabdeckung und Display beim Service entfernt werden, ohne die gesamte Verdrahtung zu lösen.

- Empfohlene Steckverbinder:
   - I2C: 4‑poliges JST‑SH oder 4‑poliges Dupont‑Kabel (VCC,GND,SDA,SCL)
   - SPI: 8‑poliges Kabelbündel oder 2×4 Dupont‑Strip (MOSI,MISO,SCLK,CS,RST,IRQ,+VCC,+GND)
   - GPIO/Taster: Einzelfarbige Dupont‑Leitungen oder kleine Schraubklemmen an der Platine

- Montagehinweise Elektriker/CAD:
   1. Vorsehen von 3–4 Standoffs zwischen LCD und Perfboard; Bohrungen sollten entkoppelt von Pi‑Montagepunkten sein.
   2. Verwende Pfostenleisten oder Buchsenleisten auf der Lochrasterplatte, um Kabel vom Pi aufzunehmen (schnelle Demontage).
   3. Markiere auf der Platine die Schnittstellen (I2C, SPI, LEDs, Taster) und dokumentiere Farbcodierung der Kabel.

## Verkabelung zum Pi (praktisch)
- Länge: Kabel zwischen Pi und Platine ≤ 100 mm empfohlen; zwischen LCD und Platine ≤ 40 mm.
- Aderquerschnitt: 26–28 AWG flexible Litze.
- Sorgfältige Beschriftung: Beide Enden der Kabel beschriften (z. B. SDA, SCL, MOSI).


## Kabeltypen & Längen
- Verwende flexible Jumperkabel (Dupont) oder Litzen 26–28 AWG für interne Verbindungen.
- Halte Leitungslängen kurz (< 100 mm) für SPI und IRQ, um Störungen zu vermeiden.

## Löt‑ und Sicherheits‑Hinweise
- Saubere Lötstellen; keine Kurzschlüsse auf der Unterseite.
- Alle Masse (GND) der Module mit GND des Pi verbinden (gemeinsame Masse).
- Beim ersten Inbetriebnehmen: Vor Einstecken am Pi alle Verbindungen messen (Kurzschlüsse), dann Pi ohne Peripherie starten und 3.3 V / 5 V messen.

## Testprozedur nach Aufbau
1. Ohne Pi: Sichtprüfung, Durchgangstest GND↔5V (keine Verbindung).
2. Mit Pi: Stecke Pi ein, starte nur das Netzteil, messe 3.3 V und 5 V an vorgesehenen Testpunkten.
3. Testsoftware: Starte `zeiterfassung.py` im Simulationsmodus und prüfe:
   - LCD zeigt `Zeiterfassung / Bereit`
   - Taster‑Eingaben in der Konsole (wenn Software PullUps genutzt werden)
   - LEDs schalten per Testskript
4. PN532 Test: Wenn vorh. Reader, teste Scan und prüfe, ob UID erkannt wird.

## Optional: Schraubklemmen & Netzteile
- Für einfachere Wartung kann die Platine eine kleine Schraubklemme für externe 5 V Eingang haben. Beschrifte +5 V (Vin) und GND klar.

## Abschlussbemerkungen
- Vor Serienmontage: Platinenlayout prüfen, Prototypen bauen und Langzeittest (einige Tage) durchführen.
- Wenn Unsicherheit bei Spannungspegeln der verwendeten Breakout‑Module besteht (PN532, LCD), immer Datenblatt prüfen und ggf. Pegelwandler einsetzen.
