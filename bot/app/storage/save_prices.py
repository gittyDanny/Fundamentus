from app.database import get_connection


def save_daily_prices(prices):
    """
    Speichert neue Tageskurse und aktualisiert den laufenden Handelstag.

    Historische Werte bleiben unverändert, solange Yahoo keine
    tatsächlich abweichenden Werte liefert.
    """
    conn = get_connection()
    cursor = conn.cursor()

    changed_rows = 0

    for price in prices:
        cursor.execute("""
        INSERT INTO price_daily
        (ticker, date, open, high, low, close, volume, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(ticker, date, source) DO UPDATE SET
            open = excluded.open,
            high = excluded.high,
            low = excluded.low,
            close = excluded.close,
            volume = excluded.volume

        WHERE
            price_daily.open IS NOT excluded.open OR
            price_daily.high IS NOT excluded.high OR
            price_daily.low IS NOT excluded.low OR
            price_daily.close IS NOT excluded.close OR
            price_daily.volume IS NOT excluded.volume
        """, (
            price["ticker"],
            price["date"],
            price["open"],
            price["high"],
            price["low"],
            price["close"],
            price["volume"],
            price["source"]
        ))

        # 1 bei einer neuen oder tatsächlich aktualisierten Zeile.
        # 0, wenn sich der gespeicherte Datensatz nicht verändert hat.
        changed_rows += cursor.rowcount

    conn.commit()
    conn.close()

    return changed_rows