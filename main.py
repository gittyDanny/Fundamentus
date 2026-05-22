from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import update_daily_prices_for_ticker
from app.reports.console_reports import show_saved_assets, show_latest_prices


def main():
    # Schritt 1: Datenbank vorbereiten
    init_db()

    # Schritt 2: Watchlist laden und speichern
    assets = load_watchlist()
    save_assets(assets)

    # Schritt 3: gespeicherte Assets anzeigen
    show_saved_assets()

    # Schritt 4: Kursdaten für einen Test-Ticker aktualisieren
    ticker = "TSLA"
    result = update_daily_prices_for_ticker(ticker)

    # Schritt 5: letzte Kurse anzeigen
    show_latest_prices(ticker)

    print("\nFundamentus wurde erfolgreich ausgeführt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{result['loaded_rows']} Kurszeilen für {ticker} von Yahoo geladen.")
    print(f"{result['new_rows']} neue Kurszeilen gespeichert.")


if __name__ == "__main__":
    main()