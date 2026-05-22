from pathlib import Path
import sqlite3


DB_PATH = Path("data/fundamentus.db")


def get_connection():
    # hier stellen wir sicher, dass der data-Ordner existiert,
    # weil SQLite sonst keine Datenbankdatei anlegen kann
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # hier öffnen wir die Verbindung zur lokalen SQLite-Datenbank
    return sqlite3.connect(DB_PATH)


def init_db():
    # hier legen wir alle Tabellen an, die Fundamentus aktuell braucht
    # wenn Tabellen schon existieren, passiert einfach nichts Schlimmes
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        name TEXT,
        asset_type TEXT,
        region TEXT,
        currency TEXT,
        sector TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        source TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, date, source)
    );
    """)

    conn.commit()
    conn.close()