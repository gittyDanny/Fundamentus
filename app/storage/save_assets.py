from app.database import get_connection


def save_asset(asset):
    # hier speichern wir ein einzelnes Asset aus der Watchlist
    # INSERT OR IGNORE verhindert doppelte Ticker in der Datenbank
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO assets
    (ticker, name, asset_type, region, currency, sector)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        asset["ticker"],
        asset.get("name"),
        asset.get("asset_type"),
        asset.get("region"),
        asset.get("currency"),
        asset.get("sector")
    ))

    conn.commit()
    conn.close()


def save_assets(assets):
    # hier gehen wir durch alle Assets aus der Watchlist
    # und speichern sie nacheinander in der Datenbank
    for asset in assets:
        save_asset(asset)