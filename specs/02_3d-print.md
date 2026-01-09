# 3D‑Druck: Gehäuse für Terminal

Zweck: Dieses Dokument enthält technische Anweisungen für den CAD‑Konstrukteur / 3D‑Drucker, damit das Terminal (Raspberry Pi + PN532 + Perforierte Leiterplatte + LCD + LEDs + Taster) in ein passgenaues, stapelbares Gehäuse eingebaut werden kann.

Wichtig: Vor finalem Druck die realen Bauteile mit Schieblehre ausmessen und eine Passprobe mit 1:1 Ausdruck (auf Papier) durchführen. Maße hier sind Empfehlungswerte; exakte Maße an den gelieferten Teilen prüfen.

## Materialien & Druckeinstellungen
- Material: PETG empfohlen (temperaturbeständiger, robust). PLA möglich für Prototypen.
- Wandstärke: 2.5–3.0 mm
- Infill: 15–30 %
- Schichthöhe: 0.2 mm (oder nach Qualitätsbedarf)
- Bohr-/Toleranzzugabe: +0.3–0.6 mm zu Bohrlochdurchmesser für sauberen Sitz

## Grundprinzip Gehäuseaufbau
- Zweiteiliges Gehäuse: Unterteil (Elektronik, Montage) + Abnehmbarer Deckel (Front) oder Scharnier + Schrauben.
- Unterteil enthält Montagefläche für:
  - Raspberry Pi 4 (4 Befestigungsbohrungen, Abstand siehe Hinweis)
  - Lochrasterplatte (perfboard) als System‑PCB (Maße abhängig von Platine; Standard: 100 x 70 mm optional)
  - PN532 Modul (falls externe Platine), Abstand für Antenne
  - Standoffs / Messing‑Gewindeeinsätze (M2.5 empfohlen)

## Raspberry Pi Montage (Hinweis)
- Verwende die Standard‑Montagepunkte des Raspberry Pi 4. Abstand der Befestigungsbohrungen (empfohlen, bitte verifizieren): 58 mm × 49 mm (Maße cx/cx und cy/cy).
- Bohrlochdurchmesser für M2.5 Schrauben: 3.0 mm (mit 0.3 mm Toleranz je nach Drucker).
- Verwende M2.5 Schrauben und Messing‑Gewindebuchsen oder gedruckte Standoffs.

### Raspberry Pi 3 Kompatibilität
- Das Gehäuse kann alternativ einen Raspberry Pi 3 (Model B / B+) aufnehmen. Die Montagepunkte sind in der Praxis baugleich/kompatibel, dennoch: bitte die tatsächlichen Abmessungen vor finalem Druck verifizieren und eine 1:1 Schablone anfertigen.
- Wenn Abweichungen festgestellt werden, ergänze kleine Justierbohrungen (Längsschlitze) +/- 1.5 mm, damit leichte Positionsanpassungen möglich sind.

### Raspberry Pi Zero (Alternative)

- Der Raspberry Pi Zero (z.B. Zero W) ist deutlich kleiner; er eignet sich für sehr kompakte Terminal‑Varianten. Beachte:
  - Der Pi Zero hat in der Regel keine vorinstallierten Montagebohrungen wie Pi 4; often sind keine M2.5‑Befestigungslöcher vorhanden. Plane entweder eine Adapter‑Platte oder spezielle klemmbare/geklebte Befestigungspunkte.
  - Bei Verwendung des Pi Zero sollten die Bohrungen und Standoffs im CAD so ausgelegt werden, dass sie entweder eine kleine Adapterplatte aufnehmen oder flexible Standoffs/Schienen erlauben.
  - Pi Zero verfügt über den gleichen 40‑Pin Header‑Pinout (wenn Header gelötet ist) und verwendet dieselben BCM‑Pins; prüfe, ob der Header bereits bestückt ist oder nachgelötet werden muss.
  - Power: Pi Zero wird über Micro‑USB (5 V) versorgt; im Gehäuse Platz für ein Micro‑USB‑Kabel oder eine eingelassene Buchse vorsehen.
  - Da Pi Zero weniger Rechenleistung bietet, ist er für einfache Terminals ausreichend; für Lasten wie intensives Logging oder lokale Verarbeitung ist Pi 3/4 vorzuziehen.

