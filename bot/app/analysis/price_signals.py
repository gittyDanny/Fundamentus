from app.database import get_connection


SIGNAL_BUY = "BUY"
SIGNAL_HOLD = "HOLD"
SIGNAL_SELL = "SELL"
SIGNAL_NO_DATA = "NO_DATA"


def get_recent_daily_prices(ticker, limit=90):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, close, volume
    FROM price_daily
    WHERE ticker = ?
      AND close IS NOT NULL
    ORDER BY date DESC
    LIMIT ?;
    """, (ticker, limit))

    rows = cursor.fetchall()
    conn.close()

    return list(reversed(rows))


def get_latest_intraday_price(ticker):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT timestamp, close
    FROM price_intraday
    WHERE ticker = ?
      AND timeframe = '5m'
      AND source = 'yahoo'
      AND close IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1;
    """, (ticker,))

    latest_row = cursor.fetchone()

    if latest_row is None:
        conn.close()
        return None

    timestamp, close = latest_row
    trading_date = timestamp[:10]

    cursor.execute("""
    SELECT SUM(COALESCE(volume, 0))
    FROM price_intraday
    WHERE ticker = ?
      AND timeframe = '5m'
      AND source = 'yahoo'
      AND SUBSTR(timestamp, 1, 10) = ?;
    """, (
        ticker,
        trading_date
    ))

    volume_row = cursor.fetchone()
    conn.close()

    current_day_volume = (
        volume_row[0]
        if volume_row
        else None
    )

    return trading_date, close, current_day_volume


def get_analysis_prices(ticker, limit=90):
    prices = get_recent_daily_prices(
        ticker,
        limit=limit
    )

    latest_intraday = get_latest_intraday_price(ticker)

    if latest_intraday is None:
        return prices

    (
        intraday_date,
        intraday_close,
        intraday_volume
    ) = latest_intraday

    if not prices:
        return [latest_intraday]

    latest_daily_date = prices[-1][0]

    if intraday_date == latest_daily_date:
        prices[-1] = (
            intraday_date,
            intraday_close,
            intraday_volume
        )

    elif intraday_date > latest_daily_date:
        prices.append((
            intraday_date,
            intraday_close,
            intraday_volume
        ))

    return prices[-limit:]


def average(values):
    if not values:
        return None

    return sum(values) / len(values)


def percentage_change(current_value, old_value):
    if (
        current_value is None
        or old_value is None
        or old_value == 0
    ):
        return None

    return (
        (current_value - old_value)
        / old_value
    ) * 100


def calculate_volatility_pct(closes):
    if len(closes) < 2:
        return None

    returns = []

    for index in range(1, len(closes)):
        old_close = closes[index - 1]
        current_close = closes[index]

        if (
            old_close is None
            or current_close is None
            or old_close == 0
        ):
            continue

        daily_return = (
            (current_close - old_close)
            / old_close
        ) * 100

        returns.append(daily_return)

    if not returns:
        return None

    mean_return = average(returns)
    squared_distances = []

    for daily_return in returns:
        squared_distances.append(
            (daily_return - mean_return) ** 2
        )

    variance = average(squared_distances)

    return variance ** 0.5


def calculate_volume_ratio(volumes):
    if len(volumes) < 20:
        return None

    latest_volume = volumes[-1]
    average_volume_20 = average(volumes[-20:])

    if (
        latest_volume is None
        or average_volume_20 is None
        or average_volume_20 == 0
    ):
        return None

    return latest_volume / average_volume_20


def add_score_for_5d_momentum(
    score,
    reasons,
    change_5d_pct
):
    if change_5d_pct is None:
        return score

    if change_5d_pct > 3:
        score += 10
        reasons.append("starkes 5D-Momentum")

    elif change_5d_pct > 0:
        score += 5
        reasons.append("leicht positives 5D-Momentum")

    elif change_5d_pct < -3:
        score -= 10
        reasons.append("schwaches 5D-Momentum")

    elif change_5d_pct < 0:
        score -= 5
        reasons.append("leicht negatives 5D-Momentum")

    return score


def add_score_for_20d_trend(
    score,
    reasons,
    change_20d_pct
):
    if change_20d_pct is None:
        return score

    if change_20d_pct > 5:
        score += 20
        reasons.append("starker 20D-Trend")

    elif change_20d_pct > 0:
        score += 10
        reasons.append("positiver 20D-Trend")

    elif change_20d_pct < -5:
        score -= 20
        reasons.append("schwacher 20D-Trend")

    elif change_20d_pct < 0:
        score -= 10
        reasons.append("negativer 20D-Trend")

    return score


