"""
mapping_dicts.py
Master mapping and standardization module for Phase 4 (ETL Transformation).
Resolves all ≈ (approximate) key mismatches across the 43 entities.

Usage:
    from mapping_dicts import (
        clean_text, map_country_to_code, map_sector_code,
        map_admin_to_pcode, map_gender, map_vaccine_code,
        parse_fiscal_year, get_dhs_survey_type, get_domain
    )
"""

import re
from typing import Optional

# ============================================================
# 1. COUNTRY MAPPING (Resolves: country_name → country_code)
#    Covers: Country_Trade, Country_GRB_Practice, and all
#    tables where raw data has full names instead of ISO3.
# ============================================================

COUNTRY_MAP = {
    # South Asia (Primary focus)
    'bangladesh': 'BGD',
    'bangladesh peoples republic': 'BGD',
    'bangladesh, people\'s republic of': 'BGD',
    'bd': 'BGD',
    'india': 'IND',
    'myanmar': 'MMR',
    'burma': 'MMR',
    'nepal': 'NPL',
    'sri lanka': 'LKA',
    'pakistan': 'PAK',
    'afghanistan': 'AFG',
    'bhutan': 'BTN',
    'maldives': 'MDV',
    
    # Major trade partners (from Foreign Trade Statistics PDF)
    'united states': 'USA',
    'usa': 'USA',
    'u.s.a': 'USA',
    'united states of america': 'USA',
    'china': 'CHN',
    'peoples republic of china': 'CHN',
    'prc': 'CHN',
    'japan': 'JPN',
    'germany': 'DEU',
    'federal republic of germany': 'DEU',
    'united kingdom': 'GBR',
    'uk': 'GBR',
    'great britain': 'GBR',
    'france': 'FRA',
    'italy': 'ITA',
    'spain': 'ESP',
    'netherlands': 'NLD',
    'belgium': 'BEL',
    'canada': 'CAN',
    'australia': 'AUS',
    'brazil': 'BRA',
    'russia': 'RUS',
    'russian federation': 'RUS',
    'turkey': 'TUR',
    'uae': 'ARE',
    'united arab emirates': 'ARE',
    'saudi arabia': 'SAU',
    'singapore': 'SGP',
    'malaysia': 'MYS',
    'indonesia': 'IDN',
    'thailand': 'THA',
    'vietnam': 'VNM',
    'south korea': 'KOR',
    'republic of korea': 'KOR',
    'hong kong': 'HKG',
    'taiwan': 'TWN',
    'switzerland': 'CHE',
    'sweden': 'SWE',
    'norway': 'NOR',
    'denmark': 'DNK',
    'poland': 'POL',
    'austria': 'AUT',
    'portugal': 'PRT',
    'greece': 'GRC',
    'egypt': 'EGY',
    'south africa': 'ZAF',
    'mexico': 'MEX',
}

def clean_text(text: str) -> str:
    """
    Universal text cleaner: lowercases, strips, and collapses spaces.
    Removes punctuation except for standard separators.
    """
    if not isinstance(text, str):
        return ''
    # Lowercase
    t = text.lower().strip()
    # Remove excessive spaces
    t = re.sub(r'\s+', ' ', t)
    # Remove leading/trailing punctuation
    t = t.strip('.,;:!?()[]{}"\'')
    return t

def map_country_to_code(text: Optional[str]) -> str:
    """
    Converts any country name/variant to ISO3 country_code.
    Raises ValueError if unmapped — add the missing variant to COUNTRY_MAP.
    """
    if not text:
        raise ValueError("map_country_to_code: Empty input provided.")
    
    cleaned = clean_text(text)
    
    # Direct match
    if cleaned in COUNTRY_MAP:
        return COUNTRY_MAP[cleaned]
    
    # Try matching without common prefixes/suffixes (e.g., "Federal Republic of")
    tokens = cleaned.split()
    # Check if any token is a direct key
    for token in tokens:
        if token in COUNTRY_MAP:
            return COUNTRY_MAP[token]
    
    # Check partial match (e.g., "Myanmar (Burma)" -> "myanmar")
    for key in COUNTRY_MAP.keys():
        if key in cleaned or cleaned in key:
            return COUNTRY_MAP[key]
    
    # If still not found, raise error with clear instruction
    raise ValueError(
        f"Unmapped country name: '{text}'. "
        f"Please add a mapping for '{cleaned}' to COUNTRY_MAP."
    )

