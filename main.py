from app.database import init_db


def main():
    # hier starten wir erstmal nur den Datenbankaufbau
    # später ruft main.py dann unsere Import-Jobs auf
    init_db()

    print("Fundamentus wurde gestartet.")
    print("Datenbank wurde geprüft oder neu erstellt.")


if __name__ == "__main__":
    main()