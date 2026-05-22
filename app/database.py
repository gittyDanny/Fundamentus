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
    # hier legen wir die Tabellen an, falls sie noch nicht existieren
    # dadurch kann main.py mehrfach laufen, ohne jedes Mal alles kaputtzumachen
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        source TEXT,
        published_at TEXT,
        url TEXT,
        summary TEXT,
        raw_text TEXT,
        ticker TEXT,
        language TEXT,
        source_api TEXT,
        content_hash TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_api_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        endpoint TEXT,
        query TEXT,
        response_json TEXT,
        response_hash TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()