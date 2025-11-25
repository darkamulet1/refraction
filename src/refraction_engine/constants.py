"""
Constants for Refraction Engine extractors

This module provides canonical constants for:
- Planet indices (PyJHora standard order)
- House classifications (Kendra, Trikona, Dusthana, etc.)
- Severity levels for doshas
- Allowed languages

Usage:
    from .constants import PLANET_INDICES, KENDRA_HOUSES
    
    mars_idx = PLANET_INDICES['MARS']
    is_kendra = house_num in KENDRA_HOUSES
"""

# =============================================================================
# PLANET INDICES (PyJHora Standard Order)
# =============================================================================

PLANET_INDICES = {
    'SUN': 0,
    'MOON': 1,
    'MARS': 2,
    'MERCURY': 3,
    'JUPITER': 4,
    'VENUS': 5,
    'SATURN': 6,
    'RAHU': 7,
    'KETU': 8,
}

# Reverse mapping: index -> planet name
PLANET_NAMES = [
    'SUN',
    'MOON', 
    'MARS',
    'MERCURY',
    'JUPITER',
    'VENUS',
    'SATURN',
    'RAHU',
    'KETU',
]

# Alternative names for lookups
PLANET_ALIASES = {
    'RAGU': 'RAHU',
    'RAAHU': 'RAHU',
    'KETHU': 'KETU',
    'LAGNA': 'ASCENDANT',
    'ASC': 'ASCENDANT',
}

# =============================================================================
# HOUSE CLASSIFICATIONS
# =============================================================================

# Kendra (Angular) Houses - Houses of strength and stability
# 1st: Self, 4th: Home, 7th: Partnership, 10th: Career
KENDRA_HOUSES = [1, 4, 7, 10]

# Trikona (Trinal) Houses - Houses of fortune and dharma
# 1st: Self, 5th: Creativity, 9th: Fortune
TRIKONA_HOUSES = [1, 5, 9]

# Dusthana (Malefic) Houses - Difficult houses
# 6th: Disease/Enemies, 8th: Obstacles, 12th: Loss/Liberation
DUSTHANA_HOUSES = [6, 8, 12]

# Upachaya (Growth) Houses - Houses that improve with time
# 3rd: Effort, 6th: Service, 10th: Career, 11th: Gains
UPACHAYA_HOUSES = [3, 6, 10, 11]

# Manglik (Mars) Houses - Houses that trigger Manglik dosha
# Mars in these houses from Lagna can create marital difficulties
MANGLIK_HOUSES = [1, 2, 4, 7, 8, 12]

# Maraka Houses - Death-inflicting houses
# 2nd and 7th houses are considered maraka (death-dealing) houses
MARAKA_HOUSES = [2, 7]

# =============================================================================
# SIGN CLASSIFICATIONS
# =============================================================================

# Movable (Chara) Signs
MOVABLE_SIGNS = [0, 3, 6, 9]  # Aries, Cancer, Libra, Capricorn

# Fixed (Sthira) Signs
FIXED_SIGNS = [1, 4, 7, 10]  # Taurus, Leo, Scorpio, Aquarius

# Dual (Dwiswabhava) Signs
DUAL_SIGNS = [2, 5, 8, 11]  # Gemini, Virgo, Sagittarius, Pisces

# =============================================================================
# PLANETARY CLASSIFICATIONS
# =============================================================================

# Natural Benefics - Planets that generally give good results
NATURAL_BENEFICS = ['JUPITER', 'VENUS', 'MERCURY', 'MOON']

# Natural Malefics - Planets that can give challenging results
NATURAL_MALEFICS = ['MARS', 'SATURN', 'RAHU', 'KETU', 'SUN']

# Note: Moon is benefic when waxing, Mercury when not combust

# =============================================================================
# SEVERITY LEVELS (for Doshas and Afflictions)
# =============================================================================

SEVERITY_SEVERE = "SEVERE"
SEVERITY_HIGH = "HIGH"
SEVERITY_MODERATE = "MODERATE"
SEVERITY_MILD = "MILD"
SEVERITY_NONE = "NONE"

# Severity ordering (higher index = more severe)
SEVERITY_LEVELS = [
    SEVERITY_NONE,
    SEVERITY_MILD,
    SEVERITY_MODERATE,
    SEVERITY_HIGH,
    SEVERITY_SEVERE,
]

# =============================================================================
# YOGA STRENGTH CLASSIFICATIONS
# =============================================================================

