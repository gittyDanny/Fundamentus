from app.database import get_connection


def deactivate_all_assets():
    # hier setzen wir erstmal alle Assets auf inaktiv
    # danach aktivieren wir nur die Assets wieder, die aktuell in der Watchlist stehen
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE assets
    SET is_active = 0
    """)

    conn.commit()
    conn.close()


def save_asset(asset):
    # hier speichern wir ein einzelnes Asset aus der Watchlist
    # wenn der Ticker schon existiert, aktualisieren wir die Stammdaten
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO assets
    (ticker, name, asset_type, region, currency, sector, cik, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    ON CONFLICT(ticker) DO UPDATE SET
        name = excluded.name,
        asset_type = excluded.asset_type,
        region = excluded.region,
        currency = excluded.currency,
        sector = excluded.sector,
        cik = excluded.cik,
        is_active = 1
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
    # hier synchronisieren wir die Datenbank mit der aktuellen Watchlist
    # entfernte Assets bleiben historisch erhalten, werden aber deaktiviert
    deactivate_all_assets()

    for asset in assets:
        save_asset(asset)