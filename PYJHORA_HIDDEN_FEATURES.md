# 🔍 PYJHORA HIDDEN FEATURES

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

This document reveals lesser-known features, advanced capabilities, and undocumented functionality in PyJHora.

---

## 1. ADVANCED VARGA CALCULATIONS

### Custom Divisional Charts (D-N where N=1 to 300)
```python
# Any divisional chart from D1 to D300
custom_d75 = charts.divisional_chart(jd, place, divisional_chart_factor=75)
custom_d108 = charts.divisional_chart(jd, place, divisional_chart_factor=108)
custom_d249 = charts.divisional_chart(jd, place, divisional_chart_factor=249)  # KP sub-lord chart
```

### Non-Standard Varga Methods
```python
# Varga with custom base rasi
charts.divisional_chart(jd, place, dcf=9, 
                        base_rasi=True,              # Use sign itself as base
                        count_from_end_of_sign=True) # Reverse counting
```

---

## 2. ADVANCED AYANAMSA OPTIONS

### Custom Ayanamsa Value
```python
# Set your own ayanamsa value
drik.set_ayanamsa_mode('LAHIRI', ayanamsa_value=24.0, jd=julian_day)

# TRUE_CITRA - Spica exactly at 180°
drik.set_ayanamsa_mode('TRUE_CITRA')

# TRUE_REVATI - Zeta Piscium at 359°50'
drik.set_ayanamsa_mode('TRUE_REVATI')

# TRUE_MULA - Lambda Scorpii at 240°
drik.set_ayanamsa_mode('TRUE_MULA')

# GALACTIC_CENTER_0SAG - Galactic center at 0° Sagittarius
drik.set_ayanamsa_mode('GALACTIC_CENTER_0SAG')
```

---

## 3. PARIVRITTI METHODS (Division Patterns)

### Even-Reverse Pattern
```python
# Hora chart with alternating sequence
parivritti_tuple = utils.parivritti_even_reverse(dcf=2, dirn=1)
# Returns: [(0,0,0), (0,1,1), (1,1,2), (1,0,3), ...]
```

### Cyclic Pattern
```python
# Zodiacal order for each portion
parivritti_tuple = utils.parivritti_cyclic(dcf=3, dirn=1)
# Returns: [(0,1,2), (3,4,5), (6,7,8), ...]
```

### Alternate Pattern (Somanatha Method)
```python
# Odd signs forward, even signs backward
parivritti_tuple = utils.parivritti_alternate(dcf=2, dirn=1)
# Returns: [(Ar,Ta), (Pi,Aq), (Ge,Cn), (Cp,Sg), ...]
```

---

## 4. SPECIAL CHART COMBINATIONS

### Mixed Charts (Two Charts Combined)
```python
# Natal D9 with Transit D1
mixed = h.get_horoscope_information_for_mixed_chart(
    chart_index_1=8,  # D9 natal
    chart_method_1=1,
    chart_index_2=0,  # D1 transit
    chart_method_2=1
)

# Varnada for mixed charts
varnada_mixed = h.get_varnada_lagna_for_mixed_chart(
    dob, tob, place,
    varga_factor_1=1, chart_method_1=1,
    varga_factor_2=9, chart_method_2=1
)
```

---

## 5. ADVANCED TIME CALCULATIONS

### Udhayadhi Nazhikai (Tamil Time System)
```python
# Time elapsed since sunrise in Nazhikai system
nazhikai_str, nazhikai_float = utils.udhayadhi_nazhikai(jd, place)
# Returns: ['15:23:45', 15.396]
# 1 Nazhikai = 24 minutes, 1 Vinadigal = 24 seconds
```

### Solar Time vs Local Time
```python
# Convert to solar time
solar_time = drik.solar_time(jd, place)

# Local solar noon
local_noon = drik.local_solar_noon(jd, place)
```

### Kshaya Maasa Detection
```python
# Detect skipped lunar months
kshaya_maasa = drik.kshaya_maasa(jd, place)
```

---

## 6. VAAKYA PANCHANGAM (Ancient Method)

### Tamil Month Calculation
```python
# Vaakya method for Tamil month (Aryabhatiya approximation)
tamil_month_name, start_date, weekday, num_days, kd = utils.vaakya_tamil_month(year=2025, month_number=1)
# Returns: ('சித்திரை', '14-04-2025', 'திங்கள்', 30, 1826555.234)
```

---

## 7. SURYA SIDDHANTA MODE

