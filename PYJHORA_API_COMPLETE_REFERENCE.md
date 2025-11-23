# 📖 PYJHORA API COMPLETE REFERENCE

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

This document provides complete API signatures, parameters, return values, and usage examples for all major PyJHora functions.

---

## TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Core Data Structures](#core-data-structures)
3. [Horoscope Class API](#horoscope-class-api)
4. [Panchanga API](#panchanga-api)
5. [Chart Calculation API](#chart-calculation-api)
6. [Dasha API](#dasha-api)
7. [Strength Calculation API](#strength-calculation-api)
8. [Yoga Detection API](#yoga-detection-api)
9. [Tajaka (Annual Charts) API](#tajaka-api)
10. [Utility Functions API](#utility-functions-api)

---

## QUICK START

### Basic Usage Example

```python
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik

# Method 1: Using place name with country code
h = Horoscope(
    place_with_country_code='Chennai,IN',
    date_in=drik.Date(1985, 6, 9),
    birth_time='10:30:00',
    ayanamsa_mode='LAHIRI',
    language='en'
)

# Method 2: Using coordinates
h = Horoscope(
    latitude=13.0827,
    longitude=80.2707,
    timezone_offset=5.5,
    date_in=drik.Date(1985, 6, 9),
    birth_time='10:30:00',
    ayanamsa_mode='LAHIRI'
)

# Get calendar information
calendar_info = h.get_calendar_information()

# Get chart for D1 (Rasi chart)
chart_info = h.get_horoscope_information_for_chart(
    chart_index=0,  # D1
    chart_method=1,
    divisional_chart_factor=1
)
```

---

## CORE DATA STRUCTURES

### 1. Date Structure
```python
from jhora.panchanga import drik

# Creating a Date
date = drik.Date(year, month, day)

# Examples:
birth_date = drik.Date(1985, 6, 9)
today = drik.Date(2025, 11, 22)
bc_date = drik.Date(-3114, 1, 1)  # BCE dates use negative year
```

### 2. Place Structure
```python
from jhora.panchanga import drik

# Creating a Place
place = drik.Place(name, latitude, longitude, timezone_offset)

# Examples:
chennai = drik.Place('Chennai', 13.0827, 80.2707, +5.5)
newyork = drik.Place('New York', 40.7128, -74.0060, -5.0)
london = drik.Place('London', 51.5074, -0.1278, +0.0)
```

### 3. Planet Positions Format
```python
# Format: List of tuples
planet_positions = [
    (planet_id, (raasi_index, longitude_in_raasi)),
    ...
]

# Example:
# [(0, (0, 15.5)), (1, (1, 22.3)), ...]
# Planet 0 (Sun) in Raasi 0 (Aries) at 15.5°
# Planet 1 (Moon) in Raasi 1 (Taurus) at 22.3°
```

### 4. House-to-Planet List Format
```python
# Format: List of 12 strings (one per house/raasi)
house_to_planet_list = ['', '0', '1/2', '', '', 'L/3', ...]

# Explanation:
# Index 0 (Aries): Empty
# Index 1 (Taurus): Planet 0 (Sun)
# Index 2 (Gemini): Planets 1 (Moon) and 2 (Mars)
# Index 5 (Virgo): Lagna and Planet 3 (Mercury)
```

### 5. Planet-to-House Dictionary
```python
# Format: Dictionary mapping planet IDs to house indices
planet_to_house_dict = {
    0: 1,  # Sun in 2nd house
    1: 2,  # Moon in 3rd house
    2: 2,  # Mars in 3rd house
    ...
    'L': 5  # Lagna in 6th house
}
```

---

## HOROSCOPE CLASS API

### Constructor

```python
class Horoscope:
    def __init__(
        self,
        place_with_country_code: str = None,
        latitude: float = None,
        longitude: float = None,
        timezone_offset: float = None,
        date_in: drik.Date = None,
        birth_time: str = None,
        ayanamsa_mode: str = "TRUE_CITRA",
        ayanamsa_value: float = None,
        calculation_type: str = 'drik',
        years: int = 1,
        months: int = 1,
        sixty_hours: int = 1,
        pravesha_type: int = 0,
        bhava_madhya_method = const.bhaava_madhya_method,
        language: str = 'en'
    )
```

**Parameters**:
- `place_with_country_code`: Place name with country code (e.g., 'Chennai,IN', 'London,UK')
- `latitude`: Latitude in decimal degrees (-90 to +90)
- `longitude`: Longitude in decimal degrees (-180 to +180)
- `timezone_offset`: Timezone offset from UTC in hours (e.g., +5.5 for IST, -5.0 for EST)
- `date_in`: Birth date as drik.Date object
- `birth_time`: Birth time as string 'HH:MM:SS' or 'HH:MM' (24-hour format)
- `ayanamsa_mode`: Ayanamsa system (see [Configuration Options](#ayanamsa-modes))
  - Options: 'LAHIRI', 'RAMAN', 'KP', 'TRUE_CITRA', 'TRUE_REVATI', etc.
- `ayanamsa_value`: Custom ayanamsa value (overrides mode if provided)
- `calculation_type`: 'drik' (swiss ephemeris) or 'ss' (surya siddhanta)
- `years`, `months`, `sixty_hours`: For progression charts
- `pravesha_type`: 0=Janma, 1=Annual, 2=Tithi
- `bhava_madhya_method`: House cusp calculation method
- `language`: 'en', 'ta', 'te', 'hi', 'ka', 'ml'

**Example**:
```python
h = Horoscope(
    place_with_country_code='Bangalore,IN',
    date_in=drik.Date(1990, 5, 15),
    birth_time='14:30:00',
    ayanamsa_mode='LAHIRI',
    language='en'
)
```

### get_calendar_information()

```python
def get_calendar_information(self) → dict
```

**Returns**: Dictionary with panchanga elements and calendar info

**Example**:
```python
calendar = h.get_calendar_information()

# Returns:
{
    'Place': 'Chennai',
    'Latitude': '13° 4' 57" N',
    'Longitude': '80° 16' 14" E',
    'Timezone Offset': '5.50',
    'Date': '1985-6-9',
    'Vaaram': 'Sunday',
    'Tithi': 'Shukla Dasami',
    'Nakshatra': 'Uttara Phalguni 3',
    'Yoga': 'Siddha',
    'Karana': 'Bava',
    'Sunrise': '05:42:15',
    'Sunset': '18:35:20',
    'Ayanamsa': '23.65°',
    'Julian Day': 2446218.9375
}
```

### get_horoscope_information_for_chart()

```python
def get_horoscope_information_for_chart(
    self,
    chart_index: int = 0,
    chart_method: int = 1,
    divisional_chart_factor: int = None,
    base_rasi: bool = False,
    count_from_end_of_sign: bool = False
) → dict
```

**Parameters**:
- `chart_index`: Chart type index (0=D1, 1=D2, 2=D3, ...)
  - Standard charts: 0-19 for D1-D20
  - Extended: 20-42 for D24, D27, D30, D40, D45, D60, D81, D108, D144, D150, D300
- `chart_method`: Calculation method (see [Chart Methods](#chart-methods))
  - 1: Parasara (default)
  - 2: Sripathi
  - 3: Krishnamurti Paddhati (KP)
  - etc.
- `divisional_chart_factor`: Override for custom varga (e.g., D17, D75)
- `base_rasi`: For custom varga calculations
- `count_from_end_of_sign`: For custom varga calculations

**Returns**: Dictionary with chart data

**Example**:
```python
# D1 (Rasi Chart)
d1 = h.get_horoscope_information_for_chart(chart_index=0)

# D9 (Navamsa)
d9 = h.get_horoscope_information_for_chart(chart_index=8)

# D10 (Dasamsa - Career)
d10 = h.get_horoscope_information_for_chart(chart_index=9)

# Custom D17
d17 = h.get_horoscope_information_for_chart(
    divisional_chart_factor=17,
    chart_method=1
)

# Returns:
{
    'planet_positions': [(0, (0, 15.5)), (1, (1, 22.3)), ...],
    'house_to_planet_list': ['', '0', '1/2', ...],
    'planet_to_house_dict': {0: 1, 1: 2, ...},
    'ascendant': (5, 12.3),  # Virgo ascendant at 12.3°
    'special_lagnas': {...},
    'upagrahas': {...}
}
```

### get_horoscope_information_for_mixed_chart()

```python
def get_horoscope_information_for_mixed_chart(
    self,
    chart_index_1: int = 0,
    chart_method_1: int = 1,
    chart_index_2: int = 0,
    chart_method_2: int = 1,
    varga_factor_1: int = None,
    varga_factor_2: int = None
) → dict
```

**Purpose**: Combines two different divisional charts (useful for transits vs natal)

**Example**:
```python
# Transit D1 over Natal D9
mixed = h.get_horoscope_information_for_mixed_chart(
    chart_index_1=0,  # Transit D1
    chart_index_2=8   # Natal D9
)
```

---

## PANCHANGA API

All panchanga functions are in the `jhora.panchanga.drik` module.

### tithi()

```python
def tithi(jd: float, place: drik.Place) → tuple
```

**Parameters**:
- `jd`: Julian day number
- `place`: Place object

**Returns**: `(tithi_index, tithi_name, start_jd, end_jd)`
- `tithi_index`: 0-29 (0=Shukla Pratipada, 14=Pournami, 15=Krishna Pratipada, 29=Amavasya)
- `tithi_name`: String name
- `start_jd`: Julian day when tithi started
- `end_jd`: Julian day when tithi ends

**Example**:
```python
from jhora import utils
from jhora.panchanga import drik

place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)
jd = utils.gregorian_to_jd(drik.Date(2025, 11, 22))

tithi_no, tithi_name, start, end = drik.tithi(jd, place)
# Returns: (14, 'Shukla Chaturdashi', 2460636.234, 2460637.156)

# Convert to readable time
start_date = utils.jd_to_gregorian(start)
# Returns: (2025, 11, 22, 5.616)  # 5:37 AM
```

### nakshatra()

```python
def nakshatra(jd: float, place: drik.Place) → tuple
```

**Returns**: `(nakshatra_index, nakshatra_name, pada, start_jd, end_jd)`
- `nakshatra_index`: 0-26 (0=Ashwini, 26=Revati)
- `pada`: 1-4 (quarter of nakshatra)

**Example**:
```python
nak_no, nak_name, pada, start, end = drik.nakshatra(jd, place)
# Returns: (11, 'Uttara Phalguni', 3, 2460636.123, 2460637.234)
```

### yoga()

```python
def yoga(jd: float, place: drik.Place) → tuple
```

**Returns**: `(yoga_index, yoga_name, start_jd, end_jd)`
- `yoga_index`: 0-26 (0=Vishkambha, 26=Vaidhrti)

**Example**:
```python
yoga_no, yoga_name, start, end = drik.yoga(jd, place)
# Returns: (15, 'Vajra', 2460636.456, 2460637.567)
```

### karana()

```python
def karana(jd: float, place: drik.Place) → tuple
```

**Returns**: `(karana_index, karana_name, start_jd, end_jd)`
- `karana_index`: 0-10
  - 0-6: Movable karanas (Bava, Balava, Kaulava, Taitila, Garija, Vanija, Vishti)
  - 7-10: Fixed karanas (Shakuni, Chatushpada, Naga, Kimstughna)

**Example**:
```python
kar_no, kar_name, start, end = drik.karana(jd, place)
# Returns: (2, 'Kaulava', 2460636.789, 2460637.012)
```

### vaara()

```python
def vaara(jd: float) → int
```

**Returns**: Day of week (0=Sunday, 6=Saturday)

**Example**:
```python
day = drik.vaara(jd)
# Returns: 5  # Friday
```

### planets()

```python
def planets(jd: float) → list[tuple]
```

**Returns**: List of planetary positions `[(planet_id, (raasi, longitude)), ...]`
- planet_id: 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn, 7=Rahu, 8=Ketu

**Example**:
```python
planet_pos = drik.planets(jd)
# Returns:
[
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

### ascendant()

```python
def ascendant(jd: float, place: drik.Place) → tuple
```

**Returns**: `(raasi_index, longitude_in_raasi)`

**Example**:
```python
lagna_rasi, lagna_long = drik.ascendant(jd, place)
# Returns: (5, 12.345)  # Virgo ascendant at 12.345°
```

### sunrise() / sunset()

```python
def sunrise(jd: float, place: drik.Place) → tuple
def sunset(jd: float, place: drik.Place) → tuple
```

**Returns**: `(jd_event, time_string)`

**Example**:
```python
sr_jd, sr_time = drik.sunrise(jd, place)
# Returns: (2460636.7375, '05:42:15')

ss_jd, ss_time = drik.sunset(jd, place)
# Returns: (2460637.2745, '18:35:20')
```

### Special Lagnas

```python
def hora_lagna(jd: float, place: drik.Place) → float
def ghati_lagna(jd: float, place: drik.Place) → float
def bhava_lagna(jd: float, place: drik.Place) → float
def sree_lagna(jd: float, place: drik.Place) → float
def pranapada_lagna(jd: float, place: drik.Place) → float
def indu_lagna(jd: float, place: drik.Place) → float
```

**Returns**: Longitude in zodiac (0-360°)

**Example**:
```python
hora = drik.hora_lagna(jd, place)
# Returns: 187.456  # 7° Libra (187.456° from Aries)

ghati = drik.ghati_lagna(jd, place)
# Returns: 234.567

# Convert to raasi and degrees
raasi, degrees = drik.dasavarga_from_long(hora, 1)
# Returns: (6, 7.456)  # Raasi 6 (Libra), 7.456°
```

### Upagrahas

```python
def dhuma(jd: float) → float
def vyatipaata(jd: float) → float
def parivesha(jd: float) → float
def indrachaapa(jd: float) → float
def upaketu(jd: float) → float
def kaala(jd: float, place: drik.Place) → float
def mrityu(jd: float, place: drik.Place) → float
def artha_prabhara(jd: float, place: drik.Place) → float
def yama_ghantaka(jd: float, place: drik.Place) → float
def gulika(jd: float, place: drik.Place) → float
def maandi(jd: float, place: drik.Place) → float
```

**Returns**: Longitude in zodiac (0-360°)

**Example**:
```python
gulika_long = drik.gulika(jd, place)
# Returns: 156.789

maandi_long = drik.maandi(jd, place)
# Returns: 203.456
```

### Ayanamsa Functions

```python
def set_ayanamsa_mode(
    ayanamsa_mode: str = 'LAHIRI',
    ayanamsa_value: float = None,
    jd: float = None
) → None

def get_ayanamsa_value(jd: float) → float
```

**Example**:
```python
# Set ayanamsa mode
drik.set_ayanamsa_mode('LAHIRI')

# Get current ayanamsa value
ayanamsa = drik.get_ayanamsa_value(jd)
# Returns: 24.12  # degrees

# Set custom ayanamsa
drik.set_ayanamsa_mode('LAHIRI', ayanamsa_value=24.0)
```

---

## CHART CALCULATION API

### divisional_chart()

```python
from jhora.horoscope.chart import charts

def divisional_chart(
    jd: float,
    place: drik.Place,
    divisional_chart_factor: int,
    chart_method: int = 1
) → list[str]
```

**Parameters**:
- `divisional_chart_factor`: 1-300 (D1, D2, ..., D300)
- `chart_method`: Calculation method
  - 1: Parasara (default)
  - 2: Sripathi
  - 3: KP
  - 4: Others...

**Returns**: House-to-planet list

**Example**:
```python
# D9 Navamsa using Parasara method
d9_chart = charts.divisional_chart(jd, place, divisional_chart_factor=9, chart_method=1)
# Returns: ['0/1', '', '2/L', '3', '', '4/5', '', '6', '', '7', '8', '']
```

### dasavarga_from_long()

```python
def dasavarga_from_long(
    longitude: float,
    divisional_chart_factor: int
) → tuple
```

**Purpose**: Convert absolute longitude to varga position

**Parameters**:
- `longitude`: Absolute longitude in zodiac (0-360°)
- `divisional_chart_factor`: Varga number

**Returns**: `(varga_raasi, longitude_in_varga_raasi)`

**Example**:
```python
# Planet at 125.5° (5.5° Leo)
varga_rasi, varga_long = charts.dasavarga_from_long(125.5, 9)  # D9
# Returns: (8, 19.5)  # Sagittarius at 19.5°
```

### Special Divisional Charts

```python
# Specific chart calculation functions
def shodasamsa_from_long(longitude: float) → tuple  # D16
def vimsamsa_from_long(longitude: float) → tuple    # D20
def chaturvimsamsa_from_long(longitude: float) → tuple  # D24
def saptavimsamsa_from_long(longitude: float) → tuple   # D27
def trimsamsa_from_long(longitude: float) → tuple       # D30
def khavedamsa_from_long(longitude: float) → tuple      # D40
def akshavedamsa_from_long(longitude: float) → tuple    # D45
def shashtiamsa_from_long(longitude: float) → tuple     # D60
```

**Example**:
```python
# D30 Trimsamsa (health/misfortunes)
trim_rasi, trim_long = charts.trimsamsa_from_long(125.5)
# Returns: (specific raasi based on D30 rules)
```

---

## DASHA API

### vimsottari_dhasa()

```python
from jhora.horoscope.dhasa.graha import vimsottari

def vimsottari_dhasa(
    jd: float,
    place: drik.Place,
    divisional_chart_factor: int = 1
) → list[tuple]
```

**Returns**: List of dasha periods `[(planet, start_jd, duration_years), ...]`

**Example**:
```python
dasha_periods = vimsottari.vimsottari_dhasa(jd, place)
# Returns:
[
    (4, 2451545.5, 16.0),   # Jupiter dasha: 16 years
    (6, 2457390.5, 19.0),   # Saturn dasha: 19 years
    (3, 2464330.5, 17.0),   # Mercury dasha: 17 years
    (8, 2470543.5, 7.0),    # Ketu dasha: 7 years
    (5, 2473097.5, 20.0),   # Venus dasha: 20 years
    (0, 2480401.5, 6.0),    # Sun dasha: 6 years
    (1, 2482592.5, 10.0),   # Moon dasha: 10 years
    (2, 2486241.5, 7.0),    # Mars dasha: 7 years
    (7, 2488794.5, 18.0)    # Rahu dasha: 18 years
]
```

### get_dhasa_bhukthi()

```python
def get_dhasa_bhukthi(
    dasha_periods: list,
    include_antardhasha: bool = True
) → list
```

**Purpose**: Calculate antardashas (sub-periods) and pratyantardashas

**Example**:
```python
# Get mahadasha + antardhasha
detailed_dasha = vimsottari.get_dhasa_bhukthi(dasha_periods, include_antardhasha=True)
# Returns nested structure with Mahadasha -> Antardhasha -> Pratyantardhasha
```

### Other Dasha Systems

```python
from jhora.horoscope.dhasa.graha import ashtottari, yogini, shodasottari

# Ashtottari Dasha (108 years cycle)
ashtottari_periods = ashtottari.ashtottari_dhasa(jd, place)

# Yogini Dasha (36 years cycle)
yogini_periods = yogini.yogini_dhasa(jd, place)

# Shodasottari Dasha (116 years cycle)
shodasottari_periods = shodasottari.shodasottari_dhasa(jd, place)
```

### Jaimini Dashas

```python
from jhora.horoscope.dhasa.raasi import narayana, chara

# Narayana Dasha
narayana_periods = narayana.narayana_dhasa(jd, place, divisional_chart_factor=1)

# Chara Dasha
chara_periods = chara.chara_dhasa(jd, place)
```

---

## STRENGTH CALCULATION API

### shadbala()

```python
from jhora.horoscope.chart import strength

def shadbala(
    jd: float,
    place: drik.Place,
    divisional_chart_factor: int = 1
) → dict
```

**Returns**: Dictionary with all 6 bala components for each planet

**Example**:
```python
shad_bala = strength.shadbala(jd, place)
# Returns:
{
    0: {  # Sun
        'sthana_bala': 456.78,
        'dig_bala': 123.45,
        'kaala_bala': 234.56,
        'cheshta_bala': 0.0,  # Sun has no motional strength
        'naisargika_bala': 60.0,
        'drik_bala': 45.67,
        'total': 920.46
    },
    1: {  # Moon
        'sthana_bala': 567.89,
        ...
    },
    ...
}
```

### vimsopaka_bala()

```python
def vimsopaka_bala(
    planet_positions: list,
    planet: int
) → float
```

**Purpose**: Calculate varga strength based on dignity in divisional charts

**Example**:
```python
# Calculate for Jupiter
vimsopaka_strength = strength.vimsopaka_bala(planet_positions, 4)
# Returns: 18.5  # Out of 20
```

### bhava_bala()

```python
def bhava_bala(
    jd: float,
    place: drik.Place,
    house: int
) → dict
```

**Purpose**: Calculate strength of a house

**Example**:
```python
# 10th house strength
h10_strength = strength.bhava_bala(jd, place, 9)  # 9 = 10th house (0-indexed)
# Returns:
{
    'bhavadhipathi_bala': 456.78,
    'bhava_dig_bala': 123.45,
    'bhava_drishti_bala': 234.56,
    'total': 814.79
}
```

---

## YOGA DETECTION API

### Pancha Mahapurusha Yogas

```python
from jhora.horoscope.chart import yoga

def ruchaka_yoga(planet_positions: list) → bool
def bhadra_yoga(planet_positions: list) → bool
def hamsa_yoga(planet_positions: list) → bool
def malavya_yoga(planet_positions: list) → bool
def sasa_yoga(planet_positions: list) → bool
```

**Example**:
```python
# Check for Hamsa Yoga (Jupiter in kendra in own/exaltation)
has_hamsa = yoga.hamsa_yoga(planet_positions)
# Returns: True or False
```

### Raja Yogas

```python
def dharma_karmadhipati_raja_yoga(planet_positions: list) → bool
def vipareetha_raja_yoga(planet_positions: list) → bool
def neecha_bhanga_raja_yoga(planet_positions: list) → bool
```

**Example**:
```python
# Check for Dharma-Karmadhipati Raja Yoga
has_dk_raja_yoga = yoga.dharma_karmadhipati_raja_yoga(planet_positions)
# Returns: True or False
```

---

## TAJAKA API

### varsha_pravesh()

```python
from jhora.horoscope.transit import tajaka

def varsha_pravesh(
    birth_jd: float,
    place: drik.Place,
    years: int
) → float
```

**Purpose**: Calculate solar return (annual chart) JD

**Example**:
```python
# 35th birthday solar return
annual_jd = tajaka.varsha_pravesh(birth_jd, place, years=35)
# Returns: JD when Sun returns to natal position
```

### Tajaka Aspects

```python
def trinal_aspects_of_planet(house_to_planet_list: list, planet: int) → tuple
def sextile_aspects_of_planet(house_to_planet_list: list, planet: int) → tuple
def square_aspects_of_planet(house_to_planet_list: list, planet: int) → tuple
def opposition_aspects_of_planet(house_to_planet_list: list, planet: int) → tuple
```

**Example**:
```python
# Get trinal (120° - benefic) aspects of Jupiter (planet 4)
aspected_houses, aspected_planets = tajaka.trinal_aspects_of_planet(h_to_p_list, 4)
# Returns: ([aspected_houses], [aspected_planets])
```

### Sahams (Arabic Parts)

```python
from jhora.horoscope.transit import saham

def punya_saham(planet_positions: list, night_birth: bool) → float
def vidya_saham(planet_positions: list, night_birth: bool) → float
def yasas_saham(planet_positions: list, night_birth: bool) → float
...  # 36 more sahams
```

**Example**:
```python
# Calculate Part of Fortune (Punya Saham)
is_night_birth = False  # Daytime birth
fortune_long = saham.punya_saham(planet_positions, is_night_birth)
# Returns: 234.567  # Longitude in zodiac

# Convert to raasi
raasi, degrees = drik.dasavarga_from_long(fortune_long, 1)
# Returns: (7, 24.567)  # Scorpio 24.567°
```

---

## UTILITY FUNCTIONS API

### Location Functions

```python
from jhora import utils

def get_location(place_name: str) → list
```

**Example**:
```python
# Get location details
city, lat, lon, tz = utils.get_location('Mumbai,IN')
# Returns: ['Mumbai', 19.0760, 72.8777, 5.5]

# Auto-detect from IP
city, lat, lon, tz = utils.get_place_from_user_ip_address()
# Returns: ['Chennai', 13.0827, 80.2707, 5.5]
```

### Date/Time Conversion

```python
def julian_day_number(dob: tuple, tob: tuple) → float
def gregorian_to_jd(date: drik.Date) → float
def jd_to_gregorian(jd: float) → tuple
```

**Example**:
```python
# Date + Time to JD
dob = (1985, 6, 9)
tob = (10, 30, 0)
jd = utils.julian_day_number(dob, tob)
# Returns: 2446218.9375

# Date to JD (midnight)
jd = utils.gregorian_to_jd(drik.Date(1985, 6, 9))
# Returns: 2446218.5

# JD back to date
year, month, day, frac_hour = utils.jd_to_gregorian(jd)
# Returns: (1985, 6, 9, 10.5)
```

### Angle Conversion

```python
def to_dms(
    deg: float,
    as_string: bool = True,
    is_lat_long: str = None
) → str or tuple
```

**Example**:
```python
# Convert degrees to DMS string
dms_str = utils.to_dms(125.678, as_string=True)
# Returns: '125° 40' 40"'

# As tuple
d, m, s = utils.to_dms(125.678, as_string=False)
# Returns: (125, 40, 40.68)

# For latitude
lat_str = utils.to_dms(13.0827, as_string=True, is_lat_long='lat')
# Returns: '13° 4' 57" N'

# From DMS to degrees
degrees = utils.from_dms(125, 40, 40.68)
# Returns: 125.678
```

### Resource Management

```python
def set_language(language: str) → None
def get_resource_messages(language_file: str) → dict
```

**Example**:
```python
# Set language to Tamil
utils.set_language('ta')

# Get planet names in current language
planet_names = utils.PLANET_NAMES
# Returns: ['சூரியன்', 'சந்திரன்', ...] (in Tamil)

# Switch to English
utils.set_language('en')
planet_names = utils.PLANET_NAMES
# Returns: ['Sun', 'Moon', 'Mars', ...]
```

---

## APPENDIX: Quick Reference Tables

### Planet IDs
| ID | Planet | Sanskrit | Tamil |
|----|--------|----------|-------|
| 0 | Sun | Surya | சூரியன் |
| 1 | Moon | Chandra | சந்திரன் |
| 2 | Mars | Kuja/Mangala | செவ்வாய் |
| 3 | Mercury | Budha | புதன் |
| 4 | Jupiter | Guru | குரு |
| 5 | Venus | Shukra | சுக்கிரன் |
| 6 | Saturn | Shani | சனி |
| 7 | Rahu | Rahu | ராகு |
| 8 | Ketu | Ketu | கேது |

### Raasi (Sign) IDs
| ID | Raasi | Sanskrit | English |
|----|-------|----------|---------|
| 0 | Mesha | Aries | Aries |
| 1 | Vrishabha | Taurus | Taurus |
| 2 | Mithuna | Gemini | Gemini |
| 3 | Karka | Cancer | Cancer |
| 4 | Simha | Leo | Leo |
| 5 | Kanya | Virgo | Virgo |
| 6 | Tula | Libra | Libra |
| 7 | Vrischika | Scorpio | Scorpio |
| 8 | Dhanus | Sagittarius | Sagittarius |
| 9 | Makara | Capricorn | Capricorn |
| 10 | Kumbha | Aquarius | Aquarius |
| 11 | Meena | Pisces | Pisces |

### Ayanamsa Modes
- `LAHIRI`: Lahiri/Chitrapaksha (default in India)
- `RAMAN`: B.V. Raman
- `KP`: Krishnamurti Paddhati
- `TRUE_CITRA`: True Chitra Paksha
- `TRUE_REVATI`: True Revati
- `YUKTESHWAR`: Swami Sri Yukteswar
- 15+ more options

### Divisional Chart Significance
| Varga | Name | Significance |
|-------|------|--------------|
| D1 | Rasi | Overall life, physical body |
| D2 | Hora | Wealth |
| D3 | Drekkana | Siblings, courage |
| D4 | Chaturthamsa | Property, houses |
| D7 | Saptamsa | Children |
| D9 | Navamsa | Spouse, dharma |
| D10 | Dasamsa | Career, profession |
| D12 | Dwadasamsa | Parents |
| D16 | Shodasamsa | Vehicles, comforts |
| D20 | Vimsamsa | Spiritual pursuits |
| D24 | Chaturvimsamsa | Education |
| D27 | Saptavimsamsa | Strengths/weaknesses |
| D30 | Trimsamsa | Evils, misfortunes |
| D40 | Khavedamsa | Auspicious effects |
| D45 | Akshavedamsa | General indications |
| D60 | Shashtiamsa | Overall karmas |

---

**END OF API REFERENCE**
