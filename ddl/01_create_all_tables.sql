-- ============================================================
-- PHASE 2: PHYSICAL SCHEMA (DDL) FOR MODELBD
-- Oracle Database (XE / 19c+)
-- 
-- Dependency Order: Parents first, then children.
-- Run this script in SQL*Plus, SQL Developer, or DBeaver.
-- 
-- Created: August 2026
-- Team: Cardinality Crew
-- ============================================================

-- ============================================================
-- BATCH 1: REFERENCE / DIMENSION TABLES (No Dependencies)
-- ============================================================

-- 1. Country
CREATE TABLE Country (
    country_code    VARCHAR2(3)   NOT NULL,
    country_name    VARCHAR2(100) NOT NULL,
    region          VARCHAR2(50),
    income_group    VARCHAR2(50),
    special_notes   CLOB,
    CONSTRAINT pk_country PRIMARY KEY (country_code)
);

-- 2. Indicator_Definition
CREATE TABLE Indicator_Definition (
    indicator_code      VARCHAR2(50)  NOT NULL,
    indicator_name      VARCHAR2(255) NOT NULL,
    domain              VARCHAR2(50),
    source_notes        CLOB,
    source_organization VARCHAR2(255),
    CONSTRAINT pk_indicator_def PRIMARY KEY (indicator_code)
);

-- 3. Admin_Boundary (Self-referencing - ADM0 to ADM3)
CREATE TABLE Admin_Boundary (
    entity_pcode  VARCHAR2(20)   NOT NULL,
    admin_level   NUMBER(1)      NOT NULL,
    entity_name   VARCHAR2(100)  NOT NULL,
    parent_pcode  VARCHAR2(20),
    country_iso3  VARCHAR2(3)    NOT NULL,
    area_sqkm     NUMBER(15,2),
    valid_from    TIMESTAMP,
    valid_to      TIMESTAMP,
    record_date   TIMESTAMP,
    CONSTRAINT pk_admin_boundary PRIMARY KEY (entity_pcode),
    CONSTRAINT fk_admin_parent FOREIGN KEY (parent_pcode) REFERENCES Admin_Boundary(entity_pcode),
    CONSTRAINT fk_admin_country FOREIGN KEY (country_iso3) REFERENCES Country(country_code),
    CONSTRAINT chk_admin_level CHECK (admin_level BETWEEN 0 AND 3)
);
CREATE INDEX idx_admin_parent ON Admin_Boundary(parent_pcode);
CREATE INDEX idx_admin_country ON Admin_Boundary(country_iso3);

-- 4. Industry_Sector (Self-referencing) - FIXED: Removed reserved word "level"
CREATE TABLE Industry_Sector (
    sector_code        VARCHAR2(20)   NOT NULL,
    sector_name        VARCHAR2(100)  NOT NULL,
    parent_sector_code VARCHAR2(20),
    isic_division      VARCHAR2(10),
    sector_level       NUMBER(1),      -- <<< CHANGED FROM "level" to "sector_level"
    CONSTRAINT pk_industry_sector PRIMARY KEY (sector_code),
    CONSTRAINT fk_sector_parent FOREIGN KEY (parent_sector_code) REFERENCES Industry_Sector(sector_code),
    CONSTRAINT chk_sector_level CHECK (sector_level BETWEEN 0 AND 3)
);
CREATE INDEX idx_sector_parent ON Industry_Sector(parent_sector_code);

