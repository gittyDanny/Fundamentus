from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import update_daily_prices_for_ticker
from app.jobs.fundamentals_update_job import update_fundamentals_for_asset
from app.reports.console_reports import (
    show_saved_assets,
    show_latest_prices,
    show_fundamentals,
    show_quarterly_fundamentals,
    show_fundamental_metrics,
    show_quarterly_fundamental_metrics
)


def find_asset_by_ticker(assets, ticker):
    # hier suchen wir ein Asset aus der Watchlist anhand des Tickers
    for asset in assets:
        if asset["ticker"] == ticker:
            return asset

    return None


def main():
    # Schritt 1: Datenbank vorbereiten
    init_db()

    # Schritt 2: Watchlist laden und speichern
    assets = load_watchlist()
    save_assets(assets)

    # Schritt 3: gespeicherte Assets anzeigen
    show_saved_assets()

    # Schritt 4: Kursdaten für TSLA aktualisieren
    ticker = "TSLA"
    price_result = update_daily_prices_for_ticker(ticker)
    show_latest_prices(ticker)

    # Schritt 5: TSLA aus der Watchlist suchen
    selected_asset = find_asset_by_ticker(assets, ticker)

    # Schritt 6: Fundamentaldaten für TSLA aktualisieren
    if selected_asset:
        fundamentals_result = update_fundamentals_for_asset(selected_asset)
        show_fundamentals(ticker)
        show_quarterly_fundamentals(ticker)
        show_fundamental_metrics(ticker)
        show_quarterly_fundamental_metrics(ticker)
    else:
        fundamentals_result = {
            "ticker": ticker,
            "status": "error",
            "reason": f"{ticker} nicht in Watchlist gefunden",
            "loaded_rows": 0,
            "saved_rows": 0,
            "deleted_rows": 0
        }

    print("\nFundamentus wurde erfolgreich ausgeführt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{price_result['loaded_rows']} Kurszeilen für {ticker} von Yahoo geladen.")
    print(f"{price_result['new_rows']} neue Kurszeilen gespeichert.")
    print(f"{fundamentals_result['deleted_rows']} alte Fundamentaldaten für {ticker} gelöscht.")
    print(f"{fundamentals_result['loaded_rows']} Fundamentaldaten für {ticker} verarbeitet.")
    print(f"{fundamentals_result['saved_rows']} Fundamentaldaten gespeichert.")
    print(f"Fundamentaldaten-Status: {fundamentals_result['status']}")


if __name__ == "__main__":
    main()