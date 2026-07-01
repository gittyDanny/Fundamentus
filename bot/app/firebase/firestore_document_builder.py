from app.firebase.firestore_formatting import clean_firestore_document


def build_asset_document(asset, synced_at):
    """
    Baut ein Firestore-Dokument für ein Asset.

    Eingabe:
    Ein Asset-Dictionary aus SQLite.

    Ausgabe:
    Ein Dictionary, das später in Firestore unter assets/{ticker} gespeichert werden kann.

    Beispiel:
    assets/MU
    assets/ASML
    assets/AAPL
    """
    document = {
        "ticker": asset.get("ticker"),
        "name": asset.get("name"),
        "assetType": asset.get("asset_type"),
        "region": asset.get("region"),
        "currency": asset.get("currency"),
        "sector": asset.get("sector"),
        "cik": asset.get("cik"),
        "isActive": bool(asset.get("is_active")),
        "dataSource": asset.get("data_source"),
        "syncedAt": synced_at
    }

    return clean_firestore_document(document)


def build_signal_document(signal, synced_at):
    """
    Baut ein Firestore-Dokument für das neueste Signal eines Tickers.

    Eingabe:
    Ein Signal-Dictionary aus SQLite.

    Ausgabe:
    Ein Dictionary, das später in Firestore unter latest_signals/{ticker}
    gespeichert werden kann.

    Beispiel:
    latest_signals/MU
    latest_signals/ASML
    latest_signals/AAPL
    """
    document = {
        "ticker": signal.get("ticker"),
        "signal": signal.get("signal"),
        "score": signal.get("score"),
        "reason": signal.get("reason"),
        "close": signal.get("close"),
        "sma20": signal.get("sma_20"),
        "change20dPct": signal.get("change_20d_pct"),
        "source": signal.get("source"),
        "createdAt": signal.get("created_at"),
        "syncedAt": synced_at
    }

    return clean_firestore_document(document)