# ============================================================
# 2. SECTOR MAPPING (Resolves: isic_division, sector_name → sector_code)
#    Covers: Industry_Sector, Production_Energy, Sectoral_Employment,
#    Sectoral_GDP, CGE_Simulation, Quarterly_GDP.
# ============================================================

SECTOR_MAP = {
    # Broad ISIC / NACE divisions (from your Quarterly GDP & Manufacturing docs)
    'a': 'A',  # Agriculture, Forestry, Fishing
    'agriculture': 'A',
    'agri': 'A',
    'b': 'B',  # Mining and Quarrying
    'mining': 'B',
    'c': 'C',  # Manufacturing
    'manufacturing': 'C',
    'd': 'D',  # Electricity, Gas, Steam
    'electricity': 'D',
    'e': 'E',  # Water Supply, Sewerage
    'water': 'E',
    'f': 'F',  # Construction
    'construction': 'F',
    'g': 'G',  # Wholesale & Retail Trade
    'wholesale': 'G',
    'retail': 'G',
    'trade': 'G',
    'h': 'H',  # Transportation & Storage
    'transport': 'H',
    'storage': 'H',
    'i': 'I',  # Accommodation & Food Service
    'accommodation': 'I',
    'food service': 'I',
    'j': 'J',  # Information & Communication
    'information': 'J',
    'telecom': 'J',
    'communication': 'J',
    'k': 'K',  # Financial & Insurance
    'financial': 'K',
    'insurance': 'K',
    'banking': 'K',
    'l': 'L',  # Real Estate
    'real estate': 'L',
    'm': 'M',  # Professional, Scientific, Technical
    'professional': 'M',
    'technical': 'M',
    'scientific': 'M',
    'n': 'N',  # Administrative & Support
    'administrative': 'N',
    'support': 'N',
    'o': 'O',  # Public Administration
    'public admin': 'O',
    'government': 'O',
    'p': 'P',  # Education
    'education': 'P',
    'q': 'Q',  # Human Health & Social Work
    'health': 'Q',
    'social work': 'Q',
    'r': 'R',  # Arts, Entertainment, Recreation
    'arts': 'R',
    'entertainment': 'R',
    'recreation': 'R',
    's': 'S',  # Other Services
    'other services': 'S',
    'services': 'S',
    
    # Specific Bangladesh context (from garments_growth, ban-key-indicators)
    'wearing apparel': 'C_APP',
    'apparel': 'C_APP',
    'garments': 'C_APP',
    'textiles': 'C_TEX',
    'crops': 'A_CROP',
    'livestock': 'A_LIVE',
    'fisheries': 'A_FISH',
    'forestry': 'A_FOR',
    'pharmaceuticals': 'C_PHAR',
    'leather': 'C_LEA',
    'jute': 'C_JUTE',
}

def map_sector_code(text: Optional[str]) -> str:
    """
    Converts any sector name, ISIC division (e.g., 'C'), or activity
    to the canonical sector_code from Industry_Sector.
    """
    if not text:
        raise ValueError("map_sector_code: Empty input provided.")
    
    cleaned = clean_text(text)
    
    # Direct match
    if cleaned in SECTOR_MAP:
        return SECTOR_MAP[cleaned]
    
    # Match against uppercase variants
    if cleaned.upper() in SECTOR_MAP:
        return SECTOR_MAP[cleaned.upper()]
    
    # Check token match (for long descriptions like "Manufacturing of wearing apparel")
    tokens = cleaned.split()
    for token in tokens:
        if token in SECTOR_MAP:
            return SECTOR_MAP[token]
        if token.upper() in SECTOR_MAP:
            return SECTOR_MAP[token.upper()]
    
    raise ValueError(
        f"Unmapped sector: '{text}'. "
        f"Please add '{cleaned}' to SECTOR_MAP."
    )

