from app.collectors.fundamentals_sec import fetch_company_facts_from_sec
from app.collectors.fundamentals_yahoo import fetch_yahoo_fundamentals
from app.normalizers.fundamentals_sec import normalize_sec_company_facts
from app.storage.save_fundamentals import (
    delete_fundamentals_for_ticker,
    save_fundamentals
)


def should_use_yahoo_fallback(asset):
    # hier entscheiden wir, wann Yahoo-Fundamentals genutzt werden sollen
    # aktuell nehmen wir Yahoo für Aktien ohne CIK, z.B. deutsche .DE-Ticker
    asset_type = asset.get("asset_type")
    cik = asset.get("cik")

    if asset_type != "stock":
        return False

    if cik:
        return False

    return True


def update_fundamentals_from_sec(asset):
    # hier aktualisieren wir Fundamentaldaten über SEC
    # das ist für US-Aktien mit CIK die sauberere Quelle
    ticker = asset["ticker"]
    cik = asset.get("cik")

    company_facts = fetch_company_facts_from_sec(cik)
    fundamentals = normalize_sec_company_facts(ticker, company_facts)

    deleted_rows = delete_fundamentals_for_ticker(ticker)
    saved_rows = save_fundamentals(fundamentals)

    return {
        "ticker": ticker,
        "status": "ok",
        "source": "sec",
        "reason": None,
        "loaded_rows": len(fundamentals),
        "saved_rows": saved_rows,
        "deleted_rows": deleted_rows
    }


def update_fundamentals_from_yahoo(asset):
    # hier aktualisieren wir Fundamentaldaten über Yahoo
    # das ist unser Fallback für deutsche/europäische Aktien ohne CIK
    ticker = asset["ticker"]

    fundamentals = fetch_yahoo_fundamentals(ticker)

    if not fundamentals:
        return {
            "ticker": ticker,
            "status": "skipped",
            "source": "yahoo",
            "reason": "Keine Yahoo-Fundamentaldaten gefunden",
            "loaded_rows": 0,
            "saved_rows": 0,
            "deleted_rows": 0
        }

    deleted_rows = delete_fundamentals_for_ticker(ticker)
    saved_rows = save_fundamentals(fundamentals)

    return {
        "ticker": ticker,
        "status": "ok",
        "source": "yahoo",
        "reason": None,
        "loaded_rows": len(fundamentals),
        "saved_rows": saved_rows,
        "deleted_rows": deleted_rows
    }


def update_fundamentals_for_asset(asset):
    # hier aktualisieren wir Fundamentaldaten für ein Asset aus der Watchlist
    # SEC wird bevorzugt, Yahoo ist der Fallback für Aktien ohne CIK
    ticker = asset["ticker"]
    cik = asset.get("cik")

    try:
        if cik:
            return update_fundamentals_from_sec(asset)

        if should_use_yahoo_fallback(asset):
            return update_fundamentals_from_yahoo(asset)

        return {
            "ticker": ticker,
            "status": "skipped",
            "source": None,
            "reason": "Keine passende Fundamentaldatenquelle vorhanden",
            "loaded_rows": 0,
            "saved_rows": 0,
            "deleted_rows": 0
        }

    except Exception as error:
        return {
            "ticker": ticker,
            "status": "error",
            "source": None,
            "reason": str(error),
            "loaded_rows": 0,
            "saved_rows": 0,
            "deleted_rows": 0
        }


def update_fundamentals_for_assets(assets):
    # hier aktualisieren wir Fundamentaldaten für alle Assets
    # je nach Asset wird SEC oder Yahoo genutzt
    results = []

    for asset in assets:
        result = update_fundamentals_for_asset(asset)
        results.append(result)

    return results