from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.collectors.prices_yahoo import fetch_daily_prices_from_yahoo
from app.storage.save_prices import save_daily_prices
from app.reports.console_reports import show_saved_assets, show_latest_prices


def main():
    # Schritt 1: Datenbank vorbereiten
    init_db()

    # Schritt 2: Watchlist laden und speichern
    assets = load_watchlist()
    save_assets(assets)

    # Schritt 3: gespeicherte Assets anzeigen
    show_saved_assets()

    # Schritt 4: erste Kursdaten holen
    ticker = "TSLA"
    prices = fetch_daily_prices_from_yahoo(ticker)

    # Schritt 5: Kursdaten speichern
    new_rows = save_daily_prices(prices)

    # Schritt 6: letzte Kurse anzeigen
    show_latest_prices(ticker)

    print("\nFundamentus wurde erfolgreich ausgeführt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{len(prices)} Kurszeilen für {ticker} von Yahoo geladen.")
    print(f"{new_rows} neue Kurszeilen gespeichert.")


if __name__ == "__main__":
    main()