# 🎯 PYJHORA EXTRACTOR BLUEPRINT

**Version**: PyJHora v4.5.5
**Date**: 2025-11-22

**Purpose**: Complete blueprint for building a 100% PyJHora data extractor that captures ALL capabilities

---

## 1. EXTRACTOR ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│           PyJHora Extractor System              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │Input Handler │→ │ Horoscope    │           │
│  │              │  │ Initializer  │           │
│  └──────────────┘  └──────────────┘           │
│         ↓                  ↓                    │
│  ┌─────────────────────────────────────┐       │
│  │     Core Data Extraction Layer      │       │
│  │  • Panchanga  • Charts  • Dashas    │       │
│  │  • Strengths  • Yogas   • Transits  │       │
│  └─────────────────────────────────────┘       │
│         ↓                                       │
│  ┌─────────────────────────────────────┐       │
│  │    Advanced Features Layer          │       │
│  │  • Tajaka • Sahams • Arudhas        │       │
│  │  • Predictions • Compatibility      │       │
│  └─────────────────────────────────────┘       │
│         ↓                                       │
│  ┌─────────────────────────────────────┐       │
│  │      Data Serialization Layer       │       │
│  │  • JSON • CSV • Database • API      │       │
│  └─────────────────────────────────────┘       │
│         ↓                                       │
│  ┌──────────────┐  ┌──────────────┐           │
│  │Output Format │  │ Localization │           │
│  │  Handler     │  │   Handler    │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

---

## 2. COMPLETE EXTRACTION CHECKLIST

### Phase 1: Input & Initialization ✓
- [ ] Parse birth date, time, place
- [ ] Handle timezone detection
- [ ] Set ayanamsa mode
- [ ] Set language
- [ ] Initialize Horoscope object
- [ ] Validate all inputs

### Phase 2: Panchanga Extraction ✓
- [ ] Tithi (30 types)
- [ ] Nakshatra (27 types + pada)
- [ ] Yoga (27 types)
- [ ] Karana (11 types)
- [ ] Vaara (7 weekdays)
- [ ] Paksha (Shukla/Krishna)
- [ ] Lunar Month (12 months + Adhik)
- [ ] Solar Month
- [ ] Ritu (6 seasons)
- [ ] Sunrise/Sunset times
- [ ] Moonrise/Moonset times
- [ ] Rahu Kaalam
- [ ] Gulika Kaalam
- [ ] Yamaganda Kaalam
- [ ] Abhijit Muhurta
- [ ] Brahma Muhurta

### Phase 3: Planetary Positions ✓
- [ ] Sun position
- [ ] Moon position
- [ ] Mars position
- [ ] Mercury position
- [ ] Jupiter position
- [ ] Venus position
- [ ] Saturn position
- [ ] Rahu position
- [ ] Ketu position
- [ ] Uranus (optional)
- [ ] Neptune (optional)
- [ ] Pluto (optional)
- [ ] Ascendant (Lagna)
- [ ] All in absolute longitude
- [ ] All in raasi + degrees
- [ ] Retrograde status
- [ ] Combustion status

### Phase 4: Special Lagnas ✓
- [ ] Hora Lagna
- [ ] Ghati Lagna
- [ ] Vighati Lagna
- [ ] Bhava Lagna
- [ ] Sree Lagna
- [ ] Pranapada Lagna
- [ ] Indu Lagna
- [ ] Mrityu Lagna
- [ ] Varnada Lagna (for each chart)
- [ ] Kala Lagna
- [ ] Artha Lagna
- [ ] All other special lagnas (23 total)

### Phase 5: Upagrahas ✓
- [ ] Dhuma
- [ ] Vyatipaata
- [ ] Parivesha
- [ ] Indrachaapa
- [ ] Upaketu
- [ ] Kaala
- [ ] Mrityu
- [ ] Artha Prabhara
- [ ] Yama Ghantaka
- [ ] Gulika
- [ ] Maandi

