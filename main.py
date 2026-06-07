from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import update_daily_prices_for_assets
from app.jobs.signal_update_job import update_signals_for_assets
from app.reports.signal_reports import show_latest_signals
from app.reports.console_reports import (
    show_saved_assets,
    show_latest_prices
)


def print_price_update_results(price_results):
    # hier geben wir für jedes Asset aus, ob der Kursdaten-Import funktioniert hat
    # dadurch sehen wir direkt, welcher Ticker Probleme macht und welcher sauber läuft
    print("\nKursdaten-Update für Watchlist:")

    for result in price_results:
        ticker = result.get("ticker")
        status = result.get("status")
        loaded_rows = result.get("loaded_rows", 0)
        new_rows = result.get("new_rows", 0)

        if status == "ok":
            print(f"- {ticker}: {loaded_rows} Kurszeilen geladen, {new_rows} neue Zeilen gespeichert")
        else:
            error = result.get("error", "Unbekannter Fehler")
            print(f"- {ticker}: Fehler beim Kursdaten-Update: {error}")


def show_latest_prices_for_assets(assets):
    # hier zeigen wir für jedes Asset die letzten gespeicherten Kurse an
    # das ist praktisch, weil wir direkt sehen, ob die Daten wirklich in der DB gelandet sind
    print("\nLetzte gespeicherte Kurse pro Asset:")

    for asset in assets:
        ticker = asset["ticker"]
        show_latest_prices(ticker)

def print_signal_results(signal_result):
    # hier geben wir die frisch berechneten Signale aus,
    # damit wir direkt im Terminal sehen, was der Bot analysiert hat
    print("\nSignale aus Kursanalyse:")

    for signal in signal_result["signals"]:
        ticker = signal["ticker"]
        signal_name = signal["signal"]
        score = signal["score"]
        reason = signal["reason"]
        close = signal["close"]
        sma_20 = signal["sma_20"]
        change_20d_pct = signal["change_20d_pct"]

        print(
            f"- {ticker}: {signal_name} | "
            f"Score: {score} | "
            f"Close: {close} | "
            f"SMA20: {sma_20} | "
            f"20D: {change_20d_pct} | "
            f"{reason}"
        )


def main():
    print("\nFundamentus Bot startet...")

    # Schritt 1: Datenbank vorbereiten
    # hier werden die Tabellen angelegt, falls sie noch nicht existieren
    init_db()

    # Schritt 2: Watchlist laden
    # die Watchlist ist unsere zentrale Quelle dafür, welche Assets der Bot beobachten soll
    assets = load_watchlist()

    # Schritt 3: Watchlist in der Datenbank speichern
    # dadurch kennt die Datenbank alle Ticker, Namen, Regionen und Sektoren aus der YAML-Datei
    save_assets(assets)

    # Schritt 4: gespeicherte Assets anzeigen
    # hier prüfen wir kurz, ob die Assets sauber in der Datenbank stehen
    show_saved_assets()

    # Schritt 5: Kursdaten für alle Assets aktualisieren
    # vorher hatten wir nur TSLA, jetzt läuft der Bot durch die komplette Watchlist
    price_results = update_daily_prices_for_assets(assets)

    # Schritt 6: Ergebnis vom Kursdaten-Update sauber ausgeben
    # so sehen wir direkt, wie viele Zeilen geladen und neu gespeichert wurden
    print_price_update_results(price_results)

    # Schritt 7: letzte Kurse für alle Assets anzeigen
    # damit haben wir ein sichtbares erstes Ergebnis im Terminal
    show_latest_prices_for_assets(assets)

    # Schritt 8: Signale für alle Assets berechnen
    # der Bot nutzt dafür die gespeicherten Kursdaten aus der Datenbank
    signal_result = update_signals_for_assets(assets)

    # Schritt 9: Signale im Terminal anzeigen
    # damit sehen wir direkt, welche Assets BUY, HOLD oder SELL bekommen haben
    print_signal_results(signal_result)

    # Schritt 10: gespeicherte Signale nochmal aus der Datenbank anzeigen
    # dadurch prüfen wir, ob die Analyse wirklich persistiert wurde
    show_latest_signals()

    print("\nFundamentus Bot-Run abgeschlossen.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{signal_result['saved_rows']} Signale gespeichert.")


if __name__ == "__main__":
    main()