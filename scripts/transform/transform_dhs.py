
import pandas as pd
from pathlib import Path
from mapping_dicts import map_country_to_code, map_gender

RAW_DIR = Path("../../raw_data/extracted/csv")
STAGING_DIR = Path("../../staging/clean")
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_all_dhs():
    """
    Consolidates all DHS subnational CSVs into DHS_Subnational_Observation.
    """
    print("   → Consolidating DHS Subnational files...")
    
    # List of DHS files from your extracted folder
    dhs_patterns = [
        "dhs-quickstats_subnational_bgd (1).csv",
        "dhs-mobile_subnational_bgd (1).csv",
        "sdgs_subnational_bgd (1).csv",
        "mdgs_subnational_bgd (1).csv",
        "rbm_subnational_bgd (1).csv",
        "iycf_subnational_bgd (1).csv",
        "mics-indicators_subnational_bgd (1).csv",
        "access-to-health-care_subnational_bgd (1).csv",
        "anemia_subnational_bgd (1).csv",
        "birth-registration_subnational_bgd (1).csv",
        "child-mortality-rates_subnational_bgd (1).csv"
    ]
    
    all_dfs = []
    
    for pattern in dhs_patterns:
        file_path = RAW_DIR / pattern
        if not file_path.exists():
            print(f"      ⚠️ Skipping {pattern} (not found)")
            continue
        
        df = pd.read_csv(file_path, low_memory=False)
        
        # Standardize column names to match DHS_Subnational_Observation
        # Map common column names
        rename_map = {
            'ISO3': 'country_code',
            'SurveyYear': 'survey_year',
            'CharacteristicId': 'characteristic_id',
            'IndicatorId': 'indicator_id',
            'ByVariableId': 'by_variable_id',
            'DataId': 'data_id',
            'Location': 'location',
            'Indicator': 'indicator_name',
            'Value': 'value',
            'Precision': 'precision',
            'SurveyId': 'survey_id',
            'IndicatorOrder': 'indicator_order',
            'IndicatorType': 'indicator_type',
            'CharacteristicOrder': 'characteristic_order',
            'CharacteristicCategory': 'characteristic_category',
            'CharacteristicLabel': 'characteristic_label',
            'ByVariableLabel': 'by_variable_label',
            'IsTotal': 'is_total',
            'IsPreferred': 'is_preferred',
            'SDRID': 'sdr_id',
            'RegionId': 'region_id',
            'SurveyYearLabel': 'survey_year_label',
            'SurveyType': 'survey_type',
            'DenominatorWeighted': 'denominator_weighted',
            'DenominatorUnweighted': 'denominator_unweighted',
            'CILow': 'ci_low',
            'CIHigh': 'ci_high',
            'LevelRank': 'level_rank'
        }
        
        # Only rename columns that exist
        existing_rename = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=existing_rename)
        
        # Add a discriminator domain
        df['observation_domain'] = pattern.replace('.csv', '').replace('_subnational_bgd (1)', '')
        
        # Ensure country_code is standardized (if ISO3 exists, keep it; if not, map)
        if 'country_code' not in df.columns:
            if 'CountryName' in df.columns:
                df['country_code'] = df['CountryName'].apply(map_country_to_code)
        
        # Clean boolean columns to 'Y'/'N'
        for col in ['is_total', 'is_preferred']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: 'Y' if x in [1, '1', True, 'Y', 'y'] else 'N')
        
        # Drop rows missing the composite key
        pk_cols = ['survey_id', 'indicator_id', 'characteristic_id', 'by_variable_id']
        df = df.dropna(subset=[c for c in pk_cols if c in df.columns])
        
        all_dfs.append(df)
        print(f"      ✅ Loaded {pattern} ({len(df)} rows)")
    
    if not all_dfs:
        print("      ❌ No DHS files found.")
        return
    
    # Combine all DHS dataframes
    combined = pd.concat(all_dfs, ignore_index=True, sort=False)
    
    # Deduplicate on the composite key
    combined = combined.drop_duplicates(subset=['survey_id', 'indicator_id', 'characteristic_id', 'by_variable_id'])
    
    # Save
    out_path = STAGING_DIR / "DHS_Subnational_Observation.csv"
    combined.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Combined {len(combined)} rows into {out_path}")

if __name__ == "__main__":
    transform_all_dhs()
