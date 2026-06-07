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
    CREATE TABLE IF NOT EXISTS bot_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TEXT DEFAULT CURRENT_TIMESTAMP,
        finished_at TEXT,
        status TEXT,
        assets_processed INTEGER DEFAULT 0,
        price_errors INTEGER DEFAULT 0,
        signals_saved INTEGER DEFAULT 0,
        error_message TEXT
    );
    """)

    try:
        # hier ergänzen wir die CIK-Spalte für ältere Datenbanken,
        # die schon vor dem SEC-Import erstellt wurden
        cursor.execute("ALTER TABLE assets ADD COLUMN cik TEXT;")
    except sqlite3.OperationalError:
        # hier landen wir, wenn die Spalte schon existiert
        # das ist okay, weil wir main.py mehrfach starten wollen
        pass


    try:
        # hier ergänzen wir eine Aktiv-Spalte für ältere Datenbanken,
        # damit entfernte Watchlist-Assets nicht weiter als aktiv gelten
        cursor.execute("ALTER TABLE assets ADD COLUMN is_active INTEGER DEFAULT 1;")
    except sqlite3.OperationalError:
        # hier landen wir, wenn die Spalte schon existiert
        pass

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
    CREATE TABLE IF NOT EXISTS fundamentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        fiscal_year INTEGER,
        period TEXT,
        metric TEXT NOT NULL,
        value REAL,
        unit TEXT,
        source TEXT,
        form TEXT,
        filed_at TEXT,
        end_date TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, fiscal_year, period, metric, source)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        signal TEXT NOT NULL,
        score REAL,
        reason TEXT,
        close REAL,
        sma_20 REAL,
        change_20d_pct REAL,
        source TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()