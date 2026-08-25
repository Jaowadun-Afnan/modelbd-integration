import pandas as pd
import re
from typing import Optional

# ---------- COUNTRY MAPPING ----------
COUNTRY_MAP = {
    # Bangladesh & neighbours
    'bangladesh': 'BGD', 'bd': 'BGD', 'bangladesh, people\'s republic of': 'BGD',
    'india': 'IND', 'myanmar': 'MMR', 'burma': 'MMR', 'nepal': 'NPL',
    'sri lanka': 'LKA', 'pakistan': 'PAK', 'afghanistan': 'AFG',
    'bhutan': 'BTN', 'maldives': 'MDV',
    # Major trade partners
    'united states': 'USA', 'usa': 'USA', 'u.s.a': 'USA', 'united states of america': 'USA',
    'china': 'CHN', 'peoples republic of china': 'CHN', 'prc': 'CHN',
    'japan': 'JPN', 'germany': 'DEU', 'federal republic of germany': 'DEU',
    'united kingdom': 'GBR', 'uk': 'GBR', 'great britain': 'GBR',
    'france': 'FRA', 'italy': 'ITA', 'spain': 'ESP', 'netherlands': 'NLD',
    'belgium': 'BEL', 'canada': 'CAN', 'australia': 'AUS', 'brazil': 'BRA',
    'russia': 'RUS', 'russian federation': 'RUS', 'turkey': 'TUR',
    'uae': 'ARE', 'united arab emirates': 'ARE', 'saudi arabia': 'SAU',
    'singapore': 'SGP', 'malaysia': 'MYS', 'indonesia': 'IDN',
    'thailand': 'THA', 'vietnam': 'VNM', 'south korea': 'KOR',
    'republic of korea': 'KOR', 'hong kong': 'HKG', 'taiwan': 'TWN',
    'switzerland': 'CHE', 'sweden': 'SWE', 'norway': 'NOR', 'denmark': 'DNK',
    'poland': 'POL', 'austria': 'AUT', 'portugal': 'PRT', 'greece': 'GRC',
    'egypt': 'EGY', 'south africa': 'ZAF', 'mexico': 'MEX',
    # Additional common ones
    'netherlands': 'NLD', 'luxembourg': 'LUX', 'ireland': 'IRL',
    'finland': 'FIN', 'czech republic': 'CZE', 'hungary': 'HUN',
    'romania': 'ROU', 'bulgaria': 'BGR', 'croatia': 'HRV',
    'slovakia': 'SVK', 'slovenia': 'SVN', 'lithuania': 'LTU',
    'latvia': 'LVA', 'estonia': 'EST', 'cyprus': 'CYP',
    'malta': 'MLT', 'iceland': 'ISL', 'new zealand': 'NZL',
    'argentina': 'ARG', 'chile': 'CHL', 'colombia': 'COL',
    'peru': 'PER', 'venezuela': 'VEN', 'ecuador': 'ECU',
    'uruguay': 'URY', 'paraguay': 'PRY', 'bolivia': 'BOL',
    'philippines': 'PHL', 'cambodia': 'KHM', 'laos': 'LAO',
    'brunei': 'BRN', 'mongolia': 'MNG', 'kazakhstan': 'KAZ',
    'uzbekistan': 'UZB', 'turkmensitan': 'TKM', 'kyrgyzstan': 'KGZ',
    'tajikistan': 'TJK', 'georgia': 'GEO', 'armenia': 'ARM',
    'azerbaijan': 'AZE', 'ukraine': 'UKR', 'belarus': 'BLR',
    'moldova': 'MDA', 'serbia': 'SRB', 'montenegro': 'MNE',
    'bosnia and herzegovina': 'BIH', 'albania': 'ALB',
    'north macedonia': 'MKD', 'kosovo': 'XKX', 'morocco': 'MAR',
    'tunisia': 'TUN', 'algeria': 'DZA', 'libya': 'LBY',
    'sudan': 'SDN', 'ethiopia': 'ETH', 'kenya': 'KEN',
    'nigeria': 'NGA', 'ghana': 'GHA', 'ivory coast': 'CIV',
    'senegal': 'SEN', 'cameroon': 'CMR', 'tanzania': 'TZA',
    'uganda': 'UGA', 'rwanda': 'RWA', 'zambia': 'ZMB',
    'zimbabwe': 'ZWE', 'botswana': 'BWA', 'namibia': 'NAM',
    'mozambique': 'MOZ', 'angola': 'AGO', 'congo': 'COG',
    'democratic republic of congo': 'COD', 'gabon': 'GAB',
    'equatorial guinea': 'GNQ', 'mauritius': 'MUS', 'seychelles': 'SYC',
    'fiji': 'FJI', 'papua new guinea': 'PNG', 'solomon islands': 'SLB',
    'vanuatu': 'VUT', 'samoa': 'WSM', 'tonga': 'TON',
    'cuba': 'CUB', 'dominican republic': 'DOM', 'haiti': 'HTI',
    'jamaica': 'JAM', 'trinidad and tobago': 'TTO', 'panama': 'PAN',
    'costa rica': 'CRI', 'guatemala': 'GTM', 'honduras': 'HND',
    'nicaragua': 'NIC', 'el salvador': 'SLV', 'belize': 'BLZ',
}

