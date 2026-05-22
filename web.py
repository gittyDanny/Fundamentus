from flask import Flask, render_template

from app.database import init_db, get_connection
from app.config import load_watchlist
from app.storage.save_assets import save_assets


flask_app = Flask(__name__)


def prepare_database():
    # hier sorgen wir dafür, dass die Datenbank bereit ist,
    # bevor die Webapp Daten anzeigen will
    init_db()

    # hier laden wir die Watchlist und speichern sie in die Datenbank,
    # damit die Webapp immer mindestens die aktuellen Assets kennt
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


def get_latest_prices(ticker, limit=10):
    # hier holen wir die letzten gespeicherten Tageskurse für einen Ticker,
    # aktuell z.B. für TSLA
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
    # Flask gibt die Daten an dashboard.html weiter
    selected_ticker = "TSLA"

    assets = get_assets()
    prices = get_latest_prices(selected_ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=selected_ticker
    )


@flask_app.route("/prices/<ticker>")
def prices_for_ticker(ticker):
    # hier kann man später verschiedene Aktien anklicken,
    # z.B. /prices/NVDA oder /prices/TSLA
    assets = get_assets()
    prices = get_latest_prices(ticker, limit=10)

    return render_template(
        "dashboard.html",
        assets=assets,
        prices=prices,
        selected_ticker=ticker
    )


if __name__ == "__main__":
    prepare_database()

    # debug=True ist praktisch beim Entwickeln,
    # weil Flask Änderungen schneller sichtbar macht und Fehler genauer zeigt
    flask_app.run(debug=True)