# 📐 PYJHORA DATA STRUCTURES

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

This document describes all data structures, input/output formats, and data transformations in PyJHora.

---

## 1. CORE DATA STRUCTURES

### 1.1 Date Structure
```python
from jhora.panchanga import drik

# Definition
Date = namedtuple('Date', ['year', 'month', 'day'])

# Creation
date = drik.Date(1985, 6, 9)
date = drik.Date(-3114, 1, 1)  # BCE dates use negative year

# Access
year = date.year    # 1985
month = date.month  # 6
day = date.day      # 9

# Conversion to tuple
date_tuple = (date.year, date.month, date.day)
```

### 1.2 Place Structure
```python
# Definition
Place = namedtuple('Place', ['name', 'latitude', 'longitude', 'timezone'])

# Creation
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Access
name = place.name              # 'Chennai'
lat = place.latitude           # 13.0827
lon = place.longitude          # 80.2707
tz = place.timezone            # 5.5
```

### 1.3 Planet Positions

**Format**: List of tuples
```python
planet_positions = [
    (planet_id, (raasi_index, longitude_in_raasi)),
    ...
]

# Example
planet_positions = [
    (0, (0, 25.678)),   # Sun in Aries at 25.678°
    (1, (3, 12.456)),   # Moon in Cancer at 12.456°
    (2, (7, 8.234)),    # Mars in Scorpio at 8.234°
    (3, (0, 18.912)),   # Mercury in Aries at 18.912°
    (4, (10, 22.567)),  # Jupiter in Aquarius at 22.567°
    (5, (1, 5.789)),    # Venus in Taurus at 5.789°
    (6, (6, 15.234)),   # Saturn in Libra at 15.234°
    (7, (8, 3.456)),    # Rahu in Sagittarius at 3.456°
    (8, (2, 3.456))     # Ketu in Gemini at 3.456°
]
```

### 1.4 House-to-Planet List

**Format**: List of 12 strings (one per raasi/house)
```python
house_to_planet_list = [
    '',          # Aries: Empty
    '0',         # Taurus: Sun
    '1/2',       # Gemini: Moon and Mars
    '',          # Cancer: Empty
    '',          # Leo: Empty
    'L/3',       # Virgo: Lagna and Mercury
    '',          # Libra: Empty
    '4',         # Scorpio: Jupiter
    '5',         # Sagittarius: Venus
    '',          # Capricorn: Empty
    '6',         # Aquarius: Saturn
    '7/8'        # Pisces: Rahu and Ketu
]

# Separator is '/' for multiple planets
# 'L' represents Lagna (Ascendant)
```

### 1.5 Planet-to-House Dictionary

**Format**: Dictionary mapping planet IDs to house indices (0-11)
```python
planet_to_house_dict = {
    0: 1,    # Sun in 2nd house (Taurus)
    1: 2,    # Moon in 3rd house (Gemini)
    2: 2,    # Mars in 3rd house (Gemini)
    3: 5,    # Mercury in 6th house (Virgo)
    4: 7,    # Jupiter in 8th house (Scorpio)
    5: 8,    # Venus in 9th house (Sagittarius)
    6: 10,   # Saturn in 11th house (Aquarius)
    7: 11,   # Rahu in 12th house (Pisces)
    8: 11,   # Ketu in 12th house (Pisces)
    'L': 5   # Lagna in 6th house (Virgo)
}
```

---

## 2. PANCHANGA DATA STRUCTURES

### 2.1 Tithi Output
```python
(tithi_index, tithi_name, start_jd, end_jd)

# Example
(14, 'Shukla Chaturdashi', 2460636.234, 2460637.156)

# tithi_index: 0-29
#   0-14: Shukla Paksha (Pratipada to Pournami)
#   15-29: Krishna Paksha (Pratipada to Amavasya)
```

### 2.2 Nakshatra Output
```python
(nakshatra_index, nakshatra_name, pada, start_jd, end_jd)

# Example
(11, 'Uttara Phalguni', 3, 2460636.123, 2460637.234)

# nakshatra_index: 0-26
# pada: 1-4 (quarter of nakshatra)
```

### 2.3 Yoga Output
```python
(yoga_index, yoga_name, start_jd, end_jd)

# Example
(15, 'Vajra', 2460636.456, 2460637.567)

# yoga_index: 0-26
```

### 2.4 Karana Output
```python
(karana_index, karana_name, start_jd, end_jd)

# Example
(2, 'Kaulava', 2460636.789, 2460637.012)

# karana_index: 0-10
#   0-6: Movable (Bava, Balava, Kaulava, Taitila, Garija, Vanija, Vishti)
#   7-10: Fixed (Shakuni, Chatushpada, Naga, Kimstughna)
```

### 2.5 Sunrise/Sunset Output
```python
(jd_event, time_string)

# Example
(2460636.7375, '05:42:15')
# JD when event occurs, time in HH:MM:SS format
```

---

## 3. DASHA DATA STRUCTURES

