import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

if __name__ == "__main__":
    log("🚀 STARTING PHASE 4: TRANSFORMATION PIPELINE")
    start = time.time()

    # 1. Reference / Dimension tables (no dependencies)
    log("📦 Transforming Reference Entities (Country, Indicator, Admin, Sector)...")
    # (We will add these imports as we write them)
    # from transform_wdi import transform_metadata_country, transform_metadata_indicator
    # transform_metadata_country()
    # transform_metadata_indicator()

    # 2. WDI Observations
    log("📊 Transforming WDI Country_Indicator_Observation...")
    from transform_wdi import transform_wdi_observations
    transform_wdi_observations()

    # 3. Agriculture, Science, Labor
    log("🌾 Transforming Agriculture, Science, Labor...")
    from transform_agri_labor import transform_all_agri_labor
    transform_all_agri_labor()

    # 4. Macroeconomic (GDP, Inflation, Trade, etc.)
    log("🏦 Transforming Macroeconomic Indicators...")
    from transform_macro import transform_all_macro
    transform_all_macro()

    # 5. DHS Subnational (Largest cluster)
    log("📋 Transforming DHS Subnational Observations...")
    from transform_dhs import transform_all_dhs
    transform_all_dhs()

    # 6. Economic Census
    log("🏭 Transforming Economic Census Data...")
    from transform_census import transform_all_census
    transform_all_census()

    elapsed = time.time() - start
    log(f"✅ PHASE 4 COMPLETED in {elapsed:.2f} seconds.")
    log(f"📁 Clean files are in: ../staging/clean/")
