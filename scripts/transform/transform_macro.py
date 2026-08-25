import pandas as pd
from pathlib import Path
from mapping_dicts import parse_fiscal_year, map_sector_code

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    # Find any file containing 'GDP' or 'Nominal' or 'Real'
    gdp_files = list(RAW_DIR.glob("*GDP*.csv")) + list(RAW_DIR.glob("*Nominal*.csv")) + list(RAW_DIR.glob("*Real*.csv"))
    if not gdp_files:
        print("⚠️ No GDP file found. Skipping.")
        return
    df = pd.read_csv(gdp_files[0], low_memory=False)
    # Normalise columns
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    print("   Columns found:", list(df.columns))
    
    # Rename common columns
    rename_map = {
        'period': 'period',
        'gdp_growth_rate': 'nominal_growth_rate',
        'real_gdp_growth_rate': 'real_growth_rate',
        'inflation_rate_(base:_2005-06)': 'inflation_rate',
        'inflation_rate': 'inflation_rate'
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    
    # Determine year: from 'year' or 'period'
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
    elif 'period' in df.columns:
        # Apply parse_fiscal_year, which now returns 0 for invalid
        df['year'] = df['period'].apply(parse_fiscal_year, return_start_year=True)
        # Replace 0 with NaN and drop
        df['year'] = df['year'].replace(0, pd.NA)
    else:
        print("   ❌ No 'year' or 'period' column found.")
        return
    
    # Convert year to numeric and drop NaN
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    df.drop_duplicates(subset=['year'], inplace=True)
    
    out = STAGING_DIR / "Macroeconomic_Indicator.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} rows to {out}")

# ... rest of functions unchanged ...

def transform_sectoral_gdp():
    nag_files = list(RAW_DIR.glob("*nag*.csv")) + list(RAW_DIR.glob("*NAG*.csv"))
    if not nag_files:
        print("⚠️ NAG sector file not found. Skipping.")
        return
    df = pd.read_csv(nag_files[0], header=None, low_memory=False)
    print("   First 5 rows of NAG file:")
    print(df.head(5))
    # Attempt to detect header: row containing 'Sector' or 'Industry' or 'Component'
    header_row = None
    for i, row in df.iterrows():
        row_str = ' '.join(str(x).lower() for x in row.values)
        if any(k in row_str for k in ['sector', 'industry', 'component', 'agriculture']):
            header_row = i
            break
    if header_row is None:
        print("   ❌ Could not detect header. Need manual mapping.")
        return
    df = pd.read_csv(nag_files[0], header=header_row, low_memory=False)
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    print("   Columns after header detection:", list(df.columns))
    # Expect a long format: Year, Sector, Value, etc.
    # If not, we can't process automatically – you'll need to adjust.
    # For now, save as is.
    out = STAGING_DIR / "Sectoral_GDP.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved raw sector data to {out} (needs further processing).")

def transform_exchange_rate():
    exr_files = list(RAW_DIR.glob("exr*.csv")) + list(RAW_DIR.glob("*exchange*.csv")) + list(RAW_DIR.glob("*Exchange*.csv"))
    if not exr_files:
        print("⚠️ No exchange rate file found. Skipping.")
        return
    df = pd.read_csv(exr_files[0], low_memory=False)
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    # Rename known columns
    rename_map = {
        'year': 'year',
        'month': 'month',
        'rate_type': 'rate_type',
        'exchange_rate': 'exchange_rate_value',
        'value': 'exchange_rate_value',
        'end_of_period_rate': 'end_of_period_rate',
        'period_average_rate': 'period_average_rate'
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    if 'year' not in df.columns:
        print("   ❌ No 'year' column found.")
        return
    if 'exchange_rate_value' not in df.columns:
        # Try common alternative
        if 'rate' in df.columns:
            df.rename(columns={'rate': 'exchange_rate_value'}, inplace=True)
        else:
            print("   ❌ No exchange rate value column found.")
            return
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    if 'month' not in df.columns:
        df['month'] = 0
    df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)
    df['exchange_rate_value'] = pd.to_numeric(df['exchange_rate_value'], errors='coerce')
    df.dropna(subset=['year', 'exchange_rate_value'], inplace=True)
    out = STAGING_DIR / "Exchange_Rate.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} rows to {out}")

def transform_all_macro():
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()

if __name__ == "__main__":
    transform_all_macro()
