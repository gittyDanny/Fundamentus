from app.analysis.fundamental_metrics import (
    calculate_fundamental_metrics,
    calculate_quarterly_fundamental_metrics
)


def add_point_if(condition, reasons, text):
    # hier vergeben wir einen Punkt, wenn eine Bedingung erfüllt ist
    # zusätzlich speichern wir eine kurze Begründung für die GUI
    if condition:
        reasons.append(text)
        return 1

    return 0


def add_warning_if(condition, warnings, text):
    # hier sammeln wir Warnhinweise,
    # damit Fundamentus nicht nur positiv klingt, wenn etwas kritisch ist
    if condition:
        warnings.append(text)


def build_fundamentus_score(ticker):
    # hier bauen wir eine einfache Einschätzung aus Jahres- und Quartalskennzahlen
    # das ist bewusst simpel, damit wir später nachvollziehen können, warum ein Score entsteht
    annual_metrics = calculate_fundamental_metrics(ticker)
    quarterly_metrics = calculate_quarterly_fundamental_metrics(ticker)

    if not annual_metrics:
        return {
            "ticker": ticker,
            "status": "Keine Daten",
            "status_class": "neutral",
            "score": None,
            "max_score": 0,
            "score_percent": None,
            "reasons": [],
            "warnings": ["Noch keine Jahreskennzahlen vorhanden."]
        }

    latest_annual = annual_metrics[0]

    latest_quarter = None

    if quarterly_metrics:
        latest_quarter = quarterly_metrics[0]

    score = 0
    max_score = 8
    reasons = []
    warnings = []

    # Jahreslogik
    score += add_point_if(
        latest_annual.get("revenue_growth") is not None and latest_annual["revenue_growth"] > 0,
        reasons,
        "Umsatz wächst im letzten Geschäftsjahr."
    )

    score += add_point_if(
        latest_annual.get("net_margin") is not None and latest_annual["net_margin"] >= 0.05,
        reasons,
        "Net Margin liegt bei mindestens 5%."
    )

    score += add_point_if(
        latest_annual.get("operating_margin") is not None and latest_annual["operating_margin"] >= 0.05,
        reasons,
        "Operating Margin liegt bei mindestens 5%."
    )

    score += add_point_if(
        latest_annual.get("free_cash_flow") is not None and latest_annual["free_cash_flow"] > 0,
        reasons,
        "Free Cash Flow ist positiv."
    )

    score += add_point_if(
        latest_annual.get("fcf_margin") is not None and latest_annual["fcf_margin"] >= 0.03,
        reasons,
        "FCF Margin liegt bei mindestens 3%."
    )

    score += add_point_if(
        latest_annual.get("liabilities_to_assets") is not None
        and latest_annual["liabilities_to_assets"] <= 0.60,
        reasons,
        "Verbindlichkeiten liegen unter 60% der Assets."
    )

    # Quartalslogik
    if latest_quarter:
        score += add_point_if(
            latest_quarter.get("revenue_growth_yoy") is not None
            and latest_quarter["revenue_growth_yoy"] > 0,
            reasons,
            "Letztes Quartal wächst im Vergleich zum Vorjahresquartal."
        )

        score += add_point_if(
            latest_quarter.get("net_margin") is not None
            and latest_quarter["net_margin"] >= 0.03,
            reasons,
            "Letztes Quartal ist profitabel mit mindestens 3% Net Margin."
        )
    else:
        max_score = 6
        warnings.append("Noch keine Quartalskennzahlen vorhanden.")

    # Warnhinweise aus Jahresdaten
    add_warning_if(
        latest_annual.get("revenue_growth") is not None and latest_annual["revenue_growth"] < 0,
        warnings,
        "Umsatz ist im letzten Geschäftsjahr gefallen."
    )

    add_warning_if(
        latest_annual.get("net_margin") is not None and latest_annual["net_margin"] < 0.03,
        warnings,
        "Net Margin ist niedrig."
    )

    add_warning_if(
        latest_annual.get("free_cash_flow") is not None and latest_annual["free_cash_flow"] < 0,
        warnings,
        "Free Cash Flow ist negativ."
    )

    add_warning_if(
        latest_annual.get("liabilities_to_assets") is not None
        and latest_annual["liabilities_to_assets"] > 0.60,
        warnings,
        "Verbindlichkeiten sind relativ hoch."
    )

    # Warnhinweise aus Quartalsdaten
    if latest_quarter:
        add_warning_if(
            latest_quarter.get("revenue_growth_yoy") is not None
            and latest_quarter["revenue_growth_yoy"] < 0,
            warnings,
            "Letztes Quartal ist gegenüber dem Vorjahresquartal geschrumpft."
        )

        add_warning_if(
            latest_quarter.get("operating_margin") is not None
            and latest_quarter["operating_margin"] < 0.03,
            warnings,
            "Operative Marge im letzten Quartal ist niedrig."
        )

    score_percent = score / max_score

    if score_percent >= 0.70:
        status = "Stark"
        status_class = "good"
    elif score_percent >= 0.45:
        status = "Gemischt"
        status_class = "mixed"
    else:
        status = "Schwach"
        status_class = "bad"

    return {
        "ticker": ticker,
        "status": status,
        "status_class": status_class,
        "score": score,
        "max_score": max_score,
        "score_percent": score_percent,
        "reasons": reasons,
        "warnings": warnings
    }