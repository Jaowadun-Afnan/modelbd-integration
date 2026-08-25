import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "pdf_tables"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_economic_census():
    print("   → Processing Economic Census PDFs...")
    # Look for any CSV extracted from the census PDF
    census_files = list(RAW_DIR.glob("3ab00376bfa049a9a1674fb786126915_table_*.csv"))
    if not census_files:
        census_files = list(RAW_DIR.glob("*census*.csv"))  # fallback
    if not census_files:
        print("      ⚠️ No Economic Census PDF tables found.")
        return
    all_data = []
    for file in census_files:
        print(f"      Processing {file.name}...")
        # Read raw CSV without header (often header is row 2 or 3)
        df_raw = pd.read_csv(file, header=None, low_memory=False)
        # Try to find the header row: look for a row that contains words like 'sector', 'unit', 'value'
        header_row = None
        for i, row in df_raw.iterrows():
            row_str = ' '.join(str(x).lower() for x in row.values)
            if any(keyword in row_str for keyword in ['sector', 'unit', 'establishment', 'person', 'value']):
                header_row = i
                break
        if header_row is None:
            print(f"      ⚠️ Could not detect header in {file.name}, skipping.")
            continue
        # Re-read with header
        df = pd.read_csv(file, header=header_row, low_memory=False)
        # Clean column names
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '').replace('  ', ' ') for c in df.columns]
        # Standardise some known columns
        rename_map = {
            'Sector': 'sector_name',
            'Economic Sector': 'sector_name',
            'Number of Establishments': 'num_establishments',
            'Establishments': 'num_establishments',
            'Persons Engaged': 'persons_engaged',
            'Persons': 'persons_engaged',
            'Value': 'value',
            'Year': 'year'
        }
        df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
        # If we have a sector name, map to code
        if 'sector_name' in df.columns:
            from mapping_dicts import map_sector_code
            df['sector_code'] = df['sector_name'].apply(map_sector_code)
        # Ensure at least one value column exists
        value_cols = [c for c in df.columns if c in ['num_establishments', 'persons_engaged', 'value']]
        if not value_cols:
            print(f"      ⚠️ No value column found in {file.name}.")
            continue
        # Add source file
        df['source_file'] = file.name
        all_data.append(df)
    if not all_data:
        print("      ❌ No usable data extracted.")
        return
    combined = pd.concat(all_data, ignore_index=True, sort=False)
    # Save full data (not just sample)
    out_path = STAGING_DIR / "Economic_Unit_Aggregate.csv"
    combined.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(combined)} rows to {out_path}")

def transform_all_census():
    transform_economic_census()

if __name__ == "__main__":
    transform_all_census()
