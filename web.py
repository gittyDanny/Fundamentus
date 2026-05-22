from flask import Flask, render_template, redirect, url_for

from app.database import init_db, get_connection
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.jobs.price_update_job import (
    update_daily_prices_for_ticker,
    update_daily_prices_for_assets
)


flask_app = Flask(__name__)


def prepare_database():
    # hier sorgen wir dafür, dass die Datenbank bereit ist,
    # bevor die Webapp Daten anzeigen will
    init_db()

    # hier laden wir die Watchlist und speichern sie in die Datenbank
    assets = load_watchlist()
    save_assets(assets)


def get_assets():
    # hier holen wir alle gespeicherten Assets aus der Datenbank,
    # damit wir sie im Browser als Tabelle anzeigen können
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector
    FROM assets
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_assets_as_dicts():
    # hier holen wir die Assets als Dictionary-Liste,
    # weil unser Job mit asset["ticker"] arbeitet
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector
    FROM assets
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    assets = []

    for row in rows:
        asset = {
            "ticker": row[0],
            "name": row[1],
            "asset_type": row[2],
            "region": row[3],
            "currency": row[4],
            "sector": row[5]
        }

        assets.append(asset)

    return assets


def get_latest_prices(ticker, limit=10):
    # hier holen wir die letzten gespeicherten Tageskurse für einen Ticker
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

    return rows


@flask_app.route("/")
def dashboard():
    # hier bauen wir die Startseite der Webapp
    selected_ticker = "TSLA"

    assets = get_assets()
    prices = get_latest_prices(selected_ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=selected_ticker,
        update_result=None,
        update_results=None
    )


@flask_app.route("/prices/<ticker>")
def prices_for_ticker(ticker):
    # hier kann man verschiedene Aktien anklicken,
    # z.B. /prices/NVDA oder /prices/TSLA
    assets = get_assets()
    prices = get_latest_prices(ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=ticker,
        update_result=None,
        update_results=None
    )


@flask_app.route("/update-prices/<ticker>", methods=["POST"])
def update_prices_for_ticker(ticker):
    # hier aktualisieren wir Kursdaten für genau den Ticker,
    # dessen Button im Dashboard geklickt wurde
    result = update_daily_prices_for_ticker(ticker)

    assets = get_assets()
    prices = get_latest_prices(ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=ticker,
        update_result=result,
        update_results=None
    )


@flask_app.route("/update-all-prices", methods=["POST"])
def update_all_prices():
    # hier aktualisieren wir alle Ticker aus der Watchlist
    assets_as_dicts = get_assets_as_dicts()
    results = update_daily_prices_for_assets(assets_as_dicts)

    selected_ticker = "TSLA"
    assets = get_assets()
    prices = get_latest_prices(selected_ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=selected_ticker,
        update_result=None,
        update_results=results
    )


if __name__ == "__main__":
    prepare_database()

    # debug=True ist beim Entwickeln praktisch,
    # weil Flask Änderungen und Fehler schneller sichtbar macht
    flask_app.run(debug=True)