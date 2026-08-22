import pandas as pd
import numpy as np
from pathlib import Path
from mapping_dicts import clean_text

# Paths
RAW_DIR = Path("../../raw_data/extracted/csv")
STAGING_DIR = Path("../../staging/clean")
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_wdi_observations():
    """
    Transforms the unpivoted WDI CSV into Country_Indicator_Observation.
    Also extracts Country and Indicator_Definition from metadata.
    """
    print("   → Processing WDI observations...")

    # 1. Load the melted WDI data
    wdi_file = RAW_DIR / "API_SP.POP.TOTL_DS2_en_csv_v2_282912_melted.csv"
    if not wdi_file.exists():
        print("      ⚠️ WDI melted file not found. Run Phase 3 first.")
        return

    df = pd.read_csv(wdi_file, low_memory=False)

    # 2. Rename columns to match the logical schema
    df = df.rename(columns={
        "Country Code": "country_code",
        "Indicator Code": "indicator_code",
        "year": "year",
        "value": "value"
    })

    # 3. Clean data types
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # 4. Drop rows where key fields are missing
    df = df.dropna(subset=['country_code', 'indicator_code', 'year'])

    # 5. Add a placeholder domain (can be enriched later from Metadata_Indicator)
    df['domain'] = 'Other'

    # 6. Deduplicate on the exact composite primary key
    df = df.drop_duplicates(subset=['country_code', 'indicator_code', 'year'])

    # 7. Save to staging
    output_path = STAGING_DIR / "Country_Indicator_Observation.csv"
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} rows to {output_path}")

def transform_metadata_country():
    """Extracts the Country dimension from WDI Metadata."""
    meta_file = RAW_DIR / "Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv"
    if not meta_file.exists():
        print("      ⚠️ Metadata_Country not found.")
        return
    
    df = pd.read_csv(meta_file, low_memory=False)
    df = df.rename(columns={
        "Country Code": "country_code",
        "Region": "region",
        "IncomeGroup": "income_group",
        "SpecialNotes": "special_notes"
    })
    # Add country_name from the TableName column if needed, or from main CSV
    # For simplicity, we'll just take what we have.
    df['country_name'] = df['country_code']  # Placeholder, we will enrich later
    df = df[['country_code', 'country_name', 'region', 'income_group', 'special_notes']]
    df = df.drop_duplicates(subset=['country_code'])
    
    out_path = STAGING_DIR / "Country.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} countries to {out_path}")

def transform_metadata_indicator():
    """Extracts the Indicator_Definition dimension from WDI Metadata."""
    meta_file = RAW_DIR / "Metadata_Indicator_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv"
    if not meta_file.exists():
        print("      ⚠️ Metadata_Indicator not found.")
        return
    
    df = pd.read_csv(meta_file, low_memory=False)
    df = df.rename(columns={
        "Indicator Code": "indicator_code",
        "Indicator Name": "indicator_name",
        "SOURCE_NOTE": "source_notes",
        "SOURCE_ORGANIZATION": "source_organization"
    })
    df['domain'] = 'Other'  # Placeholder
    df = df[['indicator_code', 'indicator_name', 'domain', 'source_notes', 'source_organization']]
    df = df.drop_duplicates(subset=['indicator_code'])
    
    out_path = STAGING_DIR / "Indicator_Definition.csv"
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Saved {len(df)} indicators to {out_path}")

if __name__ == "__main__":
    transform_metadata_country()
    transform_metadata_indicator()
    transform_wdi_observations()
