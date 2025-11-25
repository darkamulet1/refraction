# 🔗 PYJHORA INTEGRATION PATTERNS

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

This document describes how PyJHora modules integrate, common usage workflows, and patterns for building applications using PyJHora.

---

## 1. TYPICAL WORKFLOW PATTERN

```python
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik
from jhora import utils

# Step 1: Initialize Horoscope
h = Horoscope(
    place_with_country_code='Chennai,IN',
    date_in=drik.Date(1985, 6, 9),
    birth_time='10:30:00',
    ayanamsa_mode='LAHIRI',
    language='en'
)

# Step 2: Get Calendar/Panchanga Info
calendar = h.get_calendar_information()

# Step 3: Get Charts (D1, D9, etc.)
d1_chart = h.get_horoscope_information_for_chart(chart_index=0)
d9_chart = h.get_horoscope_information_for_chart(chart_index=8)

# Step 4: Calculate Dashas
dasha_info = h._get_graha_dhasa_bhukthi(h.Date, h.birth_time, h.Place)

# Step 5: Calculate Strengths
shadbala = h._get_shad_bala(h.Date, h.birth_time, h.Place)

# Step 6: Detect Yogas (custom implementation needed)
```

---

## 2. HOROSCOPE CLASS INTEGRATION

The `Horoscope` class is the main integration point. It:

1. **Manages configuration** (ayanamsa, language, place, time)
2. **Caches calculated values** (julian_day, ayanamsa_value)
3. **Provides high-level APIs** for charts, dashas, strengths
4. **Handles resource loading** (JSON files, language strings)

### Key Integration Points

```python
# Horoscope class internally uses:

from jhora.panchanga import drik              # Core calculations
from jhora.horoscope.chart import charts       # Chart calculations
from jhora.horoscope.chart import house        # House calculations
from jhora.horoscope.chart import arudhas      # Arudha calculations
from jhora.horoscope.chart import strength     # Strength calculations
from jhora.horoscope.dhasa.graha import *      # Graha dashas
from jhora.horoscope.dhasa.raasi import *      # Raasi dashas
from jhora.horoscope.transit import tajaka     # Annual charts
from jhora.horoscope.transit import saham      # Arabic parts
from jhora import utils                        # Utilities
from jhora import const                        # Constants
```

---

## 3. DIRECT PANCHANGA USAGE (Without Horoscope Class)

```python
from jhora.panchanga import drik
from jhora import utils

# Setup
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)
date = drik.Date(1985, 6, 9)
jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))

# Set ayanamsa
drik.set_ayanamsa_mode('LAHIRI')

# Get panchanga elements
tithi_no, tithi_name, t_start, t_end = drik.tithi(jd, place)
nak_no, nak_name, pada, n_start, n_end = drik.nakshatra(jd, place)
yoga_no, yoga_name, y_start, y_end = drik.yoga(jd, place)

# Get planetary positions
planet_positions = drik.planets(jd)
lagna_rasi, lagna_long = drik.ascendant(jd, place)

# Get special lagnas
hora = drik.hora_lagna(jd, place)
ghati = drik.ghati_lagna(jd, place)
```

---

## 4. CHART CALCULATION PATTERN

```python
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
from jhora import utils

# Get planetary positions for a given JD
jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Calculate divisional chart
h_to_p_list = charts.divisional_chart(
    jd, 
    place,
    divisional_chart_factor=9,  # D9 Navamsa
    chart_method=1              # Parasara method
)

# Convert to planet-to-house dictionary
p_to_h = utils.get_planet_to_house_dict_from_chart(h_to_p_list)

# Get specific planet's house
jupiter_house = p_to_h[4]  # Jupiter
```

---

## 5. DASHA CALCULATION PATTERN

