from app.database import get_connection


def save_asset(asset):
    # hier speichern wir ein Asset aus der Watchlist in der Datenbank
    # INSERT OR IGNORE verhindert doppelte Einträge beim mehrfachen Starten
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
    # hier gehen wir durch alle Werte aus der Watchlist
    # und speichern jeden einzelnen in der assets-Tabelle
    for asset in assets:
        save_asset(asset)