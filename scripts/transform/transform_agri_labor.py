
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_all_agri_labor():
    print("   → Transforming Agriculture, Science, Labor...")
    # Example: process files that match "agriculture_*.csv" or "labor_*.csv"
    agri_files = list(RAW_DIR.glob("*agriculture*.csv")) + list(RAW_DIR.glob("*agri*.csv"))
    labor_files = list(RAW_DIR.glob("*labor*.csv")) + list(RAW_DIR.glob("*labour*.csv"))
    all_dfs = []
    for file in agri_files + labor_files:
        print(f"      Processing {file.name}...")
        df = pd.read_csv(file, low_memory=False)
        # Generic cleaning: rename columns to lower snake case, strip spaces
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        # Here you would map columns to your schema (e.g., year, value, item_code)
        # For now, just append if it has a year column
        if 'year' in df.columns:
            all_dfs.append(df)
    if not all_dfs:
        print("      ⚠️ No agriculture/labor files found.")
        return
    combined = pd.concat(all_dfs, ignore_index=True, sort=False)
    out_path = STAGING_DIR / "Agriculture_Labor_Combined.csv"
    combined.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(combined)} rows to {out_path}")

if __name__ == "__main__":
    transform_all_agri_labor()
