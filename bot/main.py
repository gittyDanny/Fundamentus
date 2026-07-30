from app.database import init_db
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import update_daily_prices_for_assets
from app.jobs.signal_update_job import update_signals_for_assets
from app.firebase.bot_firebase_sync import sync_bot_data_to_firestore
from app.reports.signal_reports import show_latest_signals
from app.collectors.sec_ticker_mapping import resolve_ciks_for_assets
from app.reports.console_reports import show_saved_assets
from app.storage.bot_runs import start_bot_run, finish_bot_run
from app.jobs.fundamentals_update_job import (
    should_update_fundamentals,
    update_fundamentals_for_assets
)


def print_price_update_results(price_results):
    # hier geben wir für jedes Asset aus, ob der Kursdaten-Import funktioniert hat
    print("\nKursdaten-Update für Watchlist:")

    for result in price_results:
        ticker = result.get("ticker")
        status = result.get("status")
        loaded_rows = result.get("loaded_rows", 0)
        changed_rows = result.get("new_rows", 0)

        if status == "ok":
            print(
                f"- {ticker}: {loaded_rows} Kurszeilen geladen, "
                f"{changed_rows} Zeilen gespeichert/aktualisiert"
            )
        else:
            error = result.get("error", "Unbekannter Fehler")
            print(f"- {ticker}: Fehler beim Kursdaten-Update: {error}")


def print_fundamental_update_results(fundamental_results):
    # hier geben wir aus, bei welchen Assets Fundamentaldaten geladen wurden
    print("\nFundamentaldaten-Update:")

    for result in fundamental_results:
        ticker = result.get("ticker")
        status = result.get("status")
        source = result.get("source")
        loaded_rows = result.get("loaded_rows", 0)
        saved_rows = result.get("saved_rows", 0)
        reason = result.get("reason")

        source_text = source if source else "none"

        if status == "ok":
            print(
                f"- {ticker}: {loaded_rows} Fundamentaldaten verarbeitet, "
                f"{saved_rows} gespeichert | Quelle: {source_text}"
            )
        elif status == "skipped":
            print(
                f"- {ticker}: übersprungen - {reason} | "
                f"Quelle: {source_text}"
            )
        else:
            print(
                f"- {ticker}: Fehler - {reason} | "
                f"Quelle: {source_text}"
            )


def print_signal_results(signal_result):
    # hier geben wir die frisch berechneten Signale aus
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


def count_price_errors(price_results):
    # hier zählen wir fehlgeschlagene Kursdaten-Updates
    error_count = 0

    for result in price_results:
        if result.get("status") != "ok":
            error_count += 1

    return error_count


def print_firestore_sync_result(sync_result):
    """
    Gibt das Ergebnis der Firestore-Synchronisierung verständlich aus.
    """
    status = sync_result.get("status")
    reason = sync_result.get("reason")

    print("\nFirestore-Synchronisierung:")

    if status == "success":
        asset_count = sync_result.get("asset_documents_written", 0)
        signal_count = sync_result.get("signal_documents_written", 0)
        bot_status_count = sync_result.get(
            "bot_status_documents_written",
            0
        )

        print(f"- Assets geschrieben: {asset_count}")
        print(f"- Signale geschrieben: {signal_count}")
        print(f"- Bot-Status geschrieben: {bot_status_count}")

    elif status == "skipped":
        print(f"- Übersprungen: {reason}")

    else:
        error = sync_result.get("error")
        print(f"- Fehler: {reason}")
        print(f"- Details: {error}")


def main():
    print("\nFundamentus Bot startet...")

    # Datenbank und Bot-Run vorbereiten
    init_db()
    run_id = start_bot_run()

    # Watchlist laden
    assets = load_watchlist()

    # Fundamental-Update ist nur fällig, wenn das letzte Update
    # mindestens zwölf Stunden zurückliegt.
    fundamentals_due = should_update_fundamentals(
        interval_hours=12
    )

    # Die SEC-CIK-Auflösung wird nur für den Fundamental-Lauf benötigt.
    if fundamentals_due:
        assets = resolve_ciks_for_assets(assets)

    # Assets speichern. Bereits bekannte CIKs bleiben erhalten,
    # wenn bei einem technischen Lauf keine CIK mitgegeben wird.
    save_assets(assets)

    show_saved_assets()

    # Kursdaten und technische Analyse laufen bei jedem Botstart.
    # Durch den systemd-Timer geschieht das alle zehn Minuten.
    price_results = update_daily_prices_for_assets(assets)

    print_price_update_results(price_results)

    # Fundamentaldaten nur alle zwölf Stunden aktualisieren.
    if fundamentals_due:
        fundamental_results = update_fundamentals_for_assets(assets)
        print_fundamental_update_results(fundamental_results)

    else:
        print("\nFundamentaldaten-Update:")
        print(
            "- Übersprungen: Das letzte Update liegt "
            "weniger als 12 Stunden zurück."
        )

    # Die technische Analyse verwendet weiterhin die bereits
    # in SQLite gespeicherten Fundamentaldaten.
    signal_result = update_signals_for_assets(assets)

    print_signal_results(signal_result)
    show_latest_signals(limit=40)

    price_errors = count_price_errors(price_results)

    finish_bot_run(
        run_id=run_id,
        status="success",
        assets_processed=len(assets),
        price_errors=price_errors,
        signals_saved=signal_result["saved_rows"]
    )

    # Firestore-Synchronisierung bleibt unverändert.
    # Collections, Dokument-IDs und Felder ändern sich nicht.
    firestore_sync_result = sync_bot_data_to_firestore()

    print_firestore_sync_result(firestore_sync_result)

    print("\nFundamentus Bot-Run abgeschlossen.")
    print(f"{len(assets)} Assets aus der Watchlist verarbeitet.")
    print(f"{signal_result['saved_rows']} Signale gespeichert.")


if __name__ == "__main__":
    main()