from app.firebase.firebase_client import get_firestore_client_if_configured
from app.firebase.firestore_formatting import get_current_utc_timestamp
from app.firebase.sqlite_bot_data_reader import (
    get_active_assets_from_sqlite,
    get_latest_signals_from_sqlite,
    get_latest_bot_run_from_sqlite
)
from app.firebase.firestore_writer import (
    write_assets_to_firestore,
    write_latest_signals_to_firestore,
    write_bot_status_to_firestore
)


def sync_bot_data_to_firestore():
    """
    Synchronisiert die wichtigsten Botdaten nach Firestore.

    Ablauf:
    - Firestore-Client holen
    - aktive Assets aus SQLite lesen
    - aktuelle Signale aus SQLite lesen
    - letzten Botlauf aus SQLite lesen
    - alle vorbereiteten Dokumente nach Firestore schreiben

    Falls Firebase noch nicht eingerichtet ist, wird die Synchronisierung
    übersprungen. Der lokale Bot kann dadurch trotzdem normal weiterlaufen.
    """
    synced_at = get_current_utc_timestamp()

    result = {
        "status": "skipped",
        "reason": None,
        "asset_documents_written": 0,
        "signal_documents_written": 0,
        "bot_status_documents_written": 0,
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
        bot_run = get_latest_bot_run_from_sqlite()

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

        bot_status_count = write_bot_status_to_firestore(
            db=db,
            bot_run=bot_run,
            synced_at=synced_at
        )

        result["status"] = "success"
        result["reason"] = (
            "Assets, Signale und Bot-Status wurden nach Firestore synchronisiert."
        )
        result["asset_documents_written"] = asset_count
        result["signal_documents_written"] = signal_count
        result["bot_status_documents_written"] = bot_status_count

        return result

    except Exception as error:
        result["status"] = "error"
        result["reason"] = "Firestore-Synchronisierung fehlgeschlagen."
        result["error"] = str(error)

        return result