# ============================================================
# 3. ADMIN BOUNDARY MAPPING (division_id/district_id → entity_pcode)
#    Covers: Economic_Unit_Aggregate, Person_Engaged_Aggregate,
#    Business_Ecommerce_Fact, MPI_Measurement.
# ============================================================

ADMIN_MAP = {
    # Divisions (ADM1) - based on your bgd_adminboundaries_tabulardata
    'dhaka': 'BD-A',
    'dhaka division': 'BD-A',
    'chattagram': 'BD-B',
    'chittagong': 'BD-B',
    'chattagram division': 'BD-B',
    'barishal': 'BD-C',
    'barisal': 'BD-C',
    'barishal division': 'BD-C',
    'khulna': 'BD-D',
    'khulna division': 'BD-D',
    'rajshahi': 'BD-E',
    'rajshahi division': 'BD-E',
    'rangpur': 'BD-F',
    'rangpur division': 'BD-F',
    'mymensingh': 'BD-G',
    'myensingh': 'BD-G',  # Typo from your docs!
    'mymensingh division': 'BD-G',
    'sylhet': 'BD-H',
    'sylhet division': 'BD-H',
    
    # National/Total aggregates
    'bangladesh': 'BD-00',
    'national': 'BD-00',
    'bd': 'BD-00',
    
    # Some DHS region names map to admin codes
    'barisal': 'BD-C',
    'chittagong': 'BD-B',
    'dhaka': 'BD-A',
    'khulna': 'BD-D',
    'rajshahi': 'BD-E',
    'rangpur': 'BD-F',
    'sylhet': 'BD-H',
    'mymensingh': 'BD-G',
}

def map_admin_to_pcode(text: Optional[str]) -> str:
    """
    Maps division/district/location names to the Admin_Boundary.entity_pcode.
    """
    if not text:
        raise ValueError("map_admin_to_pcode: Empty input provided.")
    
    cleaned = clean_text(text)
    
    # Direct match
    if cleaned in ADMIN_MAP:
        return ADMIN_MAP[cleaned]
    
    # Remove suffixes like "division", "district", "zila"
    simplified = re.sub(r'\b(division|district|zila|upazila|thana)\b', '', cleaned).strip()
    if simplified in ADMIN_MAP:
        return ADMIN_MAP[simplified]
    
    raise ValueError(
        f"Unmapped admin region: '{text}'. "
        f"Please add '{cleaned}' to ADMIN_MAP."
    )

# ============================================================
# 4. GENDER MAPPING (Standardizes all gender representations)
#    Covers: Every table with gender/sex columns.
# ============================================================

GENDER_MAP = {
    'male': 'Male',
    'm': 'Male',
    'men': 'Male',
    'boy': 'Male',
    'boys': 'Male',
    'male (m)': 'Male',
    'female': 'Female',
    'f': 'Female',
    'women': 'Female',
    'girl': 'Female',
    'girls': 'Female',
    'female (f)': 'Female',
    'hijra': 'Hijra',
    'hijras': 'Hijra',
    'transgender': 'Hijra',
    'total': 'Total',
    'both': 'Total',
    'all': 'Total',
}

def map_gender(text: Optional[str]) -> str:
    """Returns canonical gender: 'Male', 'Female', 'Hijra', or 'Total'."""
    if not text:
        return 'Total'  # Default to total if missing
    
    cleaned = clean_text(text)
    
    if cleaned in GENDER_MAP:
        return GENDER_MAP[cleaned]
    
    # Try the first token (e.g., "Male 15-24" -> "male")
    tokens = cleaned.split()
    if tokens and tokens[0] in GENDER_MAP:
        return GENDER_MAP[tokens[0]]
    
    raise ValueError(
        f"Unmapped gender: '{text}'. "
        f"Please add '{cleaned}' to GENDER_MAP."
    )