STRENGTH_STRONG = "STRONG"
STRENGTH_MODERATE = "MODERATE"
STRENGTH_WEAK = "WEAK"

# =============================================================================
# YOGA CATEGORIES
# =============================================================================

CATEGORY_PANCHA_MAHAPURUSHA = "PANCHA_MAHAPURUSHA"
CATEGORY_RAJA = "RAJA"
CATEGORY_DHANA = "WEALTH"
CATEGORY_DOSHA = "DOSHA"
CATEGORY_CHANDRA = "CHANDRA"
CATEGORY_SURYA = "SURYA"
CATEGORY_NABHASA = "NABHASA"
CATEGORY_SPECIAL = "SPECIAL"
CATEGORY_OTHER = "OTHER"

# All valid yoga categories (for validation)
YOGA_CATEGORIES = [
    CATEGORY_PANCHA_MAHAPURUSHA,
    CATEGORY_RAJA,
    CATEGORY_DHANA,
    CATEGORY_DOSHA,
    CATEGORY_CHANDRA,
    CATEGORY_SURYA,
    CATEGORY_NABHASA,
    CATEGORY_SPECIAL,
    CATEGORY_OTHER,
]

# Set version for quick membership checks
YOGA_CATEGORIES_SET = {
    "PANCHA_MAHAPURUSHA",
    "RAJA",
    "WEALTH",
    "DOSHA",
    "CHANDRA",
    "SURYA",
    "NABHASA",
    "SPECIAL",
    "OTHER",
}

# =============================================================================
# YOGA STRENGTH & SCORING
# =============================================================================

# Strength points for yoga scoring
STRENGTH_POINTS = {
    "STRONG": 10,
    "MODERATE": 5,
    "WEAK": 2,
}

# Malefic penalty in strength calculation
MALEFIC_PENALTY = 8

# =============================================================================
# PANCHA MAHAPURUSHA YOGA DEFINITIONS
# =============================================================================

# (Planet, Yoga Name, Own Signs, Exaltation Signs)
PANCHA_MAHAPURUSHA_DEFINITIONS = [
    ("MARS", "RUCHAKA_YOGA", {"ARIES", "SCORPIO"}, {"CAPRICORN"}),
    ("MERCURY", "BHADRA_YOGA", {"GEMINI", "VIRGO"}, {"VIRGO"}),
    ("JUPITER", "HAMSA_YOGA", {"SAGITTARIUS", "PISCES"}, {"CANCER"}),
    ("VENUS", "MALAVYA_YOGA", {"TAURUS", "LIBRA"}, {"PISCES"}),
    ("SATURN", "SASA_YOGA", {"CAPRICORN", "AQUARIUS"}, {"LIBRA"}),
]

# =============================================================================
# DHANA YOGA DEFINITIONS
# =============================================================================

# Signs that favor wealth yogas for specific planets
DHANA_FAVORABLE_SIGNS = {
    "VENUS": {"TAURUS", "LIBRA", "PISCES"},
    "JUPITER": {"SAGITTARIUS", "PISCES", "CANCER"},
}

# All benefic dignity signs for wealth
ALL_WEALTH_SIGNS = {"TAURUS", "LIBRA", "PISCES", "SAGITTARIUS", "CANCER"}

# =============================================================================
# LANGUAGE SUPPORT
# =============================================================================

# Supported languages in PyJHora
ALLOWED_LANGUAGES = {"en", "ta", "te", "hi", "kn", "ml", "sa"}

# Default language
DEFAULT_LANGUAGE = "en"

# =============================================================================
# DIGNITY CLASSIFICATIONS
# =============================================================================

# Exaltation signs for each planet
EXALTATION_SIGNS = {
    'SUN': 0,       # Aries
    'MOON': 1,      # Taurus
    'MARS': 9,      # Capricorn
    'MERCURY': 5,   # Virgo
    'JUPITER': 3,   # Cancer
    'VENUS': 11,    # Pisces
    'SATURN': 6,    # Libra
}

# Debilitation signs (opposite of exaltation)
DEBILITATION_SIGNS = {
    'SUN': 6,       # Libra
    'MOON': 7,      # Scorpio
    'MARS': 3,      # Cancer
    'MERCURY': 11,  # Pisces
    'JUPITER': 9,   # Capricorn
    'VENUS': 5,     # Virgo
    'SATURN': 0,    # Aries
}

