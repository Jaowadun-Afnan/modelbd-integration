import pandas as pd
from pathlib import Path

# Correct base path: project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_metadata_country():
    meta_file = RAW_DIR / "Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv"
    if not meta_file.exists():
        print("⚠️ Metadata_Country not found. Skipping.")
        return
    df = pd.read_csv(meta_file, low_memory=False)
    # Print columns for debugging
    print("   Columns found in Metadata_Country:", list(df.columns))
    rename_map = {
        "Country Code": "country_code",
        "Region": "region",
        "IncomeGroup": "income_group",
        "SpecialNotes": "special_notes",
        "TableName": "country_name"
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    if 'country_code' not in df.columns:
        print("   ❌ 'Country Code' column not found. Check the file.")
        return
    if 'country_name' not in df.columns:
        df['country_name'] = df['country_code']
    keep_cols = ['country_code', 'country_name', 'region', 'income_group', 'special_notes']
    df = df[[c for c in keep_cols if c in df.columns]]
    df.drop_duplicates(subset=['country_code'], inplace=True)
    out = STAGING_DIR / "Country.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} countries to {out}")

def transform_metadata_indicator():
    meta_file = RAW_DIR / "Metadata_Indicator_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv"
    if not meta_file.exists():
        print("⚠️ Metadata_Indicator not found. Skipping.")
        return
    df = pd.read_csv(meta_file, low_memory=False)
    print("   Columns found in Metadata_Indicator:", list(df.columns))
    rename_map = {
        "Indicator Code": "indicator_code",
        "Indicator Name": "indicator_name",
        "SOURCE_NOTE": "source_notes",
        "SOURCE_ORGANIZATION": "source_organization"
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    if 'indicator_code' not in df.columns:
        # Try alternative case
        if 'IndicatorCode' in df.columns:
            df.rename(columns={'IndicatorCode':'indicator_code'}, inplace=True)
        else:
            print("   ❌ 'Indicator Code' column not found. Check the file.")
            return
    df['domain'] = 'Other'
    keep_cols = ['indicator_code', 'indicator_name', 'domain', 'source_notes', 'source_organization']
    df = df[[c for c in keep_cols if c in df.columns]]
    df.drop_duplicates(subset=['indicator_code'], inplace=True)
    out = STAGING_DIR / "Indicator_Definition.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} indicators to {out}")

def transform_wdi_observations():
    wdi_file = RAW_DIR / "API_SP.POP.TOTL_DS2_en_csv_v2_282912_melted.csv"
    if not wdi_file.exists():
        print("⚠️ WDI melted file not found. Skipping.")
        return
    df = pd.read_csv(wdi_file, low_memory=False)
    print("   Columns found in WDI melted:", list(df.columns))
    rename_map = {
        "Country Code": "country_code",
        "Indicator Code": "indicator_code",
        "year": "year",
        "value": "value"
    }
    df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
    required = ['country_code', 'indicator_code', 'year']
    if not all(col in df.columns for col in required):
        print("   ❌ Required columns missing. Check file.")
        return
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(subset=required, inplace=True)
    df['domain'] = 'Other'
    df.drop_duplicates(subset=['country_code', 'indicator_code', 'year'], inplace=True)
    out = STAGING_DIR / "Country_Indicator_Observation.csv"
    df.to_csv(out, index=False, encoding='utf-8')
    print(f"   ✅ Saved {len(df)} rows to {out}")

if __name__ == "__main__":
    transform_metadata_country()
    transform_metadata_indicator()
    transform_wdi_observations()