### Ancient Vedic Calculations
```python
# Use Surya Siddhanta instead of Swiss Ephemeris
h = Horoscope(..., calculation_type='ss')

# Forces SURYASIDDHANTA ayanamsa
# Uses ancient algorithms from Surya Siddhanta text
```

---

## 8. PRASNA (HORARY) SYSTEMS

### KP 249 Sub-Lord System
```python
# Get lagna for any of 249 KP sub-divisions
lagna_rasi = utils.get_prasna_lagna_KP_249_for_rasi_chart(kp_no=125)
lagna_varga = utils.get_prasna_lagna_KP_249_for_varga_chart(kp_no=125, varga_no=9)

# Get nakshatra from KP number
nak = utils.get_KP_nakshathra_from_kp_no(125)

# Get KP details from planet longitude
kp_details = utils.get_KP_details_from_planet_longitude(planet_long=125.678)
```

### 108 Nadi System
```python
lagna_rasi = utils.get_prasna_lagna_108_for_rasi_chart(nadi_no=55)
lagna_navamsa = utils.get_prasna_lagna_108_for_navamsa(nadi_no=55)
lagna_varga = utils.get_prasna_lagna_108_for_varga_chart(nadi_no=55, varga_no=12)
```

### 150 Nadi System
```python
lagna_rasi = utils.get_prasna_lagna_nadi_for_rasi_chart(nadi_no=75)
lagna_varga = utils.get_prasna_lagna_nadi_for_varga_chart(nadi_no=75, varga_no=9)
```

---

## 9. ADVANCED NAKSHATRA FUNCTIONS

### Abhijit Nakshatra (28th Star)
```python
# Include Abhijit (rarely used 28th nakshatra)
nak_list_with_abhijit = utils.get_nakshathra_list_with_abhijith()
# Returns all 28 nakshatras with Abhijit between Uttara Ashadha and Shravana

# Cyclic counting with Abhijit
next_star = utils.cyclic_count_of_stars_with_abhijit(
    from_star=21, 
    count=5, 
    direction=1, 
    star_count=28
)
```

---

## 10. MATHEMATICAL INTERPOLATION

### Inverse Lagrange
```python
# Find x when y is known, given x-y data points
x = utils.inverse_lagrange(
    x=[1, 2, 3, 4, 5],
    y=[10, 40, 90, 160, 250],
    ya=100  # Find x when y=100
)
# Returns: x ≈ 3.1
```

### Newton Polynomial Interpolation
```python
# Evaluate polynomial at any point
p_x = utils.newton_polynomial(
    x_data=[1, 2, 3, 4],
    y_data=[1, 8, 27, 64],
    x=2.5
)
```

### Bisection Search for Ayanamsa
```python
# Find ayanamsa value where Citra is exactly at 180°
ayanamsa = utils._bisection_search(utils._function, start_jd, end_jd)
```

---

## 11. GRAHA YUDDHA (PLANETARY WAR)

```python
from jhora.horoscope.chart import strength

# Detect planetary war
yuddha_bala = strength.yuddha_bala(jd, planet1, planet2)
# Returns strength change due to planetary war
# Only occurs when two planets are within 1° in same raasi
```

---

## 12. MRITYU BHAGA (Death Points)

```python
# Calculate sensitive death points for each planet
from jhora.horoscope.chart import house

mrityu_bhaga = house.mrityu_bhaga(planet, raasi)
# Returns degree range within raasi that's inauspicious
```

---

## 13. LATTHA (Kicked Away) POINTS

```python
# Degrees in each sign that are "kicked" by planets
lattha_degrees = house.lattha(planet, raasi)
# These degrees give malefic effects
```

---

## 14. UCCHA RASHMI (Exaltation Rays)

```python
# Calculate exaltation strength rays
uccha_rashmi = strength.uccha_rashmi(planet_longitude, planet)
# Returns special strength when planet is near exaltation degree
```

---

## 15. DEEPTAMSA (Deep Exaltation Range)

```python
# Get deep exaltation range for a planet
deep_min, deep_max = utils.deeptaamsa_range_of_planet(
    planet=4,  # Jupiter
    planet_longitude_within_raasi=5.0
)
# Returns: (0.0, 10.0)  # Jupiter's deep range is ±5° from 5°
```

---

## 16. PANCHA PAKSHI SASTRA

### Five-Bird System (Tamil Astrology)
```python
from jhora.panchanga import pancha_paksha

# Complex system of 5 birds ruling different time periods
pancha_pakshi_info = pancha_paksha.pancha_pakshi_sastra(jd, place, nakshatra, sex='male')
# Returns: Current bird, sub-bird, activity (eating/walking/sleeping/dying/ruling)
```

