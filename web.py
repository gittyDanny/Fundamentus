from flask import Flask, render_template, redirect, url_for, request

from app.database import init_db, get_connection
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import update_daily_prices_for_ticker, update_daily_prices_for_assets
from app.jobs.fundamentals_update_job import (
    update_fundamentals_for_asset,
    update_fundamentals_for_assets
)
from app.analysis.fundamental_metrics import (
    calculate_fundamental_metrics,
    calculate_quarterly_fundamental_metrics
)
from app.analysis.fundamental_score import build_fundamentus_score


flask_app = Flask(__name__)


def prepare_database():
    # hier sorgen wir dafür, dass die Datenbank und die Watchlist bereit sind,
    # bevor die Webapp Daten anzeigen will
    init_db()

    assets = load_watchlist()
    save_assets(assets)


def get_assets():
    # hier holen wir die Watchlist aus der Datenbank,
    # damit wir sie links im Dashboard anzeigen können
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector, cik
    FROM assets
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    assets = []

    for row in rows:
        assets.append({
            "ticker": row[0],
            "name": row[1],
            "asset_type": row[2],
            "region": row[3],
            "currency": row[4],
            "sector": row[5],
            "cik": row[6]
        })

    return assets


def get_asset_by_ticker(ticker):
    # hier suchen wir ein einzelnes Asset aus der Datenbank
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector, cik
    FROM assets
    WHERE ticker = ?;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "ticker": row[0],
        "name": row[1],
        "asset_type": row[2],
        "region": row[3],
        "currency": row[4],
        "sector": row[5],
        "cik": row[6]
    }


def get_latest_price(ticker):
    # hier holen wir den letzten gespeicherten Schlusskurs
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, close, volume
    FROM price_daily
    WHERE ticker = ?
    ORDER BY date DESC
    LIMIT 1;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "date": row[0],
        "close": row[1],
        "volume": row[2]
    }


def get_latest_prices(ticker, limit=10):
    # hier holen wir die letzten Tageskurse für die Kurstabelle
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

    prices = []

    for row in rows:
        prices.append({
            "date": row[0],
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5]
        })

    return prices


def get_latest_annual_metrics(ticker):
    # hier holen wir die neuesten Jahreskennzahlen,
    # damit die wichtigsten Werte oben als Karten angezeigt werden können
    metrics = calculate_fundamental_metrics(ticker)

    if not metrics:
        return None

    return metrics[0]


@flask_app.route("/")
def index():
    # hier leiten wir erstmal standardmäßig zu TSLA weiter
    return redirect(url_for("asset_dashboard", ticker="TSLA"))


@flask_app.route("/asset/<ticker>")
def asset_dashboard(ticker):
    # hier bauen wir die Hauptseite für einen bestimmten Ticker
    prepare_database()

    assets = get_assets()
    selected_asset = get_asset_by_ticker(ticker)

    if not selected_asset:
        return redirect(url_for("index"))

    latest_price = get_latest_price(ticker)
    latest_prices = get_latest_prices(ticker, limit=10)

    annual_metrics = calculate_fundamental_metrics(ticker)
    quarterly_metrics = calculate_quarterly_fundamental_metrics(ticker)
    latest_annual_metrics = get_latest_annual_metrics(ticker)
    fundamentus_score = build_fundamentus_score(ticker)

    message = request.args.get("message")

    return render_template(
        "dashboard.html",
        assets=assets,
        selected_asset=selected_asset,
        latest_price=latest_price,
        latest_prices=latest_prices,
        annual_metrics=annual_metrics[:6],
        quarterly_metrics=quarterly_metrics[:8],
        latest_annual_metrics=latest_annual_metrics,
        fundamentus_score=fundamentus_score,
        message=message
    )


@flask_app.route("/update/prices/<ticker>", methods=["POST"])
def update_prices(ticker):
    # hier aktualisieren wir Kursdaten für einen einzelnen Ticker
    result = update_daily_prices_for_ticker(ticker)

    message = (
        f"{ticker}: {result['loaded_rows']} Kurszeilen geladen, "
        f"{result['new_rows']} neue gespeichert."
    )

    return redirect(url_for("asset_dashboard", ticker=ticker, message=message))


@flask_app.route("/update/fundamentals/<ticker>", methods=["POST"])
def update_fundamentals(ticker):
    # hier aktualisieren wir Fundamentaldaten für einen einzelnen Ticker
    asset = get_asset_by_ticker(ticker)

    if not asset:
        message = f"{ticker}: Asset nicht gefunden."
        return redirect(url_for("asset_dashboard", ticker=ticker, message=message))

    result = update_fundamentals_for_asset(asset)

    if result["status"] == "skipped":
        message = f"{ticker}: übersprungen, keine CIK vorhanden."
    elif result["status"] == "error":
        message = f"{ticker}: Fehler beim Fundamentaldaten-Import: {result['reason']}"
    else:
        message = (
            f"{ticker}: {result['loaded_rows']} Fundamentaldaten verarbeitet, "
            f"{result['saved_rows']} gespeichert."
        )

    return redirect(url_for("asset_dashboard", ticker=ticker, message=message))


@flask_app.route("/update/all-prices", methods=["POST"])
def update_all_prices():
    # hier aktualisieren wir Kursdaten für alle Assets
    assets = get_assets()
    results = update_daily_prices_for_assets(assets)

    successful_updates = 0
    new_rows = 0

    for result in results:
        if result.get("status") == "ok":
            successful_updates += 1
            new_rows += result.get("new_rows", 0)

    message = (
        f"Alle Kurse aktualisiert: {successful_updates} Ticker erfolgreich, "
        f"{new_rows} neue Kurszeilen gespeichert."
    )

    return redirect(url_for("asset_dashboard", ticker="TSLA", message=message))


@flask_app.route("/update/all-fundamentals", methods=["POST"])
def update_all_fundamentals():
    # hier aktualisieren wir Fundamentaldaten für alle Assets mit CIK
    assets = get_assets()
    results = update_fundamentals_for_assets(assets)

    ok_count = 0
    skipped_count = 0
    error_count = 0
    saved_rows = 0

    for result in results:
        if result["status"] == "ok":
            ok_count += 1
            saved_rows += result["saved_rows"]
        elif result["status"] == "skipped":
            skipped_count += 1
        else:
            error_count += 1

    message = (
        f"Fundamentaldaten aktualisiert: {ok_count} erfolgreich, "
        f"{skipped_count} übersprungen, {error_count} Fehler, "
        f"{saved_rows} Zeilen gespeichert."
    )

    return redirect(url_for("asset_dashboard", ticker="TSLA", message=message))


if __name__ == "__main__":
    prepare_database()

    # debug=True ist beim Entwickeln praktisch,
    # später auf dem Raspberry Pi stellen wir das aus
    flask_app.run(debug=True)