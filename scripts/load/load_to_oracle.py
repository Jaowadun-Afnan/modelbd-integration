
import os
import sys
import time
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

import oracledb

# ============================================================
# CONFIGURATION
# ============================================================

# Oracle connection parameters (update these!)
ORACLE_CONFIG = {
    "user": "your_username",          # e.g., "MODELBD_USER"
    "password": "your_password",      # e.g., "MODELBD_PASS"
    "dsn": "localhost:1521/XE",       # or "your_university_server:1521/SID"
}

# Paths
CLEAN_DIR = Path("../../staging/clean")
LOG_DIR = Path("../../logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Batch size for inserts (adjust for performance)
BATCH_SIZE = 1000

# ============================================================
# TABLE LOAD ORDER (Dependency order: parents first)
# ============================================================

# All 43 tables in the exact order they must be loaded
# (Matches Phase 2 DDL dependency order)
LOAD_ORDER = [
    # Batch 1: Parents (no FKs)
    "Country",
    "Indicator_Definition",
    "Admin_Boundary",
    "Industry_Sector",
    "DHS_Survey",
    "DHS_Region",
    "Vaccine_Metadata",
    "Macroeconomic_Indicator",

    # Batch 2: Children (depend on Batch 1)
    "Country_Indicator_Observation",
    "Science_Technology_Metric",
    "Agricultural_Land_Use",
    "Labor_Force_Participation",
    "Child_Employment_Education",
    "Sectoral_Employment",
    "Working_Age_Population",
    "National_Health_Stat",
    "Youth_Mortality_Observation",
    "Immunization_Coverage_Estimate",
    "Survey_Coverage_Detail",
    "DHS_Subnational_Observation",
    "DHS_Thematic_Fact",
    "Child_Health_Diarrhea_Fact",
    "Population_Demographic",
    "Labor_Force_Overview",
    "Sectoral_GDP",
    "Quarterly_GDP",
    "Price_Index",
    "Exchange_Rate",
    "Monetary_Aggregate",
    "Interest_Rate",
    "Government_Finance",
    "CGE_Simulation_Metric",
    "External_Trade_Annual",
    "Trade_Detail",
    "Country_Trade",
    "Balance_of_Payments",
    "External_Debt_Indicator",
    "Production_Energy",
    "MPI_Measurement",
    "Economic_Unit_Aggregate",
    "Person_Engaged_Aggregate",
    "Business_Ecommerce_Fact",
    "Country_GRB_Practice",
]

# ============================================================
# SETUP LOGGING
# ============================================================

log_file = LOG_DIR / f"load_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return an Oracle connection."""
    try:
        conn = oracledb.connect(
            user=ORACLE_CONFIG["user"],
            password=ORACLE_CONFIG["password"],
            dsn=ORACLE_CONFIG["dsn"]
        )
        logger.info(f"✅ Connected to Oracle at {ORACLE_CONFIG['dsn']}")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to Oracle: {e}")
        sys.exit(1)

# ============================================================
# HELPER: Convert CSV value to Python/DB type
# ============================================================

def infer_type(val: str):
    """Convert string from CSV to appropriate Python type (int, float, datetime, or None)."""
    if not val or val.strip() == '':
        return None
    val = val.strip()
    # Try int
    try:
        return int(val)
    except ValueError:
        pass
    # Try float
    try:
        return float(val)
    except ValueError:
        pass
    # Try datetime (ISO format)
    if len(val) >= 19 and val[4] == '-' and val[7] == '-' and val[10] == ' ' and val[13] == ':':
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00'))
        except ValueError:
            pass
    # Default: string
    return val

# ============================================================
# CORE LOAD FUNCTION
# ============================================================

def load_table(conn, table_name: str, csv_path: Path) -> int:
    """
    Loads a single CSV file into the specified Oracle table.
    Returns the number of rows inserted.
    """
    if not csv_path.exists():
        logger.warning(f"⚠️ CSV not found: {csv_path}. Skipping {table_name}.")
        return 0

    logger.info(f"📥 Loading {table_name} from {csv_path.name}...")

    # Read CSV with pandas to handle large files efficiently
    try:
        import pandas as pd
        df = pd.read_csv(csv_path, low_memory=False, dtype=str)  # Read all as string first
    except Exception as e:
        logger.error(f"❌ Failed to read {csv_path}: {e}")
        return 0

    if df.empty:
        logger.warning(f"⚠️ {table_name} CSV is empty. Skipping.")
        return 0

    # Convert NaN to None
    df = df.where(pd.notnull(df), None)

    # Get column names and prepare insert statement
    columns = df.columns.tolist()
    placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
    columns_str = ', '.join([f'"{col}"' for col in columns])

    # Build INSERT statement
    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    # Convert DataFrame rows to list of tuples
    rows = [tuple(row) for row in df.to_numpy()]

    # If the table has a primary key, we may want to TRUNCATE before loading.
    # For safety, we warn the user.
    logger.info(f"   → Inserting {len(rows)} rows into {table_name}...")

    inserted = 0
    cursor = conn.cursor()

    try:
        # Batch insert
        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i:i+BATCH_SIZE]
            # Convert values to proper types
            typed_batch = []
            for row in batch:
                typed_row = tuple(infer_type(str(v)) if v is not None else None for v in row)
                typed_batch.append(typed_row)

            cursor.executemany(insert_sql, typed_batch)
            inserted += len(batch)
            logger.info(f"   → Inserted batch {i//BATCH_SIZE + 1} ({len(batch)} rows)")

        conn.commit()
        logger.info(f"✅ Loaded {inserted} rows into {table_name}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Failed to load {table_name}: {e}")
        # Print the first few rows that failed for debugging
        if len(rows) > 0:
            logger.error(f"   First row (sample): {rows[0]}")
        raise
    finally:
        cursor.close()

    return inserted

# ============================================================
# MASTER LOAD ORCHESTRATOR
# ============================================================

def truncate_table(conn, table_name: str):
    """Truncate the table before loading (optional, careful!)."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        conn.commit()
        cursor.close()
        logger.info(f"   → Truncated {table_name}")
    except Exception as e:
        logger.warning(f"   → Could not truncate {table_name}: {e}")

def load_all():
    """Iterate over LOAD_ORDER and load each table."""
    logger.info("🚀 STARTING PHASE 5: Oracle Load")
    start_time = time.time()

    conn = get_connection()
    total_rows = 0

    for table_name in LOAD_ORDER:
        csv_path = CLEAN_DIR / f"{table_name}.csv"

        # Optionally truncate before load (comment out if you want to append)
        # truncate_table(conn, table_name)

        rows_inserted = load_table(conn, table_name, csv_path)
        total_rows += rows_inserted

    elapsed = time.time() - start_time
    logger.info(f"✅ PHASE 5 COMPLETED in {elapsed:.2f} seconds.")
    logger.info(f"📊 Total rows inserted across all tables: {total_rows}")
    conn.close()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("MODELBD - Phase 5 Load to Oracle")
    logger.info(f"Clean CSV directory: {CLEAN_DIR.absolute()}")
    logger.info(f"Log file: {log_file.absolute()}")
    logger.info("="*60)

    # Validate that clean CSVs exist
    if not CLEAN_DIR.exists():
        logger.error(f"❌ Clean directory not found: {CLEAN_DIR}. Run Phase 4 first.")
        sys.exit(1)

    load_all()
