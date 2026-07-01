from pathlib import Path
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Standardpfad zur lokalen Firebase-Service-Account-Datei.
# Diese JSON-Datei enthält geheime Zugangsdaten und darf NICHT ins GitHub-Repo.
#
# Ergebnis des Pfads:
# bot/secrets/firebase-service-account.json
DEFAULT_SERVICE_ACCOUNT_PATH = (
    Path(__file__).resolve().parents[2]
    / "secrets"
    / "firebase-service-account.json"
)


def get_service_account_path():
    """
    Ermittelt den Pfad zur Firebase-Service-Account-Datei.

    Reihenfolge:
    1. Wenn FIREBASE_SERVICE_ACCOUNT_PATH gesetzt ist, wird dieser Pfad genutzt.
    2. Sonst wird bot/secrets/firebase-service-account.json genutzt.

    Vorteil:
    Lokal und auf dem Raspberry Pi können unterschiedliche Pfade genutzt werden,
    ohne den Code ändern zu müssen.
    """
    custom_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

    if custom_path:
        return Path(custom_path)

    return DEFAULT_SERVICE_ACCOUNT_PATH


def firebase_is_configured():
    """
    Prüft, ob Firebase lokal eingerichtet ist.

    Die Funktion schaut nur, ob die Service-Account-Datei existiert.
    Es wird noch keine Verbindung zu Firebase aufgebaut.
    """
    service_account_path = get_service_account_path()

    return service_account_path.exists()


def get_firebase_app():
    """
    Initialisiert die Firebase-App.

    Firebase darf pro Python-Prozess nur einmal initialisiert werden.
    Deshalb prüfen wir zuerst, ob bereits eine Firebase-App existiert.

    Falls noch keine App existiert:
    - Service-Account-Datei suchen
    - Credential laden
    - Firebase-App initialisieren
    """
    try:
        # Falls Firebase schon initialisiert wurde, nutzen wir diese App weiter.
        return firebase_admin.get_app()

    except ValueError:
        # Falls noch keine Firebase-App existiert, initialisieren wir sie neu.
        service_account_path = get_service_account_path()

        if not service_account_path.exists():
            raise FileNotFoundError(
                "Firebase-Service-Account-Datei nicht gefunden: "
                f"{service_account_path}. "
                "Lege die Datei lokal unter bot/secrets/firebase-service-account.json ab "
                "oder setze FIREBASE_SERVICE_ACCOUNT_PATH."
            )

        credential = credentials.Certificate(str(service_account_path))

        return firebase_admin.initialize_app(credential)


def get_firestore_client():
    """
    Gibt einen Firestore-Client zurück.

    Firestore ist die Firebase-Datenbank, in die der Bot später schreibt:
    - Assets
    - letzte Signale
    - Fundamentaldaten-Zusammenfassung
    - Bot-Status
    """
    firebase_app = get_firebase_app()

    return firestore.client(app=firebase_app)


def get_firestore_client_if_configured():
    """
    Gibt einen Firestore-Client zurück, wenn Firebase eingerichtet ist.
    Falls Firebase fehlt, wird None zurückgegeben.
    """
    # Ohne Service-Account-Datei soll der Bot lokal nicht abstürzen.
    if not firebase_is_configured():
        return None

    return get_firestore_client()