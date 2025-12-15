#!/usr/bin/env python3
from os import getenv
from pathlib import Path
from config.db_schema import init_mysql_db

def main():
    # ENV-Vars: TIME_DB_HOST, TIME_DB_USER, TIME_DB_PASSWORD, TIME_DB_NAME, optional TIME_DB_PORT
    host = getenv("TIME_DB_HOST", "localhost")
    user = getenv("TIME_DB_USER")
    password = getenv("TIME_DB_PASSWORD")
    dbname = getenv("TIME_DB_NAME")
    port = int(getenv("TIME_DB_PORT", "3306"))

    if not all([user, password, dbname]):
        print("Bitte setzen Sie TIME_DB_USER, TIME_DB_PASSWORD und TIME_DB_NAME in der Umgebung.")
        return

    init_mysql_db(host=host, user=user, password=password, database=dbname, port=port)
    print(f"Server-DB initialisiert in {user}@{host}:{port}/{dbname}")

if __name__ == "__main__":
    main()