# ============================================================
# 5. VACCINE MAPPING (Standardizes vaccine codes from bgd.pdf)
#    Note: Most sources already use BCG, DTP, etc. This is a
#    safe fallback for any abbreviated variants.
# ============================================================

VACCINE_MAP = {
    'bcg': 'BCG',
    'bacillus calmette guerin': 'BCG',
    'dtp': 'DTP3',
    'dtp1': 'DTP1',
    'dtp3': 'DTP3',
    'diphtheria tetanus pertussis': 'DTP3',
    'polio': 'Pol3',
    'pol3': 'Pol3',
    'ipv': 'IPV1',
    'ipv1': 'IPV1',
    'inactivated polio': 'IPV1',
    'mcv': 'MCV1',
    'mcv1': 'MCV1',
    'mcv2': 'MCV2',
    'measles': 'MCV1',
    'measles containing vaccine': 'MCV1',
    'rcv': 'RCV1',
    'rcv1': 'RCV1',
    'rubella': 'RCV1',
    'hepb': 'HepB3',
    'hepb3': 'HepB3',
    'hepatitis b': 'HepB3',
    'hib': 'Hib3',
    'hib3': 'Hib3',
    'haemophilus influenzae': 'Hib3',
    'rota': 'RotaC',
    'rotac': 'RotaC',
    'rotavirus': 'RotaC',
    'pcv': 'PcV3',
    'pcv3': 'PcV3',
    'pneumococcal': 'PcV3',
    'yfv': 'YFV',
    'yellow fever': 'YFV',
}

def map_vaccine_code(text: Optional[str]) -> str:
    """Returns canonical vaccine_code (e.g., 'BCG', 'DTP3')."""
    if not text:
        raise ValueError("map_vaccine_code: Empty input.")
    cleaned = clean_text(text)
    
    if cleaned in VACCINE_MAP:
        return VACCINE_MAP[cleaned]
    # If it's already a code (e.g., 'BCG'), just uppercase it
    if cleaned.upper() in ['BCG', 'DTP1', 'DTP3', 'POL3', 'IPV1', 'MCV1', 'MCV2', 
                           'RCV1', 'HEPB3', 'HIB3', 'ROTAC', 'PCV3', 'YFV']:
        return cleaned.upper()
    
    raise ValueError(
        f"Unmapped vaccine: '{text}'. "
        f"Please add '{cleaned}' to VACCINE_MAP."
    )

# ============================================================
# 6. FISCAL YEAR PARSER (VARCHAR '2023-24' → INT year)
#    Covers: External_Trade_Annual year, Government_Finance fiscal_year
# ============================================================

