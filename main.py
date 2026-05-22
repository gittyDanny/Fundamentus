from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets


def main():
    # hier starten wir erstmal die Datenbank
    # dadurch werden die Tabellen angelegt, falls sie noch fehlen
    init_db()

    # hier laden wir unsere Watchlist aus der YAML-Datei
    assets = load_watchlist()

    # hier speichern wir die Watchlist in der Datenbank
    save_assets(assets)

    print("Fundamentus wurde gestartet.")
    print("Datenbank wurde geprüft oder neu erstellt.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")


if __name__ == "__main__":
    main()