### Phase 6: Divisional Charts (All Vargas) ✓
- [ ] D1 (Rasi - Overall)
- [ ] D2 (Hora - Wealth)
- [ ] D3 (Drekkana - Siblings)
- [ ] D4 (Chaturthamsa - Property)
- [ ] D7 (Saptamsa - Children)
- [ ] D9 (Navamsa - Spouse/Dharma) **CRITICAL**
- [ ] D10 (Dasamsa - Career)
- [ ] D12 (Dwadasamsa - Parents)
- [ ] D16 (Shodasamsa - Vehicles)
- [ ] D20 (Vimsamsa - Spiritual)
- [ ] D24 (Chaturvimsamsa - Education)
- [ ] D27 (Saptavimsamsa - Strengths)
- [ ] D30 (Trimsamsa - Evils)
- [ ] D40 (Khavedamsa - Auspicious)
- [ ] D45 (Akshavedamsa - General)
- [ ] D60 (Shashtiamsa - Karmas)
- [ ] D81, D108, D144, D150 (Extended)
- [ ] Custom D-N charts (up to D300)
- [ ] For each chart: planet positions, house rulers, aspects

### Phase 7: Dasha Systems (46 Total) ✓
**Graha Dashas (22):**
- [ ] Vimsottari (120 years) **MOST COMMON**
- [ ] Ashtottari (108 years)
- [ ] Yogini (36 years)
- [ ] Shodasottari (116 years)
- [ ] Dwisaptati Sama (72 years)
- [ ] Satabdika (100 years)
- [ ] Chaturasithi Sama (84 years)
- [ ] Dwadasottari (112 years)
- [ ] Panchottari (105 years)
- [ ] Shashtihayani (60 years)
- [ ] + 12 more graha dashas

**Raasi Dashas (22):**
- [ ] Narayana Dasha
- [ ] Chara Dasha
- [ ] Sthira Dasha
- [ ] Kendraadhi Dasha
- [ ] + 18 more raasi dashas

**Annual Dashas (2):**
- [ ] Varsha Vimsottari
- [ ] Mudda Dasha

**For each dasha:**
- [ ] Mahadasha periods
- [ ] Antardhasha periods
- [ ] Pratyantardhasha periods
- [ ] Current running period

### Phase 8: Strength Calculations ✓
**Shadbala (6 components for each planet):**
- [ ] Sthana Bala (Positional)
- [ ] Dig Bala (Directional)
- [ ] Kaala Bala (Temporal)
- [ ] Cheshta Bala (Motional)
- [ ] Naisargika Bala (Natural)
- [ ] Drik Bala (Aspectual)
- [ ] Total Shadbala

**Bhava Bala (for each house):**
- [ ] Bhavadhipathi Bala
- [ ] Bhava Dig Bala
- [ ] Bhava Drishti Bala
- [ ] Total Bhava Bala

**Other Strength:**
- [ ] Vimsopaka Bala (Varga strength)
- [ ] Vaiseshikamsa Bala
- [ ] Ashtakavarga (for each planet)
- [ ] Bhinnashtak avarga
- [ ] Sarvashtakavarga

### Phase 9: Yoga Detection (100+ Yogas) ✓
**Pancha Mahapurusha (5):**
- [ ] Ruchaka (Mars)
- [ ] Bhadra (Mercury)
- [ ] Hamsa (Jupiter)
- [ ] Malavya (Venus)
- [ ] Sasa (Saturn)

**Nabhasa Yogas (32):**
- [ ] Akriti Yogas (20)
- [ ] Sankhya Yogas (7)
- [ ] Ashraya Yogas (5)

**Chandra Yogas (13):**
- [ ] Vesi, Vosi, Ubhayachari
- [ ] Sunaphaa, Anaphaa, Duradhara
- [ ] Kemadruma
- [ ] Adhi Yoga
- [ ] + 5 more

**Raja Yogas (20+):**
- [ ] Dharma-Karmadhipati
- [ ] Vipareetha Raja Yoga
- [ ] Neecha Bhanga Raja Yoga
- [ ] + 17 more

**Dhana Yogas (15+):**
- [ ] All wealth yogas

**Dosha Yogas:**
- [ ] Kala Sarpa Dosha (12 types)
- [ ] Manglik Dosha
- [ ] Pitri Dosha
- [ ] + others

### Phase 10: Arudha Calculations ✓
- [ ] Arudha Lagna (AL)
- [ ] Upapada Lagna (UL)
- [ ] Darapada (A7)
- [ ] Bhava Arudhas (A1-A12)
- [ ] Graha Arudhas (for each planet)
- [ ] Karakamsa

### Phase 11: Sahams/Arabic Parts (36+) ✓
- [ ] Punya Saham (Fortune)
- [ ] Vidya Saham (Education)
- [ ] Yasas Saham (Fame)
- [ ] Mitra Saham (Friend)
- [ ] Mahatmaya Saham (Greatness)
- [ ] + 31 more sahams
- [ ] Day/Night birth variations

