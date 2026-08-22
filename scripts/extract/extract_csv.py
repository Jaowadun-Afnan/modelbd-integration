import os
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any

# ============================================================
# CONFIGURATION
# ============================================================
RAW_DIR = Path("../raw_data/original")
OUTPUT_DIR = Path("../raw_data/extracted/csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# COMPLETE MASTER FILE LIST 
# (Covers ALL 43 Entities from the Conceptual Model)
# ============================================================
FILE_CONFIG: Dict[str, Dict[str, Any]] = {

    # =========================================================
    # 1. WDI & WORLD BANK (Cluster A & B)
    # =========================================================
    "API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv": {
        "type": "wdi",
        "encoding": "utf-8",
        "melt_id_vars": ["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
        "value_name": "value",
        "var_name": "year"
    },
    "Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv": {"type": "standard", "encoding": "utf-8"},
    "Metadata_Indicator_API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv": {"type": "standard", "encoding": "utf-8"},

    # =========================================================
    # 2. SCIENCE, TECH & AGRICULTURE (Cluster C)
    # =========================================================
    "science-and-technology_bgd (6).csv": {"type": "standard", "encoding": "latin1"},
    "indicators_bgd (1).csv": {"type": "standard", "encoding": "latin1"},

    # =========================================================
    # 3. SOCIAL DEVELOPMENT & LABOR (Cluster D)
    # =========================================================
    "social-development_bgd (1).csv": {"type": "standard", "encoding": "latin1"},
    "POP_XWAP_SEX_AGE_NB_A-filtered-2026-05-14.csv": {"type": "standard", "encoding": "utf-8"},

    # =========================================================
    # 4. NATIONAL HEALTH (Cluster E)
    # =========================================================
    "youth-mortality-rate.csv": {"type": "standard", "encoding": "utf-8"},
    "life-expectancy-men-women.csv": {"type": "standard", "encoding": "utf-8"},
    "maternal-mortality.csv": {"type": "standard", "encoding": "utf-8"},

    # =========================================================
    # 5. ALL DHS SUBNATIONAL OBSERVATIONS (Cluster F - 32 files)
    # =========================================================
    "select-family-planning-indicators_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "select-nutrition-indicators_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "diarrhea_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "health-insurance_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "orphans_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "select-child-mortality-indicators_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "select-education-indicators_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "select-gender-indicators_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "social-marketing_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "toilet-facilities_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "fertility-rates_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "sexual-intercourse_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "hiv-attitudes_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "hiv-behavior_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "hiv-knowledge_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "immunization_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "literacy_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "mens-fertility-and-family-planning_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "tobacco_subnational_bgd.csv": {"type": "standard", "encoding": "utf-8"},
    "dhs-quickstats_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "dhs-mobile_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "sdgs_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "mdgs_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "rbm_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "iycf_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "mics-indicators_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "access-to-health-care_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "anemia_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "birth-registration_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},
    "child-mortality-rates_subnational_bgd (1).csv": {"type": "standard", "encoding": "utf-8"},

    # =========================================================
    # 6. MACROECONOMICS & TRADE (Cluster G)
    # =========================================================
    "Nominal and Real GDP 2007-16 (csv).csv": {"type": "standard", "encoding": "utf-8"},
    "bgd_mpi_trends.csv": {"type": "standard", "encoding": "utf-8"},

    # =========================================================
    # 7. ALL EXCEL FILES (Cluster G, H, I)
    # =========================================================
    "ban-key-indicators-2023.xlsx": {"type": "excel", "sheet_name": None},
    "ban-key-indicators-2024 (1).xlsx": {"type": "excel", "sheet_name": None},
    "nag_bgd (2).xlsx": {"type": "excel", "sheet_name": None},
    "exr_bgd (1).xlsx": {"type": "excel", "sheet_name": None},
    "cpi_bgd (1).xlsx": {"type": "excel", "sheet_name": None},
    "bgd_adminboundaries_tabulardata (1).xlsx": {"type": "excel", "sheet_name": None},
    
    # =========================================================
    # 8. EXTRA SAFETY: Quarterly GDP (if it exists as a standalone file)
    #    Mentioned in Cluster G, Table 26 of the conceptual model.
    # =========================================================
    "Quarterly GDP.xlsx": {"type": "excel", "sheet_name": None},  # <-- ADDED for safety
}

# ============================================================
# (THE REST OF THE CODE BELOW IS IDENTICAL TO THE PREVIOUS VERSION)
# I AM INCLUDING IT HERE SO WE HAVE ONE COMPLETE FILE TO COPY.
# ============================================================

def try_read_csv(file_path: Path, encodings: list = None) -> pd.DataFrame:
    if encodings is None:
        encodings = ['utf-8', 'latin1', 'windows-1252', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Could not decode {file_path}")

def parse_wdi(file_path: Path, config: Dict) -> None:
    df = try_read_csv(file_path)
    header_row = 0
    for i, row in df.iterrows():
        if isinstance(row.iloc[0], str) and 'Country Name' in row.iloc[0]:
            header_row = i
            break
    if header_row > 0:
        df = pd.read_csv(file_path, skiprows=header_row, encoding='utf-8', low_memory=False)
    else:
        df = try_read_csv(file_path)
    
    id_vars = config.get('melt_id_vars', ["Country Name", "Country Code", "Indicator Name", "Indicator Code"])
    year_cols = []
    for col in df.columns:
        if isinstance(col, str) and col.isdigit() and len(col) == 4:
            year_cols.append(col)
        elif isinstance(col, int) and 1960 <= col <= 2030:
            year_cols.append(str(col))
    
    keep_cols = id_vars + year_cols
    df = df[keep_cols]
    df_melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='year', value_name='value')
    df_melted = df_melted.dropna(subset=['value'])
    df_melted['year'] = df_melted['year'].astype(int)
    
    out_name = file_path.stem + "_melted.csv"
    out_path = OUTPUT_DIR / out_name
    df_melted.to_csv(out_path, index=False, encoding='utf-8')
    print(f"✅ WDI parsed (unpivoted): {out_path} ({df_melted.shape[0]} rows)")

def parse_excel(file_path: Path, config: Dict) -> None:
    sheets = config.get('sheet_name', None)
    xl = pd.ExcelFile(file_path)
    for sheet in xl.sheet_names:
        if sheets is not None and sheet not in sheets:
            continue
        try:
            df = pd.read_excel(file_path, sheet_name=sheet, header=0)
            safe_sheet = re.sub(r'[^a-zA-Z0-9_]', '_', sheet)
            out_name = f"{file_path.stem}_{safe_sheet}.csv"
            out_path = OUTPUT_DIR / out_name
            df.to_csv(out_path, index=False, encoding='utf-8')
            print(f"✅ Excel sheet parsed: {out_path} ({df.shape[0]} rows)")
        except Exception as e:
            print(f"❌ Failed to parse sheet '{sheet}' in {file_path.name}: {e}")

def parse_standard(file_path: Path, config: Dict) -> None:
    df = try_read_csv(file_path)
    out_name = file_path.name
    out_path = OUTPUT_DIR / out_name
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"✅ CSV parsed: {out_path} ({df.shape[0]} rows, {df.shape[1]} cols)")

def parse_all_csv():
    for file_name, config in FILE_CONFIG.items():
        file_path = RAW_DIR / file_name
        if not file_path.exists():
            print(f"⚠️ Skipping {file_name} — file not found in {RAW_DIR}")
            continue
        file_type = config.get('type', 'standard')
        try:
            if file_type == 'wdi':
                parse_wdi(file_path, config)
            elif file_type == 'excel':
                parse_excel(file_path, config)
            else:
                parse_standard(file_path, config)
        except Exception as e:
            print(f"❌ FATAL ERROR parsing {file_name}: {e}")

if __name__ == "__main__":
    print("🚀 Starting CSV/Excel extraction...")
    parse_all_csv()
    print("✅ CSV/Excel extraction completed.")