```python
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.panchanga import drik
from jhora import utils

# Calculate Vimsottari Dasha
jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

dasha_periods = vimsottari.vimsottari_dhasa(jd, place)

# Get detailed antardashas
detailed_dasha = vimsottari.get_dhasa_bhukthi(
    dasha_periods, 
    include_antardhasha=True
)

# Find current mahadasha
current_jd = utils.gregorian_to_jd(drik.Date(2025, 11, 22))
for planet, start, duration in dasha_periods:
    end = start + duration * 365.25
    if start <= current_jd < end:
        print(f"Current Mahadasha: {planet}")
        break
```

---

## 6. STRENGTH CALCULATION PATTERN

```python
from jhora.horoscope.chart import strength
from jhora.panchanga import drik
from jhora import utils

jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Calculate Shadbala for all planets
shadbala_dict = strength.shadbala(jd, place)

# Get specific planet's strength
jupiter_strength = shadbala_dict[4]['total']

# Calculate Bhava Bala for a house
h10_strength = strength.bhava_bala(jd, place, 9)  # 10th house (0-indexed)
```

---

## 7. TAJAKA (ANNUAL CHART) PATTERN

```python
from jhora.horoscope.transit import tajaka
from jhora.panchanga import drik
from jhora import utils

# Birth details
birth_jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Calculate 40th solar return
years = 40
annual_jd = tajaka.varsha_pravesh(birth_jd, place, years)

# Get annual chart
from jhora.horoscope.chart import charts
annual_chart = charts.divisional_chart(annual_jd, place, 1, 1)

# Calculate muntha
lagna_rasi, _ = drik.ascendant(birth_jd, place)
muntha_rasi = tajaka.muntha_house(lagna_rasi, years)

# Calculate sahams for annual chart
planet_pos = drik.planets(annual_jd)
is_night_birth = False  # Determine from birth time
fortune = tajaka.saham.punya_saham(planet_pos, is_night_birth)
```

---

## 8. COMPATIBILITY MATCHING PATTERN

```python
from jhora.horoscope.match import compatibility
from jhora.panchanga import drik
from jhora import utils

# Boy's details
boy_jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
boy_place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Girl's details
girl_jd = utils.julian_day_number((1988, 3, 15), (14, 20, 0))
girl_place = drik.Place('Mumbai', 19.0760, 72.8777, +5.5)

# Get nakshatras
boy_nak, _, boy_pada, _, _ = drik.nakshatra(boy_jd, boy_place)
girl_nak, _, girl_pada, _, _ = drik.nakshatra(girl_jd, girl_place)

# Get raasis (Moon signs)
boy_planets = drik.planets(boy_jd)
girl_planets = drik.planets(girl_jd)
boy_moon_rasi = boy_planets[1][1][0]  # Moon raasi
girl_moon_rasi = girl_planets[1][1][0]

# Calculate Ashtakuta
ashtakuta_score = compatibility.ashtakuta(
    boy_nak, girl_nak,
    boy_moon_rasi, girl_moon_rasi
)
```

---

## 9. YOGA DETECTION PATTERN

```python
from jhora.horoscope.chart import yoga
from jhora.panchanga import drik
from jhora import utils

jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))
place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)

# Get planet positions
planet_positions = drik.planets(jd)

# Check for Pancha Mahapurusha Yogas
has_hamsa = yoga.hamsa_yoga(planet_positions)
has_malavya = yoga.malavya_yoga(planet_positions)
has_ruchaka = yoga.ruchaka_yoga(planet_positions)

# Check for Raja Yogas
has_dk_raja_yoga = yoga.dharma_karmadhipati_raja_yoga(planet_positions)
```

---

## 10. RESOURCE LOCALIZATION PATTERN

```python
from jhora import utils

# Set language
utils.set_language('ta')  # Tamil

# Now all arrays are in Tamil
planet_names = utils.PLANET_NAMES
# ['சூரியன்', 'சந்திரன்', 'செவ்வாய்', ...]

raasi_names = utils.RAASI_LIST
# ['மேஷம்', 'ரிஷபம்', ...]

# Get yoga descriptions in Tamil
yoga_msgs = utils.get_resource_messages('lang/yoga_msgs_ta.json')
```

---

## 11. TRANSIT CALCULATION PATTERN

