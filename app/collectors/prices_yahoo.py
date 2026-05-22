from datetime import datetime
import requests


def fetch_daily_prices_from_yahoo(ticker):
    # hier holen wir Tageskurse von Yahoo als JSON-Daten
    # ticker ist z.B. TSLA, NVDA oder AMD
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    params = {
        "range": "1y",
        "interval": "1d"
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
        date = datetime.fromtimestamp(timestamps[index]).strftime("%Y-%m-%d")

        open_price = opens[index]
        high_price = highs[index]
        low_price = lows[index]
        close_price = closes[index]
        volume = volumes[index]

        # hier überspringen wir leere Tage,
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