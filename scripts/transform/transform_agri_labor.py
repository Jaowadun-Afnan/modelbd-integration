import pandas as pd
from pathlib import Path
from mapping_dicts import parse_fiscal_year

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_all_agri_labor():
    # Focus on ban-key-indicators files for labor data
    files = list(RAW_DIR.glob("*ban-key-indicators*.csv"))
    if not files:
        print("⚠️ No ban-key-indicators files found. Skipping.")
        return
    all_dfs = []
    for file in files:
        print(f"   Processing {file.name}...")
        df = pd.read_csv(file, header=None, low_memory=False)
        # Find the row that contains 'LABOR FORCE'
        labor_start = None
        for i, row in df.iterrows():
            if any('LABOR FORCE' in str(val).upper() for val in row.values):
                labor_start = i
                break
        if labor_start is None:
            print("      ⚠️ Labor force section not found.")
            continue
        # Find the row with years (the next row after 'LABOR FORCE')
        years_row_idx = labor_start + 1
        # We need to find the end of the labor force section (next section like 'NATIONAL ACCOUNTS')
        national_start = None
        for i in range(labor_start + 1, len(df)):
            if any('NATIONAL ACCOUNTS' in str(val).upper() for val in df.iloc[i].values):
                national_start = i
                break
        if national_start is None:
            national_start = len(df)
        # Extract the labor force section
        section = df.iloc[labor_start:national_start].copy()
        # The row at years_row_idx contains years (e.g., 2000, 2001, ...)
        years_row = section.iloc[1]
        # Build a mapping from column index to year
        years = []
        for col_idx in range(2, len(years_row)):  # first two columns are blank/descriptor
            val = years_row.iloc[col_idx]
            year = parse_fiscal_year(val, return_start_year=True)
            years.append(year)
        # For each subsequent row, create records
        for idx in range(2, len(section)):
            row = section.iloc[idx]
            desc = str(row.iloc[0]).strip()
            if desc in ['', 'nan', 'Employed', 'Unemployed', 'Labor force participation rate', 'Male', 'Female']:
                # Skip header/blank lines or maybe these are indicators we want?
                # We'll include all rows that have a description and values.
                pass
            # Create records for this indicator
            for col_idx in range(2, len(years_row)):
                year = years[col_idx - 2]
                value = row.iloc[col_idx]
                if pd.notna(value) and year > 0:
                    all_dfs.append({
                        'source_file': file.name,
                        'indicator': desc,
                        'year': year,
                        'value': value
                    })
    if all_dfs:
        combined = pd.DataFrame(all_dfs)
        out = STAGING_DIR / "Labor_Force_Summary.csv"
        combined.to_csv(out, index=False, encoding='utf-8')
        print(f"   ✅ Saved {len(combined)} labor force records to {out}")
    else:
        print("   ❌ No labor force data extracted.")

if __name__ == "__main__":
    transform_all_agri_labor()