def clean_text(text: str) -> str:
    """Lowercase, strip, collapse spaces, remove punctuation."""
    if not isinstance(text, str):
        return ''
    t = text.lower().strip()
    t = re.sub(r'\s+', ' ', t)
    t = t.strip('.,;:!?()[]{}"\'')
    return t

def map_country_to_code(text: Optional[str]) -> str:
    """Return ISO3 code or 'UNMAPPED' if not found (no crash)."""
    if not text:
        return 'UNMAPPED'
    cleaned = clean_text(text)
    if cleaned in COUNTRY_MAP:
        return COUNTRY_MAP[cleaned]
    tokens = cleaned.split()
    for token in tokens:
        if token in COUNTRY_MAP:
            return COUNTRY_MAP[token]
    for key in COUNTRY_MAP.keys():
        if key in cleaned or cleaned in key:
            return COUNTRY_MAP[key]
    return 'UNMAPPED'

# ---------- SECTOR MAPPING (Expanded for NAG and other sources) ----------
SECTOR_MAP = {
    # ISIC letters (broad)
    'a': 'A', 'agriculture': 'A', 'agri': 'A', 'agriculture forestry and fishing': 'A',
    'b': 'B', 'mining': 'B', 'quarrying': 'B',
    'c': 'C', 'manufacturing': 'C', 'industry': 'C',
    'd': 'D', 'electricity': 'D', 'gas': 'D', 'steam': 'D',
    'e': 'E', 'water supply': 'E', 'sewerage': 'E',
    'f': 'F', 'construction': 'F',
    'g': 'G', 'wholesale': 'G', 'retail': 'G', 'trade': 'G',
    'h': 'H', 'transport': 'H', 'storage': 'H',
    'i': 'I', 'accommodation': 'I', 'food service': 'I',
    'j': 'J', 'information': 'J', 'telecom': 'J', 'communication': 'J',
    'k': 'K', 'financial': 'K', 'insurance': 'K', 'banking': 'K',
    'l': 'L', 'real estate': 'L',
    'm': 'M', 'professional': 'M', 'technical': 'M', 'scientific': 'M',
    'n': 'N', 'administrative': 'N', 'support': 'N',
    'o': 'O', 'public admin': 'O', 'government': 'O',
    'p': 'P', 'education': 'P',
    'q': 'Q', 'health': 'Q', 'social work': 'Q',
    'r': 'R', 'arts': 'R', 'entertainment': 'R', 'recreation': 'R',
    's': 'S', 'other services': 'S', 'services': 'S',
    # Bangladesh specifics (from NAG, ban-key-indicators, etc.)
    'wearing apparel': 'C_APP', 'apparel': 'C_APP', 'garments': 'C_APP',
    'textiles': 'C_TEX',
    'crops': 'A_CROP', 'crops and horticulture': 'A_CROP',
    'livestock': 'A_LIVE', 'animal farmings': 'A_LIVE',
    'fisheries': 'A_FISH', 'fishing': 'A_FISH',
    'forestry': 'A_FOR', 'forest and related services': 'A_FOR',
    'rice': 'A_CROP', 'wheat': 'A_CROP',
    'natural gas and crude petroleum': 'B',
    'other mining and coal': 'B',
    'large industry': 'C', 'small medium and micro industry': 'C', 'cottage industry': 'C',
    'electricity gas steam and air conditioning supply': 'D', 'electricity, gas, steam and air conditioning supply': 'D',
    'water supply sewerage waste management': 'E', 'water supply, sewerage, waste management': 'E',
    'wholesale and retail trade repair of motor vehicles': 'G', 'wholesale and retail trade; repair of motor vehicles': 'G',
    'transportation and storage': 'H', 'land transport': 'H', 'water transport': 'H', 'air transport': 'H',
    'warehousing and support activities': 'H', 'postal and courrier activities': 'H',
    'accomodation and food services activities': 'I', 'accommodation and food service activities': 'I',
    'information and communication': 'J',
    'financial and insurance activities': 'K', 'monetary intermediation (banks)': 'K', 'insurance': 'K',
    'other financial auxillaries': 'K',
    'real estate activities': 'L',
    'professional scientific and technical activities': 'M',
    'administrative and support service activities': 'N',
    'public administration and defense compulsory': 'O', 'public administration and defense; compulsory': 'O',
    'human health and social work activities': 'Q',
    'arts entertainment and recreation': 'R', 'arts, entertainment and recreation': 'R',
    'other service activities': 'S',
    # Total/aggregate placeholders (we'll map to 'TOTAL' but decide later)
    'total gva at current basic price': 'TOTAL',
    'total gva at constant basic price': 'TOTAL',
    'gdp at current market prices': 'TOTAL',
    'gdp at constant market prices': 'TOTAL',
}

