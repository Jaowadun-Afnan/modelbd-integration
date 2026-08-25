import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_all_agri_labor():
    # List all CSV files in raw_data/extracted/csv for debugging
    all_files = list(RAW_DIR.glob("*.csv"))
    if not all_files:
        print("⚠️ No CSV files found in raw_data/extracted/csv. Check the folder.")
        return
    print("   All files in raw_data/extracted/csv:")
    for f in all_files:
        print(f"      - {f.name}")
    # Search for likely agriculture/labor files
    patterns = ["*agri*.csv", "*agriculture*.csv", "*labor*.csv", "*labour*.csv", "*employment*.csv", "*crop*.csv"]
    files = []
    for p in patterns:
        files.extend(RAW_DIR.glob(p))
    files = list(set(files))  # remove duplicates
    if not files:
        print("⚠️ No agriculture/labor files matched. Skipping.")
        return
    all_dfs = []
    for file in files:
        print(f"   Processing {file.name}...")
        df = pd.read_csv(file, low_memory=False)
        # Clean columns
        df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
        # If 'year' present, keep; otherwise just save raw for inspection
        df['source_file'] = file.name
        all_dfs.append(df)
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True, sort=False)
        out = STAGING_DIR / "Agriculture_Labor_Combined.csv"
        combined.to_csv(out, index=False, encoding='utf-8')
        print(f"   ✅ Saved {len(combined)} rows to {out}")

if __name__ == "__main__":
    transform_all_agri_labor()
