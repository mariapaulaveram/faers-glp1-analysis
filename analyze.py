"""
analyze.py
FAERS Adverse Event Analysis — GLP-1 Agonists
Procesa los datos crudos descargados por fetch_data.py y genera
los datasets listos para el dashboard.

Author: María Paula Vera Morandini
ICH-GCP E6(R3) | ANMAT 7516/25
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def analyze():
    print("\n" + "="*60)
    print("  FAERS ANALYZER — GLP-1 Agonists")
    print("="*60 + "\n")

    df = pd.read_csv("faers_glp1_raw.csv")
    print(f"Registros cargados: {len(df)}")
    print(f"Drogas: {df['drug'].unique()}")

    # ── 1. KPIs generales ────────────────────────────────────────────────────
    kpis = {
        "total_reports":    int(len(df)),
        "total_reactions":  int(df["reaction"].nunique()),
        "serious_pct":      round(df["serious"].fillna(0).astype(int).mean() * 100, 1),
        "fatal_pct":        round((df["outcome"] == "Fatal").mean() * 100, 2),
        "drugs":            int(df["drug"].nunique()),
        "countries":        int(df["country"].nunique()),
    }

    # ── 2. Top 15 reacciones adversas ────────────────────────────────────────
    top_reactions = (
        df["reaction"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    top_reactions.columns = ["reaction", "count"]

    # ── 3. Reacciones por droga (top 10 por droga) ───────────────────────────
    reactions_by_drug = (
        df.groupby(["drug", "reaction"])
        .size()
        .reset_index(name="count")
        .sort_values(["drug", "count"], ascending=[True, False])
    )
    top_by_drug = (
        reactions_by_drug
        .groupby("drug")
        .head(10)
        .reset_index(drop=True)
    )

    # ── 4. Distribución por sexo ─────────────────────────────────────────────
    sex_dist = (
        df[df["sex"].isin(["Male", "Female"])]
        .groupby(["drug", "sex"])
        .size()
        .reset_index(name="count")
    )

    # ── 5. Distribución por outcome ──────────────────────────────────────────
    outcome_dist = (
        df.groupby(["drug", "outcome"])
        .size()
        .reset_index(name="count")
    )

    # ── 6. Evolución por año ─────────────────────────────────────────────────
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    yearly = (
        df[df["year"].between(2018, 2024)]
        .groupby(["year", "drug"])
        .size()
        .reset_index(name="count")
    )
    yearly["year"] = yearly["year"].astype(int)

    # ── 7. Distribución por grupo etario ─────────────────────────────────────
    bins   = [18, 30, 45, 60, 75, 100]
    labels = ["18-30", "31-45", "46-60", "61-75", "76+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
    age_dist = (
        df.dropna(subset=["age_group"])
        .groupby(["age_group", "drug"])
        .size()
        .reset_index(name="count")
    )
    age_dist["age_group"] = age_dist["age_group"].astype(str)

    # ── 8. Reacciones graves (serious=1, outcome fatal o no recuperado) ───────
    serious_df = df[
        (df["serious"] == 1) &
        (df["outcome"].isin(["Fatal", "Not recovered"]))
    ][["drug", "reaction", "outcome", "sex", "age", "country", "year"]].head(50)

    # ── Guardar CSVs ──────────────────────────────────────────────────────────
    import json
    with open("faers_kpis.json", "w") as f:
        json.dump(kpis, f)

    top_reactions.to_csv("faers_top_reactions.csv", index=False)
    top_by_drug.to_csv("faers_reactions_by_drug.csv", index=False)
    sex_dist.to_csv("faers_sex_dist.csv", index=False)
    outcome_dist.to_csv("faers_outcome_dist.csv", index=False)
    yearly.to_csv("faers_yearly.csv", index=False)
    age_dist.to_csv("faers_age_dist.csv", index=False)
    serious_df.to_csv("faers_serious.csv", index=False)

    print(f"KPIs: {kpis}")
    print(f"Top reacción: {top_reactions.iloc[0]['reaction']} ({top_reactions.iloc[0]['count']} reportes)")
    print(f"\n✅ Análisis completo. Archivos generados:")
    for f in ["faers_kpis.json","faers_top_reactions.csv","faers_reactions_by_drug.csv",
              "faers_sex_dist.csv","faers_outcome_dist.csv","faers_yearly.csv",
              "faers_age_dist.csv","faers_serious.csv"]:
        print(f"  · {f}")

    return {
        "kpis": kpis,
        "top_reactions": top_reactions,
        "top_by_drug": top_by_drug,
        "sex_dist": sex_dist,
        "outcome_dist": outcome_dist,
        "yearly": yearly,
        "age_dist": age_dist,
        "serious_df": serious_df,
    }

if __name__ == "__main__":
    analyze()