Hinweis CAD: Falls Pi Zero verwendet wird, füge in der Montageplatte optionale Durchbrüche/Schlitze (z. B. 4 kleine Löcher oder eine Adapterfläche) ein, die eine flexible Positionierung der Standoffs ermöglichen (Toleranz ±5 mm). Prüfe USB/Micro‑SD Zugänglichkeit.

## Front‑Panel (Ausschnitte & Bohrungen)
Die Frontplatte sollte die folgenden Elemente aufnehmen. Maße sind Angabe/Empfehlung; CAD bitte nach Bauteil prüfen:

- LCD 16×2 (I2C, Standardmodul mit PCB‑Backpack):
  - Sichtfenster rechteckig, innenmaß ca. 68 × 20 mm (Passe den Rand so, dass Display sichtbar ist). Abstand zum Montageplan ca. 4–5 mm.
  - Befestigung: Falls das Display Schraubenlöcher hat, ergänze entsprechende Standoffs.

- LEDs (5 mm Standard):
  - Lochdurchmesser: 5.5 mm (Toleranz 0.3–0.6 mm).
  - Abstand zueinander je nach UI (z.B. zwei kleine LEDs oben: 12–16 mm Abstand).

- Taster / Druckschalter (Panel mount / SMD Taster je nach Wahl):
  - Für runde Schalter (6 mm Minitaster): Loch 6.5 mm.
  - Für flache Panel‑Taster: Maße nach Komponentendatenblatt (evtl. rechteckiger Ausschnitt).

- Öffnung für PN532 Antenne (falls externe Antenne nötig):
  - Keine metallische Abschirmung direkt vor Antenne; freie Fläche von ca. 30×30 mm.

- Kabeldurchführung:
  - Rückseitig/ganz unten: schmale Schlitzöffnung (6–10 mm) für Flachbandkabel / Jumper; abgerundete Kanten.

## Montage: LCD und Raspberry verschrauben, Platine unter dem LCD

Die Standardmontage soll so erfolgen, dass das Display und der Raspberry Pi fest im Gehäuse verschraubt sind und mittels kurzer Kabel (Flachband oder Litzen) mit der darunter liegenden Lochrasterplatte verbunden werden. Das reduziert Zugkräfte auf Lötstellen und erleichtert Service.

- Montageschritte (Mechanisch):
  1. Front‑Ausschnitt: gestalte das LCD‑Fenster so, dass das LCD‑Modul mit Montagebohrungen befestigt werden kann (je nach Modul 4x Schrauben M2.5 oder 2x Clips). Verwende 4 Standoffs/Schrauben für das Display.
  2. Platinenlage: Die Lochrasterplatte (Perfboard) wird direkt unter dem LCD befestigt, parallel zur Frontplatte. Plane 3–4 Standoffs zwischen Front/Display und Platine ein, Höhe ca. 8–12 mm, sodass Bauteile unter dem Display Platz haben.
  3. Raspberry Pi: Befestige den Pi auf separaten Standoffs im Unterteil oder auf einer eigenen Montagefläche nahe einer Seitenöffnung für Anschlüsse. Alternativ kann der Pi verschraubt werden und mittels 2×20 (oder flexibler) Stiftleiste über Kabel mit der Lochrasterplatte verbunden werden.
  4. Kabelverbindung: Verwende fürs LV‑Signal (I2C, SPI, GPIO) kurze abgeschirmte Litzen oder Dupont‑Kabel (4–10 cm). Für I2C reicht ein 4‑adriges Kabel (VCC,GND,SDA,SCL). Für SPI benötigst du 6–8 Adern (MOSI,MISO,SCLK,CS,RST,IRQ,+VCC,GND).

- Hinweise zur Bohrung/Toleranz:
  - Bei verschraubtem LCD und Pi sollten die Schrauben nicht durch die Platine ragen; prüfe Bauteilhöhen.
  - Platinenbefestigung unter dem LCD: Bohrlochdurchmesser 3.0 mm für M2.5 Schrauben mit 0.3 mm Toleranz.

