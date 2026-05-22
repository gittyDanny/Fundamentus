from pathlib import Path
from datetime import datetime
import sqlite3
import yaml
import requests


DB_PATH = Path("data/fundamentus.db")
WATCHLIST_PATH = Path("config/watchlist.yaml")


def create_database():
    # hier stellen wir sicher, dass der data-Ordner existiert,
    # weil SQLite sonst keine Datenbankdatei anlegen kann
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # hier verbinden wir uns mit unserer lokalen SQLite-Datenbank
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # hier speichern wir die Stammdaten unserer beobachteten Aktien
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

    # hier speichern wir Tageskurse,
    # also Open, High, Low, Close und Volume pro Datum
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        source TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, date, source)
    );
    """)

    conn.commit()
    conn.close()


def load_watchlist():
    # hier prüfen wir zuerst, ob unsere Watchlist-Datei überhaupt existiert
    if not WATCHLIST_PATH.exists():
        raise FileNotFoundError("config/watchlist.yaml wurde nicht gefunden")

    # hier lesen wir die YAML-Datei ein
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # hier holen wir die Liste aus dem assets-Bereich raus
    return data.get("assets", [])


def save_asset(asset):
    # hier speichern wir ein einzelnes Asset aus der Watchlist
    conn = sqlite3.connect(DB_PATH)
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


def save_watchlist_to_database(assets):
    # hier gehen wir durch alle Assets aus der Watchlist
    # und speichern sie nacheinander in der Datenbank
    for asset in assets:
        save_asset(asset)


def show_saved_assets():
    # hier zeigen wir an, welche Assets aktuell in der Datenbank stehen
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


def fetch_daily_prices_from_yahoo(ticker):
    # hier holen wir Tageskurse von Yahoo als JSON-Daten
    # das ist für unseren Prototyp angenehmer als Stooq, weil wir keinen API-Key brauchen
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    params = {
        "range": "1y",      # hier sagen wir: wir wollen ungefähr ein Jahr Kursdaten
        "interval": "1d"    # hier sagen wir: wir wollen Tageskerzen
    }

    headers = {
        # hier geben wir einen normalen User-Agent mit,
        # damit der Request weniger nach kaputtem Bot aussieht
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # hier holen wir den eigentlichen Ergebnisblock aus der Yahoo-Antwort
    result = data["chart"]["result"][0]

    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    opens = quote["open"]
    highs = quote["high"]
    lows = quote["low"]
    closes = quote["close"]
    volumes = quote["volume"]

    prices = []

    # hier laufen wir durch alle Tageswerte gleichzeitig durch
    for index in range(len(timestamps)):
        # Yahoo gibt Unix-Zeitstempel zurück,
        # deshalb wandeln wir sie in ein normales Datum um
        date = datetime.fromtimestamp(timestamps[index]).strftime("%Y-%m-%d")

        open_price = opens[index]
        high_price = highs[index]
        low_price = lows[index]
        close_price = closes[index]
        volume = volumes[index]

        # hier überspringen wir kaputte oder leere Tage,
        # weil APIs manchmal None-Werte liefern
        if close_price is None:
            continue

        price = {
            "ticker": ticker,
            "date": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume,
            "source": "yahoo"
        }

        prices.append(price)

    return prices


def save_daily_prices(prices):
    # hier speichern wir alle Tageskurse in die price_daily-Tabelle
    # INSERT OR IGNORE verhindert doppelte Kurse für denselben Tag
    conn = sqlite3.connect(DB_PATH)
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


def show_latest_prices(ticker, limit=5):
    # hier zeigen wir die letzten gespeicherten Tageskurse für einen Ticker an
    conn = sqlite3.connect(DB_PATH)
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
            f"Open {open_price}, High {high}, Low {low}, Close {close}, Volume {volume}"
        )


def main():
    # Schritt 1: Datenbank und Tabellen vorbereiten
    create_database()

    # Schritt 2: Watchlist laden und speichern
    assets = load_watchlist()
    save_watchlist_to_database(assets)

    # Schritt 3: gespeicherte Assets anzeigen
    show_saved_assets()

    # Schritt 4: erste echte Kursdaten holen
    # wir starten mit TSLA, weil die Aktie volatiler ist und später für Signale spannender wird
    ticker = "TSLA"

    prices = fetch_daily_prices_from_yahoo(ticker)

    # Schritt 5: Kursdaten in SQLite speichern
    new_rows = save_daily_prices(prices)

    # Schritt 6: zeigen, was gespeichert wurde
    show_latest_prices(ticker)

    print("\nFundamentus wurde erfolgreich ausgeführt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{len(prices)} Kurszeilen für {ticker} von Stooq geladen.")
    print(f"{new_rows} neue Kurszeilen gespeichert.")


if __name__ == "__main__":
    main()