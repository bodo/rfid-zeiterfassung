# Abnahme‑Protokoll — Auszug

Projekt: Zeiterfassung Terminal (RFID, PN532)  
Auftraggeber: [Name Auftraggeber]  
Auftragnehmer: [Name Auftragnehmer / Team Karl]  
Datum / Ort: YYYY‑MM‑DD / [Ort]

## 1. Umfang der Abnahme
- Funktionsumfang: Terminal‑Software (zeiterfassung.py), CLI‑Tools (benutzeradmin.py, reports.py), Server‑API (zeitserver.py), DB‑Migrationen.
- Hardware: Raspberry Pi 4 mit PN532, LCD, LEDs, Taster.
- Dokumentation: INSTALL.md, README.md, specs/01_general.md, Abnahme‑Protokoll.

## 2. Abnahmekriterien (stichpunktartig)
- RFID‑Lesen: NTAG215 UID wird zuverlässig gelesen und als HEX in employees.rfuid_uid gespeichert.
- Lokal: Events werden korrekt in SQLite (data/zeiterfassung.db) gespeichert mit synced‑Flag.
- Sync: Unsynced‑Events werden erfolgreich an /sync/events gesendet; Server antwortet 200 / 403 / 502 gemäß Spec.
- CLI: Mitarbeiter anlegen/ändern/löschen funktioniert interaktiv.
- Systemd: Dienste starten/stoppen via systemd (zeiterfassung, zeitserver).
- Sicherheit: TIME_SHARED_SECRET konfigurierbar, nicht im Repo.
- Logging: High‑level Logs auf Konsole/Journal verfügbar; Fehler in logs‑Tabelle.

## 3. Durchführung der Abnahme (Kurz)
- Testlauf Terminal:
  - Start des Dienstes → Status OK
  - Präsentation bekannter Tag → Event erstellt, Konsole zeigt Log "kommt"
  - Präsentation unbekannter Tag → rotes Blinkmuster / Log "Unbekannter Tag"
  - Pause/Ext‑Termin simuliert über Tasten → entsprechende Events erzeugt
- Testlauf Sync:
  - Erzeuge unsynced Events lokal, aktiviere Netzwerk → /sync/events POST → Server bestätigt 200, lokale Einträge marked synced=1
- CLI & Reports:
  - Benutzer anlegen → Tag registrieren → in employees sichtbar
  - Reports zeigen letzte X Tage korrekt

## 4. Ergebnis Zusammenfassung
- Prüfungsergebnis: [erfüllt / teil‑erfüllt / nicht erfüllt]  (kurze Begründung)
- Offene Punkte / Mängel:
  1. [Kurzbeschreibung, z.B. Logging‑Level, fehlende Unit‑Tests XYZ]
  2. [Weitere offene ToDos mit Verantwortlichem und Frist]

## 5. Abnahmeentscheidung
- Entscheidung Auftraggeber: [Abnahme erteilt / Abnahme verweigert / Teilabnahme]
- Bei Teilabnahme: Lieferumfang für die Abnahme und Nacharbeiten festhalten.

## 6. Signaturen (Auszug)
Auftraggeber: _______________________   Datum: __________

Auftragnehmer: ______________________  Datum: __________

(Ende Auszug)