def add_score_for_sma20(
    score,
    reasons,
    distance_to_sma20_pct
):
    if distance_to_sma20_pct is None:
        return score

    if distance_to_sma20_pct > 3:
        score += 15
        reasons.append("Kurs klar über SMA20")

    elif distance_to_sma20_pct > 0:
        score += 5
        reasons.append("Kurs leicht über SMA20")

    elif distance_to_sma20_pct < -3:
        score -= 15
        reasons.append("Kurs klar unter SMA20")

    elif distance_to_sma20_pct < 0:
        score -= 5
        reasons.append("Kurs leicht unter SMA20")

    return score


def add_score_for_sma50(
    score,
    reasons,
    distance_to_sma50_pct
):
    if distance_to_sma50_pct is None:
        return score

    if distance_to_sma50_pct > 5:
        score += 10
        reasons.append("Kurs deutlich über SMA50")

    elif distance_to_sma50_pct > 0:
        score += 5
        reasons.append("Kurs über SMA50")

    elif distance_to_sma50_pct < -5:
        score -= 10
        reasons.append("Kurs deutlich unter SMA50")

    elif distance_to_sma50_pct < 0:
        score -= 5
        reasons.append("Kurs unter SMA50")

    return score


def add_score_for_volatility(
    score,
    reasons,
    volatility_20d_pct
):
    if volatility_20d_pct is None:
        return score

    if volatility_20d_pct > 5:
        score -= 10
        reasons.append("hohe 20D-Volatilität")

    elif volatility_20d_pct > 3:
        score -= 5
        reasons.append("erhöhte 20D-Volatilität")

    elif volatility_20d_pct < 1.5:
        score += 5
        reasons.append("ruhige Kursbewegung")

    return score


def add_score_for_volume(
    score,
    reasons,
    volume_ratio_20d,
    change_5d_pct
):
    if (
        volume_ratio_20d is None
        or change_5d_pct is None
    ):
        return score

    if (
        volume_ratio_20d > 1.5
        and change_5d_pct > 0
    ):
        score += 5
        reasons.append(
            "positives Momentum mit erhöhtem Volumen"
        )

    elif (
        volume_ratio_20d > 1.5
        and change_5d_pct < 0
    ):
        score -= 5
        reasons.append(
            "negatives Momentum mit erhöhtem Volumen"
        )

    return score


def calculate_price_signal(ticker):
    prices = get_analysis_prices(
        ticker,
        limit=90
    )

    if len(prices) < 55:
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
    volumes = [row[2] for row in prices]

    latest_close = closes[-1]
    close_5_days_ago = closes[-6]
    close_20_days_ago = closes[-21]

    sma_20 = average(closes[-20:])
    sma_50 = average(closes[-50:])

    change_5d_pct = percentage_change(
        latest_close,
        close_5_days_ago
    )

    change_20d_pct = percentage_change(
        latest_close,
        close_20_days_ago
    )

    distance_to_sma20_pct = percentage_change(
        latest_close,
        sma_20
    )

    distance_to_sma50_pct = percentage_change(
        latest_close,
        sma_50
    )

    volatility_20d_pct = calculate_volatility_pct(
        closes[-20:]
    )

    volume_ratio_20d = calculate_volume_ratio(
        volumes
    )

    if (
        latest_close is None
        or sma_20 is None
        or sma_50 is None
        or change_20d_pct is None
    ):
        return {
            "ticker": ticker,
            "signal": SIGNAL_NO_DATA,
            "score": 0,
            "reason": "Unvollständige Kursdaten",
            "close": latest_close,
            "sma_20": sma_20,
            "change_20d_pct": change_20d_pct
        }

    score = 50
    reasons = []

    score = add_score_for_5d_momentum(
        score,
        reasons,
        change_5d_pct
    )

    score = add_score_for_20d_trend(
        score,
        reasons,
        change_20d_pct
    )

    score = add_score_for_sma20(
        score,
        reasons,
        distance_to_sma20_pct
    )

    score = add_score_for_sma50(
        score,
        reasons,
        distance_to_sma50_pct
    )

    score = add_score_for_volatility(
        score,
        reasons,
        volatility_20d_pct
    )

    score = add_score_for_volume(
        score,
        reasons,
        volume_ratio_20d,
        change_5d_pct
    )

    score = max(0, min(100, score))

    if score >= 70:
        signal = SIGNAL_BUY

    elif score <= 35:
        signal = SIGNAL_SELL

    else:
        signal = SIGNAL_HOLD

    reason = ", ".join(reasons)

    if not reason:
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