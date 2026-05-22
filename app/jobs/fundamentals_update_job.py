from app.collectors.fundamentals_sec import fetch_company_facts_from_sec
from app.normalizers.fundamentals_sec import normalize_sec_company_facts
from app.storage.save_fundamentals import (
    delete_fundamentals_for_ticker,
    save_fundamentals
)


def update_fundamentals_for_asset(asset):
    # hier aktualisieren wir Fundamentaldaten für ein Asset aus der Watchlist
    # dafür brauchen wir aktuell eine CIK, weil die SEC damit arbeitet
    ticker = asset["ticker"]
    cik = asset.get("cik")

    if not cik:
        return {
            "ticker": ticker,
            "status": "skipped",
            "reason": "Keine CIK vorhanden",
            "loaded_rows": 0,
            "saved_rows": 0,
            "deleted_rows": 0
        }

    company_facts = fetch_company_facts_from_sec(cik)
    fundamentals = normalize_sec_company_facts(ticker, company_facts)

    deleted_rows = delete_fundamentals_for_ticker(ticker)
    saved_rows = save_fundamentals(fundamentals)

    return {
        "ticker": ticker,
        "status": "ok",
        "loaded_rows": len(fundamentals),
        "saved_rows": saved_rows,
        "deleted_rows": deleted_rows
    }