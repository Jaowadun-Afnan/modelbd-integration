
import sys
from pathlib import Path
import oracledb

# (Same connection config as above)
ORACLE_CONFIG = {
    "user": "your_username",
    "password": "your_password",
    "dsn": "localhost:1521/XE",
}

def verify():
    conn = oracledb.connect(**ORACLE_CONFIG)
    cursor = conn.cursor()

    print("\n=== ROW COUNTS BY TABLE ===")
    tables = [
        "Country", "Indicator_Definition", "Admin_Boundary", "Industry_Sector",
        "DHS_Survey", "DHS_Region", "Vaccine_Metadata", "Macroeconomic_Indicator",
        "Country_Indicator_Observation", "Macroeconomic_Indicator",
        "DHS_Subnational_Observation", "Population_Demographic"
    ]

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:35} → {count:,} rows")
        except Exception as e:
            print(f"  {table:35} → ERROR: {e}")

    print("\n=== FOREIGN KEY INTEGRITY CHECKS ===")
    # Check for orphaned records in Country_Indicator_Observation
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Country_Indicator_Observation c
            WHERE NOT EXISTS (SELECT 1 FROM Country p WHERE p.country_code = c.country_code)
        """)
        orphans = cursor.fetchone()[0]
        print(f"  Orphaned Country_Indicator_Observation (missing Country): {orphans}")
    except Exception as e:
        print(f"  FK check failed: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    verify()
