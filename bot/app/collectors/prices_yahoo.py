from datetime import datetime, timezone

import requests


YAHOO_CHART_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
)

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_yahoo_chart(ticker, params):
    url = YAHOO_CHART_URL.format(ticker=ticker)

    response = requests.get(
        url,
        params=params,
        headers=YAHOO_HEADERS,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()
    chart = data.get("chart", {})
    error = chart.get("error")
    results = chart.get("result")

    if error:
        description = error.get(
            "description",
            "Unbekannter Yahoo-Fehler"
        )
        raise ValueError(description)

    if not results:
        return None

    return results[0]


def fetch_daily_prices_from_yahoo(ticker, range_value="1y"):
    result = fetch_yahoo_chart(
        ticker=ticker,
        params={
            "range": range_value,
            "interval": "1d",
            "includePrePost": "false"
        }
    )

    if result is None:
        return []

    timestamps = result.get("timestamp", [])
    quote = result.get("indicators", {}).get("quote", [{}])[0]

    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    volumes = quote.get("volume", [])

    prices = []

    for index, timestamp in enumerate(timestamps):
        close_price = closes[index]

        if close_price is None:
            continue

        date = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        ).strftime("%Y-%m-%d")

        prices.append({
            "ticker": ticker,
            "date": date,
            "open": opens[index],
            "high": highs[index],
            "low": lows[index],
            "close": close_price,
            "volume": volumes[index],
            "source": "yahoo"
        })

    return prices


def parse_utc_timestamp(timestamp_text):
    parsed = datetime.fromisoformat(timestamp_text)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)

    return int(parsed.timestamp())


def fetch_intraday_prices_from_yahoo(
    ticker,
    latest_timestamp=None
):
    params = {
        "interval": "5m",
        "includePrePost": "false"
    }

    if latest_timestamp is None:
        # Beim ersten Import werden fünf Handelstage geladen.
        params["range"] = "5d"
    else:
        latest_unix_timestamp = parse_utc_timestamp(
            latest_timestamp
        )

        # Die letzten zehn Minuten werden erneut geladen,
        # damit eine laufende Kerze aktualisiert werden kann.
        params["period1"] = max(
            0,
            latest_unix_timestamp - 10 * 60
        )

        params["period2"] = int(
            datetime.now(timezone.utc).timestamp()
        ) + 5 * 60

    result = fetch_yahoo_chart(
        ticker=ticker,
        params=params
    )

    if result is None:
        return []

    timestamps = result.get("timestamp", [])
    quote = result.get("indicators", {}).get("quote", [{}])[0]

    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    volumes = quote.get("volume", [])

    prices = []

    for index, timestamp in enumerate(timestamps):
        close_price = closes[index]

        if close_price is None:
            continue

        timestamp_text = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        ).isoformat(timespec="seconds")

        prices.append({
            "ticker": ticker,
            "timestamp": timestamp_text,
            "timeframe": "5m",
            "open": opens[index],
            "high": highs[index],
            "low": lows[index],
            "close": close_price,
            "volume": volumes[index],
            "source": "yahoo"
        })

    return prices