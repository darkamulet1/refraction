# ⚙️ PYJHORA CONFIGURATION OPTIONS

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

Complete guide to all configuration options, constants, and system settings in PyJHora.

---

## 1. AYANAMSA MODES (21+ Options)

```python
# Primary Ayanamsa Systems
drik.set_ayanamsa_mode('LAHIRI')          # Lahiri/Chitrapaksha (default in India)
drik.set_ayanamsa_mode('RAMAN')           # B.V. Raman
drik.set_ayanamsa_mode('KP')              # Krishnamurti Paddhati
drik.set_ayanamsa_mode('TRUE_CITRA')      # True Chitra Paksha (Spica at 180°)
drik.set_ayanamsa_mode('TRUE_REVATI')     # True Revati (zeta Piscium at 359°50')
drik.set_ayanamsa_mode('YUKTESHWAR')      # Swami Sri Yukteswar
drik.set_ayanamsa_mode('SURYASIDDHANTA')  # Surya Siddhanta (ancient)

# Additional Options
'FAGAN_BRADLEY', 'DELUCE', 'SASSANIAN', 'USHASHASHI', 'TRUE_MULA', 
'TRUE_PUSHYA', 'GALACTIC_CENTER_0SAG', etc.

# Custom Ayanamsa
drik.set_ayanamsa_mode('LAHIRI', ayanamsa_value=24.0, jd=2451545.0)
```

---

## 2. HOUSE SYSTEMS (17 Options)

### Indian Systems (5)
```python
const.available_house_systems = {
    'EQUAL': 'Equal House (default)',
    'WHOLE_SIGN': 'Whole Sign Houses',
    'SRIPATHI': 'Sripathi',
    'KP': 'Krishnamurti Paddhati',
    'BHAVA': 'Bhava Madhya'
}
```

### Western Systems (12)
```python
'PLACIDUS', 'KOCH', 'REGIOMONTANUS', 'CAMPANUS', 
'PORPHYRY', 'MORINUS', 'TOPOCENTRIC', 'ALCABITIUS',
'MERIDIAN', 'VEHLOW_EQUAL', 'AXIAL_ROTATION', 'HORIZONTAL'
```

**Usage**:
```python
h.get_bhava_chart_information(jd, place, bhaava_madhya_method='EQUAL')
```

---

## 3. CALCULATION TYPES (2)

```python
# Swiss Ephemeris (High Accuracy)
Horoscope(..., calculation_type='drik')

# Surya Siddhanta (Ancient Vedic)
Horoscope(..., calculation_type='ss')
```

---

## 4. CHART CALCULATION METHODS

### Standard Methods
```python
chart_method = 1  # Parasara (default)
chart_method = 2  # Sripathi
chart_method = 3  # Krishnamurti Paddhati (KP)
chart_method = 4  # Jagannatha
chart_method = 5  # Other variations
```

### Method-Specific Parameters
```python
# Custom varga with base rasi
charts.divisional_chart(
    jd, place, 
    divisional_chart_factor=17,
    chart_method=1,
    base_rasi=True,              # Start from sign itself
    count_from_end_of_sign=False # Count from beginning
)
```

---

## 5. DIVISIONAL CHART FACTORS

### Standard Shodasavarga (16 Charts)
```python
const.shodasavarga_charts = [1, 2, 3, 9, 12, 30, 16, 24, 4, 7, 10, 40, 45, 60, 27, 20]
```

### Dasavarga (10 Charts)
```python
const.dasavarga_charts = [1, 2, 3, 7, 9, 12, 30, 16, 24, 40]
```

### Shadvarga (6 Charts)
```python
const.shadvarga_charts = [1, 2, 3, 9, 12, 30]
```

### All Available Factors
```python
# D1-D300 all supported
const.all_division_chart_factors = list(range(1, 301))

# Common charts
D1=1    # Rasi
D2=2    # Hora
D3=3    # Drekkana
D4=4    # Chaturthamsa
D7=7    # Saptamsa
D9=9    # Navamsa (most important)
D10=10  # Dasamsa
D12=12  # Dwadasamsa
D16=16  # Shodasamsa
D20=20  # Vimsamsa
D24=24  # Chaturvimsamsa
D27=27  # Saptavimsamsa
D30=30  # Trimsamsa
D40=40  # Khavedamsa
D45=45  # Akshavedamsa
D60=60  # Shashtiamsa
D81=81  # Navanavamsa
D108=108 # Ashtottaramsa
D144=144 # Dwadas-dwadasamsa
D150=150 # Nadi amsa
D300=300 # Special analysis
```

---

## 6. LANGUAGE SUPPORT (6 Languages)