def parse_fiscal_year(text: str, return_start_year: bool = True) -> int:
    """
    Converts '2023-24', '2023/24', 'FY2023-24' to INT year.
    Default: returns the starting year (2023).
    Set return_start_year=False to return ending year (2024).
    """
    if not isinstance(text, str):
        # If it's already an int, return it
        if isinstance(text, int):
            return text
        raise ValueError(f"parse_fiscal_year: Expected string, got {type(text)}")
    
    cleaned = text.strip()
    # Remove 'FY' prefix
    cleaned = re.sub(r'^fy\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Extract 4-digit years
    years = re.findall(r'\b(19|20)\d{2}\b', cleaned)
    if not years:
        # Try to find any numbers
        nums = re.findall(r'\d+', cleaned)
        if nums and len(nums) >= 1:
            # If only one year (e.g., '2023'), assume it's the start
            return int(nums[0]) if return_start_year else int(nums[0]) + 1
        raise ValueError(f"parse_fiscal_year: No valid year found in '{text}'")
    
    # If multiple years found, take first as start, last as end
    start_year = int(years[0])
    end_year = int(years[-1])
    
    if return_start_year:
        return start_year
    else:
        return end_year

# ============================================================
# 7. DHS SURVEY TYPE & DOMAIN STANDARDIZERS
# ============================================================

DHS_SURVEY_TYPE_MAP = {
    'dhs': 'DHS',
    'demographic and health survey': 'DHS',
    'mics': 'MICS',
    'multiple indicator cluster survey': 'MICS',
    'ces': 'CES',
    'coverage evaluation survey': 'CES',
    'epi': 'EPI',
    'uesds': 'UESDS',
    'utilization of essential service delivery survey': 'UESDS',
    'nce': 'NCE',
    'national coverage evaluation': 'NCE',
}

def get_dhs_survey_type(text: Optional[str]) -> str:
    """Returns standardized DHS survey type."""
    if not text:
        return 'UNKNOWN'
    cleaned = clean_text(text)
    for key, val in DHS_SURVEY_TYPE_MAP.items():
        if key in cleaned:
            return val
    return 'OTHER'

DOMAINS = {
    'economic', 'demographic', 'health', 'education', 'environment',
    'agriculture', 'infrastructure', 'government', 'financial',
    'technology', 'business', 'poverty', 'external', 'gender'
}

def get_domain(text: Optional[str]) -> str:
    """Returns a valid domain string (title case) or raises error."""
    if not text:
        return 'OTHER'
    cleaned = clean_text(text)
    # Check if it matches any domain
    for domain in DOMAINS:
        if domain in cleaned:
            return domain.title()
    # If domain is literally in the list, just title it
    if cleaned in DOMAINS:
        return cleaned.title()
    # Fallback: return as-is with title case
    return cleaned.title()

# ============================================================
# 8. MASTER RESOLVER FOR COUNTRY NAMES (For batch processing)
# ============================================================

def resolve_country_column(df, column_name, new_column_name='country_code'):
    """
    Utility function to apply map_country_to_code to a DataFrame column.
    Example:
        df = resolve_country_column(df, 'country_name')
    """
    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found in DataFrame.")
    
    df[new_column_name] = df[column_name].apply(map_country_to_code)
    return df

# ============================================================
# 9. SANITY CHECK (Run this when you import to verify all maps)
# ============================================================

def run_sanity_checks():
    """Executes a quick test of all mapping functions."""
    print("Running mapping_dicts.py sanity checks...")
    
    # Country
    assert map_country_to_code("Bangladesh") == "BGD"
    assert map_country_to_code("bd") == "BGD"
    assert map_country_to_code("United States of America") == "USA"
    
    # Sector
    assert map_sector_code("Manufacturing") == "C"
    assert map_sector_code("C") == "C"
    assert map_sector_code("Agriculture") == "A"
    assert map_sector_code("Wearing Apparel") == "C_APP"
    
    # Admin
    assert map_admin_to_pcode("Dhaka Division") == "BD-A"
    assert map_admin_to_pcode("Chittagong") == "BD-B"
    assert map_admin_to_pcode("Myensingh") == "BD-G"  # Typo handle
    
    # Gender
    assert map_gender("Male") == "Male"
    assert map_gender("M") == "Male"
    assert map_gender("F") == "Female"
    assert map_gender("Hijra") == "Hijra"
    
    # Fiscal Year
    assert parse_fiscal_year("2023-24") == 2023
    assert parse_fiscal_year("FY2023-24") == 2023
    assert parse_fiscal_year("2023/24") == 2023
    assert parse_fiscal_year("2023") == 2023
    
    # Vaccine
    assert map_vaccine_code("bcg") == "BCG"
    assert map_vaccine_code("DTP3") == "DTP3"
    
    print("✅ All sanity checks passed. mapping_dicts.py is ready.")

if __name__ == "__main__":
    run_sanity_checks()
