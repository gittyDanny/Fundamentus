from app.collectors.prices_yahoo import fetch_daily_prices_from_yahoo
from app.storage.save_prices import save_daily_prices


def update_daily_prices_for_ticker(ticker):
    # hier bündeln wir den kompletten Ablauf für einen Ticker:
    # Kursdaten holen, speichern und ein kleines Ergebnis zurückgeben
    prices = fetch_daily_prices_from_yahoo(ticker)
    new_rows = save_daily_prices(prices)

    result = {
        "ticker": ticker,
        "loaded_rows": len(prices),
        "new_rows": new_rows
    }

    return result


def update_daily_prices_for_assets(assets):
    # hier gehen wir durch alle Assets aus der Watchlist
    # und aktualisieren die Kursdaten für jedes einzelne Asset
    results = []

    for asset in assets:
        ticker = asset["ticker"]

        try:
            result = update_daily_prices_for_ticker(ticker)
            result["status"] = "ok"

        except Exception as error:
            # hier fangen wir Fehler pro Ticker ab,
            # damit nicht die ganze Aktualisierung stirbt, nur weil ein Ticker Probleme macht
            result = {
                "ticker": ticker,
                "loaded_rows": 0,
                "new_rows": 0,
                "status": "error",
                "error": str(error)
            }

        results.append(result)

    return results
