from app.database import get_connection


def save_fundamentals(fundamentals):
    # hier speichern wir mehrere Fundamentaldaten in die Datenbank
    # bei gleicher Kennzahl und gleichem Jahr aktualisieren wir den Wert
    conn = get_connection()
    cursor = conn.cursor()

    saved_rows = 0

    for item in fundamentals:
        cursor.execute("""
        INSERT INTO fundamentals
        (ticker, fiscal_year, period, metric, value, unit, source, form, filed_at, end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker, fiscal_year, period, metric, source) DO UPDATE SET
            value = excluded.value,
            unit = excluded.unit,
            form = excluded.form,
            filed_at = excluded.filed_at,
            end_date = excluded.end_date
        """, (
            item["ticker"],
            item["fiscal_year"],
            item["period"],
            item["metric"],
            item["value"],
            item["unit"],
            item["source"],
            item["form"],
            item["filed_at"],
            item["end_date"]
        ))

        saved_rows += cursor.rowcount

    conn.commit()
    conn.close()

    return saved_rows