from app.database import get_connection


def show_latest_signals(limit=20):
    # hier zeigen wir die neuesten gespeicherten Signale aus der Datenbank an
    # damit wir nach jedem Bot-Run direkt sehen, was die Analyse gespeichert hat
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, signal, score, close, sma_20, change_20d_pct, created_at
    FROM signals
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    print("\nLetzte gespeicherte Signale:")

    if not rows:
        print("- Keine Signale gefunden")
        return

    for row in rows:
        ticker = row[0]
        signal = row[1]
        score = row[2]
        close = row[3]
        sma_20 = row[4]
        change_20d_pct = row[5]
        created_at = row[6]

        print(
            f"- {ticker}: {signal} | "
            f"Score: {score} | "
            f"Close: {close:.2f} | "
            f"SMA20: {sma_20:.2f} | "
            f"20D: {change_20d_pct:.2f}% | "
            f"{created_at}"
        )