---

## 17. SPECIAL CHAKRAS

### Sarvatobhadra Chakra
```python
from jhora.horoscope.chart import chakra

# Multi-dimensional nakshatra chakra
stb_chakra = chakra.sarvatobhadra_chakra(planet_positions)
```

### Kalachakra Dasha
```python
# Complex 9-year dasha cycle based on nakshatra
kalachakra = dhasa.kalachakra.kalachakra_dhasa(jd, place)
```

---

## 18. NISHEKA LAGNA (Conception Ascendant)

```python
# Calculate conception time from birth time
nisheka_lagna = house.nisheka_lagna(birth_jd, place)
# Returns JD of conception based on pregnancy duration algorithms
```

---

## 19. VAKRA GATHI (RETROGRADE TRACKING)

```python
from jhora.horoscope.transit import transit

# Find exact retrograde start/end dates
retro_start = transit.vakra_start_date(planet=4, jd_start)
retro_end = transit.vakra_end_date(planet=4, jd_start)

# Find when planet becomes direct (maargi)
direct_date = transit.maargi_date(planet=4, jd_start)
```

---

## 20. CONJUNCTION FINDER

```python
# Find all conjunctions in a time range
conjunctions = transit.find_conjunctions(
    planet1=4,  # Jupiter
    planet2=6,  # Saturn
    start_jd=jd1,
    end_jd=jd2,
    orb=1.0  # Within 1 degree
)
```

---

## 21. TITHI PRAVESHA (Lunar Return)

```python
# Annual lunar return chart
tithi_pravesha_jd = drik.tithi_pravesha(
    birth_jd, 
    birth_place, 
    years_from_birth=35
)

# When Moon returns to same tithi as birth
```

---

## 22. AMSA DEITIES

### Rulers of Divisional Chart Portions
```python
# Get deity names for D60 chart portions
amsa_rulers_json = utils.get_resource_messages('lang/amsa_rulers_en.json')
d60_deities = json.loads(amsa_rulers_json)['60']
# Returns: ['Ghoraa', 'Rakshasa', 'Deva', ...] - all 60 deity names
```

---

## 23. TRIGUNA CALCULATION

```python
# Calculate Sattwa/Rajas/Tamas quality for day-time
triguna, min_key, next_key = utils.triguna_of_the_day_time(
    day_index=3,  # Wednesday
    time_of_day=10.5  # 10:30 AM
)
# Returns which guna is predominant
```

---

## 24. ECLIPSE CALCULATIONS

```python
# Next solar eclipse
eclipse_jd, eclipse_type, magnitude = drik.next_solar_eclipse(jd)

# Next lunar eclipse  
eclipse_jd, eclipse_type, magnitude = drik.next_lunar_eclipse(jd)

# Eclipse types: 'total', 'partial', 'annular', 'penumbral'
```

---

## 25. WORLD CITIES DATABASE

```python
# Enable fast city lookup from database
utils.use_database_for_world_cities(enable_database=True)

# Database contains 100,000+ cities with lat/lon/timezone
# Located at: const._world_city_csv_file

# Add new city to database
utils.save_location_to_database([
    'Country', 'CityName', latitude, longitude, 'TZ_String', tz_offset
])
```

---

## 26. ANGLE UNWRAPPING

```python
# Handle circular angle continuity
angles = [340, 350, 10, 20]  # Crosses 0°
unwrapped = utils.unwrap_angles(angles)
# Returns: [340, 350, 370, 380]  # Continuous for interpolation
```

---

## 27. DATE FORMAT PARSER

```python
# Parse any date format automatically
year, month, day = utils.get_year_month_day_from_date_format('09/02/2025')
year, month, day = utils.get_year_month_day_from_date_format('2025-02-09')
year, month, day = utils.get_year_month_day_from_date_format('Feb 09, 2025')

# Handles BCE dates
year, month, day = utils.get_year_month_day_from_date_format('-3114-01-01')
# Returns: (-3114, 1, 1)
```

---

## 28. KALI YUGA DAY

```python
# Days elapsed since Kali Yuga start (Feb 18, 3102 BCE)
kali_day = utils.kali_yuga_jd(jd)
# Returns: Days since 3102 BCE (used in ancient calculations)
```

---

## 29. TRIMMING OUTPUT

```python
# Trim info lines intelligently
info_lines = ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Show more']
trimmed = utils.trim_info_list_lines(info_lines, skip_lines=2)
# Returns: ['Line 1', 'Line 2', 'Show more']
```

---

## 30. VALIDATION FUNCTIONS

