from datetime import datetime


METRIC_RULES = {
    "revenue": {
        "tags": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ],
        "strategy": "max_value"
    },
    "net_income": {
        "tags": [
            "NetIncomeLoss"
        ],
        "strategy": "latest_filed"
    },
    "operating_income": {
        "tags": [
            "OperatingIncomeLoss"
        ],
        "strategy": "latest_filed"
    },
    "total_assets": {
        "tags": [
            "Assets"
        ],
        "strategy": "latest_filed"
    },
    "total_liabilities": {
        "tags": [
            "Liabilities"
        ],
        "strategy": "latest_filed"
    },
    "cash": {
        "tags": [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
        ],
        "strategy": "latest_filed"
    },
    "long_term_debt": {
        "tags": [
            "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
            "LongTermDebtNoncurrent"
        ],
        "strategy": "latest_filed"
    },
    "operating_cash_flow": {
        "tags": [
            "NetCashProvidedByUsedInOperatingActivities"
        ],
        "strategy": "latest_filed"
    },
    "capex": {
        "tags": [
            "PaymentsToAcquirePropertyPlantAndEquipment"
        ],
        "strategy": "latest_filed_abs"
    }
}


def parse_date(date_text):
    # hier wandeln wir ein Datumsfeld in ein echtes Datum um,
    # damit wir später sauber nach dem neuesten Filing sortieren können
    if not date_text:
        return datetime.min

    try:
        return datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return datetime.min


def get_usd_facts_for_tag(company_facts, tag):
    # hier holen wir einen bestimmten US-GAAP Tag aus der SEC-Antwort
    # falls der Tag nicht existiert, geben wir eine leere Liste zurück
    facts = company_facts.get("facts", {})
    us_gaap = facts.get("us-gaap", {})
    tag_data = us_gaap.get(tag, {})
    units = tag_data.get("units", {})

    return units.get("USD", [])


def is_annual_fact(fact):
    # hier prüfen wir, ob ein SEC-Fact zu einem Jahresbericht gehört
    # für den Anfang nehmen wir nur 10-K und FY, weil das am saubersten ist
    form = fact.get("form")
    fiscal_period = fact.get("fp")
    fiscal_year = fact.get("fy")
    value = fact.get("val")

    if form != "10-K":
        return False

    if fiscal_period != "FY":
        return False

    if fiscal_year is None:
        return False

    if value is None:
        return False

    return True


def collect_annual_facts_for_metric(company_facts, tags):
    # hier sammeln wir für eine Kennzahl alle passenden Jahreswerte
    # aus mehreren möglichen XBRL-Tags
    collected_facts = []

    for tag in tags:
        raw_facts = get_usd_facts_for_tag(company_facts, tag)

        for fact in raw_facts:
            if not is_annual_fact(fact):
                continue

            enriched_fact = {
                "tag": tag,
                "fy": fact.get("fy"),
                "val": fact.get("val"),
                "form": fact.get("form"),
                "filed": fact.get("filed"),
                "end": fact.get("end"),
                "start": fact.get("start")
            }

            collected_facts.append(enriched_fact)

    return collected_facts


def group_facts_by_year(facts):
    # hier gruppieren wir alle Facts nach Geschäftsjahr,
    # damit wir pro Jahr nur einen finalen Wert auswählen
    facts_by_year = {}

    for fact in facts:
        fiscal_year = fact["fy"]

        if fiscal_year not in facts_by_year:
            facts_by_year[fiscal_year] = []

        facts_by_year[fiscal_year].append(fact)

    return facts_by_year


def pick_best_fact_for_year(facts, strategy):
    # hier wählen wir aus mehreren möglichen SEC-Facts den besten Wert aus
    # je nach Kennzahl brauchen wir dafür eine leicht andere Logik

    if not facts:
        return None

    if strategy == "max_value":
        # beim Umsatz nehmen wir den größten positiven Wert,
        # weil kleinere Werte oft Teilsegmente oder alternative Tags sein können
        positive_facts = []

        for fact in facts:
            if fact["val"] is not None and fact["val"] > 0:
                positive_facts.append(fact)

        if positive_facts:
            return max(positive_facts, key=lambda fact: fact["val"])

        return max(facts, key=lambda fact: fact["val"])

    if strategy == "latest_filed_abs":
        # bei Capex wollen wir die Investitionshöhe als positiven Betrag sehen
        # deshalb nehmen wir später den Absolutwert
        return max(
            facts,
            key=lambda fact: (
                parse_date(fact.get("filed")),
                parse_date(fact.get("end"))
            )
        )

    # Standardfall:
    # wir nehmen den zuletzt eingereichten Wert,
    # weil spätere 10-K/A oder Korrekturen ältere Werte überschreiben können
    return max(
        facts,
        key=lambda fact: (
            parse_date(fact.get("filed")),
            parse_date(fact.get("end"))
        )
    )


def normalize_sec_company_facts(ticker, company_facts):
    # hier wandeln wir die große SEC-Antwort in einfache Fundamentus-Kennzahlen um
    # wichtig: pro Kennzahl und Jahr speichern wir nur einen ausgewählten Wert
    normalized = []

    for metric, rule in METRIC_RULES.items():
        tags = rule["tags"]
        strategy = rule["strategy"]

        annual_facts = collect_annual_facts_for_metric(company_facts, tags)
        facts_by_year = group_facts_by_year(annual_facts)

        for fiscal_year, facts in facts_by_year.items():
            best_fact = pick_best_fact_for_year(facts, strategy)

            if not best_fact:
                continue

            value = best_fact["val"]

            if strategy == "latest_filed_abs":
                value = abs(value)

            normalized.append({
                "ticker": ticker,
                "fiscal_year": fiscal_year,
                "period": "FY",
                "metric": metric,
                "value": value,
                "unit": "USD",
                "source": "sec_companyfacts",
                "form": best_fact.get("form"),
                "filed_at": best_fact.get("filed"),
                "end_date": best_fact.get("end")
            })

    return normalized