from app.analysis.price_signals import calculate_price_signal
from app.analysis.fundamental_metrics import calculate_fundamental_metrics


def safe_value(value, fallback=0):
    # hier sorgen wir dafür, dass None-Werte den Score nicht kaputt machen
    if value is None:
        return fallback

    return value


def calculate_fundamental_score(ticker):
    # hier berechnen wir einen ersten einfachen Fundamental-Score
    # Grundlage sind Jahreskennzahlen aus der fundamentals-Tabelle
    metrics = calculate_fundamental_metrics(ticker)

    if not metrics:
        return {
            "ticker": ticker,
            "score": None,
            "status": "missing",
            "reason": "Keine Fundamentaldaten vorhanden"
        }

    latest = metrics[0]

    score = 50
    reasons = []

    revenue_growth = latest.get("revenue_growth")
    net_margin = latest.get("net_margin")
    operating_margin = latest.get("operating_margin")
    fcf_margin = latest.get("fcf_margin")
    liabilities_to_assets = latest.get("liabilities_to_assets")
    cash_to_assets = latest.get("cash_to_assets")

    # hier bewerten wir Umsatzwachstum
    if revenue_growth is not None:
        if revenue_growth > 0.15:
            score += 15
            reasons.append("starkes Umsatzwachstum")
        elif revenue_growth > 0.05:
            score += 8
            reasons.append("positives Umsatzwachstum")
        elif revenue_growth < -0.05:
            score -= 12
            reasons.append("sinkender Umsatz")

    # hier bewerten wir Profitabilität über Net Margin
    if net_margin is not None:
        if net_margin > 0.20:
            score += 15
            reasons.append("starke Net Margin")
        elif net_margin > 0.10:
            score += 8
            reasons.append("solide Net Margin")
        elif net_margin < 0:
            score -= 18
            reasons.append("negative Net Margin")

    # hier bewerten wir operative Profitabilität
    if operating_margin is not None:
        if operating_margin > 0.25:
            score += 10
            reasons.append("starke Operating Margin")
        elif operating_margin > 0.10:
            score += 5
            reasons.append("solide Operating Margin")
        elif operating_margin < 0:
            score -= 12
            reasons.append("negative Operating Margin")

    # hier bewerten wir Free-Cashflow-Qualität
    if fcf_margin is not None:
        if fcf_margin > 0.15:
            score += 12
            reasons.append("starke FCF Margin")
        elif fcf_margin > 0.05:
            score += 6
            reasons.append("positive FCF Margin")
        elif fcf_margin < 0:
            score -= 15
            reasons.append("negative FCF Margin")

    # hier bewerten wir Verschuldung grob über Verbindlichkeiten zu Assets
    if liabilities_to_assets is not None:
        if liabilities_to_assets > 0.80:
            score -= 15
            reasons.append("hohe Verbindlichkeiten im Verhältnis zu Assets")
        elif liabilities_to_assets < 0.50:
            score += 8
            reasons.append("solide Bilanzstruktur")

    # hier bewerten wir Cash-Polster
    if cash_to_assets is not None:
        if cash_to_assets > 0.20:
            score += 5
            reasons.append("gutes Cash-Polster")
        elif cash_to_assets < 0.03:
            score -= 5
            reasons.append("geringes Cash-Polster")

    score = max(0, min(100, score))

    reason = ", ".join(reasons)

    if not reason:
        reason = "Fundamentaldaten neutral"

    return {
        "ticker": ticker,
        "score": score,
        "status": "ok",
        "reason": reason
    }


def calculate_combined_signal(asset):
    # hier kombinieren wir technischen Score und Fundamental-Score
    # wichtig: Ohne Fundamentals wird aus einem technischen BUY erstmal nur WATCH
    ticker = asset["ticker"]

    technical = calculate_price_signal(ticker)
    fundamental = calculate_fundamental_score(ticker)

    technical_score = technical["score"]
    technical_signal = technical["signal"]

    if fundamental["status"] == "ok":
        fundamental_score = fundamental["score"]

        # Gewichtung:
        # 60% technische Lage, 40% fundamentale Qualität
        final_score = (technical_score * 0.60) + (fundamental_score * 0.40)

        if final_score >= 70:
            final_signal = "BUY"
        elif final_score <= 35:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        reason = (
            f"Technisch: {technical['reason']} | "
            f"Fundamental: {fundamental['reason']}"
        )

    else:
        fundamental_score = None
        final_score = technical_score

        # Ohne Fundamentaldaten wird ein technisches BUY bewusst nicht als echter Kauf gewertet
        if technical_signal == "BUY":
            final_signal = "WATCH"
            reason = (
                f"Technisch interessant, aber keine Fundamentaldaten vorhanden | "
                f"Technisch: {technical['reason']}"
            )
        else:
            final_signal = technical_signal
            reason = (
                f"Keine Fundamentaldaten vorhanden | "
                f"Technisch: {technical['reason']}"
            )

    return {
        "ticker": ticker,
        "signal": final_signal,
        "score": round(final_score, 2),
        "reason": reason,
        "close": technical["close"],
        "sma_20": technical["sma_20"],
        "change_20d_pct": technical["change_20d_pct"],
        "technical_score": technical_score,
        "fundamental_score": fundamental_score
    }