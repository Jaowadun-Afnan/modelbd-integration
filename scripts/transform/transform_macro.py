import pandas as pd
import re
from pathlib import Path
from mapping_dicts import parse_fiscal_year, map_sector_code

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    """Parse 'Nominal and Real GDP 2007-16 (csv).csv'."""
    # Find the file explicitly (prefer the one with 'Nominal and Real GDP')
    gdp_files = list(RAW_DIR.glob("*Nominal*GDP*.csv")) + list(RAW_DIR.glob("*GDP*.csv"))
    if not gdp_files:
        print("⚠️ GDP file not found. Skipping.")
        return
    file = gdp_files[0]
    print(f"   Using file: {file.name}")
    df = pd.read_csv(file, low_memory=False)
    # Show original columns for debugging
    print("   Original columns:", list(df.columns))

    # The file has two header rows. We'll use the first as header,
    # and drop the second row that contains 'Nominal growth rate' etc.
    df.columns = [str(c).strip() for c in df.columns]
    # Drop the row where 'Period' is NaN (the sub-header row)
    df = df.dropna(subset=['Period'])

    # Rename columns
    rename_map = {
        "Period": "period",
        "GDP growth rate": "nominal_growth_rate",
        "Inflation rate (Base: 2005-06)": "inflation_rate"
    }
    df.rename(columns=rename_map, inplace=True)

    # The third column (empty name or 'Unnamed: 2') holds 'Real growth rate'
    unnamed_cols = [c for c in df.columns if c.startswith('Unnamed') or c == '']
    if unnamed_cols:
        # There might be multiple unnamed columns; take the first one after gdp_growth_rate
        # We'll rename it to 'real_growth_rate'
        df.rename(columns={unnamed_cols[0]: 'real_growth_rate'}, inplace=True)

    # Convert period to string and extract year
    df['period'] = df['period'].astype(str).str.strip()
    df['year'] = df['period'].apply(parse_fiscal_year, return_start_year=True)
    # Drop rows where year is 0 (invalid)
    df = df[df['year'] != 0]

    # Convert numeric columns
    for col in ['nominal_growth_rate', 'real_growth_rate', 'inflation_rate']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Keep only relevant columns
    keep = ['year', 'nominal_growth_rate', 'real_growth_rate', 'inflation_rate']
    df = df[[c for c in keep if c in df.columns]]
    df.drop_duplicates(subset=['year'], inplace=True)

    out = STAGING_DIR / "Macroeconomic_Indicator.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} rows to {out}")

def transform_sectoral_gdp():
    """Parse NAG file (e.g., nag_bgd (2)_NAG_2015_16.csv)."""
    nag_files = list(RAW_DIR.glob("*NAG*.csv")) + list(RAW_DIR.glob("*nag*.csv"))
    if not nag_files:
        print("⚠️ NAG sector file not found. Skipping.")
        return
    df_raw = pd.read_csv(nag_files[0], header=None, low_memory=False)
    # Find the row that contains "Descriptor" – that's the header row.
    header_row = None
    for i, row in df_raw.iterrows():
        if any(str(val).strip().lower() == 'descriptor' for val in row.values):
            header_row = i
            break
    if header_row is None:
        print("   ❌ Could not find 'Descriptor' row in NAG file.")
        return
    df = pd.read_csv(nag_files[0], header=header_row, low_memory=False)
    # Clean column names
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    id_col = df.columns[0]
    # All other columns are years
    year_cols = [c for c in df.columns if c != id_col and c != '']
    # Melt
    df_melted = df.melt(id_vars=[id_col], value_vars=year_cols,
                        var_name='year', value_name='value_millions')
    df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce').astype(int)
    df_melted = df_melted.rename(columns={id_col: 'sector_name'})
    df_melted['sector_code'] = df_melted['sector_name'].apply(map_sector_code)
    # Drop unmapped sectors and missing values
    df_melted = df_melted[df_melted['sector_code'] != 'UNMAPPED']
    df_melted = df_melted.dropna(subset=['year', 'value_millions'])
    # Add base year and price type (adjust as needed)
    df_melted['base_year'] = 2015  # or extract from filename
    df_melted['price_type'] = 'current'
    out = STAGING_DIR / "Sectoral_GDP.csv"
    df_melted.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df_melted)} sector records to {out}")

def transform_exchange_rate():
    """Parse exr CSV (wide format with year-month columns)."""
    exr_files = list(RAW_DIR.glob("exr*.csv")) + list(RAW_DIR.glob("*exchange*.csv"))
    if not exr_files:
        print("⚠️ Exchange rate file not found. Skipping.")
        return
    df_raw = pd.read_csv(exr_files[0], header=None, low_memory=False)
    # Find the row that contains 'Descriptor' – that's the header row.
    header_row = None
    for i, row in df_raw.iterrows():
        if any(str(val).strip().lower() == 'descriptor' for val in row.values):
            header_row = i
            break
    if header_row is None:
        # Try to find 'Exchange Rate' row
        for i, row in df_raw.iterrows():
            if any('exchange rate' in str(val).lower() for val in row.values):
                header_row = i
                break
    if header_row is None:
        print("   ❌ Could not find header row in exchange rate file.")
        return
    df = pd.read_csv(exr_files[0], header=header_row, low_memory=False)
    # Clean column names
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    id_col = df.columns[0]
    date_cols = [c for c in df.columns if c != id_col]
    # Melt
    df_melted = df.melt(id_vars=[id_col], value_vars=date_cols,
                        var_name='date_str', value_name='exchange_rate_value')
    df_melted = df_melted.rename(columns={id_col: 'rate_type'})
    # Filter out rows where date_str is not in YYYY-MM format
    df_melted = df_melted[df_melted['date_str'].str.match(r'^\d{4}-\d{2}$', na=False)]
    # Split into year and month
    df_melted[['year', 'month']] = df_melted['date_str'].str.split('-', expand=True)
    df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce')
    df_melted['month'] = pd.to_numeric(df_melted['month'], errors='coerce')
    # Drop rows with missing year or value
    df_melted = df_melted.dropna(subset=['year', 'exchange_rate_value'])
    # Add flags for rate type
    df_melted['end_of_period_rate'] = df_melted['rate_type'].str.contains('End of period', case=False).astype(int)
    df_melted['period_average_rate'] = df_melted['rate_type'].str.contains('Period average', case=False).astype(int)
    # Clean rate_type
    df_melted['rate_type'] = df_melted['rate_type'].str.strip()
    # Keep only relevant columns
    keep = ['year', 'month', 'rate_type', 'exchange_rate_value', 'end_of_period_rate', 'period_average_rate']
    out = STAGING_DIR / "Exchange_Rate.csv"
    df_melted[keep].to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df_melted)} exchange rate records to {out}")

def transform_all_macro():
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()

if __name__ == "__main__":
    transform_all_macro()