```python
# Set language
utils.set_language('en')  # English (default)
utils.set_language('ta')  # Tamil
utils.set_language('te')  # Telugu
utils.set_language('hi')  # Hindi
utils.set_language('ka')  # Kannada
utils.set_language('ml')  # Malayalam

# Affects:
# - Planet names (utils.PLANET_NAMES)
# - Raasi names (utils.RAASI_LIST)
# - Nakshatra names (utils.NAKSHATRA_LIST)
# - UI labels
# - Yoga/Dosha descriptions
```

---

## 7. DASHA SYSTEMS (46 Total)

### Graha (Planetary) Dashas (22)
```python
# Parasara Dashas
'VIMSOTTARI'      # 120 years (most common)
'ASHTOTTARI'      # 108 years
'YOGINI'          # 36 years
'SHODASOTTARI'    # 116 years
'DWISAPTATI_SAMA' # 72 years
'SATABDIKA'       # 100 years
'CHATURASITHI_SAMA' # 84 years
'DWADASOTTARI'    # 112 years
'PANCHOTTARI'     # 105 years
'SHASHTIHAYANI'   # 60 years

# Jaimini Dashas (Rasi-based)
'NARAYANA'
'PADHANADHI'
'MANDOOKA'
'STHIRA'
'CHARA'
'KENDRAADI'
'NIRAYANA_SHOOLA'
'SUDASA'
'BRAHMA'
'LAGNA_KENDRADI'
'NAISARGIKA'      # Fixed periods
'KALACHAKRA'
```

### Annual Dashas (2)
```python
'VARSHA_VIMSOTTARI'  # Annual Vimsottari
'MUDDA'              # Tajaka annual dasha
```

---

## 8. PRAVESHA (RETURN CHART) TYPES

```python
pravesha_type = 0  # Janma (Natal)
pravesha_type = 1  # Varsha Pravesha (Solar Return)
pravesha_type = 2  # Tithi Pravesha (Lunar Return)
pravesha_type = 3  # Lunar Month Return
pravesha_type = 4  # 60-Hour Return
```

---

## 9. EPHEMERIS PATH CONFIGURATION

```python
# Set custom ephemeris data path
utils.set_ephemeris_data_path('/path/to/ephe/data/')

# Default path (auto-detected)
const._ephe_path = './ephe/'
```

---

## 10. WORLD CITIES DATABASE

```python
# Enable database for faster lookups
utils.use_database_for_world_cities(enable_database=True)

# Database file
const._world_city_csv_file = './data/world_cities_db.csv'

# Add new location to database
utils.save_location_to_database(['Country', 'City', lat, lon, 'TZ_String', tz_offset])
```

---

## 11. PLANET CONSTANTS

### Planet Relationships
```python
# Friends, Enemies, Neutrals for each planet
const.planet_relations = {
    0: {  # Sun
        'friends': [1, 2, 4],
        'enemies': [5, 6],
        'neutral': [3]
    },
    # ... for all 9 planets
}
```

### Exaltation/Debilitation
```python
const.exalted_planets = {
    0: (0, 10),   # Sun exalted in Aries at 10°
    1: (1, 3),    # Moon exalted in Taurus at 3°
    2: (9, 28),   # Mars exalted in Capricorn at 28°
    3: (5, 15),   # Mercury exalted in Virgo at 15°
    4: (3, 5),    # Jupiter exalted in Cancer at 5°
    5: (11, 27),  # Venus exalted in Pisces at 27°
    6: (6, 20)    # Saturn exalted in Libra at 20°
}

const.debilitated_planets = {
    # Opposite signs, opposite degrees
}
```

### Own Signs (Rulership)
```python
const.own_signs = {
    0: [4],        # Sun: Leo
    1: [3],        # Moon: Cancer
    2: [0, 7],     # Mars: Aries, Scorpio
    3: [2, 5],     # Mercury: Gemini, Virgo
    4: [8, 11],    # Jupiter: Sagittarius, Pisces
    5: [1, 6],     # Venus: Taurus, Libra
    6: [9, 10]     # Saturn: Capricorn, Aquarius
}
```

### Moolatrikona Signs
```python
const.moolatrikona_signs = {
    0: (4, 0, 20),    # Sun: Leo 0-20°
    1: (1, 3, 27),    # Moon: Taurus 3-27°
    2: (0, 0, 12),    # Mars: Aries 0-12°
    3: (5, 16, 20),   # Mercury: Virgo 16-20°
    4: (8, 0, 10),    # Jupiter: Sagittarius 0-10°
    5: (6, 0, 15),    # Venus: Libra 0-15°
    6: (10, 0, 20)    # Saturn: Aquarius 0-20°
}
```

### Deeptamsa (Deep Exaltation Range)
```python
const.deeptaamsa_of_planets = {
    0: 10.0,  # Sun ±10° from exaltation point
    1: 3.0,   # Moon ±3°
    2: 5.0,   # Mars ±5°
    3: 4.0,   # Mercury ±4°
    4: 5.0,   # Jupiter ±5°
    5: 5.0,   # Venus ±5°
    6: 3.0    # Saturn ±3°
}
```