def map_sector_code(text: Optional[str]) -> str:
    """Return canonical sector code or 'UNMAPPED'."""
    if not text:
        return 'UNMAPPED'
    cleaned = clean_text(text)
    if cleaned in SECTOR_MAP:
        return SECTOR_MAP[cleaned]
    if cleaned.upper() in SECTOR_MAP:
        return SECTOR_MAP[cleaned.upper()]
    # Try token matching
    tokens = cleaned.split()
    for token in tokens:
        if token in SECTOR_MAP:
            return SECTOR_MAP[token]
        if token.upper() in SECTOR_MAP:
            return SECTOR_MAP[token.upper()]
    # Try substring matching (e.g., "crops" appears in "Crops and Horticulture")
    for key in SECTOR_MAP.keys():
        if key in cleaned or cleaned in key:
            return SECTOR_MAP[key]
    return 'UNMAPPED'

# ---------- ADMIN MAPPING (Divisions, districts, etc.) ----------
ADMIN_MAP = {
    'dhaka': 'BD-A', 'dhaka division': 'BD-A',
    'chattagram': 'BD-B', 'chittagong': 'BD-B', 'chattagram division': 'BD-B',
    'barishal': 'BD-C', 'barisal': 'BD-C', 'barishal division': 'BD-C',
    'khulna': 'BD-D', 'khulna division': 'BD-D',
    'rajshahi': 'BD-E', 'rajshahi division': 'BD-E',
    'rangpur': 'BD-F', 'rangpur division': 'BD-F',
    'mymensingh': 'BD-G', 'myensingh': 'BD-G', 'mymensingh division': 'BD-G',
    'sylhet': 'BD-H', 'sylhet division': 'BD-H',
    'bangladesh': 'BD-00', 'national': 'BD-00', 'bd': 'BD-00',
    'dhaka district': 'BD-A-1', 'gazipur': 'BD-A-2',
    'chittagong district': 'BD-B-1', 'cox\'s bazar': 'BD-B-2',
}

def map_admin_to_pcode(text: Optional[str]) -> str:
    """Return admin pcode or 'UNMAPPED'."""
    if not text:
        return 'UNMAPPED'
    cleaned = clean_text(text)
    if cleaned in ADMIN_MAP:
        return ADMIN_MAP[cleaned]
    simplified = re.sub(r'\b(division|district|zila|upazila|thana)\b', '', cleaned).strip()
    if simplified in ADMIN_MAP:
        return ADMIN_MAP[simplified]
    return 'UNMAPPED'

# ---------- GENDER MAPPING ----------
GENDER_MAP = {
    'male': 'Male', 'm': 'Male', 'men': 'Male', 'boy': 'Male', 'boys': 'Male',
    'female': 'Female', 'f': 'Female', 'women': 'Female', 'girl': 'Female', 'girls': 'Female',
    'hijra': 'Hijra', 'hijras': 'Hijra', 'transgender': 'Hijra',
    'total': 'Total', 'both': 'Total', 'all': 'Total',
}

def map_gender(text: Optional[str]) -> str:
    """Return canonical gender, default to 'Total' if unknown."""
    if not text:
        return 'Total'
    cleaned = clean_text(text)
    if cleaned in GENDER_MAP:
        return GENDER_MAP[cleaned]
    tokens = cleaned.split()
    if tokens and tokens[0] in GENDER_MAP:
        return GENDER_MAP[tokens[0]]
    return 'Total'  # fallback