### Phase 12: Tajaka (Annual Charts) ✓
- [ ] Varsha Pravesh (Solar Return)
- [ ] Varsha chart (D1 annual)
- [ ] Muntha position
- [ ] Varsheshwara (Year Lord)
- [ ] Tri-pataki Chakra
- [ ] Tajaka aspects (5 types)
- [ ] Tajaka yogas (19 types)
- [ ] Pancha Vargiya Bala
- [ ] Dwadasa Vargiya Bala
- [ ] Annual dashas (Mudda/Varsha Vimsottari)

### Phase 13: Transits ✓
- [ ] Current planetary transits
- [ ] Upcoming transits (next 2 years)
- [ ] Sade Sati status
- [ ] Ashtama Shani status
- [ ] Jupiter transit effects
- [ ] Retrograde periods
- [ ] Combustion periods
- [ ] Transit yogas
- [ ] Gochara phala

### Phase 14: Compatibility (If applicable) ✓
**Ashtakuta (10 components):**
- [ ] Varna Kuta
- [ ] Vashya Kuta
- [ ] Tara Kuta
- [ ] Yoni Kuta
- [ ] Graha Maitri
- [ ] Gana Kuta
- [ ] Rasi Kuta
- [ ] Nadi Kuta
- [ ] Mahendra Kuta
- [ ] Stree Deergha
- [ ] Total score (/36)

**Additional Matching:**
- [ ] Dasa Sandhi
- [ ] Rajju Dosha
- [ ] Vedha Dosha
- [ ] Papa Samyam

### Phase 15: Predictions ✓
- [ ] Lagna predictions
- [ ] Planet in house predictions
- [ ] Lord in house predictions
- [ ] Dasha period predictions
- [ ] Longevity category
- [ ] General life predictions

### Phase 16: Sphutas (Sensitive Points) ✓
- [ ] Beeja Sphuta
- [ ] Kshetra Sphuta
- [ ] Tithi Pravesha Lagna
- [ ] Prana Sphuta
- [ ] Deha Sphuta
- [ ] Mrityu Sphuta
- [ ] + 8 more sphutas

### Phase 17: Additional Features ✓
- [ ] Pancha Pakshi
- [ ] Vratha/Festival calculations
- [ ] Chakra displays (7 types)
- [ ] Nisheka Lagna
- [ ] Graha Yuddha (planetary war)
- [ ] Eclipse effects
- [ ] KP System data
- [ ] Prasna (Horary) chart support

### Phase 18: Localization ✓
- [ ] Extract in all 6 languages (en/ta/te/hi/ka/ml)
- [ ] Planet names localized
- [ ] Raasi names localized
- [ ] Nakshatra names localized
- [ ] Yoga descriptions localized
- [ ] Dosha messages localized
- [ ] Prediction texts localized

---

## 3. PYTHON EXTRACTOR IMPLEMENTATION

