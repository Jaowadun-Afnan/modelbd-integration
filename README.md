# MODELBD Integration — Bangladesh Socioeconomic Database

> **Team:** Cardinality Crew  
**Course:** Database Systems Lab (CSE, Chittagong University) 
> **Supervisor:** Prof. Dr. Rudra Pratap Deb Nath  

## 📖 Project Overview
This repository contains the ETL pipeline, DDL schemas, and integration logic for the unified Bangladesh Socioeconomic Database.


## 👥 Team Members
- [Adnan Abir Rangan]   - [24701052] - [leader]
- [Sanjida Ferdous Sara]- [23701044] 
- [Jaowadun Afnan Tean] - [24701045]
- [Samia Jahan Nourin]  - [24701053]

 ### 🔑 Key Highlights
- **43 Unified Entities** consolidated from 130+ raw tables.
- **Zero Data Loss** consolidation strategy.
- **Time-series integrity** preserved (`year` embedded in every PK).
- **Handles messy PDF tables** (Camelot/Tabula fallback).
- **Resolves approximate key mismatches** (`country_name` → `ISO3`, `sector` → `sector_code`).


## 📁 Repository Structure
├── raw_data/

│ ├── original/ (original CSVs/PDFs here)

│ ├── extracted/ (unprocessed CSV extracts)

│ ├── csv/

│ └── pdf_tables/

├── staging/

│ └── clean/  (cleaned, transformed CSVs)

├── scripts/

│ ├── extract/ # Parsers for CSV/Excel/PDF

│ │ ├── extract_csv.py

│ │ ├── extract_pdf.py

│ │ └── run_all_extract.py

│ ├── transform/ # Cleaning & mapping logic

│ │ ├── mapping_dicts.py

│ │ ├── transform_wdi.py

│ │ ├── transform_macro.py

│ │ ├── transform_dhs.py

│ │ ├── transform_agri_labor.py

│ │ ├── transform_census.py

│ │ └── run_all_transform.py

│ └── load/ # Oracle database loader

│ ├── load_to_oracle.py

│ └── verify_load.py

├── ddl/ # Database schema

│ └── 01_create_all_tables.sql

├── logs/ # Runtime logs for debugging

└── README.md 

