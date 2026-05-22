from app.database import get_connection


def save_asset(asset):
    # hier speichern wir ein einzelnes Asset aus der Watchlist
    # wenn der Ticker schon existiert, aktualisieren wir die Stammdaten
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO assets
    (ticker, name, asset_type, region, currency, sector, cik)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(ticker) DO UPDATE SET
        name = excluded.name,
        asset_type = excluded.asset_type,
        region = excluded.region,
        currency = excluded.currency,
        sector = excluded.sector,
        cik = excluded.cik
    """, (
        asset["ticker"],
        asset.get("name"),
        asset.get("asset_type"),
        asset.get("region"),
        asset.get("currency"),
        asset.get("sector"),
        asset.get("cik")
    ))

    conn.commit()
    conn.close()


def save_assets(assets):
    # hier gehen wir durch alle Assets aus der Watchlist
    # und speichern sie nacheinander in der Datenbank
    for asset in assets:
        save_asset(asset)