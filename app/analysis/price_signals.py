from app.database import get_connection


SIGNAL_BUY = "BUY"
SIGNAL_HOLD = "HOLD"
SIGNAL_SELL = "SELL"
SIGNAL_NO_DATA = "NO_DATA"


def get_recent_prices(ticker, limit=60):
    # hier holen wir die letzten gespeicherten Kurse aus der Datenbank,
    # weil die Analyse nicht nochmal direkt Yahoo anfragen soll
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, close
    FROM price_daily
    WHERE ticker = ? AND close IS NOT NULL
    ORDER BY date DESC
    LIMIT ?
    """, (ticker, limit))

    rows = cursor.fetchall()
    conn.close()

    # SQLite liefert die neuesten Kurse zuerst,
    # für die Berechnung drehen wir die Reihenfolge wieder um
    return list(reversed(rows))


def average(values):
    # hier berechnen wir einen einfachen Durchschnitt,
    # aber nur wenn wirklich Werte vorhanden sind
    if not values:
        return None

    return sum(values) / len(values)


def calculate_price_signal(ticker):
    # hier entsteht unser erstes simples Analyse-Signal:
    # wir vergleichen den aktuellen Kurs mit dem 20-Tage-Durchschnitt
    # und schauen zusätzlich auf die Veränderung der letzten 20 Handelstage
    prices = get_recent_prices(ticker, limit=60)

    if len(prices) < 25:
        return {
            "ticker": ticker,
            "signal": SIGNAL_NO_DATA,
            "score": 0,
            "reason": "Zu wenige Kursdaten für Analyse",
            "close": None,
            "sma_20": None,
            "change_20d_pct": None
        }

    closes = [row[1] for row in prices]

    latest_close = closes[-1]
    close_20_days_ago = closes[-21]
    sma_20 = average(closes[-20:])

    if latest_close is None or close_20_days_ago is None or sma_20 is None:
        return {
            "ticker": ticker,
            "signal": SIGNAL_NO_DATA,
            "score": 0,
            "reason": "Unvollständige Kursdaten",
            "close": latest_close,
            "sma_20": sma_20,
            "change_20d_pct": None
        }

    change_20d_pct = ((latest_close - close_20_days_ago) / close_20_days_ago) * 100
    distance_to_sma_pct = ((latest_close - sma_20) / sma_20) * 100

    score = 50

    # hier bewerten wir den 20-Tage-Trend
    if change_20d_pct > 5:
        score += 20
    elif change_20d_pct > 0:
        score += 10
    elif change_20d_pct < -5:
        score -= 20
    elif change_20d_pct < 0:
        score -= 10

    # hier bewerten wir, ob der Kurs über oder unter seinem 20-Tage-Durchschnitt liegt
    if distance_to_sma_pct > 3:
        score += 15
    elif distance_to_sma_pct > 0:
        score += 5
    elif distance_to_sma_pct < -3:
        score -= 15
    elif distance_to_sma_pct < 0:
        score -= 5

    # hier begrenzen wir den Score sauber auf 0 bis 100,
    # damit später keine komischen Werte in der App oder Webapp landen
    score = max(0, min(100, score))

    if score >= 70:
        signal = SIGNAL_BUY
        reason = "Positiver 20-Tage-Trend und Kurs über Durchschnitt"
    elif score <= 35:
        signal = SIGNAL_SELL
        reason = "Schwacher 20-Tage-Trend oder Kurs unter Durchschnitt"
    else:
        signal = SIGNAL_HOLD
        reason = "Kein klares Signal, weiter beobachten"

    return {
        "ticker": ticker,
        "signal": signal,
        "score": score,
        "reason": reason,
        "close": latest_close,
        "sma_20": sma_20,
        "change_20d_pct": change_20d_pct
    }