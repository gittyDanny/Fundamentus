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


def get_annual_fundamentals_by_year(ticker):
    # hier holen wir nur Jahresdaten aus der Datenbank
    # wichtig: Quartale werden bewusst ausgeschlossen
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fiscal_year, metric, value
    FROM fundamentals
    WHERE ticker = ? AND period = 'FY'
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


def get_quarterly_fundamentals_by_period(ticker):
    # hier holen wir nur Quartalsdaten aus der Datenbank
    # diese Daten analysieren wir getrennt von den Jahresdaten
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fiscal_year, period, metric, value
    FROM fundamentals
    WHERE ticker = ? AND period != 'FY'
    ORDER BY fiscal_year ASC, period ASC;
    """, (ticker,))

    rows = cursor.fetchall()
    conn.close()

    fundamentals_by_period = {}

    for fiscal_year, period, metric, value in rows:
        key = (fiscal_year, period)

        if key not in fundamentals_by_period:
            fundamentals_by_period[key] = {}

        fundamentals_by_period[key][metric] = value

    return fundamentals_by_period


def get_previous_quarter_key(current_key):
    # hier bestimmen wir das vorherige Quartal
    # z.B. aus 2025/Q2 wird 2025/Q1, aus 2025/Q1 wird 2024/Q3
    fiscal_year, period = current_key

    if period == "Q3":
        return fiscal_year, "Q2"

    if period == "Q2":
        return fiscal_year, "Q1"

    if period == "Q1":
        return fiscal_year - 1, "Q3"

    return None


def get_same_quarter_previous_year_key(current_key):
    # hier bestimmen wir das gleiche Quartal im Vorjahr
    # z.B. aus 2025/Q2 wird 2024/Q2
    fiscal_year, period = current_key
    return fiscal_year - 1, period


def calculate_metrics_for_year(fiscal_year, values, previous_values=None):
    # hier holen wir die wichtigsten Rohwerte für ein bestimmtes Geschäftsjahr heraus
    revenue = values.get("revenue")
    net_income = values.get("net_income")
    operating_income = values.get("operating_income")
    operating_cash_flow = values.get("operating_cash_flow")
    capex = values.get("capex")
    total_assets = values.get("total_assets")
    total_liabilities = values.get("total_liabilities")
    cash = values.get("cash")

    free_cash_flow = None

    if operating_cash_flow is not None and capex is not None:
        free_cash_flow = operating_cash_flow - capex

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
        "revenue_growth": revenue_growth,
        "net_margin": safe_divide(net_income, revenue),
        "operating_margin": safe_divide(operating_income, revenue),
        "fcf_margin": safe_divide(free_cash_flow, revenue),
        "liabilities_to_assets": safe_divide(total_liabilities, total_assets),
        "cash_to_assets": safe_divide(cash, total_assets),
        "capex_to_revenue": safe_divide(capex, revenue)
    }

    return metrics


def calculate_metrics_for_quarter(period_key, values, all_period_values):
    # hier berechnen wir Kennzahlen für ein einzelnes Quartal
    fiscal_year, period = period_key

    revenue = values.get("revenue")
    net_income = values.get("net_income")
    operating_income = values.get("operating_income")
    operating_cash_flow = values.get("operating_cash_flow")
    capex = values.get("capex")
    total_assets = values.get("total_assets")
    total_liabilities = values.get("total_liabilities")
    cash = values.get("cash")

    free_cash_flow = None

    if operating_cash_flow is not None and capex is not None:
        free_cash_flow = operating_cash_flow - capex

    previous_quarter_key = get_previous_quarter_key(period_key)
    previous_quarter_values = all_period_values.get(previous_quarter_key, {})

    same_quarter_previous_year_key = get_same_quarter_previous_year_key(period_key)
    same_quarter_previous_year_values = all_period_values.get(same_quarter_previous_year_key, {})

    previous_quarter_revenue = previous_quarter_values.get("revenue")
    same_quarter_previous_year_revenue = same_quarter_previous_year_values.get("revenue")

    revenue_growth_qoq = None
    revenue_growth_yoy = None

    if revenue is not None and previous_quarter_revenue is not None and previous_quarter_revenue != 0:
        revenue_growth_qoq = (revenue - previous_quarter_revenue) / previous_quarter_revenue

    if revenue is not None and same_quarter_previous_year_revenue is not None and same_quarter_previous_year_revenue != 0:
        revenue_growth_yoy = (revenue - same_quarter_previous_year_revenue) / same_quarter_previous_year_revenue

    metrics = {
        "fiscal_year": fiscal_year,
        "period": period,
        "revenue": revenue,
        "net_income": net_income,
        "operating_income": operating_income,
        "operating_cash_flow": operating_cash_flow,
        "capex": capex,
        "free_cash_flow": free_cash_flow,
        "revenue_growth_qoq": revenue_growth_qoq,
        "revenue_growth_yoy": revenue_growth_yoy,
        "net_margin": safe_divide(net_income, revenue),
        "operating_margin": safe_divide(operating_income, revenue),
        "fcf_margin": safe_divide(free_cash_flow, revenue),
        "liabilities_to_assets": safe_divide(total_liabilities, total_assets),
        "cash_to_assets": safe_divide(cash, total_assets),
        "capex_to_revenue": safe_divide(capex, revenue)
    }

    return metrics


def calculate_fundamental_metrics(ticker):
    # hier berechnen wir nur Jahreskennzahlen
    fundamentals_by_year = get_annual_fundamentals_by_year(ticker)

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

    return sorted(
        all_metrics,
        key=lambda item: item["fiscal_year"],
        reverse=True
    )


def calculate_quarterly_fundamental_metrics(ticker):
    # hier berechnen wir Quartalskennzahlen getrennt von den Jahreskennzahlen
    fundamentals_by_period = get_quarterly_fundamentals_by_period(ticker)

    period_keys = sorted(
        fundamentals_by_period.keys(),
        key=lambda key: (key[0], key[1])
    )

    all_metrics = []

    for period_key in period_keys:
        values = fundamentals_by_period[period_key]

        metrics = calculate_metrics_for_quarter(
            period_key=period_key,
            values=values,
            all_period_values=fundamentals_by_period
        )

        all_metrics.append(metrics)

    return sorted(
        all_metrics,
        key=lambda item: (item["fiscal_year"], item["period"]),
        reverse=True
    )