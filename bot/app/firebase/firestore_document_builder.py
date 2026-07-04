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


def build_bot_status_document(bot_run, synced_at):
    """
    Baut ein Firestore-Dokument für den letzten Botlauf.

    Das Dokument wird später unter bot_status/latest gespeichert.
    Die Android-App kann dadurch den aktuellen Zustand des Bots anzeigen:
    - Zeitpunkt des letzten Laufs
    - erfolgreicher oder fehlgeschlagener Lauf
    - Anzahl verarbeiteter Assets
    - Anzahl gespeicherter Signale
    - mögliche Fehlermeldung
    """
    document = {
        "runId": bot_run.get("id"),
        "startedAt": bot_run.get("started_at"),
        "finishedAt": bot_run.get("finished_at"),
        "status": bot_run.get("status"),
        "assetsProcessed": bot_run.get("assets_processed"),
        "priceErrors": bot_run.get("price_errors"),
        "signalsSaved": bot_run.get("signals_saved"),
        "errorMessage": bot_run.get("error_message"),
        "syncedAt": synced_at
    }

    return clean_firestore_document(document)