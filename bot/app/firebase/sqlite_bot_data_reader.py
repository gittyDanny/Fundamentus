import sqlite3

from app.database import get_connection


def row_to_dict(row):
    """
    Wandelt eine SQLite-Zeile in ein normales Dictionary um.

    Dadurch können wir später mit Spaltennamen arbeiten.
    Beispiel:
    row["ticker"] statt row[0]
    """
    return dict(row)


def get_active_assets_from_sqlite():
    """
    Holt alle aktiven Assets aus der lokalen SQLite-Datenbank.

    Diese Daten braucht die Android-App später für die Watchlist- und Stocks-Ansicht.
    Zusätzlich wird die zuletzt verwendete Fundamentaldatenquelle gelesen,
    z.B. sec_companyfacts oder yahoo.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        a.ticker,
        a.name,
        a.asset_type,
        a.region,
        a.currency,
        a.sector,
        a.cik,
        a.is_active,
        (
            SELECT f.source
            FROM fundamentals f
            WHERE f.ticker = a.ticker
              AND f.source IS NOT NULL
            ORDER BY f.created_at DESC
            LIMIT 1
        ) AS data_source
    FROM assets a
    WHERE a.is_active = 1
    ORDER BY a.ticker ASC;
    """)

    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


def get_latest_signals_from_sqlite():
    """
    Holt pro Ticker das neueste gespeicherte Signal aus SQLite.

    In der Tabelle signals können mehrere alte Signale pro Ticker liegen.
    Für die App brauchen wir zunächst nur den aktuellen Stand:
    BUY, HOLD oder SELL inklusive Score und Begründung.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ticker,
        signal,
        score,
        reason,
        close,
        sma_20,
        change_20d_pct,
        source,
        created_at
    FROM signals
    WHERE id IN (
        SELECT MAX(id)
        FROM signals
        GROUP BY ticker
    )
    ORDER BY ticker ASC;
    """)

    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


def get_latest_bot_run_from_sqlite():
    """
    Holt den letzten Botlauf aus SQLite.

    Diese Information wird später für den App-Bereich Bot Health genutzt:
    - Wann lief der Bot zuletzt?
    - War der Lauf erfolgreich?
    - Wie viele Assets wurden verarbeitet?
    - Gab es Kursdatenfehler?
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        started_at,
        finished_at,
        status,
        assets_processed,
        price_errors,
        signals_saved,
        error_message
    FROM bot_runs
    ORDER BY id DESC
    LIMIT 1;
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return row_to_dict(row)
