from app.database import get_connection


def save_daily_prices(prices):
    # hier speichern wir mehrere Tageskurse in die Datenbank
    # INSERT OR IGNORE verhindert doppelte Kurse für denselben Tag
    conn = get_connection()
    cursor = conn.cursor()

    new_rows = 0

    for price in prices:
        cursor.execute("""
        INSERT OR IGNORE INTO price_daily
        (ticker, date, open, high, low, close, volume, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        # rowcount ist 1, wenn wirklich eine neue Zeile gespeichert wurde
        # bei doppelten Einträgen bleibt es 0
        new_rows += cursor.rowcount

    conn.commit()
    conn.close()

    return new_rows