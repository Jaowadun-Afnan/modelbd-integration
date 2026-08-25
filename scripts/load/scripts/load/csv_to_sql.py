import pandas as pd
from pathlib import Path

# Paths
clean_dir = Path("../../staging/clean")
output_dir = Path("../../staging/sql_scripts")
output_dir.mkdir(parents=True, exist_ok=True)

# Load order (parents first, children later)
load_order = [
    "Country",
    "Indicator_Definition",
    "Admin_Boundary",
    "Industry_Sector",
    "DHS_Survey",
    "DHS_Region",
    "Vaccine_Metadata",
    "Macroeconomic_Indicator",
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
    "Country_GRB_Practice"
]

# Create a combined SQL file
combined_sql = output_dir / "all_tables_load.sql"

with open(combined_sql, 'w') as combined:
    combined.write("-- ============================================================\n")
    combined.write("-- PHASE 5: DATA LOAD SCRIPT FOR ORACLE LIVE SQL\n")
    combined.write("-- Generated from clean CSVs\n")
    combined.write("-- Run this script in Oracle Live SQL SQL Worksheet\n")
    combined.write("-- ============================================================\n\n")
    
    total_rows_loaded = 0
    
    for table_name in load_order:
        csv_file = clean_dir / f"{table_name}.csv"
        if not csv_file.exists():
            print(f"⚠️ Skipping {table_name} (file not found at {csv_file})")
            continue
        
        print(f"✅ Processing {table_name}")
        
        df = pd.read_csv(csv_file)
        if df.empty:
            print(f"   ⚠️ {table_name} is empty, skipping")
            continue
        
        # Get columns
        columns = df.columns.tolist()
        columns_str = ', '.join(columns)
        
        combined.write(f"\n-- ============================================================\n")
        combined.write(f"-- Table: {table_name} ({len(df)} rows)\n")
        combined.write(f"-- ============================================================\n\n")
        combined.write(f"INSERT ALL\n")
        
        for _, row in df.iterrows():
            values = []
            for val in row:
                if pd.isna(val):
                    values.append("NULL")
                elif isinstance(val, str):
                    # Escape single quotes
                    val_escaped = val.replace("'", "''")
                    values.append(f"'{val_escaped}'")
                elif isinstance(val, (int, float)):
                    if val == '' or pd.isna(val):
                        values.append("NULL")
                    else:
                        values.append(str(val))
                else:
                    values.append(f"'{str(val)}'")
            
            combined.write(f"    INTO {table_name} ({columns_str}) VALUES ({', '.join(values)})\n")
        
        combined.write("SELECT 1 FROM DUAL;\n")
        combined.write("/\n")
        combined.write(f"\n-- ✅ {table_name} loaded successfully ({len(df)} rows)\n\n")
        total_rows_loaded += len(df)

print("\n" + "="*60)
print("✅ SQL generation complete!")
print(f"📁 Combined SQL file: {combined_sql}")
print(f"📊 Total rows across all tables: {total_rows_loaded}")
print("="*60)
