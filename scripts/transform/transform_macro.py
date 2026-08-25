import pandas as pd
import re
from pathlib import Path
from mapping_dicts import map_sector_code, parse_fiscal_year

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    print("   → Processing Macroeconomic Indicator...")
    gdp_file = RAW_DIR / "Nominal and Real GDP 2007-16 (csv).csv"
    if not gdp_file.exists():
        print("      ⚠️ Nominal GDP file not found.")
        return
    df = pd.read_csv(gdp_file)
    # Normalise column names (strip spaces, parentheses)
    df.columns = [re.sub(r'\s+', ' ', str(c).strip()) for c in df.columns]
    # Map common names
    rename_map = {
        'Year': 'year',
        'Nominal GDP Growth (%)': 'nominal_growth_rate',
        'Real GDP Growth (%)': 'real_growth_rate',
        'Inflation Rate (%)': 'inflation_rate'
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    if 'year' not in df.columns:
        print("      ⚠️ GDP file missing 'Year' column.")
        return
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df.dropna(subset=['year'], inplace=True)
    df['year'] = df['year'].astype(int)
    df.drop_duplicates(subset=['year'], inplace=True)
    out_path = STAGING_DIR / "Macroeconomic_Indicator.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} years to {out_path}")

def transform_sectoral_gdp():
    print("   → Processing Sectoral GDP...")
    # Search for any NAG export file (CSV version of the Excel sheet)
    nag_files = list(RAW_DIR.glob("nag_bgd_*NAG_2015-16*.csv")) + list(RAW_DIR.glob("nag_bgd_*.csv"))
    if not nag_files:
        print("      ⚠️ NAG sector sheet not found. Run Excel extraction.")
        return
    # For simplicity, take the first matching file
    file = nag_files[0]
    print(f"      Using file: {file.name}")
    # Read the file. It may have a header row with merged cells.
    # We'll try to detect the header row.
    df_raw = pd.read_csv(file, header=None, low_memory=False)
    # Find the row that contains 'Year' or 'Component' etc.
    header_row = None
    for i, row in df_raw.iterrows():
        if any(str(val).strip().lower() in ['year', 'component', 'sector'] for val in row.values):
            header_row = i
            break
    if header_row is None:
        print("      ⚠️ Could not detect header row in NAG file.")
        return
    # Set header
    df = pd.read_csv(file, header=header_row, low_memory=False)
    # Clean columns
    df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df.columns]
    # Attempt to unpivot if the data is wide (e.g., sectors as columns)
    # We'll detect if there is a 'Year' column and many sector columns.
    if 'Year' in df.columns or 'year' in df.columns:
        year_col = 'Year' if 'Year' in df.columns else 'year'
        # Assume all other numeric columns are sector values
        id_vars = [year_col] + [c for c in df.columns if c.lower() in ['base year', 'price type', 'component']]
        value_vars = [c for c in df.columns if c not in id_vars]
        df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='sector_name', value_name='value_millions')
        # Map sector names using map_sector_code
        df_melted['sector_code'] = df_melted['sector_name'].apply(map_sector_code)
        # Rename remaining columns
        rename_cols = {
            'Year': 'year', 'year': 'year',
            'Base Year': 'base_year', 'base year': 'base_year',
            'Price Type': 'price_type', 'price type': 'price_type',
            'Component': 'component_type', 'component': 'component_type'
        }
        df_melted.rename(columns={k:v for k,v in rename_cols.items() if k in df_melted.columns}, inplace=True)
        # Ensure required columns exist
        required = ['year', 'sector_code', 'value_millions']
        if not all(col in df_melted.columns for col in required):
            print("      ⚠️ Melted data missing required columns.")
            return
        # Clean types
        df_melted['year'] = pd.to_numeric(df_melted['year'], errors='coerce')
        df_melted['value_millions'] = pd.to_numeric(df_melted['value_millions'], errors='coerce')
        df_melted.dropna(subset=required, inplace=True)
        # Drop rows with unmapped sector
        df_melted = df_melted[df_melted['sector_code'] != 'UNMAPPED']
        out_path = STAGING_DIR / "Sectoral_GDP.csv"
        df_melted.to_csv(out_path, index=False, encoding='utf-8')
        print(f"      ✅ Saved {len(df_melted)} sector records to {out_path}")
    else:
        print("      ⚠️ NAG file structure not as expected. Please adjust logic or provide a melted CSV.")
        # If the file is already long format, just rename and save.
        # Assume columns like: Year, Base_Year, Price_Type, Component, Sector, Value
        # We'll just map common columns.
        rename_map = {
            'Year': 'year', 'Base Year': 'base_year', 'Price Type': 'price_type',
            'Component': 'component_type', 'Sector': 'sector_name', 'Value': 'value_millions'
        }
        df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
        if 'value_millions' not in df.columns:
            print("      ⚠️ Cannot find value column in NAG file.")
            return
        if 'sector_name' in df.columns:
            df['sector_code'] = df['sector_name'].apply(map_sector_code)
            df = df[df['sector_code'] != 'UNMAPPED']
        # Save
        out_path = STAGING_DIR / "Sectoral_GDP.csv"
        df.to_csv(out_path, index=False, encoding='utf-8')
        print(f"      ✅ Saved {len(df)} sector records (fallback) to {out_path}")

def transform_exchange_rate():
    print("   → Processing Exchange Rate...")
    exr_files = list(RAW_DIR.glob("exr_bgd_*.csv"))
    if not exr_files:
        print("      ⚠️ Exchange rate file not found.")
        return
    df = pd.read_csv(exr_files[0], low_memory=False)
    rename_map = {
        'Year': 'year', 'Month': 'month', 'Rate_Type': 'rate_type',
        'Exchange_Rate': 'exchange_rate_value', 'End_of_Period_Rate': 'end_of_period_rate',
        'Period_Average_Rate': 'period_average_rate'
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    if 'year' not in df.columns:
        print("      ⚠️ Exchange rate file missing 'Year' column.")
        return
    # Fill missing columns
    if 'month' not in df.columns:
        df['month'] = 0
    if 'rate_type' not in df.columns:
        df['rate_type'] = 'Unknown'
    if 'exchange_rate_value' not in df.columns:
        df['exchange_rate_value'] = df.get('Value', pd.Series(dtype=float))
    if 'end_of_period_rate' not in df.columns:
        df['end_of_period_rate'] = None
    if 'period_average_rate' not in df.columns:
        df['period_average_rate'] = None
    # Clean
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)
    df['exchange_rate_value'] = pd.to_numeric(df['exchange_rate_value'], errors='coerce')
    df.dropna(subset=['year', 'exchange_rate_value'], inplace=True)
    out_path = STAGING_DIR / "Exchange_Rate.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} exchange rates to {out_path}")

def transform_all_macro():
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()

if __name__ == "__main__":
    transform_all_macro()