```python
# Validate all input data with defaults
place, lat, lon, tz, dob, tob, dcf = utils._validate_data(
    place='Chennai,IN',
    latitude=None,  # Will auto-detect
    longitude=None,
    time_zone_offset=None,
    dob=None,  # Defaults to today
    tob=None,  # Defaults to now
    division_chart_factor=17
)
```

---

## 31. 2D CHART CONVERSION

```python
# Convert 1D raasi list to 2D array for display

# South Indian style (4x4)
chart_2d = utils._convert_1d_house_data_to_2d(
    rasi_1d=['', '0', '1/2', '', '', ...],
    chart_type='south_indian'
)

# East Indian style (3x3)
chart_2d = utils._convert_1d_house_data_to_2d(
    rasi_1d=['', '0', '1/2', '', '', ...],
    chart_type='east_indian'
)
```

---

## 32. SEARCH/REPLACE IN CHARTS

```python
# Search and replace in chart lists
chart = ['L', '0/1', 'L/2', '3', ...]
modified = utils.search_replace(chart, 'L', 'Asc')
# Returns: ['Asc', '0/1', 'Asc/2', '3', ...]
```

---

## 33. CLOSEST ELEMENT MATCHING

```python
# Find closest value in list
value = 15.7
list_array = [10, 12, 16, 20, 25]
closest = utils.closest_element_from_list(list_array, value)
# Returns: 16

# Find closest pair between two lists
arr1 = [10, 20, 30]
arr2 = [15, 25, 35]
elem1, elem2 = utils.closest_elements(arr1, arr2)
# Returns: (20, 15)  # Closest pair
```

---

## 34. CYCLIC NUMBER OPERATIONS

```python
# Cyclic counting in any range
result = utils.cyclic_count_of_numbers(
    from_number=28,
    to_number=5,
    dir=1,
    number_count=30
)
# Wraps around 30
```

---

## 35. EPHEMERIS PATH CUSTOMIZATION

```python
# Use custom ephemeris files location
utils.set_ephemeris_data_path('/custom/path/to/ephe/')

# Useful for:
# - Extended date ranges (13000 BCE to 17000 CE)
# - Asteroid ephemeris
# - Custom solar system body data
```

---

## 36. MULTIPLE AYANAMSA COMPARISON

```python
# Calculate position with different ayanamsas
ayanamsas = ['LAHIRI', 'RAMAN', 'KP', 'TRUE_CITRA', 'YUKTESHWAR']

for ayan in ayanamsas:
    drik.set_ayanamsa_mode(ayan)
    planet_pos = drik.planets(jd)
    print(f"{ayan}: {planet_pos[0]}")  # Compare Sun positions
```

---

## 37. JULIAN DAY UTILITIES

```python
# JD to local date/time
year, month, day, frac_hour = utils.jd_to_local(jd, place)

# Pretty print JD
date_time_str = utils.julian_day_to_date_time_string(jd)
# Returns: "1985-06-09 10:30:00"
```

---

## 38. UNDOCUMENTED TAJAKA FEATURES

### Tri-Pataki Chakra
```python
# Complex annual prediction chakra
tri_pataki = tajaka.tri_pataki_chakra(jd, place)
```

### Pancha Vargiya Bala (5-fold Strength)
```python
# Tajaka strength in 5 charts
pv_bala = tajaka.pancha_vargiya_bala(annual_jd, planet)
```

---

## 39. FRACTION CALCULATIONS

```python
# Calculate elapsed fraction between two times
fraction = utils.get_fraction(
    start_time_hrs=5.7,   # 5:42 AM
    end_time_hrs=18.6,    # 6:36 PM
    birth_time_hrs=10.5   # 10:30 AM
)
# Returns: Fraction of time elapsed
```

---

## 40. ADVANCED TESTING SUPPORT

```python
from jhora.tests import pvr_tests

# Run all 633 test cases
pvr_tests.pvr_tests()

# Run specific chapter tests
pvr_tests.chapter_1_tests()
pvr_tests.chapter_15_tests()

# Test specific features
pvr_tests.divisional_chart_tests()
pvr_tests.shadbala_tests()
pvr_tests.yoga_tests()
```

---

**CONCLUSION**

PyJHora contains numerous hidden features and advanced capabilities beyond standard horoscope calculation. These features enable:

- **Research**: Academic study of different calculation methods
- **Precision**: Fine-tuning calculations for specific traditions
- **Integration**: Building advanced astrological applications
- **Experimentation**: Exploring alternative systems and theories

**END OF HIDDEN FEATURES DOCUMENTATION**
