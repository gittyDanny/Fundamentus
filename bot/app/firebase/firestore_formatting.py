import math
from datetime import datetime, timezone


def get_current_utc_timestamp():
    """
    Erstellt einen aktuellen Zeitstempel in UTC.

    UTC ist sinnvoll, weil der Raspberry Pi, Firebase und Android-Geräte
    unterschiedliche Zeitzonen haben können.
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_firestore_value(value):
    """
    Bereitet einen einzelnen Wert für Firestore vor.

    Firestore kann normale Python-Werte speichern:
    - Text
    - Zahlen
    - Boolean
    - None
    - Listen
    - Dictionaries

    Problematisch sind ungültige Float-Werte wie NaN oder Infinity.
    Diese werden hier zu None umgewandelt.
    """
    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

        return value

    if isinstance(value, dict):
        return clean_firestore_document(value)

    if isinstance(value, list):
        return [clean_firestore_value(item) for item in value]

    return value


def clean_firestore_document(document):
    """
    Bereitet ein komplettes Firestore-Dokument vor.

    Jedes Feld wird einmal durch clean_firestore_value geschickt.
    Dadurch werden problematische Werte entfernt, bevor sie an Firestore gehen.
    """
    cleaned_document = {}

    for key, value in document.items():
        cleaned_document[key] = clean_firestore_value(value)

    return cleaned_document


def build_document_id(value):
    """
    Baut eine sichere Firestore-Dokument-ID.

    Ticker wie AAPL oder MU können direkt genutzt werden.
    Falls ein Wert aber einen Slash enthält, wird er ersetzt,
    weil Slashes in Firestore-Pfaden eine besondere Bedeutung haben.
    """
    return str(value).replace("/", "_")