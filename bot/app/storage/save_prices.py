from app.database import get_connection


def save_daily_prices(prices):
    conn = get_connection()
    cursor = conn.cursor()

    changed_rows = 0

    for price in prices:
        cursor.execute("""
        INSERT INTO price_daily
        (
            ticker,
            date,
            open,
            high,
            low,
            close,
            volume,
            source
        )
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

        changed_rows += cursor.rowcount

    conn.commit()
    conn.close()

    return changed_rows


def save_intraday_prices(prices):
    conn = get_connection()
    cursor = conn.cursor()

    changed_rows = 0

    for price in prices:
        cursor.execute("""
        INSERT INTO price_intraday
        (
            ticker,
            timestamp,
            timeframe,
            open,
            high,
            low,
            close,
            volume,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(
            ticker,
            timestamp,
            timeframe,
            source
        ) DO UPDATE SET
            open = excluded.open,
            high = excluded.high,
            low = excluded.low,
            close = excluded.close,
            volume = excluded.volume

        WHERE
            price_intraday.open IS NOT excluded.open OR
            price_intraday.high IS NOT excluded.high OR
            price_intraday.low IS NOT excluded.low OR
            price_intraday.close IS NOT excluded.close OR
            price_intraday.volume IS NOT excluded.volume
        """, (
            price["ticker"],
            price["timestamp"],
            price["timeframe"],
            price["open"],
            price["high"],
            price["low"],
            price["close"],
            price["volume"],
            price["source"]
        ))

        changed_rows += cursor.rowcount

    conn.commit()
    conn.close()

    return changed_rows


def get_latest_intraday_timestamp(ticker):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT MAX(timestamp)
    FROM price_intraday
    WHERE ticker = ?
      AND timeframe = '5m'
      AND source = 'yahoo';
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]


def count_daily_prices_for_ticker(ticker):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM price_daily
    WHERE ticker = ?
      AND close IS NOT NULL;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    return row[0]