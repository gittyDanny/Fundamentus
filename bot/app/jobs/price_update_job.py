from app.collectors.prices_yahoo import (
    fetch_daily_prices_from_yahoo,
    fetch_intraday_prices_from_yahoo
)
from app.storage.save_prices import (
    count_daily_prices_for_ticker,
    get_latest_intraday_timestamp,
    save_daily_prices,
    save_intraday_prices
)


MINIMUM_DAILY_ROWS = 55


def has_sufficient_daily_history_for_assets(
    assets,
    minimum_rows=MINIMUM_DAILY_ROWS
):
    for asset in assets:
        ticker = asset["ticker"]
        row_count = count_daily_prices_for_ticker(ticker)

        if row_count < minimum_rows:
            return False

    return True


def update_daily_prices_for_ticker(ticker):
    existing_rows = count_daily_prices_for_ticker(ticker)

    # Erster Import: ein Jahr.
    # Spätere Aktualisierungen: nur fünf Tage.
    range_value = (
        "1y"
        if existing_rows < MINIMUM_DAILY_ROWS
        else "5d"
    )

    prices = fetch_daily_prices_from_yahoo(
        ticker=ticker,
        range_value=range_value
    )

    changed_rows = save_daily_prices(prices)

    return {
        "ticker": ticker,
        "loaded_rows": len(prices),
        "new_rows": changed_rows
    }


def update_daily_prices_for_assets(assets):
    results = []

    for asset in assets:
        ticker = asset["ticker"]

        try:
            result = update_daily_prices_for_ticker(ticker)
            result["status"] = "ok"

        except Exception as error:
            result = {
                "ticker": ticker,
                "loaded_rows": 0,
                "new_rows": 0,
                "status": "error",
                "error": str(error)
            }

        results.append(result)

    return results


def update_intraday_prices_for_ticker(ticker):
    latest_timestamp = get_latest_intraday_timestamp(ticker)

    prices = fetch_intraday_prices_from_yahoo(
        ticker=ticker,
        latest_timestamp=latest_timestamp
    )

    changed_rows = save_intraday_prices(prices)

    return {
        "ticker": ticker,
        "loaded_rows": len(prices),
        "new_rows": changed_rows
    }


def update_intraday_prices_for_assets(assets):
    results = []

    for asset in assets:
        ticker = asset["ticker"]

        try:
            result = update_intraday_prices_for_ticker(ticker)
            result["status"] = "ok"

        except Exception as error:
            result = {
                "ticker": ticker,
                "loaded_rows": 0,
                "new_rows": 0,
                "status": "error",
                "error": str(error)
            }

        results.append(result)

    return results