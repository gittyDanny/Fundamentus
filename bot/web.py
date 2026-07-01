from flask import Flask, render_template, redirect, url_for, request

from app.database import init_db, get_connection
from app.config import load_watchlist
from app.storage.save_assets import save_assets
from app.collectors.sec_ticker_mapping import resolve_ciks_for_assets

from app.jobs.price_update_job import (
    update_daily_prices_for_ticker,
    update_daily_prices_for_assets
)

from app.jobs.fundamentals_update_job import (
    update_fundamentals_for_asset,
    update_fundamentals_for_assets
)

from app.jobs.signal_update_job import update_signals_for_assets

from app.analysis.fundamental_metrics import (
    calculate_fundamental_metrics,
    calculate_quarterly_fundamental_metrics
)

from app.analysis.fundamental_score import build_fundamentus_score


# Flask-App-Objekt.
# Darüber werden später alle Web-Routen registriert.
flask_app = Flask(__name__)


def prepare_database():
    """
    Bereitet die Datenbank für die Webapp vor.

    Wichtig:
    Die Webapp soll dieselbe Watchlist-Logik nutzen wie main.py.
    Deshalb:
    1. Tabellen anlegen
    2. Watchlist aus YAML laden
    3. CIKs für US-Aktien ergänzen
    4. Assets in der DB speichern/aktivieren
    """
    init_db()

    assets = load_watchlist()
    assets = resolve_ciks_for_assets(assets)
    save_assets(assets)


def get_fundamental_source(ticker):
    """
    Prüft, aus welcher Quelle Fundamentaldaten für einen Ticker gespeichert sind.

    Beispiele:
    - US-Aktien wie AAPL, MSFT, MU meistens: sec
    - ASML aktuell: yahoo
    - Wenn nichts vorhanden ist: None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT source
    FROM fundamentals
    WHERE ticker = ?
      AND source IS NOT NULL
    GROUP BY source
    ORDER BY MAX(created_at) DESC
    LIMIT 1;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return row[0]


def build_data_status(ticker, cik):
    """
    Baut das Label für die Watchlist-Badges.

    Ziel:
    - SEC aktiv: SEC-Fundamentaldaten liegen bereits in der DB.
    - Yahoo aktiv: Yahoo-Fundamentaldaten liegen bereits in der DB.
    - SEC bereit: CIK vorhanden, aber noch keine Fundamentaldaten gespeichert.
    - Nur Kurse: keine CIK und keine Fundamentaldaten.
    """
    source = get_fundamental_source(ticker)

    if source in ["sec", "sec_companyfacts"]:
        return {
            "label": "SEC aktiv",
            "class": "sec",
            "source": source
        }

    if source == "yahoo":
        return {
            "label": "Yahoo aktiv",
            "class": "yahoo",
            "source": source
        }

    if cik:
        return {
            "label": "SEC bereit",
            "class": "ready",
            "source": None
        }

    return {
        "label": "Nur Kurse",
        "class": "price",
        "source": None
    }

def get_assets():
    """
    Holt alle aktiven Assets aus der Datenbank.

    is_active = 1 bedeutet:
    Das Asset steht aktuell in der Watchlist.
    Historische entfernte Assets bleiben zwar in der DB,
    werden aber nicht mehr im Dashboard angezeigt.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector, cik
    FROM assets
    WHERE is_active = 1
    ORDER BY ticker;
    """)

    rows = cursor.fetchall()
    conn.close()

    assets = []

    for row in rows:
        ticker = row[0]
        cik = row[6]
        data_status = build_data_status(ticker, cik)

        assets.append({
            "ticker": ticker,
            "name": row[1],
            "asset_type": row[2],
            "region": row[3],
            "currency": row[4],
            "sector": row[5],
            "cik": cik,
            "data_status": data_status,
        })

    return assets


def get_asset_by_ticker(ticker):
    """
    Holt ein einzelnes aktives Asset.

    Wird für die Detailseite verwendet.
    Falls der Ticker nicht aktiv ist, wird None zurückgegeben.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ticker, name, asset_type, region, currency, sector, cik
    FROM assets
    WHERE ticker = ?
      AND is_active = 1;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    data_status = build_data_status(row[0], row[6])

    return {
        "ticker": row[0],
        "name": row[1],
        "asset_type": row[2],
        "region": row[3],
        "currency": row[4],
        "sector": row[5],
        "cik": row[6],
        "data_status": data_status,
    }


def get_latest_price(ticker):
    """
    Holt den letzten gespeicherten Schlusskurs.

    Diese Daten kommen aus price_daily.
    """
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
    """
    Holt die letzten Tageskurse für die Tabelle auf der Detailseite.
    """
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


def get_signal_status_class(signal):
    """
    Wandelt BUY/HOLD/SELL in CSS-Klassen um.
    Dadurch können Signale farblich dargestellt werden.
    """
    if signal == "BUY":
        return "good"

    if signal == "SELL":
        return "bad"

    if signal == "HOLD":
        return "mixed"

    return "neutral"


def get_latest_signal(ticker):
    """
    Holt das letzte gespeicherte BUY/HOLD/SELL-Signal.

    Das ist der Score, der auch in main.py ausgegeben wird:
    BUY/HOLD/SELL, Score, Close, SMA20, 20D-Veränderung.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, ticker, signal, score, reason, close, sma_20, change_20d_pct, source, created_at
    FROM signals
    WHERE ticker = ?
    ORDER BY created_at DESC, id DESC
    LIMIT 1;
    """, (ticker,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "ticker": row[1],
        "signal": row[2],
        "score": row[3],
        "reason": row[4],
        "close": row[5],
        "sma_20": row[6],
        "change_20d_pct": row[7],
        "source": row[8],
        "created_at": row[9],
        "status_class": get_signal_status_class(row[2])
    }


