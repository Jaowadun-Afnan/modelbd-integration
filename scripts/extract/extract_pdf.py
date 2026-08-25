import pandas as pd
from pathlib import Path
import re

RAW_DIR = Path("../../raw_data/original")
OUTPUT_DIR = Path("../../raw_data/extracted/pdf_tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ALL 9 PDFs (NOW INCLUDES 3ab00376...)
PDF_FILES = [
    "garments_growth (1).pdf",
    "3ab00376bfa049a9a1674fb786126915.pdf",  # <-- MISSING PDF ADDED
    "bgd.pdf",
    "gender_responsive_budget (1).pdf",
    "bangladesh-gender-equality-diagnostic.pdf",
    "GDPandPCIofBD(1).pdf",
    "d76506a501674dc294cc730a7bbee52f (1).pdf",
    "023fa68d-5117-474e-b9bd-8585e3737244 (1).pdf",
    "c7582226-d542-4ef3-acca-98d6e9ec0b00 (1).pdf",
]

def parse_pdf(file_path: Path):
    print(f"📄 Parsing PDF: {file_path.name}")
    tables = []
    try:
        import camelot
        try:
            tables = camelot.read_pdf(str(file_path), pages='all', flavor='lattice')
            if len(tables) == 0:
                tables = camelot.read_pdf(str(file_path), pages='all', flavor='stream')
        except Exception as e:
            print(f"   ⚠️ Camelot failed: {e}. Trying tabula...")
            tables = []
    except ImportError:
        print("   ⚠️ Camelot not installed. Trying tabula-py...")
        tables = []
    
    if len(tables) == 0:
        try:
            import tabula
            dfs = tabula.read_pdf(str(file_path), pages='all', multiple_tables=True)
            if dfs:
                for i, df in enumerate(dfs):
                    if df is not None and not df.empty:
                        out_name = f"{file_path.stem}_tabula_{i+1}.csv"
                        out_path = OUTPUT_DIR / out_name
                        df.to_csv(out_path, index=False, encoding='utf-8')
                        print(f"   ✅ Tabula table {i+1}: {out_path} ({df.shape[0]} rows)")
            else:
                print(f"   ❌ No tables found in {file_path.name}")
        except ImportError:
            print(f"   ❌ Tabula-py not installed. Install: pip install tabula-py")
        except Exception as e:
            print(f"   ❌ Tabula error: {e}")
        return
    
    for i, table in enumerate(tables):
        df = table.df
        out_name = f"{file_path.stem}_table_{i+1}.csv"
        out_path = OUTPUT_DIR / out_name
        df.to_csv(out_path, index=False, encoding='utf-8')
        print(f"   ✅ Camelot table {i+1}: {out_path} ({df.shape[0]} rows)")

def parse_all_pdf():
    for file_name in PDF_FILES:
        file_path = RAW_DIR / file_name
        if not file_path.exists():
            print(f"⚠️ Skipping {file_name} — file not found in {RAW_DIR}")
            continue
        try:
            parse_pdf(file_path)
        except Exception as e:
            print(f"❌ FATAL ERROR parsing {file_name}: {e}")

if __name__ == "__main__":
    print("🚀 Starting PDF extraction...")
    parse_all_pdf()
    print("✅ PDF extraction completed.")
