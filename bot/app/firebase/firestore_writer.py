from app.firebase.firestore_formatting import build_document_id
from app.firebase.firestore_document_builder import (
    build_asset_document,
    build_signal_document,
    build_bot_status_document
)


def write_assets_to_firestore(db, assets, synced_at):
    """
    Schreibt aktive Assets nach Firestore.

    Eingabe:
    - db: Firestore-Client
    - assets: Liste von Asset-Dictionaries aus SQLite
    - synced_at: Zeitpunkt der Synchronisierung

    Firestore-Ziel:
    Collection: assets
    Dokument-ID: Ticker, z.B. MU oder ASML
    """
    written_count = 0

    for asset in assets:
        ticker = asset.get("ticker")

        # Ohne Ticker können wir keine sinnvolle Dokument-ID bauen.
        if not ticker:
            continue

        document_id = build_document_id(ticker)
        document = build_asset_document(asset, synced_at)

        db.collection("assets").document(document_id).set(document)

        written_count += 1

    return written_count


def write_latest_signals_to_firestore(db, signals, synced_at):
    """
    Schreibt die neuesten Signale nach Firestore.

    Eingabe:
    - db: Firestore-Client
    - signals: Liste von Signal-Dictionaries aus SQLite
    - synced_at: Zeitpunkt der Synchronisierung

    Firestore-Ziel:
    Collection: latest_signals
    Dokument-ID: Ticker, z.B. MU oder ASML
    """
    written_count = 0

    for signal in signals:
        ticker = signal.get("ticker")

        # Ohne Ticker können wir keine sinnvolle Dokument-ID bauen.
        if not ticker:
            continue

        document_id = build_document_id(ticker)
        document = build_signal_document(signal, synced_at)

        db.collection("latest_signals").document(document_id).set(document)

        written_count += 1

    return written_count


def write_bot_status_to_firestore(db, bot_run, synced_at):
    """
    Schreibt den letzten Botlauf nach Firestore.

    Firestore-Ziel:
    Collection: bot_status
    Dokument-ID: latest

    Es gibt immer nur ein aktuelles Statusdokument.
    Bei jedem Botlauf wird dieses Dokument überschrieben.
    """
    if bot_run is None:
        return 0

    document = build_bot_status_document(bot_run, synced_at)

    db.collection("bot_status").document("latest").set(document)

    return 1