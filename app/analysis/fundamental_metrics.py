from app.database import get_connection


def safe_divide(numerator, denominator):
    # hier teilen wir zwei Werte, aber nur wenn beide sinnvoll vorhanden sind
    # dadurch vermeiden wir Fehler, wenn z.B. revenue fehlt oder 0 ist
    if numerator is None:
        return None

    if denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def get_fundamentals_by_year(ticker):
    # hier holen wir alle gespeicherten Fundamentaldaten für einen Ticker
    # und sortieren sie in ein Dictionary nach Geschäftsjahr
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fiscal_year, metric, value
    FROM fundamentals
    WHERE ticker = ?
    ORDER BY fiscal_year ASC;
    """, (ticker,))

    rows = cursor.fetchall()
    conn.close()

    fundamentals_by_year = {}

    for fiscal_year, metric, value in rows:
        if fiscal_year not in fundamentals_by_year:
            fundamentals_by_year[fiscal_year] = {}

        fundamentals_by_year[fiscal_year][metric] = value

    return fundamentals_by_year


def calculate_metrics_for_year(fiscal_year, values, previous_values=None):
    # hier holen wir die wichtigsten Rohwerte für ein bestimmtes Jahr heraus
    revenue = values.get("revenue")
    net_income = values.get("net_income")
    operating_income = values.get("operating_income")
    operating_cash_flow = values.get("operating_cash_flow")
    capex = values.get("capex")
    total_assets = values.get("total_assets")
    total_liabilities = values.get("total_liabilities")
    cash = values.get("cash")

    # hier berechnen wir Free Cash Flow
    # klassisch vereinfacht: operativer Cashflow minus Capex
    free_cash_flow = None

    if operating_cash_flow is not None and capex is not None:
        free_cash_flow = operating_cash_flow - capex

    # hier berechnen wir das Umsatzwachstum gegenüber dem Vorjahr
    revenue_growth = None

    if previous_values:
        previous_revenue = previous_values.get("revenue")

        if revenue is not None and previous_revenue is not None and previous_revenue != 0:
            revenue_growth = (revenue - previous_revenue) / previous_revenue

    metrics = {
        "fiscal_year": fiscal_year,
        "revenue": revenue,
        "net_income": net_income,
        "operating_income": operating_income,
        "operating_cash_flow": operating_cash_flow,
        "capex": capex,
        "free_cash_flow": free_cash_flow,

        # hier entstehen die eigentlichen Analyse-Kennzahlen
        "revenue_growth": revenue_growth,
        "net_margin": safe_divide(net_income, revenue),
        "operating_margin": safe_divide(operating_income, revenue),
        "fcf_margin": safe_divide(free_cash_flow, revenue),
        "liabilities_to_assets": safe_divide(total_liabilities, total_assets),
        "cash_to_assets": safe_divide(cash, total_assets),
        "capex_to_revenue": safe_divide(capex, revenue)
    }

    return metrics


def calculate_fundamental_metrics(ticker):
    # hier berechnen wir Kennzahlen für alle Jahre,
    # für die Fundamentaldaten in der Datenbank gespeichert sind
    fundamentals_by_year = get_fundamentals_by_year(ticker)

    years = sorted(fundamentals_by_year.keys())
    all_metrics = []

    for index, fiscal_year in enumerate(years):
        values = fundamentals_by_year[fiscal_year]

        previous_values = None

        if index > 0:
            previous_year = years[index - 1]
            previous_values = fundamentals_by_year[previous_year]

        metrics = calculate_metrics_for_year(
            fiscal_year=fiscal_year,
            values=values,
            previous_values=previous_values
        )

        all_metrics.append(metrics)

    # hier drehen wir die Reihenfolge um,
    # damit das neueste Jahr oben angezeigt wird
    return sorted(
        all_metrics,
        key=lambda item: item["fiscal_year"],
        reverse=True
    )