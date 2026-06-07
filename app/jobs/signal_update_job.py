from app.analysis.combined_signals import calculate_combined_signal
from app.storage.save_signals import save_signals


def update_signals_for_assets(assets):
    # hier berechnen wir für jedes Asset aus der Watchlist ein frisches Signal
    # dadurch bleibt die Analyse-Schicht sauber vom reinen Kursdaten-Import getrennt
    signals = []

    for asset in assets:
        ticker = asset["ticker"]

        try:
            # hier wird aus den gespeicherten Kursdaten ein BUY / HOLD / SELL Signal berechnet
            signal = calculate_combined_signal(asset)
            signal["status"] = "ok"

        except Exception as error:
            # hier fangen wir Fehler pro Ticker ab,
            # damit nicht der ganze Bot-Run wegen einem kaputten Asset abbricht
            signal = {
                "ticker": ticker,
                "signal": "ERROR",
                "score": 0,
                "reason": str(error),
                "close": None,
                "sma_20": None,
                "change_20d_pct": None,
                "status": "error"
            }

        signals.append(signal)

    # hier speichern wir alle berechneten Signale in der Datenbank
    saved_rows = save_signals(signals)

    return {
        "signals": signals,
        "saved_rows": saved_rows
    }