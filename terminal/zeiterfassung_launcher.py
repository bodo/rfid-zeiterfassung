#!/usr/bin/env python3
"""
Launcher für die Terminal-Komponente. Fügt Projekt-Root zum sys.path hinzu
und startet die vorhandene zeiterfassung.py.
"""
from pathlib import Path
import sys
import argparse
import os

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Force gpiozero to use the RPi.GPIO backend to avoid lgpio fallback warnings
# If you prefer lgpio, install it on the Pi: `sudo apt install python3-lgpio`
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "rpi")

import zeiterfassung as terminal_mod  # type: ignore

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launcher für das Terminal. Leitet Argumente an das Zeiterfassungsmodul weiter.")
    parser.add_argument("--test-reader", action="store_true", help="Test-/Simulationsmodus: Eingaben per Konsole (statt echten Reader)")
    args = parser.parse_args()
    # Default: real reader (echte Hardware). Mit --test-reader wird auf Simulationsmodus umgeschaltet.
    terminal_mod.main_loop(simulate_input=args.test_reader)