```python
from jhora.horoscope.transit import transit
from jhora.panchanga import drik
from jhora import utils

# Find when Jupiter enters Pisces
planet = 4  # Jupiter
target_raasi = 11  # Pisces
start_jd = utils.gregorian_to_jd(drik.Date(2025, 1, 1))
end_jd = utils.gregorian_to_jd(drik.Date(2026, 12, 31))

entry_jd = transit.next_planet_entry(planet, start_jd, target_raasi)

# Check retrograde periods
retro_start = transit.vakra_start_date(planet, start_jd)
retro_end = transit.vakra_end_date(planet, start_jd)
```

---

## 12. EPHEMERIS CALCULATION PATTERN

```python
import swisseph as swe
from jhora import utils

# Calculate planetary longitude for any JD
jd = 2460636.5

# Sun
sun_long = swe.calc_ut(jd, swe.SUN)[0][0]

# Moon
moon_long = swe.calc_ut(jd, swe.MOON)[0][0]

# Mars (with Rahu/Ketu mean node)
mars_long = swe.calc_ut(jd, swe.MARS)[0][0]

# Rahu (mean node)
rahu_long = swe.calc_ut(jd, swe.MEAN_NODE)[0][0]

# Ketu (180° opposite)
ketu_long = (rahu_long + 180) % 360
```

---

## 13. BATCH PROCESSING PATTERN

```python
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik
import csv

# Read birth data from CSV
birth_data = []
with open('births.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        birth_data.append(row)

# Process each horoscope
results = []
for person in birth_data:
    h = Horoscope(
        place_with_country_code=person['place'],
        date_in=drik.Date(int(person['year']), int(person['month']), int(person['day'])),
        birth_time=person['time'],
        ayanamsa_mode='LAHIRI'
    )
    
    # Get required information
    calendar = h.get_calendar_information()
    d1 = h.get_horoscope_information_for_chart(chart_index=0)
    
    results.append({
        'name': person['name'],
        'nakshatra': calendar['Nakshatra'],
        'lagna': d1['ascendant']
    })
```

---

## 14. ERROR HANDLING PATTERN

```python
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik

try:
    h = Horoscope(
        place_with_country_code='UnknownCity,XX',
        date_in=drik.Date(1985, 6, 9),
        birth_time='10:30:00'
    )
except Exception as e:
    # Handle location lookup failure
    print(f"Location error: {e}")
    
    # Use coordinates instead
    h = Horoscope(
        latitude=13.0827,
        longitude=80.2707,
        timezone_offset=5.5,
        date_in=drik.Date(1985, 6, 9),
        birth_time='10:30:00'
    )
```

---

## 15. CUSTOM EXTRACTOR PATTERN

```python
class VedicHoroscopeExtractor:
    def __init__(self, birth_data):
        self.h = Horoscope(**birth_data)
        
    def extract_all(self):
        return {
            'calendar': self.h.get_calendar_information(),
            'charts': self.get_all_charts(),
            'dashas': self.get_all_dashas(),
            'strengths': self.get_all_strengths(),
            'yogas': self.detect_yogas(),
            'special_points': self.get_special_points()
        }
    
    def get_all_charts(self):
        charts = {}
        for dcf in [1, 2, 3, 9, 10, 12, 16, 20, 30, 60]:
            chart_idx = self.dcf_to_index(dcf)
            charts[f'D{dcf}'] = self.h.get_horoscope_information_for_chart(
                chart_index=chart_idx
            )
        return charts
    
    def get_all_dashas(self):
        return {
            'vimsottari': self.h._get_graha_dhasa_bhukthi(
                self.h.Date, self.h.birth_time, self.h.Place
            )
        }
    
    def get_all_strengths(self):
        return {
            'shadbala': self.h._get_shad_bala(
                self.h.Date, self.h.birth_time, self.h.Place
            ),
            'bhava_bala': self.h._get_bhava_bala(
                self.h.Date, self.h.birth_time, self.h.Place
            )
        }
```

---

**END OF INTEGRATION PATTERNS**
