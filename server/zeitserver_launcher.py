#!/usr/bin/env python3
"""
Launcher für den Server: stellt sicher, dass Projekt-Root im PYTHONPATH ist
und startet die vorhandene zeitserver.py (im Projekt-Root).
"""
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importiert die bestehende zeitserver.py aus dem Projekt-Root
import zeitserver as app_mod  # type: ignore

if __name__ == "__main__":
    # zeitserver.py stellt Flask app und entrypoint bereit; wir rufen main run
    # falls zeitserver.py bei __main__ runnen soll, delegieren wir darauf
    # ansonsten starten wir den Flask server direkt
    try:
        # einige Module definieren app.run() nur unter __main__; falls vorhanden, benutze es
        app_mod.app.run(host="0.0.0.0", port=5000)
    except Exception:
        # fallback: versuchen zeitserver.py als skript auszuführen
        import runpy
        runpy.run_module("zeitserver", run_name="__main__")
