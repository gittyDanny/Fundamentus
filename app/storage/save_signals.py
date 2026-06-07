from app.database import get_connection


def save_signal(signal):
    # hier speichern wir ein einzelnes Analyse-Signal in der Datenbank
    # dadurch können wir später im Web-Dashboard und in der App den Signalverlauf anzeigen
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO signals
    (ticker, signal, score, reason, close, sma_20, change_20d_pct, source)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        signal["ticker"],
        signal["signal"],
        signal["score"],
        signal["reason"],
        signal["close"],
        signal["sma_20"],
        signal["change_20d_pct"],
        "price_signal_v1"
    ))

    conn.commit()
    conn.close()


def save_signals(signals):
    # hier speichern wir mehrere Signale aus einem Bot-Run
    # saved_rows nutzen wir später für eine saubere Konsolenausgabe
    saved_rows = 0

    for signal in signals:
        save_signal(signal)
        saved_rows += 1

    return saved_rows