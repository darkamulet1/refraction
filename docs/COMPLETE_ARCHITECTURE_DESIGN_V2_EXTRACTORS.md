# 🏗️ طراحی کامل - بخش 2: Extractors Refactored

## 🔄 Refactored Extractors

### 1. core_chart.py (REFACTORED)

```python
"""
Core Chart Extractor - Refactored with graha.py
"""

from typing import Dict, Any, List
from .base import BaseExtractor
from ..core.graha import (
    GrahaID,
    graha_id_to_string,
    graha_id_to_name,
    rasi_index_from_longitude,
    degree_in_rasi,
    rasi_index_to_name,
    nakshatra_from_longitude,
    nakshatra_index_to_name,
)


class CoreChartExtractor(BaseExtractor):
    """Extract core chart data (D1)"""
    
    def extract(self) -> Dict[str, Any]:
        """Extract core chart"""
        import jhora.panchanga.drik as drik
        import jhora.horoscope.chart.charts as charts
        
        # Set ayanamsa
        drik.set_ayanamsa_mode(self.config.ayanamsa_mode)
        
        # Get divisional chart (D1)
        h_to_p = charts.divisional_chart(
            self.jd,
            self.place,
            divisional_chart_factor=1,
            chart_method=1
        )
        
        # Get planet positions
        planet_positions = drik.planets(self.jd)
        
        # Get ascendant
        asc_rasi, asc_long = drik.ascendant(self.jd, self.place)
        
        # Build result
        return {
            'meta': self.create_meta('core_chart_spec_v1'),
            'person': self._build_person_section(),
            'config_echo': self.config.dict(),
            'frames': [
                self._build_d1_frame(planet_positions, asc_rasi, asc_long, h_to_p)
            ]
        }
    
    def _build_person_section(self) -> Dict[str, Any]:
        """Build person section"""
        return {
            'name': self.person.get('label'),
            'birth_date': self.dt.strftime('%Y-%m-%d'),
            'birth_time': self.dt.strftime('%H:%M:%S'),
            'timezone': self.timezone_name,
        }
    
    def _build_d1_frame(
        self,
        planet_positions: List[tuple],
        asc_rasi: int,
        asc_long: float,
        h_to_p: List[str]
    ) -> Dict[str, Any]:
        """Build D1 frame"""
        
        frame = {
            'frame_id': 'D1',
            'description': 'Natal D1 chart',
            'jd': self.jd,
            'place': {
                'latitude': self.location['lat'],
                'longitude': self.location['lon'],
                'place_name': self.location.get('name', 'Unknown'),
            },
            'ascendant': self._format_ascendant(asc_rasi, asc_long, h_to_p),
            'planets': self._format_planets(planet_positions, h_to_p),
            'houses': self._format_houses(asc_rasi, asc_long),
        }
        
        return frame
    
    def _format_ascendant(
        self,
        asc_rasi: int,
        asc_long: float,
        h_to_p: List[str]
    ) -> Dict[str, Any]:
        """Format ascendant using graha.py utilities"""
        
        # Calculate rasi
        rasi_idx = rasi_index_from_longitude(asc_long)
        degree = degree_in_rasi(asc_long)
        rasi_name = rasi_index_to_name(rasi_idx)
        
        # Calculate nakshatra
        nak_idx, pada, span = nakshatra_from_longitude(asc_long)
        nak_name = nakshatra_index_to_name(nak_idx)
        
        # Find house index (lagna is always house 1)
        house_idx = 1
        
        return {
            'longitude_deg': asc_long,
            'degree_in_sign': degree,
            'sign_index': rasi_idx,
            'sign_name': rasi_name,
            'house_index': house_idx,
            'nakshatra_index': nak_idx,
            'nakshatra_name': nak_name,
            'nakshatra_pada': pada,
        }
    
    def _format_planets(
        self,
        planet_positions: List[tuple],
        h_to_p: List[str]
    ) -> List[Dict[str, Any]]:
        """Format planets using graha.py utilities"""
        
        planets = []
        
        for planet_idx, (rasi_idx, longitude_in_rasi) in planet_positions:
            # Skip if not in include_bodies
            graha_id = GrahaID(planet_idx)
            planet_string_id = graha_id_to_string(graha_id)
            
            if planet_string_id not in self.config.include_bodies:
                continue
            
            # Calculate absolute longitude
            longitude_deg = (rasi_idx * 30) + longitude_in_rasi
            
            # Use graha.py utilities
            planet_name = graha_id_to_name(graha_id)
            sign_idx = rasi_index_from_longitude(longitude_deg)
            degree = degree_in_rasi(longitude_deg)
            sign_name = rasi_index_to_name(sign_idx)
            nak_idx, pada, span = nakshatra_from_longitude(longitude_deg)
            nak_name = nakshatra_index_to_name(nak_idx)
            
            # Calculate house index from h_to_p
            house_idx = self._find_planet_house(planet_idx, h_to_p)
            
            # Calculate speed & retrograde
            speed, retrograde = self._calculate_speed_retrograde(planet_idx)
            
            planets.append({
                'id': planet_string_id,
                'name': planet_name,
                'longitude_deg': longitude_deg,
                'degree_in_sign': degree,
                'sign_index': sign_idx,
                'sign_name': sign_name,
                'house_index': house_idx,
                'nakshatra_index': nak_idx,
                'nakshatra_name': nak_name,
                'nakshatra_pada': pada,
                'speed_deg_per_day': speed,
                'retrograde': retrograde,
            })
        
        return planets
    
    def _find_planet_house(self, planet_idx: int, h_to_p: List[str]) -> int:
        """Find which house planet is in"""
        for house_idx, occupants in enumerate(h_to_p, start=1):
            if str(planet_idx) in occupants.split('/'):
                return house_idx
        return None
    
    def _calculate_speed_retrograde(self, planet_idx: int) -> tuple:
        """Calculate planet speed and retrograde status"""
        import swisseph as swe
        
        # Swiss Ephemeris planet codes
        swe_planets = {
            0: swe.SUN,
            1: swe.MOON,
            2: swe.MARS,
            3: swe.MERCURY,
            4: swe.JUPITER,
            5: swe.VENUS,
            6: swe.SATURN,
            7: swe.MEAN_NODE,  # Rahu
            8: swe.MEAN_NODE,  # Ketu (handle separately)
        }
        
        if planet_idx not in swe_planets:
            return (0.0, False)
        
        # Calculate
        result = swe.calc_ut(self.jd, swe_planets[planet_idx])
        speed = result[0][3]  # Speed in deg/day
        retrograde = speed < 0
        
        return (round(abs(speed), 3), retrograde)
    
    def _format_houses(
        self,
        asc_rasi: int,
        asc_long: float
    ) -> List[Dict[str, Any]]:
        """Format houses (12 houses starting from ascendant)"""
        
        houses = []
        asc_degree = degree_in_rasi(asc_long)
        
        for house_idx in range(1, 13):
            # Calculate house rasi (whole sign system)
            house_rasi = (asc_rasi + house_idx - 1) % 12
            
            # House boundaries
            start_deg = house_rasi * 30
            end_deg = start_deg + 30
            cusp_deg = start_deg + asc_degree
            
            houses.append({
                'index': house_idx,
                'start_deg': start_deg,
                'end_deg': end_deg,
                'cusp_deg': cusp_deg % 360,
                'sign_index': house_rasi + 1,  # 1-based
                'sign_name': rasi_index_to_name(house_rasi + 1),
            })
        
        return houses
```

