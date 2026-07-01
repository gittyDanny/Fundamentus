from app.database import get_connection


def start_bot_run():
    # hier legen wir einen neuen Bot-Run an
    # dadurch wissen wir später, wann der Bot gestartet ist
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bot_runs
    (status)
    VALUES (?)
    """, ("running",))

    run_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return run_id


def finish_bot_run(run_id, status, assets_processed, price_errors, signals_saved, error_message=None):
    # hier schließen wir den Bot-Run sauber ab
    # dadurch kann die Webapp später direkt sehen, ob der letzte Lauf erfolgreich war
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE bot_runs
    SET
        finished_at = CURRENT_TIMESTAMP,
        status = ?,
        assets_processed = ?,
        price_errors = ?,
        signals_saved = ?,
        error_message = ?
    WHERE id = ?
    """, (
        status,
        assets_processed,
        price_errors,
        signals_saved,
        error_message,
        run_id
    ))

    conn.commit()
    conn.close()


def get_latest_bot_run():
    # hier holen wir den letzten Bot-Run aus der Datenbank
    # das brauchen wir später für Dashboard und Health-Ansicht
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, started_at, finished_at, status, assets_processed, price_errors, signals_saved, error_message
    FROM bot_runs
    ORDER BY id DESC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row