### 3.1 Dasha Periods (Mahadasha)
```python
# Format: List of tuples
dasha_periods = [
    (planet_id, start_jd, duration_years),
    ...
]

# Vimsottari Example
dasha_periods = [
    (4, 2451545.5, 16.0),   # Jupiter: 16 years
    (6, 2457390.5, 19.0),   # Saturn: 19 years
    (3, 2464330.5, 17.0),   # Mercury: 17 years
    (8, 2470543.5, 7.0),    # Ketu: 7 years
    (5, 2473097.5, 20.0),   # Venus: 20 years
    (0, 2480401.5, 6.0),    # Sun: 6 years
    (1, 2482592.5, 10.0),   # Moon: 10 years
    (2, 2486241.5, 7.0),    # Mars: 7 years
    (7, 2488794.5, 18.0)    # Rahu: 18 years
]
```

### 3.2 Dasha-Bhukti (Nested Periods)
```python
# Format: Nested list structure
dasha_bhukti = [
    [mahadasha_lord, mahadasha_start, mahadasha_duration, [
        [antardhasha_lord, antardhasha_start, antardhasha_duration, [
            [pratyantardhasha_lord, pratyantar_start, pratyantar_duration],
            ...
        ]],
        ...
    ]],
    ...
]
```

---

## 4. STRENGTH DATA STRUCTURES

### 4.1 Shadbala Output
```python
# Format: Dictionary with planet IDs as keys
shadbala_dict = {
    planet_id: {
        'sthana_bala': float,
        'dig_bala': float,
        'kaala_bala': float,
        'cheshta_bala': float,
        'naisargika_bala': float,
        'drik_bala': float,
        'total': float
    },
    ...
}

# Example for Sun
{
    0: {
        'sthana_bala': 456.78,
        'dig_bala': 123.45,
        'kaala_bala': 234.56,
        'cheshta_bala': 0.0,
        'naisargika_bala': 60.0,
        'drik_bala': 45.67,
        'total': 920.46
    }
}
```

### 4.2 Bhava Bala Output
```python
# Format: Dictionary for a single house
bhava_bala_dict = {
    'bhavadhipathi_bala': float,
    'bhava_dig_bala': float,
    'bhava_drishti_bala': float,
    'total': float
}

# Example
{
    'bhavadhipathi_bala': 456.78,
    'bhava_dig_bala': 123.45,
    'bhava_drishti_bala': 234.56,
    'total': 814.79
}
```

---

## 5. CHART DATA STRUCTURES

### 5.1 Chart Information Output
```python
chart_info = {
    'planet_positions': [...],           # List of (planet, (raasi, long))
    'house_to_planet_list': [...],       # 12-element list
    'planet_to_house_dict': {...},       # Dict mapping planets to houses
    'ascendant': (raasi, longitude),     # Lagna position
    'special_lagnas': {...},             # Special ascendants
    'upagrahas': {...}                   # Sub-planets
}
```

### 5.2 Special Lagnas Dictionary
```python
special_lagnas = {
    'hora_lagna': longitude,
    'ghati_lagna': longitude,
    'vighati_lagna': longitude,
    'bhava_lagna': longitude,
    'sree_lagna': longitude,
    'pranapada_lagna': longitude,
    'indu_lagna': longitude,
    'mrityu_lagna': longitude,
    ...
}
```

### 5.3 Upagrahas Dictionary
```python
upagrahas = {
    'dhuma': longitude,
    'vyatipaata': longitude,
    'parivesha': longitude,
    'indrachaapa': longitude,
    'upaketu': longitude,
    'kaala': longitude,
    'mrityu': longitude,
    'artha_prabhara': longitude,
    'yama_ghantaka': longitude,
    'gulika': longitude,
    'maandi': longitude
}
```

---

## 6. ARUDHA DATA STRUCTURES

```python
arudha_dict = {
    'arudha_lagna': (raasi, longitude),
    'upapada_lagna': (raasi, longitude),
    'bhava_arudhas': {
        1: (raasi, longitude),  # A1
        2: (raasi, longitude),  # A2
        ...
        12: (raasi, longitude)  # A12
    },
    'graha_arudhas': {
        0: (raasi, longitude),  # Sun arudha
        1: (raasi, longitude),  # Moon arudha
        ...
    }
}
```

---

## 7. YOGA DATA STRUCTURES

```python
# Yoga detection returns boolean
yoga_result = bool

# Yoga list with interpretations
yoga_list = [
    {
        'name': 'Hamsa Yoga',
        'present': True,
        'description': 'Jupiter in kendra in own/exaltation',
        'result': 'Great person of ethery nature...'
    },
    ...
]
```

---

## 8. JSON RESOURCE FILE STRUCTURES

### 8.1 Amsa Rulers JSON
```json
{
    "2": ["Devas", "Pitris"],
    "3": ["Naarada", "Agastya", "Durvaasa"],
    "7": ["Kshaara", "Ksheera", "Dadhi", "Ghrita", ...],
    "10": ["Indra", "Agni", "Yama", "Nirriti", ...],
    "60": ["Ghoraa", "Rakshasa", "Deva", ...],
    "150": ["Vasudhaa", "Vaishnavi", "Braahmi", ...]
}
```

