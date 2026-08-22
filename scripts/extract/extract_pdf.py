import os
import camelot
import pandas as pd
from pathlib import Path

RAW_DIR = Path("../raw_data/original")
OUTPUT_DIR = Path("../raw_data/extracted/pdf_tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pdf_files = [
    "garments_growth (1).pdf",
    "bgd.pdf",
    "gender_responsive_budget (1).pdf",
    "bangladesh-gender-equality-diagnostic.pdf",
    "d76506a501674dc294cc730a7bbee52f (1).pdf",
    "GDPandPCIofBD (1).pdf",
    # ... add all PDFs from your sources
]

def extract_pdf_tables(file_name):
    file_path = RAW_DIR / file_name
    if not file_path.exists():
        print(f"❌ PDF not found: {file_path}")
        return
    
    try:
        # Use Lattice for bordered tables, Stream for borderless
        tables = camelot.read_pdf(str(file_path), pages='all', flavor='lattice')
        if len(tables) == 0:
            # Fallback to stream mode
            tables = camelot.read_pdf(str(file_path), pages='all', flavor='stream')
        
        # Save each table found
        base_name = file_name.replace('.pdf', '')
        for i, table in enumerate(tables):
            df = table.df  # This is a pandas DataFrame
            out_path = OUTPUT_DIR / f"{base_name}_table_{i+1}.csv"
            df.to_csv(out_path, index=False, encoding='utf-8')
            print(f"✅ PDF table extracted: {out_path} ({df.shape[0]} rows)")
    except Exception as e:
        print(f"❌ Failed to parse {file_name}: {e}")
        # Fallback to tabula-py if camelot fails
        try:
            import tabula
            dfs = tabula.read_pdf(str(file_path), pages='all', multiple_tables=True)
            for i, df in enumerate(dfs):
                out_path = OUTPUT_DIR / f"{base_name}_tabula_{i+1}.csv"
                df.to_csv(out_path, index=False, encoding='utf-8')
                print(f"✅ Tabula fallback: {out_path}")
        except Exception as e2:
            print(f"❌ Tabula also failed: {e2}")

if __name__ == "__main__":
    for f in pdf_files:
        extract_pdf_tables(f)
