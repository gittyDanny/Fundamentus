from pathlib import Path
import yaml


WATCHLIST_PATH = Path("config/watchlist.yaml")


def load_watchlist():
    # hier prüfen wir, ob die Watchlist-Datei vorhanden ist
    # ohne Watchlist weiß Fundamentus nicht, welche Aktien er beobachten soll
    if not WATCHLIST_PATH.exists():
        raise FileNotFoundError("config/watchlist.yaml wurde nicht gefunden")

    # hier lesen wir die YAML-Datei ein
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # hier holen wir die Liste unter assets raus
    # falls nichts drinsteht, geben wir eine leere Liste zurück
    return data.get("assets", [])