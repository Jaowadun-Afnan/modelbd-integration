import pandas as pd
from pathlib import Path

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
    # Normalise column names: strip and lower
    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {
        "country code": "country_code",
        "region": "region",
        "incomegroup": "income_group",
        "specialnotes": "special_notes",
        "tablename": "country_name"
    }
    df.rename(columns=rename_map, inplace=True)
    if 'country_code' not in df.columns:
        print("   ❌ 'Country Code' column not found.")
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
    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {
        "indicator_code": "indicator_code",
        "indicator_name": "indicator_name",
        "source_note": "source_notes",
        "source_organization": "source_organization"
    }
    # If 'indicator_code' not present, try to find it
    if 'indicator_code' not in df.columns:
        # Look for any column containing 'indicator' and 'code'
        for col in df.columns:
            if 'indicator' in col and 'code' in col:
                df.rename(columns={col: 'indicator_code'}, inplace=True)
                break
    if 'indicator_code' not in df.columns:
        print("   ❌ 'Indicator Code' column not found.")
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
    # Already has proper names? Maybe not - check
    # If 'country_code' not present, rename from 'Country Code'
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
