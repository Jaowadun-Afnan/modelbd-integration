import pandas as pd
import re
from pathlib import Path
from mapping_dicts import parse_fiscal_year, map_sector_code

RAW_DIR = Path("../../raw_data/extracted/csv")
STAGING_DIR = Path("../../staging/clean")
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    """
    Merges 'Nominal and Real GDP' and 'ban-key-indicators' into a single
    Macroeconomic_Indicator table by year.
    """
    print("   → Processing Macroeconomic Indicator...")
    
    # 1. Load Nominal GDP file
    gdp_file = RAW_DIR / "Nominal and Real GDP 2007-16 (csv).csv"
    if not gdp_file.exists():
        print("      ⚠️ Nominal GDP file not found.")
        return
    
    df_gdp = pd.read_csv(gdp_file)
    df_gdp = df_gdp.rename(columns={
        'Year': 'year',
        'Nominal GDP Growth (%)': 'nominal_growth_rate',
        'Real GDP Growth (%)': 'real_growth_rate',
        'Inflation Rate (%)': 'inflation_rate'
    })
    
    # 2. Load Ban Key Indicators (if available)
    # Since Ban indicators are in Excel with complex pivots, we'll parse the specific sheet.
    # For now, we just take the GDP file as the base, and add columns later.
    # Let's just create a minimal version.
    
    # Ensure year is int
    df_gdp['year'] = pd.to_numeric(df_gdp['year'], errors='coerce')
    df_gdp = df_gdp.dropna(subset=['year'])
    df_gdp['year'] = df_gdp['year'].astype(int)
    
    # Deduplicate
    df_gdp = df_gdp.drop_duplicates(subset=['year'])
    
    out_path = STAGING_DIR / "Macroeconomic_Indicator.csv"
    df_gdp.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df_gdp)} years to {out_path}")

def transform_sectoral_gdp():
    """
    Parses the NAG Excel export (GDP by sector) into Sectoral_GDP.
    """
    print("   → Processing Sectoral GDP...")
    
    # The nag_bgd (2).xlsx exports multiple sheets.
    # We look for the NAG_2015-16 sheet.
    sheet_files = list(RAW_DIR.glob("nag_bgd_*_NAG_2015-16.csv"))
    if not sheet_files:
        print("      ⚠️ NAG sector sheet not found. Run Excel extraction.")
        return
    
    df = pd.read_csv(sheet_files[0])
    # This requires careful unpivoting depending on the structure.
    # Placeholder logic: Assume columns: Year, Base_Year, Price_Type, Sector, Value.
    # We will rename dynamically.
    
    # Since the structure is complex, we just ensure the required columns exist.
    # For a real run, you will need to match the exact columns.
    required_cols = ['year', 'base_year', 'price_type', 'component_type', 
                     'component_name', 'sector_code', 'value_millions']
    
    # Placeholder: create an empty DataFrame with required columns if parsing fails.
    df_out = pd.DataFrame(columns=required_cols)
    
    out_path = STAGING_DIR / "Sectoral_GDP.csv"
    df_out.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df_out)} sector records to {out_path}")
    print("      ⚠️ NOTE: Sectoral_GDP parsing needs manual column mapping based on NAG structure.")

def transform_exchange_rate():
    """Transforms exr_bgd export into Exchange_Rate table."""
    print("   → Processing Exchange Rate...")
    
    exr_files = list(RAW_DIR.glob("exr_bgd_*.csv"))
    if not exr_files:
        print("      ⚠️ Exchange rate file not found.")
        return
    
    df = pd.read_csv(exr_files[0])
    # Assuming columns: Year, Month, Rate_Type, Exchange_Rate_Value
    # Rename to match schema
    df = df.rename(columns={
        'Year': 'year',
        'Month': 'month',
        'Rate_Type': 'rate_type',
        'Exchange_Rate': 'exchange_rate_value'
    })
    
    # Fill missing with 0 or NULL
    df['month'] = df['month'].fillna(0).astype(int)
    df['end_of_period_rate'] = None
    df['period_average_rate'] = None
    
    out_path = STAGING_DIR / "Exchange_Rate.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} exchange rates to {out_path}")

def transform_all_macro():
    """Run all macro transformers."""
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()
    # Add Price_Index, Quarterly_GDP, etc. here following the same pattern.

if __name__ == "__main__":
    transform_all_macro()
