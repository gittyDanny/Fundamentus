from pathlib import Path
import sqlite3
import yaml


DB_PATH = Path("data/fundamentus.db")
WATCHLIST_PATH = Path("config/watchlist.yaml")


def create_database():
    # hier stellen wir sicher, dass der data-Ordner existiert,
    # weil SQLite sonst keine Datenbankdatei anlegen kann
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # hier verbinden wir uns mit der lokalen SQLite-Datenbank
    # falls die Datei noch nicht existiert, wird sie automatisch erstellt
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # hier erstellen wir die assets-Tabelle,
    # in der unsere beobachteten Aktien gespeichert werden
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        name TEXT,
        asset_type TEXT,
        region TEXT,
        currency TEXT,
        sector TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def load_watchlist():
    # hier prüfen wir zuerst, ob unsere Watchlist-Datei überhaupt existiert
    if not WATCHLIST_PATH.exists():
        raise FileNotFoundError("config/watchlist.yaml wurde nicht gefunden")

    # hier öffnen wir die YAML-Datei und lesen ihren Inhalt ein
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # hier holen wir die Liste unter assets heraus
    # falls assets fehlt, nehmen wir einfach eine leere Liste
    assets = data.get("assets", [])

    return assets


def save_asset(asset):
    # hier verbinden wir uns wieder mit der Datenbank
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # hier speichern wir ein einzelnes Asset aus der Watchlist
    # INSERT OR IGNORE sorgt dafür, dass derselbe Ticker nicht doppelt gespeichert wird
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


def save_watchlist_to_database(assets):
    # hier gehen wir durch alle Assets aus der Watchlist
    # und speichern sie nacheinander in der Datenbank
    for asset in assets:
        save_asset(asset)


def show_saved_assets():
    # hier lesen wir aus der Datenbank aus,
    # welche Assets wirklich gespeichert sind
    conn = sqlite3.connect(DB_PATH)
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


def main():
    # Schritt 1: Datenbank und Tabelle vorbereiten
    create_database()

    # Schritt 2: Watchlist aus YAML-Datei laden
    assets = load_watchlist()

    # Schritt 3: Watchlist in die Datenbank speichern
    save_watchlist_to_database(assets)

    # Schritt 4: anzeigen, was jetzt wirklich in der Datenbank steht
    show_saved_assets()

    print("\nFundamentus wurde erfolgreich ausgeführt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")


if __name__ == "__main__":
    main()