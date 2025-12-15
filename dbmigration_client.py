#!/usr/bin/env python3
from pathlib import Path
from config.db_schema import CLIENT_SCHEMA, init_db

DB_PATH = Path(__file__).parent / "data" / "zeiterfassung.db"

def main():
    init_db(DB_PATH, CLIENT_SCHEMA)
    print(f"Client-DB initialisiert: {DB_PATH}")

if __name__ == "__main__":
    main()
