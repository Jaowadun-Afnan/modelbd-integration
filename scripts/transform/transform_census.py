import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "pdf_tables"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_economic_census():
    census_files = list(RAW_DIR.glob("*census*.csv")) + list(RAW_DIR.glob("*table*.csv"))
    if not census_files:
        print("⚠️ No census table files found. Skipping.")
        return
    all_data = []
    for file in census_files:
        print(f"   Processing {file.name}...")
        # Read raw, no header
        df_raw = pd.read_csv(file, header=None, low_memory=False)
        # Try to find header row: first row that contains any of these keywords
        keywords = ['sector', 'unit', 'establishment', 'persons', 'value', 'year']
        header_row = None
        for i, row in df_raw.iterrows():
            row_str = ' '.join(str(x).lower() for x in row.values)
            if any(k in row_str for k in keywords):
                header_row = i
                break
        if header_row is None:
            # Print first 5 rows to help user identify manually
            print("   ⚠️ Could not detect header. Showing first 5 rows:")
            print(df_raw.head(5))
            continue
        df = pd.read_csv(file, header=header_row, low_memory=False)
        # Clean column names
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '').replace('  ', ' ') for c in df.columns]
        # Append with source file
        df['source_file'] = file.name
        all_data.append(df)
    if all_data:
        combined = pd.concat(all_data, ignore_index=True, sort=False)
        out = STAGING_DIR / "Economic_Unit_Aggregate.csv"
        combined.to_csv(out, index=False, encoding='utf-8')
        print(f"   ✅ Saved {len(combined)} rows to {out}")
    else:
        print("   ❌ No usable data extracted.")

def transform_all_census():
    transform_economic_census()

if __name__ == "__main__":
    transform_all_census()
