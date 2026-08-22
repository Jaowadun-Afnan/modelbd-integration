#!/usr/bin/env python3
"""
run_all_extract.py
Master orchestrator for Phase 3 Extraction.
Runs CSV/Excel parser first, then PDF parser.
Logs start/end time and any errors.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path so we can import other scripts
sys.path.insert(0, str(Path(__file__).parent))

# Import the parsing functions
from extract_csv import parse_all_csv
from extract_pdf import parse_all_pdf

def log(msg: str):
    """Print with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def main():
    log("🚀 STARTING EXTRACTION PIPELINE (Phase 3)")
    start_time = time.time()
    
    # Step 1: CSV / Excel
    log("📂 Running CSV/Excel extraction...")
    try:
        parse_all_csv()
    except Exception as e:
        log(f"❌ CSV extraction crashed: {e}")
        # Continue to PDF anyway
    
    # Step 2: PDF
    log("📄 Running PDF extraction...")
    try:
        parse_all_pdf()
    except Exception as e:
        log(f"❌ PDF extraction crashed: {e}")
    
    # Summary
    elapsed = time.time() - start_time
    log(f"✅ EXTRACTION PIPELINE COMPLETED in {elapsed:.2f} seconds.")
    log(f"   Check output folders: ../raw_data/extracted/csv/ and ../raw_data/extracted/pdf_tables/")

if __name__ == "__main__":
    main()
