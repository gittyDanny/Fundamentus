from app.database import get_connection
from app.analysis.fundamental_metrics import (
    calculate_fundamental_metrics,
    calculate_quarterly_fundamental_metrics
)


def show_saved_assets():
    # hier zeigen wir an, welche Assets aktuell in der Datenbank stehen
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, region, sector
    FROM assets
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    print("\nGespeicherte Assets in der Datenbank:")

    for row in rows:
        ticker, name, region, sector = row
        print(f"- {ticker}: {name} | {region} | {sector}")

    print(f"\nInsgesamt gespeichert: {len(rows)} Assets")


def show_latest_prices(ticker, limit=5):
    # hier zeigen wir die letzten gespeicherten Tageskurse für einen Ticker an
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, open, high, low, close, volume
    FROM price_daily
    WHERE ticker = ?
    ORDER BY date DESC
    LIMIT ?;
    """, (ticker, limit))

    rows = cursor.fetchall()
    conn.close()

    print(f"\nLetzte {limit} gespeicherte Kurse für {ticker}:")

    for row in rows:
        date, open_price, high, low, close, volume = row

        print(
            f"- {date}: "
            f"Open {open_price:.2f}, "
            f"High {high:.2f}, "
            f"Low {low:.2f}, "
            f"Close {close:.2f}, "
            f"Volume {volume}"
        )


def show_fundamentals(ticker, limit_years=5):
    # hier zeigen wir nur Jahresdaten an,
    # damit die langfristige Entwicklung lesbar bleibt
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT fiscal_year
    FROM fundamentals
    WHERE ticker = ? AND period = 'FY'
    ORDER BY fiscal_year DESC
    LIMIT ?;
    """, (ticker, limit_years))

    year_rows = cursor.fetchall()
    years = [row[0] for row in year_rows]

    print(f"\nJahres-Fundamentaldaten für {ticker}:")

    if not years:
        print("- Noch keine Jahresdaten gespeichert.")
        conn.close()
        return

    for fiscal_year in years:
        cursor.execute("""
        SELECT metric, value, unit
        FROM fundamentals
        WHERE ticker = ? AND fiscal_year = ? AND period = 'FY'
        ORDER BY metric ASC;
        """, (ticker, fiscal_year))

        rows = cursor.fetchall()

        print(f"\nGeschäftsjahr {fiscal_year}:")

        for metric, value, unit in rows:
            print(f"- {metric}: {value:,.0f} {unit}")

    conn.close()


def show_quarterly_fundamentals(ticker, limit_periods=9):
    # hier zeigen wir Quartalsdaten an,
    # damit wir kurzfristigere operative Trends erkennen können
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT fiscal_year, period
    FROM fundamentals
    WHERE ticker = ? AND period != 'FY'
    ORDER BY fiscal_year DESC, period DESC
    LIMIT ?;
    """, (ticker, limit_periods))

    period_rows = cursor.fetchall()

    print(f"\nQuartals-Fundamentaldaten für {ticker}:")

    if not period_rows:
        print("- Noch keine Quartalsdaten gespeichert.")
        conn.close()
        return

    for fiscal_year, period in period_rows:
        cursor.execute("""
        SELECT metric, value, unit
        FROM fundamentals
        WHERE ticker = ? AND fiscal_year = ? AND period = ?
        ORDER BY metric ASC;
        """, (ticker, fiscal_year, period))

        rows = cursor.fetchall()

        print(f"\n{period} {fiscal_year}:")

        for metric, value, unit in rows:
            print(f"- {metric}: {value:,.0f} {unit}")

    conn.close()


def format_money(value):
    # hier machen wir große Geldbeträge besser lesbar
    if value is None:
        return "n/a"

    billion = 1_000_000_000
    million = 1_000_000

    if abs(value) >= billion:
        return f"{value / billion:,.2f} Mrd."

    if abs(value) >= million:
        return f"{value / million:,.2f} Mio."

    return f"{value:,.0f}"


def format_percent(value):
    # hier wandeln wir Dezimalwerte in Prozentwerte um
    if value is None:
        return "n/a"

    return f"{value * 100:.2f}%"


def show_fundamental_metrics(ticker, limit_years=6):
    # hier zeigen wir die aus den Jahres-Rohdaten berechneten Kennzahlen
    metrics = calculate_fundamental_metrics(ticker)

    print(f"\nBerechnete Jahres-Kennzahlen für {ticker}:")

    if not metrics:
        print("- Noch keine Kennzahlen berechenbar.")
        return

    for year_metrics in metrics[:limit_years]:
        fiscal_year = year_metrics["fiscal_year"]

        print(f"\nGeschäftsjahr {fiscal_year}:")
        print(f"- Umsatz: {format_money(year_metrics['revenue'])} USD")
        print(f"- Umsatzwachstum YoY: {format_percent(year_metrics['revenue_growth'])}")
        print(f"- Net Margin: {format_percent(year_metrics['net_margin'])}")
        print(f"- Operating Margin: {format_percent(year_metrics['operating_margin'])}")
        print(f"- Free Cash Flow: {format_money(year_metrics['free_cash_flow'])} USD")
        print(f"- FCF Margin: {format_percent(year_metrics['fcf_margin'])}")
        print(f"- Verbindlichkeiten / Assets: {format_percent(year_metrics['liabilities_to_assets'])}")
        print(f"- Cash / Assets: {format_percent(year_metrics['cash_to_assets'])}")
        print(f"- Capex / Umsatz: {format_percent(year_metrics['capex_to_revenue'])}")

def show_quarterly_fundamental_metrics(ticker, limit_periods=8):
    # hier zeigen wir berechnete Quartalskennzahlen
    # dadurch sehen wir kurzfristige Trends wie QoQ- und YoY-Wachstum
    metrics = calculate_quarterly_fundamental_metrics(ticker)

    print(f"\nBerechnete Quartals-Kennzahlen für {ticker}:")

    if not metrics:
        print("- Noch keine Quartalskennzahlen berechenbar.")
        return

    for quarter_metrics in metrics[:limit_periods]:
        fiscal_year = quarter_metrics["fiscal_year"]
        period = quarter_metrics["period"]

        print(f"\n{period} {fiscal_year}:")
        print(f"- Umsatz: {format_money(quarter_metrics['revenue'])} USD")
        print(f"- Umsatzwachstum QoQ: {format_percent(quarter_metrics['revenue_growth_qoq'])}")
        print(f"- Umsatzwachstum YoY: {format_percent(quarter_metrics['revenue_growth_yoy'])}")
        print(f"- Net Margin: {format_percent(quarter_metrics['net_margin'])}")
        print(f"- Operating Margin: {format_percent(quarter_metrics['operating_margin'])}")
        print(f"- Free Cash Flow: {format_money(quarter_metrics['free_cash_flow'])} USD")
        print(f"- FCF Margin: {format_percent(quarter_metrics['fcf_margin'])}")
        print(f"- Verbindlichkeiten / Assets: {format_percent(quarter_metrics['liabilities_to_assets'])}")
        print(f"- Cash / Assets: {format_percent(quarter_metrics['cash_to_assets'])}")