-- 5. DHS_Survey
CREATE TABLE DHS_Survey (
    survey_id          VARCHAR2(50)  NOT NULL,
    survey_year        NUMBER(4)     NOT NULL,
    survey_year_label  VARCHAR2(20),
    survey_type        VARCHAR2(50),
    country_code       VARCHAR2(3)   NOT NULL,
    country_name       VARCHAR2(100),
    iso3               VARCHAR2(3),
    dhs_country_code   VARCHAR2(10),
    CONSTRAINT pk_dhs_survey PRIMARY KEY (survey_id),
    CONSTRAINT fk_dhs_survey_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_dhs_survey_country ON DHS_Survey(country_code);

-- 6. DHS_Region
CREATE TABLE DHS_Region (
    region_id              VARCHAR2(50)  NOT NULL,
    location_name          VARCHAR2(100),
    characteristic_id      NUMBER(10),
    characteristic_order   NUMBER(10),
    characteristic_category VARCHAR2(50),
    characteristic_label   VARCHAR2(100),
    level_rank             NUMBER(10,2),
    is_total               CHAR(1)       DEFAULT 'N' CHECK (is_total IN ('Y', 'N')),
    CONSTRAINT pk_dhs_region PRIMARY KEY (region_id)
);

-- 7. Vaccine_Metadata
CREATE TABLE Vaccine_Metadata (
    vaccine_code      VARCHAR2(20)  NOT NULL,
    vaccine_full_name VARCHAR2(100) NOT NULL,
    target_population VARCHAR2(100),
    schedule_notes    CLOB,
    CONSTRAINT pk_vaccine_metadata PRIMARY KEY (vaccine_code)
);

-- 8. Macroeconomic_Indicator (Parent for many 1:1/1:N macro tables)
CREATE TABLE Macroeconomic_Indicator (
    year                          NUMBER(4)     NOT NULL,
    nominal_growth_rate           NUMBER(10,4),
    real_growth_rate              NUMBER(10,4),
    inflation_rate                NUMBER(10,4),
    gdp_current                   NUMBER(20,2),
    gdp_constant                  NUMBER(20,2),
    gdp_growth                    NUMBER(10,4),
    gni_current                   NUMBER(20,2),
    gni_constant                  NUMBER(20,2),
    per_capita_gdp                NUMBER(15,2),
    per_capita_gni                NUMBER(15,2),
    gross_domestic_saving_pct_gdp NUMBER(10,4),
    gross_national_saving_pct_gdp NUMBER(10,4),
    gross_capital_formation_pct_gdp NUMBER(10,4),
    exports_pct_gdp               NUMBER(10,4),
    imports_pct_gdp               NUMBER(10,4),
    implicit_gdp_deflator         NUMBER(10,4),
    actual_gdp_growth_pct         NUMBER(10,4),
    actual_pci_growth_pct         NUMBER(10,4),
    trend_gdp_growth_pct          NUMBER(10,4),
    trend_pci_growth_pct          NUMBER(10,4),
    CONSTRAINT pk_macroeconomic_indicator PRIMARY KEY (year)
);

-- ============================================================
-- BATCH 2: FACT / OBSERVATION TABLES (Depends on Batch 1)
-- ============================================================

-- 9. Country_Indicator_Observation (WDI)
CREATE TABLE Country_Indicator_Observation (
    country_code   VARCHAR2(3)   NOT NULL,
    indicator_code VARCHAR2(50)  NOT NULL,
    year           NUMBER(4)     NOT NULL,
    value          NUMBER(20,4),
    domain         VARCHAR2(50),
    CONSTRAINT pk_country_indicator_obs PRIMARY KEY (country_code, indicator_code, year),
    CONSTRAINT fk_cio_country FOREIGN KEY (country_code) REFERENCES Country(country_code),
    CONSTRAINT fk_cio_indicator FOREIGN KEY (indicator_code) REFERENCES Indicator_Definition(indicator_code)
);
CREATE INDEX idx_cio_country ON Country_Indicator_Observation(country_code);
CREATE INDEX idx_cio_indicator ON Country_Indicator_Observation(indicator_code);

-- 10. Science_Technology_Metric
CREATE TABLE Science_Technology_Metric (
    country_code  VARCHAR2(3)   NOT NULL,
    year          NUMBER(4)     NOT NULL,
    metric_type   VARCHAR2(30)  NOT NULL,
    sub_category  VARCHAR2(50)  NOT NULL,
    numeric_value NUMBER(20,4),
    value_usd     NUMBER(20,2),
    pct_value     NUMBER(10,4),
    CONSTRAINT pk_science_tech PRIMARY KEY (country_code, year, metric_type, sub_category),
    CONSTRAINT fk_st_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_st_country ON Science_Technology_Metric(country_code);

-- 11. Agricultural_Land_Use
CREATE TABLE Agricultural_Land_Use (
    country_code               VARCHAR2(3)   NOT NULL,
    year                       NUMBER(4)     NOT NULL,
    agri_land_sqkm             NUMBER(15,2),
    agri_land_pct_of_total     NUMBER(10,4),
    arable_area_hectares       NUMBER(15,2),
    arable_hectares_per_person NUMBER(15,4),
    arable_pct_of_land         NUMBER(10,4),
    cereal_area_hectares       NUMBER(15,2),
    fertilizer_pct_of_production NUMBER(10,4),
    fertilizer_kg_per_hectare  NUMBER(15,4),
    CONSTRAINT pk_agri_land_use PRIMARY KEY (country_code, year),
    CONSTRAINT fk_agri_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_agri_country ON Agricultural_Land_Use(country_code);

-- 12. Labor_Force_Participation
CREATE TABLE Labor_Force_Participation (
    country_code                 VARCHAR2(3)   NOT NULL,
    year                         NUMBER(4)     NOT NULL,
    gender                       VARCHAR2(10)  NOT NULL,
    area_type                    VARCHAR2(20)  NOT NULL,
    age_group                    VARCHAR2(20)  NOT NULL,
    characteristic_category      VARCHAR2(50)  NOT NULL,
    characteristic_value         VARCHAR2(50)  NOT NULL,
    labour_force_millions        NUMBER(15,4),
    lfpr_pct                     NUMBER(10,4),
    unemployment_rate_pct        NUMBER(10,4),
    unemployed_millions          NUMBER(15,4),
    employed_millions            NUMBER(15,4),
    good_jobs_pct                NUMBER(10,4),
    vulnerable_employment_pct    NUMBER(10,4),
    seats_pct                    NUMBER(10,4),
    participation_pct            NUMBER(10,4),
    CONSTRAINT pk_labor_force_participation PRIMARY KEY (country_code, year, gender, area_type, age_group, characteristic_category, characteristic_value),
    CONSTRAINT fk_lfp_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_lfp_country ON Labor_Force_Participation(country_code);

-- 13. Child_Employment_Education
CREATE TABLE Child_Employment_Education (
    country_code   VARCHAR2(3)   NOT NULL,
    year           NUMBER(4)     NOT NULL,
    gender         VARCHAR2(10)  NOT NULL,
    age_group      VARCHAR2(20)  NOT NULL,
    category_type  VARCHAR2(30)  NOT NULL,
    category_value VARCHAR2(50)  NOT NULL,
    metric_value   NUMBER(15,4),
    target_2015    NUMBER(15,4),
    goal_target    VARCHAR2(100),
    CONSTRAINT pk_child_emp_edu PRIMARY KEY (country_code, year, gender, age_group, category_type, category_value),
    CONSTRAINT fk_cee_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_cee_country ON Child_Employment_Education(country_code);

-- 14. Sectoral_Employment
CREATE TABLE Sectoral_Employment (
    country_code          VARCHAR2(3)   NOT NULL,
    year                  NUMBER(4)     NOT NULL,
    sector_code           VARCHAR2(20)  NOT NULL,
    gender                VARCHAR2(10)  NOT NULL,
    area_type             VARCHAR2(20)  NOT NULL,
    age_group             VARCHAR2(20)  NOT NULL,
    employment_type       VARCHAR2(30)  NOT NULL,
    employed_millions     NUMBER(15,4),
    employed_count        NUMBER(10),
    distribution_pct      NUMBER(10,4),
    informal_share_pct    NUMBER(10,4),
    employment_status_pct NUMBER(10,4),
    CONSTRAINT pk_sectoral_employment PRIMARY KEY (country_code, year, sector_code, gender, area_type, age_group, employment_type),
    CONSTRAINT fk_se_country FOREIGN KEY (country_code) REFERENCES Country(country_code),
    CONSTRAINT fk_se_sector FOREIGN KEY (sector_code) REFERENCES Industry_Sector(sector_code)
);
CREATE INDEX idx_se_country ON Sectoral_Employment(country_code);
CREATE INDEX idx_se_sector ON Sectoral_Employment(sector_code);

-- 15. Working_Age_Population (ILO data)
CREATE TABLE Working_Age_Population (
    ref_area              VARCHAR2(3)   NOT NULL,
    year                  NUMBER(4)     NOT NULL,
    sex                   VARCHAR2(10)  NOT NULL,
    age_class_type        VARCHAR2(30)  NOT NULL,
    age_band              VARCHAR2(20)  NOT NULL,
    source_label          VARCHAR2(100),
    indicator_label       VARCHAR2(100),
    obs_value_thousands   NUMBER(15,2),
    obs_status_label      VARCHAR2(50),
    note_classif_label    VARCHAR2(255),
    note_indicator_label  VARCHAR2(255),
    note_source_label     VARCHAR2(255),
    CONSTRAINT pk_working_age_pop PRIMARY KEY (ref_area, year, sex, age_class_type, age_band),
    CONSTRAINT fk_wap_country FOREIGN KEY (ref_area) REFERENCES Country(country_code)
);
CREATE INDEX idx_wap_country ON Working_Age_Population(ref_area);

-- 16. National_Health_Stat
CREATE TABLE National_Health_Stat (
    country_code              VARCHAR2(3)   NOT NULL,
    year                      NUMBER(4)     NOT NULL,
    gender                    VARCHAR2(10)  NOT NULL,
    life_expectancy_value     NUMBER(10,4),
    maternal_mortality_ratio  NUMBER(10,2),
    hiv_prevalence_pct        NUMBER(10,4),
    age_group                 VARCHAR2(20),
    CONSTRAINT pk_nat_health PRIMARY KEY (country_code, year, gender),
    CONSTRAINT fk_nhs_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_nhs_country ON National_Health_Stat(country_code);

-- 17. Youth_Mortality_Observation
CREATE TABLE Youth_Mortality_Observation (
    country_code                  VARCHAR2(3)  NOT NULL,
    year                          NUMBER(4)    NOT NULL,
    under_fifteen_mortality_rate  NUMBER(10,4),
    CONSTRAINT pk_youth_mortality PRIMARY KEY (country_code, year),
    CONSTRAINT fk_ym_country FOREIGN KEY (country_code) REFERENCES Country(country_code)
);
CREATE INDEX idx_ym_country ON Youth_Mortality_Observation(country_code);

-- 18. Immunization_Coverage_Estimate
CREATE TABLE Immunization_Coverage_Estimate (
    year               NUMBER(4)     NOT NULL,
    vaccine_code       VARCHAR2(20)  NOT NULL,
    estimate_type      VARCHAR2(30)  NOT NULL,
    coverage_percent   NUMBER(3),
    grade_of_confidence VARCHAR2(20),
    estimation_notes   CLOB,
    CONSTRAINT pk_immunization_estimate PRIMARY KEY (year, vaccine_code, estimate_type),
    CONSTRAINT fk_imm_vaccine FOREIGN KEY (vaccine_code) REFERENCES Vaccine_Metadata(vaccine_code)
);
CREATE INDEX idx_imm_vaccine ON Immunization_Coverage_Estimate(vaccine_code);

-- 19. Survey_Coverage_Detail
CREATE TABLE Survey_Coverage_Detail (
    survey_year          NUMBER(4)     NOT NULL,
    survey_name          VARCHAR2(50)  NOT NULL,
    vaccine_code         VARCHAR2(20)  NOT NULL,
    confirmation_method  VARCHAR2(30)  NOT NULL,
    age_cohort           VARCHAR2(20)  NOT NULL,
    coverage_percent     NUMBER(10,2),
    sample_size          NUMBER(10),
    cards_seen           NUMBER(10),
    reference_birth_year NUMBER(4),
    CONSTRAINT pk_survey_coverage_detail PRIMARY KEY (survey_year, survey_name, vaccine_code, confirmation_method, age_cohort),
    CONSTRAINT fk_scd_vaccine FOREIGN KEY (vaccine_code) REFERENCES Vaccine_Metadata(vaccine_code)
);
CREATE INDEX idx_scd_vaccine ON Survey_Coverage_Detail(vaccine_code);

-- 20. DHS_Subnational_Observation - FIXED: Added region_id column
CREATE TABLE DHS_Subnational_Observation (
    survey_id                VARCHAR2(50)  NOT NULL,
    indicator_id             VARCHAR2(50)  NOT NULL,
    characteristic_id        NUMBER(10)    NOT NULL,
    by_variable_id           NUMBER(10)    NOT NULL,
    data_id                  NUMBER(20),
    survey_year              NUMBER(4),
    country_code             VARCHAR2(3),
    location                 VARCHAR2(100),
    indicator_name           VARCHAR2(255),
    indicator_order          NUMBER(10),
    indicator_type           VARCHAR2(30),
    characteristic_order     NUMBER(10),
    characteristic_category  VARCHAR2(50),
    characteristic_label     VARCHAR2(100),
    by_variable_label        VARCHAR2(100),
    is_total                 CHAR(1)       DEFAULT 'N' CHECK (is_total IN ('Y', 'N')),
    is_preferred             CHAR(1)       DEFAULT 'N' CHECK (is_preferred IN ('Y', 'N')),
    sdr_id                   VARCHAR2(50),
    survey_year_label        VARCHAR2(20),
    survey_type              VARCHAR2(50),
    level_rank               NUMBER(10),
    value                    NUMBER(20,4),
    precision                NUMBER(10),
    denominator_weighted     NUMBER(10),
    denominator_unweighted   NUMBER(10),
    ci_low                   NUMBER(20,4),
    ci_high                  NUMBER(20,4),
    observation_domain       VARCHAR2(50),
    region_id                VARCHAR2(50)  NOT NULL,   -- <<< ADDED region_id column
    CONSTRAINT pk_dhs_subnational_obs PRIMARY KEY (survey_id, indicator_id, characteristic_id, by_variable_id),
    CONSTRAINT fk_dso_survey FOREIGN KEY (survey_id) REFERENCES DHS_Survey(survey_id),
    CONSTRAINT fk_dso_region FOREIGN KEY (region_id) REFERENCES DHS_Region(region_id)
);
CREATE INDEX idx_dso_survey ON DHS_Subnational_Observation(survey_id);
CREATE INDEX idx_dso_region ON DHS_Subnational_Observation(region_id);

-- 21. DHS_Thematic_Fact
CREATE TABLE DHS_Thematic_Fact (
    survey_id            VARCHAR2(50)  NOT NULL,
    region_id            VARCHAR2(50)  NOT NULL,
    characteristic_id    NUMBER(10)    NOT NULL,
    indicator_id         VARCHAR2(50)  NOT NULL,
    value                NUMBER(20,4),
    denominator_weighted NUMBER(10),
    denominator_unweighted NUMBER(10),
    ci_low               NUMBER(20,4),
    ci_high              NUMBER(20,4),
    is_preferred         CHAR(1)       DEFAULT 'N' CHECK (is_preferred IN ('Y', 'N')),
    survey_year          NUMBER(4),
    thematic_domain      VARCHAR2(50),
    CONSTRAINT pk_dhs_thematic PRIMARY KEY (survey_id, region_id, characteristic_id, indicator_id),
    CONSTRAINT fk_dt_survey FOREIGN KEY (survey_id) REFERENCES DHS_Survey(survey_id),
    CONSTRAINT fk_dt_region FOREIGN KEY (region_id) REFERENCES DHS_Region(region_id)
);
CREATE INDEX idx_dt_survey ON DHS_Thematic_Fact(survey_id);
CREATE INDEX idx_dt_region ON DHS_Thematic_Fact(region_id);

-- 22. Child_Health_Diarrhea_Fact
CREATE TABLE Child_Health_Diarrhea_Fact (
    survey_id              VARCHAR2(50)  NOT NULL,
    region_id              VARCHAR2(50)  NOT NULL,
    characteristic_id      NUMBER(10)    NOT NULL,
    observation_type       VARCHAR2(30)  NOT NULL,
    sub_type               VARCHAR2(30)  NOT NULL,
    value                  NUMBER(20,4),
    denominator_weighted   NUMBER(10),
    denominator_unweighted NUMBER(15,2),
    CONSTRAINT pk_diarrhea_fact PRIMARY KEY (survey_id, region_id, characteristic_id, observation_type, sub_type),
    CONSTRAINT fk_df_survey FOREIGN KEY (survey_id) REFERENCES DHS_Survey(survey_id),
    CONSTRAINT fk_df_region FOREIGN KEY (region_id) REFERENCES DHS_Region(region_id)
);
CREATE INDEX idx_df_survey ON Child_Health_Diarrhea_Fact(survey_id);
CREATE INDEX idx_df_region ON Child_Health_Diarrhea_Fact(region_id);

-- 23. Population_Demographic (1:1 with Macroeconomic_Indicator)
CREATE TABLE Population_Demographic (
    year                    NUMBER(4)     NOT NULL,
    total_population_million NUMBER(15,4),
    population_density      NUMBER(15,2),
    population_change_pct   NUMBER(10,4),
    urban_population_pct    NUMBER(10,4),
    CONSTRAINT pk_pop_demographic PRIMARY KEY (year),
    CONSTRAINT fk_pop_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);

-- 24. Labor_Force_Overview (1:1 with Macroeconomic_Indicator)
CREATE TABLE Labor_Force_Overview (
    year                         NUMBER(4)     NOT NULL,
    total_labor_force_millions   NUMBER(15,4),
    total_employed_millions      NUMBER(15,4),
    total_unemployed_millions    NUMBER(15,4),
    unemployment_rate_pct        NUMBER(10,4),
    CONSTRAINT pk_labor_overview PRIMARY KEY (year),
    CONSTRAINT fk_labor_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);

-- 25. Sectoral_GDP
CREATE TABLE Sectoral_GDP (
    year                       NUMBER(4)     NOT NULL,
    base_year                  VARCHAR2(10)  NOT NULL,
    price_type                 VARCHAR2(10)  NOT NULL,
    component_type             VARCHAR2(20)  NOT NULL,
    component_name             VARCHAR2(50)  NOT NULL,
    sector_code                VARCHAR2(20)  NOT NULL,
    value_millions             NUMBER(20,2),
    growth_rate                NUMBER(10,4),
    share_pct                  NUMBER(10,4),
    productivity_ratio_to_agri NUMBER(10,4),
    avg_annual_growth_pct      NUMBER(10,4),
    unit                       VARCHAR2(20),
    CONSTRAINT pk_sectoral_gdp PRIMARY KEY (year, base_year, price_type, component_type, component_name, sector_code),
    CONSTRAINT fk_sg_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year),
    CONSTRAINT fk_sg_sector FOREIGN KEY (sector_code) REFERENCES Industry_Sector(sector_code)
);
CREATE INDEX idx_sg_macro ON Sectoral_GDP(year);
CREATE INDEX idx_sg_sector ON Sectoral_GDP(sector_code);

-- 26. Quarterly_GDP
CREATE TABLE Quarterly_GDP (
    year                NUMBER(4)     NOT NULL,
    quarter             VARCHAR2(10)  NOT NULL,
    sector_code         VARCHAR2(20)  NOT NULL,
    measure_type        VARCHAR2(20)  NOT NULL,
    price_type          VARCHAR2(10)  NOT NULL,
    value_million_tk    NUMBER(20,2),
    growth_rate_percent NUMBER(10,4),
    share_percent       NUMBER(10,4),
    CONSTRAINT pk_quarterly_gdp PRIMARY KEY (year, quarter, sector_code, measure_type, price_type),
    CONSTRAINT fk_qg_sector FOREIGN KEY (sector_code) REFERENCES Industry_Sector(sector_code)
);
CREATE INDEX idx_qg_sector ON Quarterly_GDP(sector_code);

-- 27. Price_Index
CREATE TABLE Price_Index (
    year              NUMBER(4)     NOT NULL,
    month             NUMBER(2)     NOT NULL,
    base_year         VARCHAR2(10)  NOT NULL,
    index_name        VARCHAR2(50)  NOT NULL,
    area_level        VARCHAR2(20)  NOT NULL,
    area_name         VARCHAR2(50)  NOT NULL,
    index_value       NUMBER(15,4),
    weight_value      NUMBER(10,4),
    annual_change_pct NUMBER(10,4),
    pct_change        NUMBER(10,4),
    CONSTRAINT pk_price_index PRIMARY KEY (year, month, base_year, index_name, area_level, area_name)
);

-- 28. Exchange_Rate
CREATE TABLE Exchange_Rate (
    year                 NUMBER(4)     NOT NULL,
    month                NUMBER(2)     NOT NULL,
    rate_type            VARCHAR2(20)  NOT NULL,
    exchange_rate_value  NUMBER(15,4),
    end_of_period_rate   NUMBER(15,4),
    period_average_rate  NUMBER(15,4),
    CONSTRAINT pk_exchange_rate PRIMARY KEY (year, month, rate_type)
);

-- 29. Monetary_Aggregate
CREATE TABLE Monetary_Aggregate (
    year                  NUMBER(4)     NOT NULL,
    metric_name           VARCHAR2(50)  NOT NULL,
    value_tk_million      NUMBER(20,2),
    m1_billion_tk         NUMBER(15,4),
    m2_billion_tk         NUMBER(15,4),
    m2_annual_change_pct  NUMBER(10,4),
    m2_pct_gdp            NUMBER(10,4),
    currency_in_circulation NUMBER(15,4),
    demand_deposits       NUMBER(15,4),
    quasi_money           NUMBER(15,4),
    net_foreign_assets    NUMBER(15,4),
    domestic_credit       NUMBER(15,4),
    CONSTRAINT pk_monetary_agg PRIMARY KEY (year, metric_name),
    CONSTRAINT fk_ma_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);
CREATE INDEX idx_ma_macro ON Monetary_Aggregate(year);

-- 30. Interest_Rate
CREATE TABLE Interest_Rate (
    year            NUMBER(4)     NOT NULL,
    deposit_type    VARCHAR2(30)  NOT NULL,
    rate_per_annum  NUMBER(10,4),
    CONSTRAINT pk_interest_rate PRIMARY KEY (year, deposit_type),
    CONSTRAINT fk_ir_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);
CREATE INDEX idx_ir_macro ON Interest_Rate(year);

-- 31. Government_Finance
CREATE TABLE Government_Finance (
    year                            NUMBER(4)     NOT NULL,
    fiscal_year                     VARCHAR2(10)  NOT NULL,
    account_type                    VARCHAR2(30)  NOT NULL,
    component_name                  VARCHAR2(50)  NOT NULL,
    ministry_name                   VARCHAR2(100) NOT NULL,
    value_billion_tk                NUMBER(20,2),
    value_million_tk                NUMBER(20,2),
    budget_amount_cr                NUMBER(15,2),
    pct_change_from_base_year       NUMBER(10,4),
    total_revenue_grants_bn         NUMBER(15,4),
    total_revenue_bn                NUMBER(15,4),
    total_expenditure_bn            NUMBER(15,4),
    overall_surplus_deficit_bn      NUMBER(15,4),
    overall_surplus_deficit_pct_gdp NUMBER(10,4),
    domestic_borrowing_bn           NUMBER(15,4),
    foreign_borrowing_bn            NUMBER(15,4),
    CONSTRAINT pk_gov_finance PRIMARY KEY (year, fiscal_year, account_type, component_name, ministry_name),
    CONSTRAINT fk_gf_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);
CREATE INDEX idx_gf_macro ON Government_Finance(year);

-- 32. CGE_Simulation_Metric
CREATE TABLE CGE_Simulation_Metric (
    ministry_name          VARCHAR2(100) NOT NULL,
    fiscal_year            VARCHAR2(10)  NOT NULL,
    sector_code            VARCHAR2(20)  NOT NULL,
    area_type              VARCHAR2(20)  NOT NULL,
    education_level        VARCHAR2(30)  NOT NULL,
    metric_type            VARCHAR2(30)  NOT NULL,
    base_value             NUMBER(20,2),
    pct_change_from_base   NUMBER(10,4),
    CONSTRAINT pk_cge_sim PRIMARY KEY (ministry_name, fiscal_year, sector_code, area_type, education_level, metric_type)
);

-- 33. External_Trade_Annual (PK is VARCHAR for fiscal year)
CREATE TABLE External_Trade_Annual (
    year                      VARCHAR2(10)  NOT NULL,
    total_import_tk           NUMBER(20,2),
    total_import_usd          NUMBER(20,2),
    import_growth_rate_pct    NUMBER(10,4),
    import_pct_gdp            NUMBER(10,4),
    import_pct_revenue        NUMBER(10,4),
    per_capita_import_tk      NUMBER(15,2),
    total_export_tk           NUMBER(20,2),
    total_export_usd          NUMBER(20,2),
    export_growth_rate_pct    NUMBER(10,4),
    export_pct_gdp            NUMBER(10,4),
    per_capita_export_tk      NUMBER(15,2),
    trade_balance_tk          NUMBER(20,2),
    exports_fob_billion_tk    NUMBER(15,4),
    exports_annual_change_pct NUMBER(10,4),
    imports_cif_billion_tk    NUMBER(15,4),
    imports_annual_change_pct NUMBER(10,4),
    CONSTRAINT pk_ext_trade_annual PRIMARY KEY (year)
);

-- 34. Trade_Detail
CREATE TABLE Trade_Detail (
    year                      VARCHAR2(10)  NOT NULL,
    trade_type                VARCHAR2(10)  NOT NULL,
    detail_category           VARCHAR2(30)  NOT NULL,
    detail_value              VARCHAR2(50)  NOT NULL,
    month                     VARCHAR2(10)  NOT NULL,
    value_million_tk          NUMBER(20,2),
    value_million_usd         NUMBER(20,2),
    composition_pct           NUMBER(10,4),
    unit                      VARCHAR2(20),
    unit_price_tk             NUMBER(15,4),
    index_value               NUMBER(15,4),
    pct_of_annual_total       NUMBER(10,4),
    section_number            NUMBER(5),
    partner_country           VARCHAR2(100),
    value_million_usd_partner NUMBER(20,2),
    CONSTRAINT pk_trade_detail PRIMARY KEY (year, trade_type, detail_category, detail_value, month)
);

-- 35. Country_Trade (Conceptual FK to Country via country_name - resolved in ETL)
CREATE TABLE Country_Trade (
    year              VARCHAR2(10)  NOT NULL,
    country_name      VARCHAR2(100) NOT NULL,
    area_name         VARCHAR2(100),
    export_value_tk   NUMBER(20,2),
    export_pct        NUMBER(10,4),
    import_value_tk   NUMBER(20,2),
    import_pct        NUMBER(10,4),
    trade_balance_tk  NUMBER(20,2),
    CONSTRAINT pk_country_trade PRIMARY KEY (year, country_name)
);

-- 36. Balance_of_Payments
CREATE TABLE Balance_of_Payments (
    year                      NUMBER(4)     NOT NULL,
    current_account_balance   NUMBER(20,2),
    balance_on_goods          NUMBER(20,2),
    balance_on_services       NUMBER(20,2),
    balance_on_primary_income NUMBER(20,2),
    balance_on_secondary_income NUMBER(20,2),
    financial_account         NUMBER(20,2),
    direct_investment_net     NUMBER(20,2),
    portfolio_investment_net  NUMBER(20,2),
    overall_balance           NUMBER(20,2),
    total_reserves_million_usd NUMBER(20,2),
    CONSTRAINT pk_bop PRIMARY KEY (year),
    CONSTRAINT fk_bop_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);
CREATE INDEX idx_bop_macro ON Balance_of_Payments(year);

-- 37. External_Debt_Indicator
CREATE TABLE External_Debt_Indicator (
    year                           NUMBER(4)     NOT NULL,
    total_debt_outstanding_mn_usd  NUMBER(20,2),
    total_debt_pct_gni             NUMBER(10,4),
    long_term_debt_pct_total       NUMBER(10,4),
    short_term_debt_pct_total      NUMBER(10,4),
    debt_service_pct_exports       NUMBER(10,4),
    avg_interest_rate_new_commitments NUMBER(10,4),
    avg_maturity_years             NUMBER(10,4),
    CONSTRAINT pk_ext_debt PRIMARY KEY (year),
    CONSTRAINT fk_ed_macro FOREIGN KEY (year) REFERENCES Macroeconomic_Indicator(year)
);
CREATE INDEX idx_ed_macro ON External_Debt_Indicator(year);

-- 38. Production_Energy (Conceptual FK to Industry_Sector via isic_division)
CREATE TABLE Production_Energy (
    year              NUMBER(4)     NOT NULL,
    period_label      VARCHAR2(20)  NOT NULL,
    base_year         VARCHAR2(10)  NOT NULL,
    resource_name     VARCHAR2(50)  NOT NULL,
    activity_type     VARCHAR2(30)  NOT NULL,
    isic_division     VARCHAR2(10)  NOT NULL,
    value             NUMBER(20,2),
    unit              VARCHAR2(20),
    index_value       NUMBER(15,4),
    weight            NUMBER(10,4),
    revision_flag     VARCHAR2(10),
    CONSTRAINT pk_prod_energy PRIMARY KEY (year, period_label, base_year, resource_name, activity_type, isic_division)
);

-- 39. MPI_Measurement
CREATE TABLE MPI_Measurement (
    survey_year            NUMBER(4)     NOT NULL,
    admin_1_pcode          VARCHAR2(20)  NOT NULL,
    survey_name            VARCHAR2(50)  NOT NULL,
    admin_1_name           VARCHAR2(100),
    country_iso3           VARCHAR2(3)   NOT NULL,
    mpi                    NUMBER(15,6),
    headcount_ratio        NUMBER(15,6),
    intensity_of_deprivation NUMBER(15,6),
    vulnerable_to_poverty  NUMBER(15,6),
    in_severe_poverty      NUMBER(15,6),
    start_date             TIMESTAMP,
    end_date               TIMESTAMP,
    CONSTRAINT pk_mpi PRIMARY KEY (survey_year, admin_1_pcode, survey_name),
    CONSTRAINT fk_mpi_admin FOREIGN KEY (admin_1_pcode) REFERENCES Admin_Boundary(entity_pcode),
    CONSTRAINT fk_mpi_country FOREIGN KEY (country_iso3) REFERENCES Country(country_code)
);
CREATE INDEX idx_mpi_admin ON MPI_Measurement(admin_1_pcode);
CREATE INDEX idx_mpi_country ON MPI_Measurement(country_iso3);

-- 40. Economic_Unit_Aggregate (Conceptual FK to Admin_Boundary)
CREATE TABLE Economic_Unit_Aggregate (
    year           NUMBER(4)     NOT NULL,
    division_id    VARCHAR2(20)  NOT NULL,
    district_id    VARCHAR2(20)  NOT NULL,
    unit_type      VARCHAR2(20)  NOT NULL,
    locality       VARCHAR2(10)  NOT NULL,
    industry_type  VARCHAR2(30)  NOT NULL,
    unit_count     NUMBER(20),
    CONSTRAINT pk_economic_unit PRIMARY KEY (year, division_id, district_id, unit_type, locality, industry_type)
);

-- 41. Person_Engaged_Aggregate (Conceptual FK to Admin_Boundary)
CREATE TABLE Person_Engaged_Aggregate (
    year               NUMBER(4)     NOT NULL,
    division_id        VARCHAR2(20)  NOT NULL,
    district_id        VARCHAR2(20)  NOT NULL,
    establishment_type VARCHAR2(20)  NOT NULL,
    locality           VARCHAR2(10)  NOT NULL,
    sex                VARCHAR2(10)  NOT NULL,
    tpe_count          NUMBER(20),
    CONSTRAINT pk_person_engaged PRIMARY KEY (year, division_id, district_id, establishment_type, locality, sex)
);

-- 42. Business_Ecommerce_Fact (Conceptual FK to Admin_Boundary)
CREATE TABLE Business_Ecommerce_Fact (
    year                    NUMBER(4)     NOT NULL,
    division_id             VARCHAR2(20)  NOT NULL,
    fact_type               VARCHAR2(30)  NOT NULL,
    sub_category            VARCHAR2(50)  NOT NULL,
    sex                     VARCHAR2(10)  NOT NULL,
    unit_head_count         NUMBER(20),
    ecommerce_unit_count    NUMBER(10),
    number_of_responses     NUMBER(10),
    percentage_of_responses NUMBER(10,4),
    percentage_of_units     NUMBER(10,4),
    unit_count              NUMBER(20),
    CONSTRAINT pk_ecommerce_fact PRIMARY KEY (year, division_id, fact_type, sub_category, sex)
);

-- 43. Country_GRB_Practice (Conceptual FK to Country via country_name)
CREATE TABLE Country_GRB_Practice (
    country_name           VARCHAR2(100) NOT NULL,
    initiatives_description CLOB,
    CONSTRAINT pk_grb PRIMARY KEY (country_name)
);

-- ============================================================
-- VERIFICATION QUERIES (Run after creation to confirm)
-- ============================================================

-- Check all tables were created
SELECT table_name FROM user_tables ORDER BY table_name;

-- Check table count (should be 43)
SELECT COUNT(*) AS total_tables FROM user_tables;

PROMPT ============================================================
PROMPT Phase 2 DDL execution complete. All 43 tables created.
PROMPT ============================================================
