import pandas as pd
from pathlib import Path
from mapping_dicts import parse_fiscal_year, map_sector_code

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    """Parse 'Nominal and Real GDP 2007-16 (csv).csv'."""
    gdp_files = list(RAW_DIR.glob("*GDP*.csv")) + list(RAW_DIR.glob("*Nominal*.csv"))
    if not gdp_files:
        print("⚠️ No GDP file found. Skipping.")
        return
    df = pd.read_csv(gdp_files[0], low_memory=False)
    # The file has two header rows; we'll take the first as header, but the second row
    # contains the sub‑headers (Nominal growth, Real growth). We'll just drop that row.
    df.columns = [str(c).strip() for c in df.columns]
    # Rename known columns
    rename_map = {
        "Period": "period",
        "GDP growth rate": "nominal_growth_rate",
        "Inflation rate (Base: 2005-06)": "inflation_rate"
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    # The empty column (third) holds 'Real growth rate' in the second row – we'll rename it.
    # Find the column with empty name or 'Unnamed: 2'
    for col in df.columns:
        if col.startswith('Unnamed'):
            df.rename(columns={col: 'real_growth_rate'}, inplace=True)
            break
    # Drop the second header row (where period is NaN)
    df['period'] = df['period'].astype(str).str.strip()
    df = df[df['period'] != 'nan']
    # Extract year
    df['year'] = df['period'].apply(parse_fiscal_year, return_start_year=True)
    # Drop rows with year 0 (invalid)
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
    # Use that row as header, skip the rows before it.
    df = pd.read_csv(nag_files[0], header=header_row, low_memory=False)
    # Clean column names: first column should be sector/indicator, rest are years.
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    # The first column is the sector/indicator name.
    id_col = df.columns[0]
    # We only want rows that are actual sectors (not total or descriptions).
    # Let's melt: all year columns become 'year', values become 'value'.
    year_cols = [c for c in df.columns if c != id_col and c != '' and c != 'Unnamed: 0']
    df_melted = df.melt(id_vars=[id_col], value_vars=year_cols,
                        var_name='year', value_name='value_millions')
    # Convert year to int (they are like 2016.0, 2017.0)
    df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce').astype(int)
    # Map sector code from the id_col
    df_melted = df_melted.rename(columns={id_col: 'sector_name'})
    df_melted['sector_code'] = df_melted['sector_name'].apply(map_sector_code)
    # Drop rows with unmapped sector or missing values
    df_melted = df_melted[df_melted['sector_code'] != 'UNMAPPED']
    df_melted = df_melted.dropna(subset=['year', 'value_millions'])
    # Add base_year and price_type based on file name or content
    df_melted['base_year'] = 2015  # you can extract from file name
    df_melted['price_type'] = 'current'  # adjust if constant
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
    # Find the row that contains "Descriptor" or "Exchange Rate" – that's the header row.
    header_row = None
    for i, row in df_raw.iterrows():
        if any(str(val).strip().lower() in ['descriptor', 'exchange rate'] for val in row.values):
            header_row = i
            break
    if header_row is None:
        print("   ❌ Could not find header row in exchange rate file.")
        return
    df = pd.read_csv(exr_files[0], header=header_row, low_memory=False)
    # Clean column names
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    # First column is descriptor (rate type), rest are year-month (e.g., 2005-01)
    id_col = df.columns[0]
    date_cols = [c for c in df.columns if c != id_col]
    # Melt
    df_melted = df.melt(id_vars=[id_col], value_vars=date_cols,
                        var_name='date_str', value_name='exchange_rate_value')
    df_melted = df_melted.rename(columns={id_col: 'rate_type'})
    # Parse date_str like '2005-01'
    df_melted[['year', 'month']] = df_melted['date_str'].str.split('-', expand=True)
    df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce')
    df_melted['month'] = pd.to_numeric(df_melted['month'], errors='coerce')
    # Keep rows with valid year and value
    df_melted = df_melted.dropna(subset=['year', 'exchange_rate_value'])
    # Add end_of_period and period_average flags based on rate_type
    df_melted['end_of_period_rate'] = df_melted['rate_type'].str.contains('End of period', case=False).astype(int)
    df_melted['period_average_rate'] = df_melted['rate_type'].str.contains('Period average', case=False).astype(int)
    # Clean up rate_type (optional)
    df_melted['rate_type'] = df_melted['rate_type'].str.strip()
    out = STAGING_DIR / "Exchange_Rate.csv"
    df_melted[['year', 'month', 'rate_type', 'exchange_rate_value', 'end_of_period_rate', 'period_average_rate']].to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df_melted)} exchange rate records to {out}")

def transform_all_macro():
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()

if __name__ == "__main__":
    transform_all_macro()