### 8.2 Yoga Messages JSON
```json
{
    "yoga_name": [
        "Display Name",
        "Formation Condition",
        "Result/Interpretation"
    ]
}

// Example
{
    "hamsa_yoga": [
        "Hamsa Yoga",
        "Jupiter in kendra in own/exaltation",
        "You are a great man of ethery nature..."
    ]
}
```

### 8.3 Dosha Messages JSON
```json
{
    "dosha_name": [
        "No dosha message",
        "House 1 interpretation",
        "House 2 interpretation",
        ...
        "House 12 interpretation",
        "General description"
    ]
}
```

### 8.4 Prediction Messages JSON
```json
{
    "lord_of_a_house_joining_lord_of_another_house": {
        "house_number": [
            "Lagna lord + House lord interpretation",
            "2nd lord + House lord interpretation",
            ...
            "12th lord + House lord interpretation"
        ]
    }
}
```

---

## 9. COMPATIBILITY DATA STRUCTURES

### 9.1 Ashtakuta Output
```python
ashtakuta_dict = {
    'varna': (points, max_points),
    'vashya': (points, max_points),
    'tara': (points, max_points),
    'yoni': (points, max_points),
    'graha_maitri': (points, max_points),
    'gana': (points, max_points),
    'rasi': (points, max_points),
    'nadi': (points, max_points),
    'total': (total_points, 36)
}

# Example
{
    'varna': (1, 1),
    'vashya': (2, 2),
    'tara': (3, 3),
    'yoni': (4, 4),
    'graha_maitri': (5, 5),
    'gana': (6, 6),
    'rasi': (7, 7),
    'nadi': (8, 8),
    'total': (30, 36)
}
```

---

## 10. TAJAKA DATA STRUCTURES

### 10.1 Tajaka Aspect Output
```python
(aspected_houses, aspected_planets)

# Example - Trinal aspect
([4, 8], ['2', '5'])  
# Aspects 5th and 9th houses, aspects Mars and Venus
```

### 10.2 Saham Output
```python
# Single value: Longitude in zodiac (0-360°)
saham_longitude = 234.567

# Convert to raasi
raasi, degrees = drik.dasavarga_from_long(saham_longitude, 1)
# Returns: (7, 24.567)  # Scorpio 24.567°
```

---

## 11. CALENDAR INFORMATION STRUCTURE

```python
calendar_info = {
    'Place': str,
    'Latitude': str,  # DMS format
    'Longitude': str,  # DMS format
    'Timezone Offset': str,
    'Date': str,  # YYYY-MM-DD
    'Vaaram': str,  # Weekday name
    'Tithi': str,
    'Paksha': str,  # Shukla/Krishna
    'Nakshatra': str,
    'Nakshatra Pada': str,
    'Yoga': str,
    'Karana': str,
    'Sunrise': str,  # HH:MM:SS
    'Sunset': str,
    'Rahu Kaalam': str,
    'Gulika Kaalam': str,
    'Yamaganda Kaalam': str,
    'Abhijit Muhurta': str,
    'Maasam': str,  # Lunar month
    'Solar Month': str,
    'Ayanamsa': str,
    'Julian Day': float,
    'Calculation Type': str  # Drik/SS
}
```

---

## 12. DATA CONVERSION FUNCTIONS

### 12.1 House-Planet Conversions
```python
from jhora import utils

# Planet-to-House dict → House-to-Planet list
h_to_p = utils.get_house_to_planet_dict_from_planet_to_house_dict(p_to_h)

# House-to-Planet list → Planet-to-House dict
p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p)

# Planet positions → Planet-to-House dict
p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_pos)

# Planet positions → House-to-Planet list
h_to_p = utils.get_house_planet_list_from_planet_positions(planet_pos)
```

### 12.2 Chart Format Conversions
```python
# 1D list → 2D array for display (South Indian / East Indian)
rasi_2d = utils._convert_1d_house_data_to_2d(rasi_1d, chart_type='south_indian')

# Returns 4x4 array for South Indian chart
# Returns 3x3 array for East Indian chart
```

---

## 13. CONSTANT DATA STRUCTURES

### 13.1 Planet Arrays
```python
# Planet IDs: 0-8
const.planet_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# Planet names (multilingual via utils.PLANET_NAMES after set_language)
utils.PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
```

### 13.2 Raasi Arrays
```python
# Raasi IDs: 0-11
const.raasi_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Raasi names
utils.RAASI_LIST = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
```

### 13.3 Nakshatra Arrays
```python
# Nakshatra IDs: 0-26
const.nakshatra_list = [0, 1, 2, ..., 26]

# Nakshatra names (27 total)
utils.NAKSHATRA_LIST = ['Ashwini', 'Bharani', 'Krittika', ..., 'Revati']
```

### 13.4 Division Chart Factors
```python
# Standard factors
const.division_chart_factors = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

# All supported factors (D1 to D300)
const.all_division_chart_factors = [1, 2, 3, ..., 300]
```

---

**END OF DATA STRUCTURES DOCUMENTATION**
