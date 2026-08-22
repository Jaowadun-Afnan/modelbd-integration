import os
import pandas as pd
from pathlib import Path

# Configuration
RAW_DIR = Path("../raw_data/original")
OUTPUT_DIR = Path("../raw_data/extracted/csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# List of all CSV files from your 40+ sources
csv_files = [
    "API_SP.POP.TOTL_DS2_en_csv_v2_282912.csv",
    "science-and-technology_bgd (6).csv",
    "social-development_bgd (1).csv",
    "indicators_bgd (1).csv",
    "youth-mortality-rate.csv",
    "ban-key-indicators-2023.xlsx",  # Actually Excel, handled separately
    "select-family-planning-indicators_subnational_bgd.csv",
    "select-nutrition-indicators_subnational_bgd.csv",
    # ... add all others from your document list
]

def extract_csv(file_name):
    """Reads a CSV, saves a clean copy with inferred types."""
    file_path = RAW_DIR / file_name
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
    
    # Save to extracted folder with the same name
    output_path = OUTPUT_DIR / file_name
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"✅ Extracted: {file_name} → {df.shape[0]} rows, {df.shape[1]} cols")

if __name__ == "__main__":
    for f in csv_files:
        extract_csv(f)