---

## 12. SIGN CONSTANTS

### Sign Categories
```python
const.odd_signs = [0, 2, 4, 6, 8, 10]      # Aries, Gemini, Leo, ...
const.even_signs = [1, 3, 5, 7, 9, 11]     # Taurus, Cancer, Virgo, ...

const.movable_signs = [0, 3, 6, 9]         # Chara: Aries, Cancer, Libra, Capricorn
const.fixed_signs = [1, 4, 7, 10]          # Sthira: Taurus, Leo, Scorpio, Aquarius
const.dual_signs = [2, 5, 8, 11]           # Dwi: Gemini, Virgo, Sagittarius, Pisces

const.fire_signs = [0, 4, 8]               # Aries, Leo, Sagittarius
const.earth_signs = [1, 5, 9]              # Taurus, Virgo, Capricorn
const.air_signs = [2, 6, 10]               # Gemini, Libra, Aquarius
const.water_signs = [3, 7, 11]             # Cancer, Scorpio, Pisces
```

---

## 13. NAKSHATRA LORDS
```python
const.nakshatra_lords = [
    8,  # Ashwini: Ketu
    5,  # Bharani: Venus
    0,  # Krittika: Sun
    1,  # Rohini: Moon
    2,  # Mrigashira: Mars
    7,  # Ardra: Rahu
    4,  # Punarvasu: Jupiter
    6,  # Pushya: Saturn
    3,  # Ashlesha: Mercury
    # ... 27 total
]
```

---

## 14. KARANA LORDS
```python
const.karana_lords = {
    0: ([0, 1], 'Bava'),      # Karana 0, 1: Lord + Name
    1: ([2, 3], 'Balava'),
    2: ([4, 5], 'Kaulava'),
    3: ([6, 7], 'Taitila'),
    4: ([8, 9], 'Garija'),
    5: ([10, 11], 'Vanija'),
    6: ([12, 13], 'Vishti'),
    7: ([57], 'Shakuni'),     # Fixed karanas
    8: ([58], 'Chatushpada'),
    9: ([59], 'Naga'),
    10: ([0], 'Kimstughna')
}
```

---

## 15. KP SYSTEM CONFIGURATION

### Sub-Lord Table (249 Sub-divisions)
```python
const.prasna_kp_249_dict = {
    kp_no: [raasi, nakshatra, start_deg, end_deg, raasi_lord, star_lord, sub_lord],
    # ... 249 entries
}
```

---

## 16. TIME-RELATED CONSTANTS

```python
const.sidereal_year = 365.25636  # Days in sidereal year
const.tropical_year = 365.24219  # Days in tropical year
const.lunar_month = 29.530588    # Days in synodic month
```

---

## 17. ANGLE/DMS DISPLAY OPTIONS

```python
# Use 24-hour format for time display
const.use_24hour_format_in_to_dms = True  # or False

# Degree/Minute/Second symbols
const._degree_symbol = '°'
const._minute_symbol = "'"
const._second_symbol = '"'

# Lagna symbol
const._ascendant_symbol = 'L'
```

---

## 18. RESOURCE FILE PATHS

```python
# Language resources
const._LANGUAGE_PATH = './lang/'
const._DEFAULT_LANGUAGE = 'en'
const._DEFAULT_LANGUAGE_LIST_STR = 'list_values_'
const._DEFAULT_LANGUAGE_MSG_STR = 'msg_strings_'

# JSON resources
const._AMSA_RULERS_JSON = 'lang/amsa_rulers_{lang}.json'
const._YOGA_MSGS_JSON = 'lang/yoga_msgs_{lang}.json'
const._DOSHA_MSGS_JSON = 'lang/dosha_msgs_{lang}.json'
const._RAJA_YOGA_MSGS_JSON = 'lang/raja_yoga_msgs_{lang}.json'
const._PREDICTION_MSGS_JSON = 'lang/prediction_msgs_{lang}.json'
```

---

## 19. CHART DISPLAY OPTIONS

```python
# Chart types
const.chart_types = ['south_indian', 'north_indian', 'east_indian', 'western']

# Default chart style
const.default_chart_style = 'south_indian'
```

---

## 20. COMPATIBILITY OPTIONS

```python
# Ashtakuta maximum points
const.ashtakuta_max = {
    'varna': 1,
    'vashya': 2,
    'tara': 3,
    'yoni': 4,
    'graha_maitri': 5,
    'gana': 6,
    'rasi': 7,
    'nadi': 8,
    'total': 36
}

# Minimum passing score
const.ashtakuta_minimum_pass = 18
```

---

**END OF CONFIGURATION OPTIONS**
