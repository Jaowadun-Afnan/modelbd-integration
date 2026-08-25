import pandas as pd
from pathlib import Path
from mapping_dicts import parse_fiscal_year

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)
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
def transform_all_agri_labor():
    # Find all ban-key-indicators and other relevant files
    patterns = ["*ban-key-indicators*.csv", "*agriculture*.csv", "*labor*.csv", "*labour*.csv"]
    files = []
    for p in patterns:
        files.extend(RAW_DIR.glob(p))
    files = list(set(files))
    if not files:
        print("⚠️ No agriculture/labor files found. Skipping.")
        return
    all_dfs = []
    for file in files:
        print(f"   Processing {file.name}...")
        # The ban-key-indicators file is complex. We'll extract the labor force section.
        if "ban-key-indicators" in file.name.lower():
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
            # The next row is the header: years (e.g., 2000, 2001...)
            header_row = labor_start + 1
            # Find the row that contains 'Labor force participation rate'
            # Actually we'll just take the rows from labor_start to the next section.
            # For simplicity, we'll extract from labor_start until a row with empty first column and all NaN? 
            # We'll grab a chunk: from labor_start to the row that starts with 'NATIONAL ACCOUNTS'
            national_start = None
            for i in range(labor_start, len(df)):
                if any('NATIONAL ACCOUNTS' in str(val).upper() for val in df.iloc[i].values):
                    national_start = i
                    break
            if national_start is None:
                national_start = len(df)
            labor_df = df.iloc[labor_start:national_start].copy()
            # Now clean: the first column is indicator, second is maybe blank, then years.
            # We'll convert to proper dataframe using the years row as header.
            # But the labor_df has row with years: after the 'LABOR FORCE' title, there is a row with years.
            # Actually the structure is: row0: 'LABOR FORCE', row1: years, row2: 'Employed', etc.
            # So we can extract years from row1.
            years_row = labor_df.iloc[1]
            years = [parse_fiscal_year(str(y), return_start_year=True) for y in years_row[2:] if str(y) not in ['', 'nan']]
            # For each subsequent row, we have a description and values.
            for idx in range(2, len(labor_df)):
                row = labor_df.iloc[idx]
                desc = str(row.iloc[0])
                if desc.lower() in ['', 'nan', 'employ']:  # skip header?
                    # Actually we want all rows after the years row.
                    # We'll create a DataFrame with columns: description, year, value
                    # For simplicity, we'll save raw rows.
                    pass
            # Since this file is very complex, we'll just save the labor section raw for now.
            out = STAGING_DIR / "Labor_Force_Raw.csv"
            labor_df.to_csv(out, index=False, encoding='utf-8')
            print(f"      ✅ Saved labor force raw section to {out}")
        else:
            # For simple agriculture/labor files, just copy with standardized columns
            df = pd.read_csv(file, low_memory=False)
            df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
            df['source_file'] = file.name
            all_dfs.append(df)
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True, sort=False)
        out = STAGING_DIR / "Agriculture_Labor_Combined.csv"
        combined.to_csv(out, index=False, encoding='utf-8')
        print(f"   ✅ Saved {len(combined)} rows to {out}")

if __name__ == "__main__":
    transform_all_agri_labor()