def get_latest_annual_metrics(ticker):
    """
    Berechnet die Jahreskennzahlen und gibt das neueste Jahr zurück.
    """
    metrics = calculate_fundamental_metrics(ticker)

    if not metrics:
        return None

    return metrics[0]


def build_overview_rows(assets):
    """
    Baut die Daten für die Gesamtübersicht.

    Pro Asset werden zusammengeführt:
    - Stammdaten
    - letzter Kurs
    - letztes BUY/HOLD/SELL-Signal
    - neueste Jahreskennzahlen
    - fundamentaler Qualitätscheck
    """
    rows = []

    for asset in assets:
        ticker = asset["ticker"]

        latest_price = get_latest_price(ticker)
        latest_signal = get_latest_signal(ticker)
        latest_annual_metrics = get_latest_annual_metrics(ticker)
        fundamentus_score = build_fundamentus_score(ticker)

        row = {
            "ticker": ticker,
            "name": asset["name"],
            "region": asset["region"],
            "sector": asset["sector"],
            "currency": asset["currency"],
            "cik": asset["cik"],
            "data_status": asset["data_status"],
            "latest_price": latest_price,
            "latest_signal": latest_signal,
            "latest_annual_metrics": latest_annual_metrics,
            "fundamentus_score": fundamentus_score
        }

        rows.append(row)

    return rows


@flask_app.route("/")
def index():
    """
    Startseite.
    Leitet direkt auf die Gesamtübersicht weiter.
    """
    return redirect(url_for("overview"))


@flask_app.route("/overview")
def overview():
    """
    Gesamtübersicht aller Watchlist-Assets.
    """
    prepare_database()

    assets = get_assets()
    overview_rows = build_overview_rows(assets)
    message = request.args.get("message")

    return render_template(
        "overview.html",
        assets=assets,
        overview_rows=overview_rows,
        message=message
    )


@flask_app.route("/asset/<ticker>")
def asset_dashboard(ticker):
    """
    Detailseite für einen einzelnen Ticker.
    """
    prepare_database()

    assets = get_assets()
    selected_asset = get_asset_by_ticker(ticker)

    if not selected_asset:
        return redirect(url_for("overview"))

    latest_price = get_latest_price(ticker)
    latest_prices = get_latest_prices(ticker, limit=10)
    latest_signal = get_latest_signal(ticker)

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
        latest_signal=latest_signal,
        annual_metrics=annual_metrics[:6],
        quarterly_metrics=quarterly_metrics[:8],
        latest_annual_metrics=latest_annual_metrics,
        fundamentus_score=fundamentus_score,
        message=message
    )


@flask_app.route("/update/prices/<ticker>", methods=["POST"])
def update_prices(ticker):
    """
    Aktualisiert Kurse für einen einzelnen Ticker.
    """
    prepare_database()

    result = update_daily_prices_for_ticker(ticker)

    if result.get("status") == "ok":
        message = (
            f"{ticker}: {result.get('loaded_rows', 0)} Kurszeilen geladen, "
            f"{result.get('new_rows', 0)} neue gespeichert."
        )
    else:
        message = f"{ticker}: Fehler beim Kursdaten-Update: {result.get('error', 'Unbekannter Fehler')}"

    return redirect(url_for("asset_dashboard", ticker=ticker, message=message))


@flask_app.route("/update/fundamentals/<ticker>", methods=["POST"])
def update_fundamentals(ticker):
    """
    Aktualisiert Fundamentaldaten für einen einzelnen Ticker.
    """
    prepare_database()

    asset = get_asset_by_ticker(ticker)

    if not asset:
        message = f"{ticker}: Asset nicht gefunden."
        return redirect(url_for("overview", message=message))

    result = update_fundamentals_for_asset(asset)

    if result["status"] == "skipped":
        message = f"{ticker}: übersprungen, keine passende Fundamentaldatenquelle vorhanden."

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
    """
    Aktualisiert Kurse für alle aktiven Assets.
    """
    prepare_database()

    assets = get_assets()
    results = update_daily_prices_for_assets(assets)

    successful_updates = 0
    error_count = 0
    new_rows = 0

    for result in results:
        if result.get("status") == "ok":
            successful_updates += 1
            new_rows += result.get("new_rows", 0)
        else:
            error_count += 1

    message = (
        f"Alle Kurse aktualisiert: {successful_updates} Ticker erfolgreich, "
        f"{error_count} Fehler, {new_rows} neue Kurszeilen gespeichert."
    )

    return redirect(url_for("overview", message=message))


@flask_app.route("/update/all-fundamentals", methods=["POST"])
def update_all_fundamentals():
    """
    Aktualisiert Fundamentaldaten für alle aktiven Assets.
    """
    prepare_database()

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

    return redirect(url_for("overview", message=message))


@flask_app.route("/update/all-signals", methods=["POST"])
def update_all_signals():
    """
    Berechnet BUY/HOLD/SELL-Signale neu.

    Das ist praktisch für die Webapp:
    Man muss nicht immer main.py starten,
    nur um die Signaltabelle neu zu befüllen.
    """
    prepare_database()

    assets = get_assets()
    result = update_signals_for_assets(assets)

    message = (
        f"Signale aktualisiert: {len(result.get('signals', []))} Signale berechnet, "
        f"{result.get('saved_rows', 0)} gespeichert."
    )

    return redirect(url_for("overview", message=message))


if __name__ == "__main__":
    prepare_database()

    # debug=True ist nur für Entwicklung gedacht.
    # Später auf dem Raspberry Pi sollte das deaktiviert werden.
    flask_app.run(debug=True)