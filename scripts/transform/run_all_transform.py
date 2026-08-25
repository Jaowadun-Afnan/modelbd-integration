import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def main():
    log("🚀 STARTING PHASE 4: TRANSFORMATION PIPELINE")
    start = time.time()

    log("📊 Transforming WDI...")
    from transform_wdi import transform_metadata_country, transform_metadata_indicator, transform_wdi_observations
    transform_metadata_country()
    transform_metadata_indicator()
    transform_wdi_observations()

    log("🏦 Transforming Macroeconomic...")
    from transform_macro import transform_all_macro
    transform_all_macro()

    log("📋 Transforming DHS Subnational...")
    from transform_dhs import transform_all_dhs
    transform_all_dhs()

    log("🏭 Transforming Economic Census...")
    from transform_census import transform_all_census
    transform_all_census()

    log("🌾 Transforming Agriculture & Labor...")
    from transform_agri_labor import transform_all_agri_labor
    transform_all_agri_labor()

    elapsed = time.time() - start
    log(f"✅ PHASE 4 COMPLETED in {elapsed:.2f} seconds.")
    log(f"📁 Clean files are in: {Path(__file__).resolve().parent.parent.parent / 'staging' / 'clean'}")

if __name__ == "__main__":
    main()