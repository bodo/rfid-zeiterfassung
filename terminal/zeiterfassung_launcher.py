#!/usr/bin/env python3
"""
Launcher für die Terminal-Komponente. Fügt Projekt-Root zum sys.path hinzu
und startet die vorhandene zeiterfassung.py.
"""
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import zeiterfassung as terminal_mod  # type: ignore

if __name__ == "__main__":
    # Delegiere an die vorhandene main_loop / CLI
    terminal_mod.main_loop(simulate_input=True)
