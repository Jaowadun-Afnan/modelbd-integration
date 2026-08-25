import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "pdf_tables"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def is_sequential_numbers(row):
    """Check if a row is just 0,1,2,3... (likely a dummy header)"""
    values = []
    for v in row:
        try:
            values.append(int(float(v)))
        except:
            return False
    return values == list(range(len(values)))

def transform_economic_census():
    # Find all CSVs in the pdf_tables folder
    census_files = list(RAW_DIR.glob("*.csv"))
    if not census_files:
        print("⚠️ No census table files found in pdf_tables. Skipping.")
        return
    all_data = []
    for file in census_files:
        print(f"   Processing {file.name}...")
        # Read without header
        df_raw = pd.read_csv(file, header=None, low_memory=False, skipinitialspace=True)
        # Skip empty rows and rows that are just 0,1,2...
        df_raw = df_raw.dropna(how='all')
        # Find header row: first row that has at least 2 non-null values and is not sequential
        header_row = None
        for i, row in df_raw.iterrows():
            if is_sequential_numbers(row):
                continue
            # Count non-null values
            non_null = row.notna().sum()
            if non_null >= 2:
                # Heuristic: if row contains any alpha character, it's likely a header
                row_str = ' '.join(str(x) for x in row.values if pd.notna(x))
                if any(c.isalpha() for c in row_str):
                    header_row = i
                    break
        if header_row is None:
            # Fallback: use row with most non-null values
            non_null_counts = df_raw.notna().sum(axis=1)
            header_row = non_null_counts.idxmax()
        # Set header
        df = pd.read_csv(file, header=header_row, low_memory=False, skipinitialspace=True)
        # Clean column names
        df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '').replace('  ', ' ') for c in df.columns]
        # Remove any column that is entirely NaN
        df = df.dropna(axis=1, how='all')
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
