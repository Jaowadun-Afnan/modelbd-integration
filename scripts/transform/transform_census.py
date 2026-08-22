
import pandas as pd
from pathlib import Path
from mapping_dicts import map_admin_to_pcode

RAW_DIR = Path("../../raw_data/extracted/pdf_tables")
STAGING_DIR = Path("../../staging/clean")
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_economic_census():
    """
    Reads the Economic Census PDF tables and maps them to 
    Economic_Unit_Aggregate, Person_Engaged_Aggregate, Business_Ecommerce_Fact.
    """
    print("   → Processing Economic Census PDFs...")
    
    # Look for tables from the 3ab00376... PDF
    census_files = list(RAW_DIR.glob("3ab00376bfa049a9a1674fb786126915_table_*.csv"))
    if not census_files:
        print("      ⚠️ Economic Census PDF tables not found.")
        return
    
    # Usually Table 4.2, 4.4, 4.7, etc. contain the unit aggregates.
    # For this template, we consolidate them.
    
    all_data = []
    for f in census_files:
        df = pd.read_csv(f, header=None)  # PDF tables often lack proper headers
        # This is highly manual. In a real scenario, you will:
        # 1. Identify the header row.
        # 2. Set the header.
        # 3. Rename columns to match the schema.
        
        # Placeholder: just save a few sample rows for proof of concept.
        df['source_file'] = f.name
        all_data.append(df)
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        # Save a sample
        out_path = STAGING_DIR / "Economic_Unit_Aggregate.csv"
        combined.head(10).to_csv(out_path, index=False, encoding='utf-8')
        print(f"      ✅ Saved sample 10 rows to {out_path}")
    else:
        print("      ❌ No data extracted.")

def transform_all_census():
    transform_economic_census()

if __name__ == "__main__":
    transform_all_census()