---

### 2. panchanga.py (REFACTORED)

```python
"""
Panchanga Extractor - Refactored with graha.py
"""

from .base import BaseExtractor
from ..core.graha import (
    nakshatra_index_to_name,
    nakshatra_lord,
    vaara_index_to_name,
)


class PanchangaExtractor(BaseExtractor):
    """Extract panchanga data"""
    
    def extract(self) -> Dict[str, Any]:
        """Extract panchanga"""
        import jhora.panchanga.drik as drik
        
        # Set ayanamsa
        drik.set_ayanamsa_mode(self.config.ayanamsa_mode)
        
        # Get panchanga elements
        tithi_no, tithi_name, t_start, t_end = drik.tithi(self.jd, self.place)
        nak_no, nak_name, pada, n_start, n_end = drik.nakshatra(self.jd, self.place)
        yoga_no, yoga_name, y_start, y_end = drik.yogam(self.jd, self.place)
        karana_no, karana_name, k_start, k_end = drik.karana(self.jd, self.place)
        vaara = drik.vaara(self.jd)
        
        # Get sunrise/sunset
        sunrise_jd, sunrise_str = drik.sunrise(self.jd, self.place)
        sunset_jd, sunset_str = drik.sunset(self.jd, self.place)
        
        # Get hora lord
        hora_lord = self._get_hora_lord()
        
        # Get auspicious/inauspicious windows
        auspicious = self._get_auspicious_windows()
        inauspicious = self._get_inauspicious_windows()
        
        # Build result
        return {
            'meta': self.create_meta('panchanga_spec_v1'),
            'panchanga': {
                'reference': self._build_reference(),
                'vaara': self._format_vaara(vaara),
                'tithi': self._format_tithi(tithi_no, tithi_name, t_end),
                'nakshatra': self._format_nakshatra(nak_no, pada, n_start, n_end),
                'yoga': self._format_yoga(yoga_no, yoga_name),
                'karana': self._format_karana(karana_no, karana_name),
                'hora_lord': hora_lord,
                'sunrise': self._format_time(sunrise_jd),
                'sunset': self._format_time(sunset_jd),
                'auspicious_windows': auspicious,
                'inauspicious_windows': inauspicious,
            }
        }
    
    def _build_reference(self) -> Dict[str, Any]:
        """Build reference section"""
        return {
            'datetime_utc': self.dt.isoformat(),
            'timezone': self.timezone_name,
            'location': {
                'latitude': self.location['lat'],
                'longitude': self.location['lon'],
            }
        }
    
    def _format_vaara(self, vaara_idx: int) -> Dict[str, Any]:
        """Format vaara using graha.py"""
        return {
            'index': vaara_idx,
            'name': vaara_index_to_name(vaara_idx),
        }
    
    def _format_tithi(
        self,
        tithi_no: int,
        tithi_name: str,
        end_jd: float
    ) -> Dict[str, Any]:
        """Format tithi"""
        # Calculate remaining percentage
        remaining = (end_jd - self.jd) / (end_jd - (self.jd - 1))
        
        # Determine paksha
        paksha = "SHUKLA" if tithi_no < 15 else "KRISHNA"
        
        return {
            'index': tithi_no,
            'name': tithi_name.upper(),
            'paksha': paksha,
            'remaining_percentage': remaining,
        }
    
    def _format_nakshatra(
        self,
        nak_no: int,
        pada: int,
        start_jd: float,
        end_jd: float
    ) -> Dict[str, Any]:
        """Format nakshatra using graha.py"""
        
        # Calculate span in degrees
        span_deg = (self.jd - start_jd) / (end_jd - start_jd) * 13.33333
        
        # Get nakshatra name from graha.py
        nak_name = nakshatra_index_to_name(nak_no + 1)  # graha.py uses 1-based
        
        # Get lord from graha.py
        lord_id = nakshatra_lord(nak_no)
        from ..core.graha import graha_id_to_name
        lord_name = graha_id_to_name(GrahaID(lord_id))
        
        return {
            'index': nak_no + 1,  # 1-based for output
            'name': nak_name,
            'pada': pada,
            'lord': lord_name,
            'span_deg': span_deg,
        }
    
    def _format_yoga(self, yoga_no: int, yoga_name: str) -> Dict[str, Any]:
        """Format yoga"""
        return {
            'index': yoga_no,
            'name': yoga_name.upper(),
        }
    
    def _format_karana(self, karana_no: int, karana_name: str) -> Dict[str, Any]:
        """Format karana"""
        return {
            'index': karana_no,
            'name': karana_name.upper(),
        }
    
    def _get_hora_lord(self) -> str:
        """Get current hora lord"""
        import jhora.panchanga.drik as drik
        
        hora_planet_id = drik.hora(self.jd, self.place)
        from ..core.graha import graha_id_to_name, GrahaID
        return graha_id_to_name(GrahaID(hora_planet_id))
    
    def _format_time(self, jd: float) -> str:
        """Format JD as ISO timestamp"""
        from datetime import datetime, timedelta
        import pytz
        
        # Convert JD to datetime
        base = datetime(2000, 1, 1, 12, 0, 0)
        dt = base + timedelta(days=jd - 2451545.0)
        
        # Localize to timezone
        tz = pytz.timezone(self.timezone_name)
        dt_local = pytz.utc.localize(dt).astimezone(tz)
        
        return dt_local.isoformat()
    
    def _get_auspicious_windows(self) -> List[Dict[str, Any]]:
        """Get auspicious time windows"""
        import jhora.panchanga.drik as drik
        
        # Abhijit muhurta
        abhijit = drik.abhijit_muhurta(self.jd, self.place)
        
        return [
            {
                'start': self._format_time(abhijit[0]),
                'end': self._format_time(abhijit[1]),
                'tag': 'ABHIJIT',
            }
        ]
    
    def _get_inauspicious_windows(self) -> List[Dict[str, Any]]:
        """Get inauspicious time windows"""
        import jhora.panchanga.drik as drik
        
        rahu = drik.raahu_kaalam(self.jd, self.place)
        yama = drik.yamagandam(self.jd, self.place)
        gulika = drik.gulika_kaalam(self.jd, self.place)
        
        return [
            {
                'start': self._format_time(rahu[0]),
                'end': self._format_time(rahu[1]),
                'tag': 'RAHU_KALAM',
            },
            {
                'start': self._format_time(yama[0]),
                'end': self._format_time(yama[1]),
                'tag': 'YAMAGANDA',
            },
            {
                'start': self._format_time(gulika[0]),
                'end': self._format_time(gulika[1]),
                'tag': 'GULIKAI',
            },
        ]
```

