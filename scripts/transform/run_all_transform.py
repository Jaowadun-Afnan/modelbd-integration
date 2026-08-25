import sys
import time
from datetime import datetime
from pathlib import Path

# Add this script's directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def main():
    log("🚀 STARTING PHASE 4: TRANSFORMATION PIPELINE")
    start = time.time()

    # 1. WDI (Country, Indicator, Observations)
    log("📊 Transforming WDI...")
    from transform_wdi import transform_metadata_country, transform_metadata_indicator, transform_wdi_observations
    transform_metadata_country()
    transform_metadata_indicator()
    transform_wdi_observations()

    # 2. Macroeconomic
    log("🏦 Transforming Macroeconomic...")
    from transform_macro import transform_all_macro
    transform_all_macro()

    # 3. DHS Subnational
    log("📋 Transforming DHS Subnational...")
    from transform_dhs import transform_all_dhs
    transform_all_dhs()

    # 4. Economic Census
    log("🏭 Transforming Economic Census...")
    from transform_census import transform_all_census
    transform_all_census()

    # 5. Agriculture & Labor
    log("🌾 Transforming Agriculture & Labor...")
    from transform_agri_labor import transform_all_agri_labor
    transform_all_agri_labor()

    elapsed = time.time() - start
    log(f"✅ PHASE 4 COMPLETED in {elapsed:.2f} seconds.")
    log(f"📁 Clean files are in: {Path(__file__).resolve().parent.parent / 'staging' / 'clean'}")

if __name__ == "__main__":
    main()