```python
from jhora.horoscope.main import Horoscope
from jhora.panchanga import drik
from jhora import utils
import json
from datetime import datetime

class PyJHoraExtractor:
    """
    Complete PyJHora Data Extractor
    Extracts 100% of PyJHora capabilities
    """
    
    def __init__(self, birth_data, language='en'):
        """
        Initialize extractor with birth data
        
        Args:
            birth_data: dict with place, date, time, etc.
            language: 'en', 'ta', 'te', 'hi', 'ka', 'ml'
        """
        utils.set_language(language)
        self.h = Horoscope(**birth_data)
        self.language = language
        self.jd = self.h.julian_day
        self.place = self.h.Place
        
    def extract_all(self):
        """Extract everything"""
        return {
            'metadata': self.extract_metadata(),
            'panchanga': self.extract_panchanga(),
            'planets': self.extract_planets(),
            'special_lagnas': self.extract_special_lagnas(),
            'upagrahas': self.extract_upagrahas(),
            'charts': self.extract_all_charts(),
            'dashas': self.extract_all_dashas(),
            'strengths': self.extract_all_strengths(),
            'yogas': self.extract_yogas(),
            'arudhas': self.extract_arudhas(),
            'sahams': self.extract_sahams(),
            'tajaka': self.extract_tajaka(),
            'transits': self.extract_transits(),
            'predictions': self.extract_predictions(),
            'sphutas': self.extract_sphutas()
        }
    
    def extract_metadata(self):
        """Extract basic information"""
        return {
            'place': self.h.place_name,
            'latitude': self.h.latitude,
            'longitude': self.h.longitude,
            'timezone': self.h.timezone_offset,
            'date': str(self.h.Date),
            'time': self.h.birth_time,
            'julian_day': self.jd,
            'ayanamsa_mode': self.h.ayanamsa_mode,
            'ayanamsa_value': self.h.ayanamsa_value,
            'calculation_type': self.h.calculation_type,
            'language': self.language,
            'extraction_timestamp': datetime.now().isoformat()
        }
    
    def extract_panchanga(self):
        """Extract all panchanga elements"""
        tithi_no, tithi_name, t_start, t_end = drik.tithi(self.jd, self.place)
        nak_no, nak_name, pada, n_start, n_end = drik.nakshatra(self.jd, self.place)
        yoga_no, yoga_name, y_start, y_end = drik.yoga(self.jd, self.place)
        kar_no, kar_name, k_start, k_end = drik.karana(self.jd, self.place)
        
        return {
            'tithi': {
                'number': tithi_no,
                'name': tithi_name,
                'start_jd': t_start,
                'end_jd': t_end
            },
            'nakshatra': {
                'number': nak_no,
                'name': nak_name,
                'pada': pada,
                'start_jd': n_start,
                'end_jd': n_end
            },
            'yoga': {
                'number': yoga_no,
                'name': yoga_name,
                'start_jd': y_start,
                'end_jd': y_end
            },
            'karana': {
                'number': kar_no,
                'name': kar_name,
                'start_jd': k_start,
                'end_jd': k_end
            },
            'vaara': drik.vaara(self.jd),
            'sunrise': drik.sunrise(self.jd, self.place),
            'sunset': drik.sunset(self.jd, self.place),
            'rahu_kaalam': drik.rahu_kaalam(self.jd, self.place),
            'gulika_kaalam': drik.gulika_kaalam(self.jd, self.place)
        }
    
    def extract_planets(self):
        """Extract all planetary positions"""
        planet_positions = drik.planets(self.jd)
        planets = {}
        
        planet_names = utils.PLANET_NAMES
        for planet, (raasi, longitude) in planet_positions:
            planets[planet_names[planet]] = {
                'raasi': raasi,
                'raasi_name': utils.RAASI_LIST[raasi],
                'longitude_in_raasi': longitude,
                'absolute_longitude': raasi * 30 + longitude,
                'is_retrograde': drik.is_planet_retrograde(self.jd, planet),
                'is_combust': drik.is_planet_in_combustion(self.jd, planet)
            }
        
        # Add Lagna
        lagna_rasi, lagna_long = drik.ascendant(self.jd, self.place)
        planets['Lagna'] = {
            'raasi': lagna_rasi,
            'raasi_name': utils.RAASI_LIST[lagna_rasi],
            'longitude_in_raasi': lagna_long,
            'absolute_longitude': lagna_rasi * 30 + lagna_long
        }
        
        return planets
    
    def extract_special_lagnas(self):
        """Extract all 23 special lagnas"""
        return {
            'hora_lagna': drik.hora_lagna(self.jd, self.place),
            'ghati_lagna': drik.ghati_lagna(self.jd, self.place),
            'bhava_lagna': drik.bhava_lagna(self.jd, self.place),
            'sree_lagna': drik.sree_lagna(self.jd, self.place),
            'pranapada_lagna': drik.pranapada_lagna(self.jd, self.place),
            'indu_lagna': drik.indu_lagna(self.jd, self.place),
            # ... add all 23
        }
    
    def extract_upagrahas(self):
        """Extract all upagrahas"""
        return {
            'dhuma': drik.dhuma(self.jd),
            'vyatipaata': drik.vyatipaata(self.jd),
            'parivesha': drik.parivesha(self.jd),
            'indrachaapa': drik.indrachaapa(self.jd),
            'upaketu': drik.upaketu(self.jd),
            'kaala': drik.kaala(self.jd, self.place),
            'mrityu': drik.mrityu(self.jd, self.place),
            'gulika': drik.gulika(self.jd, self.place),
            'maandi': drik.maandi(self.jd, self.place)
        }
    
    def extract_all_charts(self):
        """Extract all divisional charts"""
        charts = {}
        
        # Standard charts
        for dcf in [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]:
            chart_idx = self._dcf_to_index(dcf)
            charts[f'D{dcf}'] = self.h.get_horoscope_information_for_chart(
                chart_index=chart_idx
            )
        
        return charts
    
    def extract_all_dashas(self):
        """Extract all dasha systems"""
        return {
            'vimsottari': self.h._get_graha_dhasa_bhukthi(
                self.h.Date, self.h.birth_time, self.h.Place
            ),
            # Add all 46 dasha systems
        }
    
    def extract_all_strengths(self):
        """Extract all strength calculations"""
        return {
            'shadbala': self.h._get_shad_bala(
                self.h.Date, self.h.birth_time, self.h.Place
            ),
            'bhava_bala': self.h._get_bhava_bala(
                self.h.Date, self.h.birth_time, self.h.Place
            ),
            'vimsopaka': self.h._get_vimsopaka_bala(
                self.h.Date, self.h.birth_time, (self.h.place_name, 
                self.h.latitude, self.h.longitude, self.h.timezone_offset)
            )
        }
    
    def extract_yogas(self):
        """Extract all yoga detections"""
        # Implement yoga detection for all 100+ yogas
        pass
    
    def extract_arudhas(self):
        """Extract all arudha calculations"""
        return self.h._get_arudha_padhas(
            self.h.Date, self.h.birth_time, self.h.Place, 
            divisional_chart_factor=1, chart_method=1
        )
    
    def extract_sahams(self):
        """Extract all 36 sahams"""
        from jhora.horoscope.transit import saham
        planet_pos = drik.planets(self.jd)
        is_night = self._is_night_birth()
        
        sahams = {}
        # Extract all 36 sahams
        sahams['punya'] = saham.punya_saham(planet_pos, is_night)
        # ... add all 36
        
        return sahams
    
    def extract_tajaka(self):
        """Extract Tajaka (annual chart) data"""
        # Implement complete Tajaka extraction
        pass
    
    def extract_transits(self):
        """Extract transit information"""
        # Implement transit extraction
        pass
    
    def extract_predictions(self):
        """Extract all predictions"""
        # Implement prediction extraction
        pass
    
    def extract_sphutas(self):
        """Extract all sphuta (sensitive points)"""
        return self.h._get_sphuta(
            self.h.Date, self.h.birth_time, self.h.Place,
            divisional_chart_factor=1, chart_method=1
        )
    
    def save_to_json(self, filename):
        """Save complete extraction to JSON"""
        data = self.extract_all()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _dcf_to_index(dcf):
        """Convert divisional chart factor to index"""
        mapping = {1:0, 2:1, 3:2, 4:3, 7:4, 9:8, 10:9, 12:11, 
                   16:15, 20:19, 24:23, 27:26, 30:29, 40:39, 
                   45:44, 60:59}
        return mapping.get(dcf, 0)
    
    def _is_night_birth(self):
        """Determine if birth was at night"""
        sr_jd, _ = drik.sunrise(self.jd, self.place)
        ss_jd, _ = drik.sunset(self.jd, self.place)
        return self.jd < sr_jd or self.jd > ss_jd


# USAGE EXAMPLE
if __name__ == '__main__':
    birth_data = {
        'place_with_country_code': 'Chennai,IN',
        'date_in': drik.Date(1985, 6, 9),
        'birth_time': '10:30:00',
        'ayanamsa_mode': 'LAHIRI',
        'language': 'en'
    }
    
    extractor = PyJHoraExtractor(birth_data, language='en')
    
    # Extract everything
    complete_data = extractor.extract_all()
    
    # Save to JSON
    extractor.save_to_json('complete_horoscope.json')
    
    print("Extraction complete!")
```

---

## 4. OUTPUT FORMAT SPECIFICATION

```json
{
  "metadata": {
    "place": "Chennai",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": 5.5,
    "date": "1985-06-09",
    "time": "10:30:00",
    "julian_day": 2446218.9375,
    "ayanamsa_mode": "LAHIRI",
    "ayanamsa_value": 23.65,
    "extraction_timestamp": "2025-11-22T10:30:00"
  },
  "panchanga": {
    "tithi": {...},
    "nakshatra": {...},
    "yoga": {...},
    "karana": {...}
  },
  "planets": {
    "Sun": {...},
    "Moon": {...},
    ...
  },
  "charts": {
    "D1": {...},
    "D9": {...},
    ...
  },
  "dashas": {...},
  "strengths": {...},
  "yogas": [...],
  "arudhas": {...},
  "sahams": {...},
  "tajaka": {...},
  "predictions": {...}
}
```

---

**END OF EXTRACTOR BLUEPRINT**