---

### 3. dashas_vimshottari.py (REFACTORED)

```python
"""
Vimshottari Dasha Extractor - Refactored with graha.py
"""

from .base import BaseExtractor
from ..core.graha import GrahaID, graha_id_to_string


class VimsottariDashaExtractor(BaseExtractor):
    """Extract Vimshottari Mahadasha periods"""
    
    def extract(self) -> Dict[str, Any]:
        """Extract dashas"""
        import jhora.horoscope.dhasa.graha.vimsottari as vim
        import jhora.panchanga.drik as drik
        
        # Set ayanamsa
        drik.set_ayanamsa_mode(self.config.ayanamsa_mode)
        
        # Calculate Vimshottari
        dasha_periods = vim.vimsottari_dhasa(self.jd, self.place)
        
        # Find current mahadasha
        current_planet = self._find_current_mahadasha(dasha_periods)
        
        # Build result
        return {
            'meta': self._build_meta(current_planet),
            'person': self._build_person(),
            'config_echo': self.config.dict(),
            'frames': [
                self._build_mahadasha_frame(dasha_periods, current_planet)
            ]
        }
    
    def _build_meta(self, current_planet: str) -> Dict[str, Any]:
        """Build meta with current mahadasha"""
        meta = self.create_meta('dashas_vimshottari_spec_v1')
        meta['engine'] = {
            'name': 'PyJHora',
            'version': '4.5.5',
        }
        meta['current_mahadasha'] = current_planet
        return meta
    
    def _build_person(self) -> Dict[str, Any]:
        """Build person section"""
        return {
            'id': self.person.get('id'),
            'label': self.person.get('label'),
            'name': self.person.get('label'),
            'birth_date': self.dt.strftime('%Y-%m-%d'),
            'birth_time': self.dt.strftime('%H:%M:%S'),
            'timezone': self.timezone_name,
        }
    
    def _build_mahadasha_frame(
        self,
        dasha_periods: List[tuple],
        current_planet: str
    ) -> Dict[str, Any]:
        """Build mahadasha frame"""
        
        periods = []
        
        for order_idx, (planet_id, start_jd, duration_years) in enumerate(dasha_periods):
            # Use graha.py for planet ID
            planet_string_id = graha_id_to_string(GrahaID(planet_id))
            
            # Calculate end JD
            end_jd = start_jd + (duration_years * 365.25)
            
            # Check if current
            is_current = (planet_string_id == current_planet)
            
            periods.append({
                'order_index': order_idx,
                'planet_id': planet_string_id,
                'start': self._jd_to_iso(start_jd),
                'end': self._jd_to_iso(end_jd),
                'duration_years': duration_years,
                'is_current': is_current,
            })
        
        return {
            'frame_id': 'VIMSOTTARI_MAHADASHA',
            'description': 'Chronological Vimshottari Mahadasha periods',
            'levels': [
                {
                    'level': 'MAHADASHA',
                    'periods': periods,
                }
            ]
        }
    
    def _find_current_mahadasha(self, dasha_periods: List[tuple]) -> str:
        """Find current mahadasha planet"""
        for planet_id, start_jd, duration_years in dasha_periods:
            end_jd = start_jd + (duration_years * 365.25)
            if start_jd <= self.jd < end_jd:
                return graha_id_to_string(GrahaID(planet_id))
        return "UNKNOWN"
    
    def _jd_to_iso(self, jd: float) -> str:
        """Convert JD to ISO timestamp"""
        from datetime import datetime, timedelta
        
        base = datetime(2000, 1, 1, 12, 0, 0)
        dt = base + timedelta(days=jd - 2451545.0)
        
        return dt.isoformat() + '+00:00'
```

