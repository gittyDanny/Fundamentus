import math
import yfinance as yf


YAHOO_METRIC_MAPPING = {
    "Total Revenue": "revenue",
    "Net Income": "net_income",
    "Operating Income": "operating_income",
    "Operating Cash Flow": "operating_cash_flow",
    "Capital Expenditure": "capex",
    "Total Assets": "total_assets",
    "Total Liabilities Net Minority Interest": "total_liabilities",
    "Cash And Cash Equivalents": "cash",
    "Cash Cash Equivalents And Short Term Investments": "cash"
}


def clean_number(value):
    # hier machen wir Yahoo-Werte robust,
    # weil manchmal NaN oder leere Werte zurückkommen
    if value is None:
        return None

    try:
        if math.isnan(value):
            return None
    except TypeError:
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_fiscal_year_from_column(column):
    # Yahoo liefert Spalten meist als Datum/Timestamp
    # wir nutzen daraus das Jahr als Geschäftsjahr
    try:
        return int(column.year)
    except AttributeError:
        return None


def create_fundamental_item(ticker, fiscal_year, metric, value, end_date):
    # hier bauen wir ein Fundamentaldaten-Objekt im gleichen Format wie der SEC-Normalizer
    return {
        "ticker": ticker,
        "fiscal_year": fiscal_year,
        "period": "FY",
        "metric": metric,
        "value": value,
        "unit": "EUR",
        "source": "yahoo",
        "form": "yahoo_financials",
        "filed_at": None,
        "end_date": end_date
    }


def add_rows_from_statement(fundamentals, ticker, statement, metric_mapping):
    # hier lesen wir eine Yahoo-Tabelle aus und mappen die Zeilen auf unsere internen Kennzahlen
    if statement is None or statement.empty:
        return

    for yahoo_metric, internal_metric in metric_mapping.items():
        if yahoo_metric not in statement.index:
            continue

        row = statement.loc[yahoo_metric]

        for column, raw_value in row.items():
            fiscal_year = get_fiscal_year_from_column(column)
            value = clean_number(raw_value)

            if fiscal_year is None or value is None:
                continue

            end_date = str(column.date()) if hasattr(column, "date") else str(column)

            fundamentals.append(
                create_fundamental_item(
                    ticker=ticker,
                    fiscal_year=fiscal_year,
                    metric=internal_metric,
                    value=value,
                    end_date=end_date
                )
            )


def fetch_yahoo_fundamentals(ticker):
    # hier holen wir Jahres-Fundamentaldaten über Yahoo/yfinance
    # das ist unser Fallback für deutsche/europäische Aktien ohne SEC-CIK
    yahoo_ticker = yf.Ticker(ticker)

    income_statement = yahoo_ticker.financials
    balance_sheet = yahoo_ticker.balance_sheet
    cashflow = yahoo_ticker.cashflow

    fundamentals = []

    add_rows_from_statement(
        fundamentals=fundamentals,
        ticker=ticker,
        statement=income_statement,
        metric_mapping=YAHOO_METRIC_MAPPING
    )

    add_rows_from_statement(
        fundamentals=fundamentals,
        ticker=ticker,
        statement=balance_sheet,
        metric_mapping=YAHOO_METRIC_MAPPING
    )

    add_rows_from_statement(
        fundamentals=fundamentals,
        ticker=ticker,
        statement=cashflow,
        metric_mapping=YAHOO_METRIC_MAPPING
    )

    return fundamentals