## Montageanleitung (zusammengefasst)
1. Befestige das LCD an der Front mittels Standoffs (4x M2.5). Prüfe Sitz und Sichtfeld.
2. Positioniere die Lochrasterplatte direkt unter dem LCD; befestige mit 3–4 Standoffs.
3. Verlege die Verbindungs‑Kabel (I2C/SPI/GPIO) vom LCD und vom PN532 zum Platinenrand; sichere Kabel mit Kabelbindern/Clips.
4. Befestige den Raspberry Pi mit eigenen Standoffs im Unterteil; verbinde Pi↔Lochraster per kurzen Kabelbündeln (steckbar). Verwende Buchsenleisten oder Pfostenleisten für einfache Demontage.
5. Vor finalem Zusammenbau: Kabelwege prüfen (keine Quetschungen), Schraubenlängen kontrollieren, Versuchsmontage und Software‑Check durchführen.

## Befestigungsstandoffs für Perfboard / Platine
- Lege 3–4 M2.5 Standoffs für die Lochrasterplatte vor. Abstand so wählen, dass Platine plan aufliegt und nicht überlappt mit Pi‑Befestigungspunkten.
- Standoff‑Höhe: 8–12 mm (abhängig von Bauteilhöhe auf Platine). Bei Verwendung Stiftleisten (2x20) mindestens 12 mm.

## Anschlüsse und Zugänglichkeit
- SD‑Kartenöffnung: wenn Pi freier Zugang benötigt, an entsprechender Seite eine Öffnung einplanen.
- USB/ETHERNET/HDMI: wenn extern verfügbar, Aussparungen an den Seiten vorsehen.
- Schrauben für Deckel: M2.5, 4 Stück.

## Netzanschluss / Hohlbuchse

- Front/Rückseite: Plane eine Hohlbuchse (Barrel jack) Aussparung ein, die einfach zugänglich ist. Typische Einbaumaße: Loch für Flansch ~12–14 mm Durchmesser, mit kleiner Vertiefung dahinter für den Buchsenkörper. Prüfe das konkrete Bauteil vor finalem Druck.
- Kennzeichnung: Auf der Außenseite des Gehäuses klar kennzeichnen: "Außen = GND, Innen = +Vin".

## Platz für Step‑Down Wandler

- Platziere im Unterteil eine kompakte Fläche (z. B. 40×25 mm) mit mindestens 2–4 Bohrungen oder Clips, um ein gängiges Step‑Down‑Modul (LM2596‑Style) sicher zu verschrauben. Lasse 10–15 mm Freiraum oberhalb des Moduls für Anpassungen und möglicher Kühlung.
- Wenn möglich, füge kleine Befestigungsnuten ein, damit das Modul flach montiert werden kann und keine Kabel gequetscht werden.

## Elektrische Montage & Wärme
- Lüftung: Optional kleine Schlitze an der Rückseite (5–10 × 1 mm) falls PETG und freie Konvektion gewünscht.
- Abstand zu Pi‑Bauteilen (USB‑Controller, Spannungswandler) mindestens 5 mm Freiraum.

## Montageanleitung für Mechaniker/CAD
1. Erzeuge eine Montageplatte im Unterteil mit die oben genannten Standoffs.
2. Positioniere Raspberry Pi so, dass die USB/ETH/HDMI‑Ausschnitte an der Seitenöffnung passen.
3. Platziere die Lochrasterplatte parallel zur Pi‑Platine, so dass 2×20 Stiftleisten vom Pi zur Lochrasterplatte in Reichweite sind (max. 40 mm Abstand empfohlen).
4. Freiraum für PN532: Modul sollte flach liegen; Antennenfläche oben frei halten.
5. Mache Probedruck: kundenseitig 1:1 Papier‑Schnittmuster, anschließend Druck eines Prototypen in PLA zur Passprobe.

## Hinweise an Konstrukteur
- Druckorientierung so wählen, dass Front‑Fenster glatt ist (wenig Support innen) — Frontfläche nach oben drucken.
- Verwende Fillet/Runde Kanten an Ausschnitten für bessere Ergonomie.
- Dokumentiere in CAD die Maße der finalen Ausschnitte und lade ein 2‑seites PDF mit 1:1 Schablone.

## Abschluss
- Vor Seriendruck müssten alle realen Bauteile (Display, Module, Taster, LEDs) vermessen und eine finale Passprobe durchgeführt werden.
