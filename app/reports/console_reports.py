from app.database import get_connection


def show_saved_assets():
    # hier zeigen wir an, welche Assets aktuell in der Datenbank stehen
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, region, sector
    FROM assets
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    print("\nGespeicherte Assets in der Datenbank:")

    for row in rows:
        ticker, name, region, sector = row
        print(f"- {ticker}: {name} | {region} | {sector}")

    print(f"\nInsgesamt gespeichert: {len(rows)} Assets")


def show_latest_prices(ticker, limit=5):
    # hier zeigen wir die letzten gespeicherten Tageskurse für einen Ticker an
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, open, high, low, close, volume
    FROM price_daily
    WHERE ticker = ?
    ORDER BY date DESC
    LIMIT ?;
    """, (ticker, limit))

    rows = cursor.fetchall()
    conn.close()

    print(f"\nLetzte {limit} gespeicherte Kurse für {ticker}:")

    for row in rows:
        date, open_price, high, low, close, volume = row

        print(
            f"- {date}: "
            f"Open {open_price:.2f}, "
            f"High {high:.2f}, "
            f"Low {low:.2f}, "
            f"Close {close:.2f}, "
            f"Volume {volume}"
        )


def show_fundamentals(ticker):
    # hier zeigen wir die gespeicherten Fundamentaldaten eines Tickers
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fiscal_year, metric, value, unit
    FROM fundamentals
    WHERE ticker = ?
    ORDER BY fiscal_year DESC, metric ASC;
    """, (ticker,))

    rows = cursor.fetchall()
    conn.close()

    print(f"\nFundamentaldaten für {ticker}:")

    if not rows:
        print("- Noch keine Fundamentaldaten gespeichert.")
        return

    for row in rows:
        fiscal_year, metric, value, unit = row
        print(f"- {fiscal_year} | {metric}: {value:,.0f} {unit}")