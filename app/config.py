from pathlib import Path
import yaml

WATCHLIST_PATH = Path("config/watchlist.yaml")


def load_watchlist():
    # hier lesen wir die YAML-Datei ein,
    # damit unsere Aktien nicht hart im Code stehen
    if not WATCHLIST_PATH.exists():
        raise FileNotFoundError("config/watchlist.yaml wurde nicht gefunden")

    with open(WATCHLIST_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # hier holen wir die Liste unter dem Schlüssel assets raus
    # falls nichts drinsteht, geben wir eine leere Liste zurück
    return data.get("assets", [])