# ---------- VACCINE MAPPING ----------
VACCINE_MAP = {
    'bcg': 'BCG', 'bacillus calmette guerin': 'BCG',
    'dtp': 'DTP3', 'dtp1': 'DTP1', 'dtp3': 'DTP3',
    'diphtheria tetanus pertussis': 'DTP3',
    'polio': 'Pol3', 'pol3': 'Pol3', 'ipv': 'IPV1', 'ipv1': 'IPV1',
    'mcv': 'MCV1', 'mcv1': 'MCV1', 'mcv2': 'MCV2', 'measles': 'MCV1',
    'rcv': 'RCV1', 'rcv1': 'RCV1', 'rubella': 'RCV1',
    'hepb': 'HepB3', 'hepb3': 'HepB3', 'hepatitis b': 'HepB3',
    'hib': 'Hib3', 'hib3': 'Hib3', 'haemophilus influenzae': 'Hib3',
    'rota': 'RotaC', 'rotac': 'RotaC', 'rotavirus': 'RotaC',
    'pcv': 'PcV3', 'pcv3': 'PcV3', 'pneumococcal': 'PcV3',
    'yfv': 'YFV', 'yellow fever': 'YFV',
}

def map_vaccine_code(text: Optional[str]) -> str:
    """Return canonical vaccine code or 'UNMAPPED'."""
    if not text:
        return 'UNMAPPED'
    cleaned = clean_text(text)
    if cleaned in VACCINE_MAP:
        return VACCINE_MAP[cleaned]
    if cleaned.upper() in ['BCG', 'DTP1', 'DTP3', 'POL3', 'IPV1', 'MCV1', 'MCV2', 'RCV1', 'HEPB3', 'HIB3', 'ROTAC', 'PCV3', 'YFV']:
        return cleaned.upper()
    return 'UNMAPPED'

# ---------- FISCAL YEAR PARSER (Robust) ----------
def parse_fiscal_year(text, return_start_year=True):
    """
    Convert any string containing a 4-digit year (e.g., 'FY2007', '2007-08', '2007') to int.
    Safe with NaN, None, floats.
    """
    if text is None:
        return 0
    if isinstance(text, (int, float)):
        if pd.isna(text):
            return 0
        return int(text)
    if not isinstance(text, str):
        return 0

    # Remove 'FY' prefix and any non‑digit/hyphen characters
    cleaned = re.sub(r'[^0-9\-]', '', text)  # keep only digits and hyphens
    # Find all 4‑digit numbers (years)
    years = re.findall(r'\b(19|20)\d{2}\b', cleaned)
    if years:
        start = int(years[0])
        end = int(years[-1]) if len(years) > 1 else start + 1
        return start if return_start_year else end

    # Fallback: if any numbers exist, take the first as start
    nums = re.findall(r'\d+', cleaned)
    if nums:
        start = int(nums[0])
        return start if return_start_year else start + 1

    return 0

# ---------- DHS SURVEY TYPE ----------
DHS_SURVEY_TYPE_MAP = {
    'dhs': 'DHS', 'demographic and health survey': 'DHS',
    'mics': 'MICS', 'multiple indicator cluster survey': 'MICS',
    'ces': 'CES', 'coverage evaluation survey': 'CES',
    'epi': 'EPI', 'uesds': 'UESDS',
    'utilization of essential service delivery survey': 'UESDS',
    'nce': 'NCE', 'national coverage evaluation': 'NCE',
}

def get_dhs_survey_type(text: Optional[str]) -> str:
    if not text:
        return 'UNKNOWN'
    cleaned = clean_text(text)
    for key, val in DHS_SURVEY_TYPE_MAP.items():
        if key in cleaned:
            return val
    return 'OTHER'

# ---------- DOMAIN ----------
DOMAINS = {'economic', 'demographic', 'health', 'education', 'environment', 'agriculture',
           'infrastructure', 'government', 'financial', 'technology', 'business',
           'poverty', 'external', 'gender'}

def get_domain(text: Optional[str]) -> str:
    if not text:
        return 'OTHER'
    cleaned = clean_text(text)
    for domain in DOMAINS:
        if domain in cleaned:
            return domain.title()
    if cleaned in DOMAINS:
        return cleaned.title()
    return cleaned.title()

# ---------- SANITY CHECK ----------
def run_sanity_checks():
    print("Running mapping_dicts.py sanity checks...")
    assert map_country_to_code("Bangladesh") == "BGD"
    assert map_sector_code("Manufacturing") == "C"
    assert map_sector_code("Crops and Horticulture") == "A_CROP"
    assert map_sector_code("Wholesale and Retail Trade; repair of motor vehicles") == "G"
    assert map_admin_to_pcode("Dhaka Division") == "BD-A"
    assert map_gender("M") == "Male"
    assert parse_fiscal_year("2023-24") == 2023
    assert parse_fiscal_year("FY2007") == 2007
    assert parse_fiscal_year(float('nan')) == 0
    assert map_vaccine_code("bcg") == "BCG"
    print("✅ All sanity checks passed.")

if __name__ == "__main__":
    run_sanity_checks()
