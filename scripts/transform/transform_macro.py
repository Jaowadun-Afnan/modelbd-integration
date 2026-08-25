import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_macroeconomic_indicator():
    # Find file dynamically
    gdp_files = list(RAW_DIR.glob("*GDP*.csv")) + list(RAW_DIR.glob("*gdp*.csv"))
    if not gdp_files:
        print("⚠️ No GDP file found. Skipping.")
        return
    df = pd.read_csv(gdp_files[0], low_memory=False)
    print("   Columns found in GDP file:", list(df.columns))
    # Normalise column names
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    # Try to find year column
    if 'year' not in df.columns:
        # Look for common variants
        for col in df.columns:
            if 'year' in col:
                df.rename(columns={col:'year'}, inplace=True)
                break
    if 'year' not in df.columns:
        print("   ❌ No 'Year' column found. Please rename or adjust.")
        return
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df.dropna(subset=['year'], inplace=True)
    df['year'] = df['year'].astype(int)
    # Save whatever columns exist
    out = STAGING_DIR / "Macroeconomic_Indicator.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} rows to {out}")

def transform_sectoral_gdp():
    # Search for any NAG file
    nag_files = list(RAW_DIR.glob("*nag*.csv")) + list(RAW_DIR.glob("*NAG*.csv"))
    if not nag_files:
        print("⚠️ NAG sector file not found. Skipping.")
        return
    df = pd.read_csv(nag_files[0], low_memory=False)
    print("   Columns found in NAG file:", list(df.columns))
    # ... (rest similar to earlier, but you'll need to adjust based on actual structure)

def transform_exchange_rate():
    exr_files = list(RAW_DIR.glob("exr_*.csv"))
    if not exr_files:
        print("⚠️ Exchange rate file not found. Skipping.")
        return
    # ... (similar)

def transform_all_macro():
    transform_macroeconomic_indicator()
    transform_sectoral_gdp()
    transform_exchange_rate()

if __name__ == "__main__":
    transform_all_macro()
