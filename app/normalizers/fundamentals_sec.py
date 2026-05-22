from datetime import datetime


METRIC_RULES = {
    "revenue": {
        "tags": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ],
        "strategy": "max_value",
        "type": "flow"
    },
    "net_income": {
        "tags": [
            "NetIncomeLoss"
        ],
        "strategy": "latest_filed",
        "type": "flow"
    },
    "operating_income": {
        "tags": [
            "OperatingIncomeLoss"
        ],
        "strategy": "latest_filed",
        "type": "flow"
    },
    "total_assets": {
        "tags": [
            "Assets"
        ],
        "strategy": "latest_filed",
        "type": "instant"
    },
    "total_liabilities": {
        "tags": [
            "Liabilities"
        ],
        "strategy": "latest_filed",
        "type": "instant"
    },
    "cash": {
        "tags": [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
        ],
        "strategy": "latest_filed",
        "type": "instant"
    },
    "long_term_debt": {
        "tags": [
            "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
            "LongTermDebtNoncurrent"
        ],
        "strategy": "latest_filed",
        "type": "instant"
    },
    "operating_cash_flow": {
        "tags": [
            "NetCashProvidedByUsedInOperatingActivities"
        ],
        "strategy": "latest_filed",
        "type": "flow"
    },
    "capex": {
        "tags": [
            "PaymentsToAcquirePropertyPlantAndEquipment"
        ],
        "strategy": "latest_filed_abs",
        "type": "flow"
    }
}


def parse_date(date_text):
    # hier wandeln wir ein Datumsfeld in ein echtes Datum um,
    # damit wir sauber sortieren und Perioden prüfen können
    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None


def get_year_from_end_date(fact):
    # hier nehmen wir möglichst das Jahr aus dem Perioden-Enddatum,
    # weil SEC fy manchmal eher zum Filing-Kontext passt
    end_date = parse_date(fact.get("end"))

    if end_date:
        return end_date.year

    return fact.get("fy")


def get_duration_days(fact):
    # bei Flow-Kennzahlen wie Umsatz oder Cashflow brauchen wir die Periodenlänge,
    # damit wir Quartalswerte nicht mit Halbjahres- oder Neunmonatswerten verwechseln
    start_date = parse_date(fact.get("start"))
    end_date = parse_date(fact.get("end"))

    if not start_date or not end_date:
        return None

    return (end_date - start_date).days


def get_usd_facts_for_tag(company_facts, tag):
    # hier holen wir einen bestimmten US-GAAP Tag aus der SEC-Antwort
    facts = company_facts.get("facts", {})
    us_gaap = facts.get("us-gaap", {})
    tag_data = us_gaap.get(tag, {})
    units = tag_data.get("units", {})

    return units.get("USD", [])


def is_annual_fact(fact):
    # hier prüfen wir, ob ein Fact zu einem Jahresbericht gehört
    form = fact.get("form")
    fiscal_period = fact.get("fp")
    value = fact.get("val")
    fiscal_year = get_year_from_end_date(fact)

    if form != "10-K":
        return False

    if fiscal_period != "FY":
        return False

    if fiscal_year is None:
        return False

    if value is None:
        return False

    return True


def is_quarterly_fact(fact, metric_type):
    # hier prüfen wir, ob ein Fact zu einem Quartalsbericht gehört
    form = fact.get("form")
    fiscal_period = fact.get("fp")
    value = fact.get("val")
    fiscal_year = get_year_from_end_date(fact)

    if form != "10-Q":
        return False

    if fiscal_period not in ["Q1", "Q2", "Q3"]:
        return False

    if fiscal_year is None:
        return False

    if value is None:
        return False

    # Bei Flow-Kennzahlen wollen wir echte Quartalswerte.
    # Viele SEC-Daten enthalten zusätzlich kumulierte 6M/9M-Werte.
    # Deshalb behalten wir hier nur Perioden mit ungefähr einem Quartal Länge.
    if metric_type == "flow":
        duration_days = get_duration_days(fact)

        if duration_days is None:
            return False

        if duration_days < 60 or duration_days > 120:
            return False

    return True


def collect_facts_for_metric(company_facts, tags, metric_type):
    # hier sammeln wir Jahres- und Quartalswerte aus mehreren möglichen XBRL-Tags
    collected_facts = []

    for tag in tags:
        raw_facts = get_usd_facts_for_tag(company_facts, tag)

        for fact in raw_facts:
            period = None

            if is_annual_fact(fact):
                period = "FY"

            elif is_quarterly_fact(fact, metric_type):
                period = fact.get("fp")

            if not period:
                continue

            enriched_fact = {
                "tag": tag,
                "fy": get_year_from_end_date(fact),
                "period": period,
                "val": fact.get("val"),
                "form": fact.get("form"),
                "filed": fact.get("filed"),
                "end": fact.get("end"),
                "start": fact.get("start")
            }

            collected_facts.append(enriched_fact)

    return collected_facts


def group_facts_by_year_and_period(facts):
    # hier gruppieren wir alle Facts nach Jahr und Periode,
    # also z.B. 2024/FY oder 2024/Q1
    grouped = {}

    for fact in facts:
        key = (fact["fy"], fact["period"])

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(fact)

    return grouped


def pick_best_fact_for_period(facts, strategy):
    # hier wählen wir aus mehreren möglichen SEC-Facts den besten Wert aus

    if not facts:
        return None

    if strategy == "max_value":
        positive_facts = []

        for fact in facts:
            if fact["val"] is not None and fact["val"] > 0:
                positive_facts.append(fact)

        if positive_facts:
            return max(positive_facts, key=lambda fact: fact["val"])

        return max(facts, key=lambda fact: fact["val"])

    # bei Capex wollen wir später den positiven Betrag sehen
    # die Auswahl selbst passiert aber wie beim Standardfall über das neueste Filing
    return max(
        facts,
        key=lambda fact: (
            parse_date(fact.get("filed")) or datetime.min,
            parse_date(fact.get("end")) or datetime.min
        )
    )


def normalize_sec_company_facts(ticker, company_facts):
    # hier wandeln wir die große SEC-Antwort in einfache Fundamentus-Kennzahlen um
    # jetzt speichern wir Jahresdaten und Quartalsdaten
    normalized = []

    for metric, rule in METRIC_RULES.items():
        tags = rule["tags"]
        strategy = rule["strategy"]
        metric_type = rule["type"]

        facts = collect_facts_for_metric(
            company_facts=company_facts,
            tags=tags,
            metric_type=metric_type
        )

        grouped_facts = group_facts_by_year_and_period(facts)

        for (fiscal_year, period), facts_for_period in grouped_facts.items():
            best_fact = pick_best_fact_for_period(facts_for_period, strategy)

            if not best_fact:
                continue

            value = best_fact["val"]

            if strategy == "latest_filed_abs":
                value = abs(value)

            normalized.append({
                "ticker": ticker,
                "fiscal_year": fiscal_year,
                "period": period,
                "metric": metric,
                "value": value,
                "unit": "USD",
                "source": "sec_companyfacts",
                "form": best_fact.get("form"),
                "filed_at": best_fact.get("filed"),
                "end_date": best_fact.get("end")
            })

    return normalized