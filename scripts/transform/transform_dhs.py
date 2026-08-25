import pandas as pd
from pathlib import Path
from mapping_dicts import map_admin_to_pcode, map_gender

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "raw_data" / "extracted" / "csv"
STAGING_DIR = BASE_DIR / "staging" / "clean"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def transform_all_dhs():
    print("   → Consolidating DHS Subnational files...")
    # Find all CSV files that contain 'subnational_bgd' in the name
    dhs_files = list(RAW_DIR.glob("*subnational_bgd*.csv"))
    if not dhs_files:
        print("      ⚠️ No DHS subnational files found.")
        return
    all_dfs = []
    for file in dhs_files:
        print(f"      Processing {file.name}...")
        df = pd.read_csv(file, low_memory=False)
        # Common rename map
        rename_map = {
            'ISO3': 'country_code',
            'SurveyYear': 'survey_year',
            'SurveyYearLabel': 'survey_year_label',
            'SurveyId': 'survey_id',
            'SurveyType': 'survey_type',
            'IndicatorId': 'indicator_id',
            'Indicator': 'indicator_name',
            'IndicatorType': 'indicator_type',
            'IndicatorOrder': 'indicator_order',
            'CharacteristicId': 'characteristic_id',
            'CharacteristicCategory': 'characteristic_category',
            'CharacteristicLabel': 'characteristic_label',
            'CharacteristicOrder': 'characteristic_order',
            'ByVariableId': 'by_variable_id',
            'ByVariableLabel': 'by_variable_label',
            'DataId': 'data_id',
            'Location': 'location',
            'RegionId': 'region_id',
            'Value': 'value',
            'Precision': 'precision',
            'DenominatorWeighted': 'denominator_weighted',
            'DenominatorUnweighted': 'denominator_unweighted',
            'CILow': 'ci_low',
            'CIHigh': 'ci_high',
            'IsTotal': 'is_total',
            'IsPreferred': 'is_preferred',
            'SDRID': 'sdr_id',
            'LevelRank': 'level_rank'
        }
        df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns}, inplace=True)
        # If no country_code, try to map from CountryName
        if 'country_code' not in df.columns and 'CountryName' in df.columns:
            df['country_code'] = df['CountryName'].apply(lambda x: 'BGD')  # default to BGD, but you can use map_country_to_code if needed
        # Add domain based on file name
        df['observation_domain'] = file.stem.replace('_subnational_bgd', '').replace('_', ' ').title()
        # Standardise gender if a 'Sex' or 'Gender' column exists
        if 'Sex' in df.columns:
            df['gender'] = df['Sex'].apply(map_gender)
        elif 'Gender' in df.columns:
            df['gender'] = df['Gender'].apply(map_gender)
        else:
            df['gender'] = 'Total'
        # Standardise admin location if 'Location' or 'RegionName' exists
        if 'Location' in df.columns:
            df['admin_pcode'] = df['Location'].apply(map_admin_to_pcode)
        elif 'RegionName' in df.columns:
            df['admin_pcode'] = df['RegionName'].apply(map_admin_to_pcode)
        else:
            df['admin_pcode'] = 'UNMAPPED'
        # Drop rows missing the composite key (if key columns exist)
        key_cols = ['survey_id', 'indicator_id', 'characteristic_id', 'by_variable_id']
        existing_keys = [c for c in key_cols if c in df.columns]
        if existing_keys:
            df.dropna(subset=existing_keys, inplace=True)
        # Clean booleans
        for col in ['is_total', 'is_preferred']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: 'Y' if x in [1, '1', True, 'Y', 'y'] else 'N')
        all_dfs.append(df)
    if not all_dfs:
        print("      ❌ No data loaded.")
        return
    combined = pd.concat(all_dfs, ignore_index=True, sort=False)
    # Deduplicate on available key columns
    if existing_keys:
        combined.drop_duplicates(subset=existing_keys, inplace=True)
    else:
        combined.drop_duplicates(inplace=True)
    out_path = STAGING_DIR / "DHS_Subnational_Observation.csv"
    combined.to_csv(out_path, index=False, encoding='utf-8')
    print(f"      ✅ Combined {len(combined)} rows into {out_path}")

if __name__ == "__main__":
    transform_all_dhs()