# Own signs for each planet
OWN_SIGNS = {
    'SUN': [4],           # Leo
    'MOON': [3],          # Cancer
    'MARS': [0, 7],       # Aries, Scorpio
    'MERCURY': [2, 5],    # Gemini, Virgo
    'JUPITER': [8, 11],   # Sagittarius, Pisces
    'VENUS': [1, 6],      # Taurus, Libra
    'SATURN': [9, 10],    # Capricorn, Aquarius
}

# =============================================================================
# NAKSHATRA CLASSIFICATIONS
# =============================================================================

# Gandanta (Junction) Nakshatras - Critical transition points
GANDANTA_NAKSHATRAS = [
    0,   # Ashwini (end pada)
    8,   # Ashlesha (end pada)
    17,  # Jyeshtha (end pada)
    18,  # Mula (start pada)
    26,  # Revati (end pada)
]

# Ganda Moola Nakshatras - Inauspicious for birth
GANDA_MOOLA_NAKSHATRAS = [0, 8, 17, 18, 26]

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Valid range for signs/rasis (0-11 for 12 signs)
MIN_SIGN_INDEX = 0
MAX_SIGN_INDEX = 11

# Valid range for houses (1-12 for 12 houses)
MIN_HOUSE_NUMBER = 1
MAX_HOUSE_NUMBER = 12

# Valid range for degrees in a sign (0-30)
MIN_DEGREE = 0.0
MAX_DEGREE = 30.0

# Valid range for nakshatra indices (0-26 for 27 nakshatras)
MIN_NAKSHATRA_INDEX = 0
MAX_NAKSHATRA_INDEX = 26

# Minimum expected planets in a chart
MIN_PLANETS = 9  # Sun through Ketu

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Planet mappings
    'PLANET_INDICES',
    'PLANET_NAMES',
    'PLANET_ALIASES',
    
    # House classifications
    'KENDRA_HOUSES',
    'TRIKONA_HOUSES',
    'DUSTHANA_HOUSES',
    'UPACHAYA_HOUSES',
    'MANGLIK_HOUSES',
    'MARAKA_HOUSES',
    
    # Sign classifications
    'MOVABLE_SIGNS',
    'FIXED_SIGNS',
    'DUAL_SIGNS',
    
    # Planet classifications
    'NATURAL_BENEFICS',
    'NATURAL_MALEFICS',
    
    # Severity levels
    'SEVERITY_SEVERE',
    'SEVERITY_HIGH',
    'SEVERITY_MODERATE',
    'SEVERITY_MILD',
    'SEVERITY_NONE',
    'SEVERITY_LEVELS',
    
    # Strength levels
    'STRENGTH_STRONG',
    'STRENGTH_MODERATE',
    'STRENGTH_WEAK',
    
    # Yoga categories
    'YOGA_CATEGORIES',
    'YOGA_CATEGORIES_SET',
    'CATEGORY_PANCHA_MAHAPURUSHA',
    'CATEGORY_RAJA',
    'CATEGORY_DHANA',
    'CATEGORY_DOSHA',
    'CATEGORY_CHANDRA',
    'CATEGORY_SURYA',
    'CATEGORY_NABHASA',
    'CATEGORY_SPECIAL',
    'CATEGORY_OTHER',
    
    # Yoga strength & scoring
    'STRENGTH_POINTS',
    'MALEFIC_PENALTY',
    
    # Pancha Mahapurusha
    'PANCHA_MAHAPURUSHA_DEFINITIONS',
    
    # Dhana yogas
    'DHANA_FAVORABLE_SIGNS',
    'ALL_WEALTH_SIGNS',
    
    # Languages
    'ALLOWED_LANGUAGES',
    'DEFAULT_LANGUAGE',
    
    # Dignity
    'EXALTATION_SIGNS',
    'DEBILITATION_SIGNS',
    'OWN_SIGNS',
    
    # Nakshatras
    'GANDANTA_NAKSHATRAS',
    'GANDA_MOOLA_NAKSHATRAS',
    
    # Validation
    'MIN_SIGN_INDEX',
    'MAX_SIGN_INDEX',
    'MIN_HOUSE_NUMBER',
    'MAX_HOUSE_NUMBER',
    'MIN_DEGREE',
    'MAX_DEGREE',
    'MIN_NAKSHATRA_INDEX',
    'MAX_NAKSHATRA_INDEX',
    'MIN_PLANETS',
]
