import os
import requests
from dotenv import load_dotenv


load_dotenv()


def fetch_company_facts_from_sec(cik):
    # hier holen wir die SEC CompanyFacts Daten für eine Firma
    # die CIK muss 10-stellig sein, also z.B. 0001318605 für Tesla
    user_agent = os.getenv("SEC_USER_AGENT")

    if not user_agent:
        raise ValueError("SEC_USER_AGENT fehlt in der .env Datei")

    padded_cik = str(cik).zfill(10)

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"

    headers = {
        # hier identifizieren wir unser kleines Projekt gegenüber der SEC
        # das ist wichtig für sauberen API-Zugriff
        "User-Agent": user_agent
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()