"""
main.py
FAERS Adverse Event Analysis — GLP-1 Agonists
Entry point — ejecuta el pipeline completo.

Paso 1: fetch_data.py    → descarga datos reales de openFDA API
Paso 2: analyze.py       → procesa y genera CSVs de análisis
Paso 3: dashboard.py     → genera index.html interactivo

Usage:
    python main.py

Author: María Paula Vera Morandini
ICH-GCP E6(R3) | ANMAT 7516/25
"""

import subprocess
import sys
import os

STEPS = [
    ("fetch_data.py",  "Step 1 — Downloading real FAERS data from openFDA API..."),
    ("analyze.py",     "Step 2 — Analyzing adverse events..."),
    ("dashboard.py",   "Step 3 — Generating interactive HTML dashboard..."),
]

def run_step(script, message):
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ Error in {script}. Pipeline stopped.")
        sys.exit(1)

def main():
    print("\n" + "="*60)
    print("  FAERS ADVERSE EVENT ANALYSIS")
    print("  GLP-1 Agonists — Pharmacovigilance Dashboard")
    print("  Data source: openFDA / FAERS public API")
    print("="*60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for script, message in STEPS:
        run_step(script, message)

    print("\n" + "="*60)
    print("  ✅ Pipeline complete!")
    print("  Output files:")
    print("    · faers_glp1_raw.csv          — raw FAERS data")
    print("    · faers_top_reactions.csv      — top adverse reactions")
    print("    · faers_reactions_by_drug.csv  — reactions per drug")
    print("    · faers_sex_dist.csv           — sex distribution")
    print("    · faers_outcome_dist.csv       — outcome distribution")
    print("    · faers_yearly.csv             — reports by year")
    print("    · faers_age_dist.csv           — age group distribution")
    print("    · faers_serious.csv            — serious/fatal events")
    print("    · index.html                   — interactive dashboard")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
