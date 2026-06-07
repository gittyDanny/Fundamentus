import requests


SEC_TICKER_MAPPING_URL = "https://www.sec.gov/files/company_tickers.json"


def fetch_sec_ticker_mapping():
    # hier holen wir die offizielle SEC-Ticker-Liste
    # diese Liste verbindet Börsenticker wie AAPL oder MSFT mit der CIK
    headers = {
        "User-Agent": "FundamentusBot/0.1 contact: local-development"
    }

    response = requests.get(
        SEC_TICKER_MAPPING_URL,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def normalize_cik(cik_value):
    # SEC liefert CIKs teilweise als Zahl
    # wir speichern sie aber sauber als 10-stelligen String mit führenden Nullen
    return str(cik_value).zfill(10)


def build_ticker_to_cik_map(mapping_data):
    # die SEC liefert ein Dictionary mit nummerischen Keys
    # wir bauen daraus ein einfaches Mapping: Ticker -> CIK
    ticker_to_cik = {}

    for item in mapping_data.values():
        ticker = item.get("ticker")
        cik = item.get("cik_str")

        if ticker and cik:
            ticker_to_cik[ticker.upper()] = normalize_cik(cik)

    return ticker_to_cik


def resolve_cik_for_ticker(ticker):
    # hier suchen wir für einen einzelnen Ticker die passende CIK
    # wenn nichts gefunden wird, geben wir None zurück
    mapping_data = fetch_sec_ticker_mapping()
    ticker_to_cik = build_ticker_to_cik_map(mapping_data)

    return ticker_to_cik.get(ticker.upper())


def resolve_ciks_for_assets(assets):
    # hier ergänzen wir CIKs automatisch für Assets, falls möglich
    # deutsche .DE-Ticker und ETFs bleiben meistens ohne CIK, das ist okay
    mapping_data = fetch_sec_ticker_mapping()
    ticker_to_cik = build_ticker_to_cik_map(mapping_data)

    updated_assets = []

    for asset in assets:
        ticker = asset["ticker"]
        asset_type = asset.get("asset_type")
        region = asset.get("region")
        existing_cik = asset.get("cik")

        # wenn schon eine CIK in der Watchlist steht, lassen wir sie bestehen
        if existing_cik:
            updated_assets.append(asset)
            continue

        # aktuell versuchen wir die automatische CIK-Auflösung nur für US-Aktien
        # ETFs und deutsche/europäische Ticker sollen erstmal nicht in SEC-Fundamentals laufen
        if asset_type == "stock" and region == "US":
            cik = ticker_to_cik.get(ticker.upper())

            if cik:
                asset["cik"] = cik
                asset["fundamentals_source"] = "sec"
            else:
                asset["fundamentals_source"] = "none"

        else:
            asset["fundamentals_source"] = "none"

        updated_assets.append(asset)

    return updated_assets