---

### 4. strengths.py (REFACTORED)

```python
"""
Strengths Extractor - Refactored with graha.py
"""

from .base import BaseExtractor
from ..core.graha import GrahaID, graha_id_to_string


class StrengthsExtractor(BaseExtractor):
    """Extract planetary strengths (Shadbala)"""
    
    def extract(self) -> Dict[str, Any]:
        """Extract strengths"""
        import jhora.horoscope.chart.strength as strength
        import jhora.panchanga.drik as drik
        
        # Set ayanamsa
        drik.set_ayanamsa_mode(self.config.ayanamsa_mode)
        
        # Calculate Shadbala
        shadbala_dict = strength.shadbala(self.jd, self.place)
        
        # Build result
        return {
            'meta': self._build_meta(),
            'person': self._build_person(),
            'config_echo': self.config.dict(),
            'frames': self._build_frames(shadbala_dict),
        }
    
    def _build_meta(self) -> Dict[str, Any]:
        """Build meta"""
        meta = self.create_meta('strengths_spec_v1')
        meta['engine'] = {
            'name': 'PyJHora',
            'version': '4.5.5',
        }
        meta['extractor'] = 'strengths'
        return meta
    
    def _build_person(self) -> Dict[str, Any]:
        """Build person section"""
        return {
            'id': self.person.get('id'),
            'label': self.person.get('label'),
            'birth_date': self.dt.strftime('%Y-%m-%d'),
            'birth_time': self.dt.strftime('%H:%M:%S'),
        }
    
    def _build_frames(self, shadbala_dict: Dict[int, Dict]) -> Dict[str, Any]:
        """Build frames"""
        
        planets = []
        strong_planets = []
        weak_planets = []
        
        # Standard planet sequence
        PLANET_SEQUENCE = [
            GrahaID.SUN,
            GrahaID.MOON,
            GrahaID.MARS,
            GrahaID.MERCURY,
            GrahaID.JUPITER,
            GrahaID.VENUS,
            GrahaID.SATURN,
        ]
        
        for graha_id in PLANET_SEQUENCE:
            planet_string_id = graha_id_to_string(graha_id)
            
            if graha_id.value not in shadbala_dict:
                continue
            
            strength_data = shadbala_dict[graha_id.value]
            total = strength_data.get('total', 0)
            
            # Calculate strength ratio (total / required minimum)
            required_minimum = self._get_required_minimum(graha_id)
            ratio = total / required_minimum if required_minimum > 0 else 0
            
            planets.append({
                'planet_id': planet_string_id,
                'total_shadbala': round(total, 2),
                'strength_ratio': round(ratio, 2),
            })
            
            # Classify
            if ratio >= 1.0:
                strong_planets.append(planet_string_id)
            else:
                weak_planets.append(planet_string_id)
        
        return {
            'planets': planets,
            'summary': {
                'strong_planets': strong_planets,
                'weak_planets': weak_planets,
            }
        }
    
    def _get_required_minimum(self, graha_id: GrahaID) -> float:
        """Get required minimum shadbala for planet"""
        # Standard requirements (in rupas)
        requirements = {
            GrahaID.SUN: 300,
            GrahaID.MOON: 360,
            GrahaID.MARS: 300,
            GrahaID.MERCURY: 420,
            GrahaID.JUPITER: 390,
            GrahaID.VENUS: 330,
            GrahaID.SATURN: 300,
        }
        return requirements.get(graha_id, 300)
```

---

**ادامه در فایل بعدی (Implementation Plan)...**
