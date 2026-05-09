"""
fetch_data.py
FAERS Adverse Event Analysis — GLP-1 Agonists
Descarga datos reales de eventos adversos desde la API pública de openFDA (FAERS).

Usa búsqueda por nombre comercial Y genérico para maximizar resultados.

Author: María Paula Vera Morandini
ICH-GCP E6(R3) | ANMAT 7516/25
"""

import requests
import pandas as pd
import time

BASE_URL = "https://api.fda.gov/drug/event.json"

# Búsqueda por nombre comercial y genérico separados para mayor cobertura
DRUGS = {
    "Semaglutide": [
        "semaglutide", "ozempic", "wegovy", "rybelsus",
        "SEMAGLUTIDE", "OZEMPIC", "WEGOVY", "RYBELSUS"
    ],
    "Liraglutide": [
        "liraglutide", "victoza", "saxenda",
        "LIRAGLUTIDE", "VICTOZA", "SAXENDA"
    ],
    "Dulaglutide": [
        "dulaglutide", "trulicity",
        "DULAGLUTIDE", "TRULICITY"
    ],
    "Exenatide": [
        "exenatide", "byetta", "bydureon",
        "EXENATIDE", "BYETTA", "BYDUREON"
    ],
}

LIMIT = 100

SEX_MAP = {
    "0": "Unknown",
    "1": "Male",
    "2": "Female",
}

OUTCOME_MAP = {
    "1": "Recovered",
    "2": "Recovering",
    "3": "Not recovered",
    "4": "Fatal",
    "5": "Unknown",
    "6": "Unknown",
}


def fetch_by_name(drug_name, search_name, max_records=500):
    """Descarga eventos para un nombre específico de droga."""
    records = []
    skip = 0

    # Intentar búsqueda exacta primero, luego parcial
    search_queries = [
        f'patient.drug.medicinalproduct:"{search_name}"',
        f'patient.drug.openfda.brand_name:"{search_name}"',
        f'patient.drug.openfda.generic_name:"{search_name}"',
    ]

    for query in search_queries:
        skip = 0
        while skip < max_records:
            try:
                params = {"search": query, "limit": LIMIT, "skip": skip}
                response = requests.get(BASE_URL, params=params, timeout=15)

                if response.status_code == 404:
                    break
                if response.status_code == 429:
                    time.sleep(2)
                    continue
                if response.status_code != 200:
                    break

                data = response.json()
                results = data.get("results", [])
                if not results:
                    break

                for r in results:
                    patient = r.get("patient", {})

                    sex_raw = patient.get("patientsex")
                    sex = SEX_MAP.get(str(sex_raw), "Unknown") if sex_raw is not None else "Unknown"

                    age = patient.get("patientonsetage", None)

                    serious_raw = r.get("serious", 2)
                    try:
                        serious = 1 if int(serious_raw) == 1 else 0
                    except:
                        serious = 0

                    report_date = r.get("receiptdate", None)
                    country = r.get("occurcountry", "Unknown")

                    reactions = patient.get("reaction", [])
                    for rxn in reactions:
                        outcome_raw = rxn.get("reactionoutcome")
                        outcome = OUTCOME_MAP.get(str(outcome_raw), "Unknown") if outcome_raw is not None else "Unknown"

                        records.append({
                            "drug":        drug_name,
                            "reaction":    rxn.get("reactionmeddrapt", "Unknown"),
                            "outcome":     outcome,
                            "sex":         sex,
                            "age":         age,
                            "serious":     serious,
                            "report_date": report_date,
                            "country":     country,
                        })

                skip += LIMIT
                time.sleep(0.3)

            except Exception as e:
                break

        if records:
            break  # Si encontró resultados con esta query, no sigue intentando

    return records


def fetch_events(drug_name, search_names, max_records=1000):
    print(f"  Descargando {drug_name}...")
    all_records = []
    seen_reactions = set()

    for name in search_names[:4]:  # primeros 4 nombres para no saturar la API
        records = fetch_by_name(drug_name, name, max_records=300)
        # Deduplicar por reaction+date+country
        for r in records:
            key = (r["reaction"], r["report_date"], r["country"], r["age"])
            if key not in seen_reactions:
                seen_reactions.add(key)
                all_records.append(r)
        if all_records:
            time.sleep(0.5)

    print(f"    {len(all_records)} registros únicos para {drug_name}")
    return all_records


def main():
    print("\n" + "="*60)
    print("  FAERS DATA FETCHER — GLP-1 Agonists")
    print("  Fuente: openFDA Drug Adverse Event API")
    print("="*60 + "\n")

    all_records = []
    for drug_name, search_names in DRUGS.items():
        records = fetch_events(drug_name, search_names, max_records=1000)
        all_records.extend(records)
        time.sleep(1)

    df = pd.DataFrame(all_records)

    if df.empty:
        print("❌ No se descargaron datos. Verificá tu conexión a internet.")
        return

    # Limpiar edad
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df = df[(df["age"].isna()) | ((df["age"] >= 18) & (df["age"] <= 100))]

    # Fecha y año
    df["report_date"] = pd.to_datetime(df["report_date"], format="%Y%m%d", errors="coerce")
    df["year"] = df["report_date"].dt.year

    df.to_csv("faers_glp1_raw.csv", index=False)

    print(f"\n{'='*60}")
    print(f"  ✅ {len(df)} registros descargados")
    print(f"  Por droga:  {df['drug'].value_counts().to_dict()}")
    print(f"  Sex:        {df['sex'].value_counts().to_dict()}")
    print(f"  Outcome:    {df['outcome'].value_counts().to_dict()}")
    print(f"  Serious:    {df['serious'].value_counts().to_dict()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
