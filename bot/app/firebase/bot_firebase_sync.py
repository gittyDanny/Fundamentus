from app.firebase.firebase_client import get_firestore_client_if_configured
from app.firebase.firestore_formatting import get_current_utc_timestamp
from app.firebase.sqlite_bot_data_reader import (
    get_active_assets_from_sqlite,
    get_latest_signals_from_sqlite
)
from app.firebase.firestore_writer import (
    write_assets_to_firestore,
    write_latest_signals_to_firestore
)


def sync_assets_and_signals_to_firebase():
    """
    Synchronisiert Assets und aktuelle Signale nach Firebase.

    Diese Funktion koordiniert nur den Ablauf:
    - Firestore-Client holen
    - lokale Botdaten aus SQLite lesen
    - Assets und Signale nach Firestore schreiben
    - Ergebnis als Dictionary zurückgeben

    Wenn Firebase noch nicht eingerichtet ist, wird die Synchronisierung
    sauber übersprungen und der Bot kann trotzdem weiterlaufen.
    """
    synced_at = get_current_utc_timestamp()

    result = {
        "status": "skipped",
        "reason": None,
        "asset_documents_written": 0,
        "signal_documents_written": 0,
        "synced_at": synced_at,
        "error": None
    }

    db = get_firestore_client_if_configured()

    if db is None:
        result["reason"] = "Firebase ist nicht konfiguriert."
        return result

    try:
        assets = get_active_assets_from_sqlite()
        signals = get_latest_signals_from_sqlite()

        asset_count = write_assets_to_firestore(
            db=db,
            assets=assets,
            synced_at=synced_at
        )

        signal_count = write_latest_signals_to_firestore(
            db=db,
            signals=signals,
            synced_at=synced_at
        )

        result["status"] = "success"
        result["reason"] = "Assets und Signale wurden nach Firebase synchronisiert."
        result["asset_documents_written"] = asset_count
        result["signal_documents_written"] = signal_count

        return result

    except Exception as error:
        result["status"] = "error"
        result["reason"] = "Firebase-Synchronisierung fehlgeschlagen."
        result["error"] = str(error)

        return result