from pathlib import Path
import sqlite3


DB_PATH = Path("data/fundamentus.db")


def get_connection():
    # Der data-Ordner wird bei Bedarf automatisch angelegt.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


def init_db():
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
        cik TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

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
        cursor.execute("ALTER TABLE assets ADD COLUMN cik TEXT;")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute(
            "ALTER TABLE assets "
            "ADD COLUMN is_active INTEGER DEFAULT 1;"
        )
    except sqlite3.OperationalError:
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
    CREATE TABLE IF NOT EXISTS price_intraday (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        source TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, timestamp, timeframe, source)
    );
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_price_intraday_ticker_timestamp
    ON price_intraday(ticker, timestamp DESC);
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