# PyJHora Structural Map for Extractor Design

## 1. Meta & Overview

- **Version**: UNKNOWN
- **Engine scope**: Panchanga core, divisional charts, dashas, strengths, yogas, match, transit, prediction, UI helpers
- **Default ayanamsa**: LAHIRI
- **Safe entry points**: see section 16

---
## 2. Package Structure Tree

- `jhora`
  - `_package_info`
  - `const`
  - `horoscope`
    - `chart`
      - `arudhas`
      - `ashtakavarga`
      - `charts`
      - `dosha`
      - `house`
      - `raja_yoga`
      - `sphuta`
      - `strength`
      - `yoga`
    - `dhasa`
      - `annual`
        - `mudda`
        - `patyayini`
      - `graha`
        - `aayu`
        - `applicability`
        - `ashtottari`
        - `buddhi_gathi`
        - `chathuraaseethi_sama`
        - `dwadasottari`
        - `dwisatpathi`
        - `kaala`
        - `karaka`
        - `karana_chathuraaseethi_sama`
        - `naisargika`
        - `panchottari`
        - `saptharishi_nakshathra`
        - `sataatbika`
        - `shastihayani`
        - `shattrimsa_sama`
        - `shodasottari`
        - `tara`
        - `tithi_ashtottari`
        - `tithi_yogini`
        - `vimsottari`
        - `yoga_vimsottari`
        - `yogini`
      - `raasi`
        - `brahma`
        - `chakra`
        - `chara`
        - `drig`
        - `kalachakra`
        - `kendradhi_rasi`
        - `lagnamsaka`
        - `mandooka`
        - `moola`
        - `narayana`
        - `navamsa`
        - `nirayana`
        - `padhanadhamsa`
        - `paryaaya`
        - `sandhya`
        - `shoola`
        - `sthira`
        - `sudasa`
        - `tara_lagna`
        - `trikona`
        - `varnada`
        - `yogardha`
      - `sudharsana_chakra`
    - `main`
    - `match`
      - `compatibility`
    - `prediction`
      - `general`
      - `longevity`
      - `naadi_marriage`
    - `transit`
      - `saham`
      - `tajaka`
      - `tajaka_yoga`
  - `panchanga`
    - `drik`
    - `drik1`
    - `khanda_khaadyaka`
    - `pancha_paksha`
    - `pancha_paksha - Copy`
    - `surya_sidhantha`
    - `vratha`
  - `setup`
  - `tests`
    - `book_chart_data`
    - `pvr_tests`
    - `test_ss`
    - `test_ui`
    - `test_yogas`
  - `ui`
    - `chakra`
    - `chart_styles`
    - `conjunction_dialog`
    - `dhasa_bhukthi_options_dialog`
    - `horo_chart`
    - `horo_chart_tabs`
    - `label_grid`
    - `match_ui`
    - `mixed_chart_dialog`
    - `options_dialog`
    - `pancha_pakshi_sastra_widget`
    - `panchangam`
    - `test`
    - `test1`
    - `test2`
    - `vakra_gathi_plot`
    - `varga_chart_dialog`
    - `vedic_calendar`
    - `vedic_clock`
    - `vratha_finder`
  - `utils`

---
## 3. Core Primitives & Defaults

### Planets
| Index | Name |
|---:|---|
| 0 | (12, 1) |
| 1 | (22, -1) |
| 2 | (3, 1) |
| 3 | (7, -1) |
| 4 | (6, 1) |
| 5 | (5, -1) |
| 6 | (8, 1) |
| 7 | (9, -1) |
| 8 | (9, -1) |

### Rasis (Signs)
| Index | Name |
|---:|---|
| 1 | 3 |
| 2 | 4 |
| 3 | 5 |
| 4 | 6 |
| 5 | 7 |
| 6 | 8 |

### Varga options
| ID | Description | Divisor | Implemented |
|---|---|---:|---|
| D1 | Divisional chart D1 | 1 | True |
| D2 | Divisional chart D2 | 2 | True |
| D3 | Divisional chart D3 | 3 | True |
| D4 | Divisional chart D4 | 4 | True |
| D5 | Divisional chart D5 | 5 | True |
| D6 | Divisional chart D6 | 6 | True |
| D7 | Divisional chart D7 | 7 | True |
| D8 | Divisional chart D8 | 8 | True |
| D9 | Divisional chart D9 | 9 | True |
| D10 | Divisional chart D10 | 10 | True |
| D11 | Divisional chart D11 | 11 | True |
| D12 | Divisional chart D12 | 12 | True |
| D16 | Divisional chart D16 | 16 | True |
| D20 | Divisional chart D20 | 20 | True |
| D24 | Divisional chart D24 | 24 | True |
| D27 | Divisional chart D27 | 27 | True |
| D30 | Divisional chart D30 | 30 | True |
| D40 | Divisional chart D40 | 40 | True |
| D45 | Divisional chart D45 | 45 | True |
| D60 | Divisional chart D60 | 60 | True |
| D81 | Divisional chart D81 | 81 | True |
| D108 | Divisional chart D108 | 108 | True |
| D144 | Divisional chart D144 | 144 | True |

### Ayanamsa modes
| Index | Name | Value |
|---:|---|---|
| 0 | Fagan | 0 |
| 1 | Lahiri | 1 |
| 2 | Raman | 3 |
| 3 | Ushashashi | 4 |
| 4 | Kp | 5 |
| 5 | Yukteshwar | 7 |
| 6 | Suryasiddhanta | 21 |
| 7 | Suryasiddhanta Msun | 22 |
| 8 | Aryabhata | 23 |
| 9 | Aryabhata Msun | 24 |
| 10 | Ss Revati | 25 |
| 11 | Ss Citra | 26 |
| 12 | True Citra | 27 |
| 13 | True Lahiri | 27 |
| 14 | True Revati | 28 |
| 15 | True Pushya | 29 |
| 16 | True Mula | 35 |
| 17 | Kp-senthil | 45 |
| 18 | Sidm User | 255 |
| 19 | Senthil |  |
| 20 | Sundar Ss |  |

### House systems
| ID | Name | Tradition |
|---|---|---|
| 1 | Equal Housing - Lagna in the middle | Indian |
| 2 | Equal Housing - Lagna as start | Indian |
| 3 | Sripati method | Indian |
| 4 | KP Method (aka Placidus Houses method) | Indian |
| 5 | Each Rasi is the house | Indian |
| P | Placidus | Western |
| K | Koch | Western |
| O | Porphyrius | Western |
| R | Regiomontanus | Western |
| C | Campanus | Western |
| A | Equal (cusp 1 is Ascendant) | Indian |
| V | Vehlow equal (Asc. in middle of house 1) | Indian |
| X | axial rotation system | Unknown |
| H | azimuthal or horizontal system | Western |
| T | Polich/Page (topocentric system) | Western |
| B | Alcabitus | Western |
| M | Morinus | Western |

Place structure used across modules:
```py
Place(name: str, latitude: float, longitude: float, timezone: float, elevation: float = None)
```

---
## 4. Panchanga Engine

- **Modules**: jhora.panchanga, jhora.panchanga.drik, jhora.panchanga.drik1, jhora.panchanga.khanda_khaadyaka, jhora.panchanga.pancha_paksha, jhora.panchanga.pancha_paksha - Copy, jhora.panchanga.surya_sidhantha, jhora.panchanga.vratha
- **Default ayanamsa binding**: uses `_DEFAULT_AYANAMSA_MODE` and exposes `set_ayanamsa_mode` for runtime adjustments.
- Functions cover sunrise/sunset, lunar/tamil months, samvatsara, tithi/nakshatra/yoga/karana, special lagnas, upagrahas, event scanning, festival/vratha lists, conjunction/transit helpers.
### Planetary & positional data
Longitude, speed, ascendant, declination, retrograde timings.
| Function | Signature | Doc |
|---|---|---|
| `abhijit_muhurta` | `(jd, place)` | Get Abhijit muhurta timing for the given julian day |
| `ascendant` | `(jd, place)` | Compute Lagna (=ascendant) position/longitude at any given time & place |
| `bhaava_madhya` | `(jd, place, bhava_method=1)` | returns house longitudes |
| `bhaava_madhya_kp` | `(jd, place)` | Compute the mid angle / cusp of each of each house. |
| `bhaava_madhya_swe` | `(jd, place, house_code='P')` | Acceptable house system codes in Swiss Ephemeris |
| `bhrigu_bindhu_lagna` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of bhrigu bindhu lagna |
| `dasavarga_from_long` | `(longitude, divisional_chart_factor=1)` | Calculates the dasavarga-sign in which given longitude falls |
| `day_length` | `(jd, place)` | Return local day length in float hours |
| `declination_of_planets` | `(jd, place)` | return declination of planets |
| `dhasavarga` | `(jd, place, divisional_chart_factor=1)` | Calculate planet positions for a given divisional chart index |
| `durmuhurtam` | `(jd, place)` | Get dhur muhurtham timing for the given julian day |
| `gauri_choghadiya` | `(jd, place)` | Get end times of gauri chogadiya for the given julian day |
| `graha_drekkana` | `(jd, place, use_bv_raman_table=False)` |  |
| `indu_lagna` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of indu lagna |
| `karaka_yogam` | `(jd, place)` | returns the yogam at julian day/time |
| `karana` | `(jd, place)` | returns the karanam of the day |
| `kunda_lagna` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of kunda lagna |
| `lunar_month` | `(jd, place)` | Returns lunar month and if it is adhika or not. |
| `lunar_month_date` | `(jd, place, use_purnimanta_system=False)` | Returns lunar month, lunar day and if it is adhika or not. |
| `midday` | `(jd, place)` | Return midday time |
| `midnight` | `(jd, place)` | Return midnight time |
| `moonrise` | `(jd, place)` | Return local moonrise time |
| `moonset` | `(jd, place)` | Return local moonset time |
| `nakshatra` | `(jd, place)` | returns the nakshathra at julian day/time |
| `nakshatra_new` | `(jd, place)` | returns the nakshathra at julian day/time |
| `nakshatra_pada` | `(longitude)` | Gives nakshatra (1..27) and paada (1..4) in which given longitude lies |
| `navamsa_from_long_old` | `(longitude)` | Calculates the navamsa-sign in which given longitude falls |
| `next_ascendant_entry_date` | `(jd, place, direction=1, precision=1.0, raasi=None, divisional_chart_factor=1)` | get the date when the ascendant enters a zodiac |
| `next_conjunction_of_planet_pair` | `(jd, panchanga_place: jhora.panchanga.drik.Place, p1, p2, direction=1, separation_angle=0, increment_speed_factor=0.25)` | get the date when conjunction of given two planets occur |
| `next_lunar_eclipse` | `(jd, place)` | @param jd: Julian number  |
| `next_planet_entry_date` | `(planet, jd, place, direction=1, increment_days=0.01, precision=0.1, raasi=None)` | get the date when a planet enters a zodiac |
| `next_planet_retrograde_change_date` | `(planet, panchanga_date, place, increment_days=1, direction=1)` | get the date when a retrograde planet changes its direction |
| `next_sankranti_date` | `(panchanga_date, place)` | Get the next sankranti date (sun entry to a raasi) |
| `next_solar_date` | `(jd_at_dob, place, years=1, months=1, sixty_hours=1)` | returns the next date at which sun's longitue is same as at jd_at_dob (at birth say) |
| `next_solar_eclipse` | `(jd, place)` | @param jd: Julian number  |
| `night_length` | `(jd, place)` | Return local night length in float hours |
| `planetary_positions` | `(jd, place)` | Computes instantaneous planetary positions (i.e., which celestial object lies in which constellation) |
| `planets_in_graha_yudh` | `(jd, place)` | Graha Yudh |
| `planets_in_retrograde` | `(jd, place)` | To get the list of retrograding planets |
| `planets_speed_info` | `(jd, place)` | To get the speed information of planets |
| `pranapada_lagna` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of pranapada lagna |
| `previous_ascendant_entry_date` | `(jd, place, increment_days=0.01, precision=0.1, raasi=None, divisional_chart_factor=1)` |  |
| `previous_conjunction_of_planet_pair` | `(jd, panchanga_place: jhora.panchanga.drik.Place, p1, p2, separation_angle=0, increment_speed_factor=0.25)` |  |
| `previous_planet_entry_date` | `(planet, jd, place, increment_days=0.01, precision=0.1, raasi=None)` |  |
| `previous_sankranti_date` | `(panchanga_date, place)` | Get the previous sankranti date (sun entry to a raasi) |
| `raasi` | `(jd, place)` | returns the raasi at julian day/time |
| `samvatsara` | `(panchanga_date, place, zodiac=0)` | Returns Shaka Samvatsara |
| `set_sideral_planets` | `()` |  |
| `set_tropical_planets` | `()` |  |
| `shubha_hora` | `(jd, place)` | Get end times of Shubha Hora for the given julian day |
| `sidereal_longitude` | `(jd_utc, planet)` | The sequence number of 0 to 8 for planets is not followed by swiss ephemeris |
| `solar_upagraha_longitudes` | `(solar_longitude, upagraha, divisional_chart_factor=1)` | Get logitudes of solar based upagrahas |
| `special_ascendant` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, lagna_rate_factor=1.0, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of special lagnas (Bhava,Hora,Ghati,vighati) |
| `special_ascendant_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1, lagna_rate_factor=1.0)` |  |
| `sree_lagna` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` | Get constellation and longitude of Sree Lagna |
| `sree_lagna_from_moon_asc_longitudes` | `(moon_longitude, ascendant_longitude, divisional_chart_factor=1)` |  |
| `sunrise` | `(jd, place)` | Sunrise when centre of disc is at horizon for given date and place |
| `sunset` | `(jd, place, gauri_choghadiya_setting=False)` | Sunset when centre of disc is at horizon for given date and place |
| `tamil_solar_month_and_date` | `(panchanga_date, place, tamil_month_method=3, base_time=0, use_utc=True)` | Returns tamil month and date (e.g. Aadi 28 ) |
| `tamil_solar_month_and_date_V4_3_5` | `(panchanga_date, place)` | Returns tamil month and date (e.g. Aadi 28 ) |
| `tamil_solar_month_and_date_V4_3_8` | `(panchanga_date, place)` | Returns tamil month and date (e.g. Aadi 28 ) |
| `tithi` | `(jd, place, tithi_index=1, planet1=1, planet2=0, cycle=1)` | Tithi given jd and place. Also returns tithi's end time. |
| `tithi_using_inverse_lagrange` | `(jd, place, tithi_index=1, planet1=1, planet2=0, cycle=1)` | Tithi given jd and place. Also returns tithi's end time. |
| `tithi_using_planet_speed` | `(jd, place, tithi_index=1, planet1=1, planet2=0, cycle=1)` |  |
| `trikalam` | `(jd, place, option='raahu kaalam')` | Get tri kaalam (Raahu kaalam, yama kandam and Kuligai Kaalam) for the given Julian day |
| `udhaya_lagna_muhurtha` | `(jd, place)` | returns ascendant entry jd into each of 12 rasis from given date/time |
| `upagraha_longitude` | `(dob, tob, place, planet_index, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, upagraha_part='middle')` | get upagraha longitude from dob,tob, place-lat/long and day/night ruling planet's part |
| `vedic_date` | `(jd, place, calendar_type=0, tamil_month_method=3, base_time=0, use_utc=True)` | Returns lunar month, lunar day and if it is adhika or not. and the vedic year |
| `yogam_old` | `(jd, place, planet1=1, planet2=0, tithi_index=1, cycle=1)` | returns the yogam at julian day/time |

### Tithi/Nakshatra/Yoga basics
Core panchanga essentials and paksha/vaara markers.
| Function | Signature | Doc |
|---|---|---|
| `aadal_yoga` | `(jd, place)` |  |
| `amrita_gadiya` | `(jd, place)` | Ref: Panchangam Calculations: Karanam Ramakumar |
| `anandhaadhi_yoga` | `(jd, place)` |  |
| `karaka_tithi` | `(jd, place)` |  |
| `next_panchaka_days` | `(jd, place)` | Added in V4.2.6 |
| `next_tithi` | `(jd, place, required_tithi, opt=1, start_of_tithi=True)` | TODO: UNDER EXPERIMENTATION |
| `pushkara_yoga` | `(jd, place)` | returns dwi/tri pushkara yoga if exists |
| `shiva_vaasa` | `(jd, place, method=2)` | Ref: https://vijayalur.com/2014/07/24/shiva-agni-vasa/ |
| `tamil_yogam` | `(jd, place, check_special_yogas=True, use_sringeri_panchanga_version=False)` | @return tamil yoga index |
| `vaara` | `(jd)` | Weekday for given Julian day.  |
| `varjyam` | `(jd, place)` | Ref: Panchangam Calculations: Karanam Ramakumar |
| `vidaal_yoga` | `(jd, place)` |  |
| `yogam` | `(jd, place, tithi_index=1, planet1=1, planet2=0, cycle=1)` |  |

### Calendar/season helpers
Lunar/tamil month math, ritus, samvatsara, vedic dates, festival search.
| Function | Signature | Doc |
|---|---|---|
| `days_in_tamil_month` | `(panchanga_date, place)` | get # of days in that tamil month |
| `elapsed_year` | `(jd, maasa_index)` | returns Indian era/epoch year indices (kali year number, saka year and vikrama year numbers) |
| `float_hours_to_vedic_time` | `(jd, place, float_hours=None, force_equal_day_night_ghati=False, vedic_hours_per_day=60)` | @param vedic_hours_per_day = 30 (Muhurthas) or 60 (Ghati) |
| `float_hours_to_vedic_time_equal_day_night_ghati` | `(jd, place, float_hours=None, vedic_hours_per_day=60)` | @param vedic_hours_per_day = 30 (Muhurthas) or 60 (Ghati) |
| `next_lunar_month` | `(jd, place, lunar_month_type=0, direction=1)` | @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month |
| `next_lunar_year` | `(jd, place, lunar_month_type=0, direction=1)` | @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month |
| `panchaka_rahitha` | `(jd, place)` |  |
| `previous_lunar_month` | `(jd, place, lunar_month_type=0, direction=-1)` | @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month |
| `previous_lunar_year` | `(jd, place, lunar_month_type=0)` | @param lunar_month_type: 0=>Amantha 1=>Purnimantha 2=>Solar month |
| `ritu` | `(maasa_index)` | returns ritu / season index.  |
| `tamil_jaamam` | `(jd, place)` | In Tamil 1 jaamam = 3 muhurthas. 10 jaamam = 1 day (5 jaamam) and night (5 jaamam) |
| `tamil_solar_month_and_date_RaviAnnnaswamy` | `(panchanga_date, place)` |  |
| `tamil_solar_month_and_date_from_jd` | `(jd, place)` |  |
| `tamil_solar_month_and_date_new` | `(panchanga_date, place, base_time=0, use_utc=True)` | @param base_time: 0 => sunset time, 1 => sunrise time 2 => midday time |

### Special lagnas & upagrahas
Bhrigu bindu, vighati/pranapada, indu, maandi, shiva vaasa, upagraha longitudes.
| Function | Signature | Doc |
|---|---|---|
| `bhrigu_bindhu_lagna_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1, lagna_rate_factor=1.0)` |  |
| `indu_lagna_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `kunda_lagna_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `pranapada_lagna_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `sree_lagna_mixed_chart` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1, lagna_rate_factor=1.0)` |  |

### Event & transit search
Sankranti, conjunctions, planet entries, eclipses, sankatahara.
| Function | Signature | Doc |
|---|---|---|
| `is_solar_eclipse` | `(jd, place)` |  |
| `next_annual_solar_date_approximate` | `(dob, tob, years)` |  |
| `next_solar_month` | `(jd, place, raasi=None)` | Next solar month is when Sun Enters a next zodiac/raasi |
| `next_solar_year` | `(jd, place)` | Next solar month is when Sun Enters Aries |
| `previous_solar_month` | `(jd, place, raasi=None)` | Previous solar month is when Sun Enters a previous/current zodiac/raasi |
| `previous_solar_year` | `(jd, place)` | Previous solar month is when Sun Enters Aries |

### Festivals & vrathas
Aggregators for pradosham, amavasya, ekadashi, manvaadhi, ashtaka, srartha, chandradharshan.
| Function | Signature | Doc |
|---|---|---|
| `chandrabalam` | `(jd, place)` |  |
| `chandrashtama` | `(jd, place)` |  |

### Additional helpers
Other public utilities surfaced by the module.
| Function | Signature | Doc |
|---|---|---|
| `<lambda>` | `(sun_long)` |  |
| `<lambda>` | `(sun_long)` |  |
| `<lambda>` | `(sun_long)` |  |
| `<lambda>` | `(sun_long)` |  |
| `<lambda>` | `(sun_long)` |  |
| `agni_vaasa` | `(jd, place)` | @return agni_vaasa_index  |
| `<lambda>` | `(jd)` |  |
| `amrit_kaalam` | `(jd, place)` |  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `bhaava_madhya_sripathi` | `(jd, place)` |  |
| `<lambda>` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `<lambda>` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `brahma_muhurtha` | `(jd, place)` |  |
| `<lambda>` | `(jd, place)` |  |
| `<lambda>` | `(jd, place, planet)` |  |
| `<lambda>` | `(jd, place)` |  |
| `disha_shool` | `(jd)` |  |
| `<lambda>` | `(planet)` |  |
| `fraction_moon_yet_to_traverse` | `(jd, place, round_to_digits=5)` |  |
| `full_moon` | `(jd, tithi_, opt=-1)` | Returns JDN, where |
| `get_ayanamsa_value` | `(jd)` | Get ayanamsa value for the julian day number |
| `<lambda>` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `<lambda>` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `godhuli_muhurtha` | `(jd, place)` |  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `<lambda>` | `(jd, place)` |  |
| `<lambda>` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `<lambda>` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `<lambda>` | `(jd)` |  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `<lambda>` | `(jd)` |  |
| `<lambda>` | `(rahu)` |  |
| `<lambda>` | `(jd)` |  |
| `lunar_phase` | `(jd, tithi_index=1)` |  |
| `lunar_year_index` | `(jd, maasa_index)` | TODO: Need to investigate the following patching stuff  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `muhurthas` | `(jd, place)` |  |
| `nava_thaara` | `(jd, place, from_lagna_or_moon=0)` |  |
| `<lambda>` | `(longitude)` |  |
| `new_moon` | `(jd, tithi_, opt=-1)` | Returns JDN, where |
| `nishita_kaala` | `(jd, place)` | Eighth muhurtha of the night |
| `nishita_muhurtha` | `(jd, place)` | 2 ghathis around midnight |
| `<lambda>` | `(jd, place)` |  |
| `<lambda>` | `(ketu)` |  |
| `<lambda>` | `()` |  |
| `sahasra_chandrodayam` | `(jd, place)` |  |
| `sahasra_chandrodayam_old` | `(dob, tob, place)` | TODO: Does not support BCE dates as ephem supports only datetime |
| `sandhya_periods` | `(jd, place)` | returns three sandhya periods: - each (Ghati is 1/30th of day length) |
| `set_ayanamsa_mode` | `(ayanamsa_mode='LAHIRI', ayanamsa_value=None, jd=None)` | Set Ayanamsa mode |
| `<lambda>` | `(jd)` |  |
| `special_thaara` | `(jd, place, from_lagna_or_moon=0)` | Note: the star list includes Abhijith as 21st star |
| `<lambda>` | `(jd, place)` |  |
| `namedtuple` | `(typename, field_names, *, rename=False, defaults=None, module=None)` | Returns a new subclass of tuple with named fields. |
| `thaaraabalam` | `(jd, place, return_only_good_stars=True)` | thaarabalam_names = [('Paramitra','Good'),('Janma','Not Good'),('Sampatha','Very Good'),('Vipatha','Bad'), |
| `triguna` | `(jd, place)` |  |
| `<lambda>` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `<lambda>` | `(jd, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `vijaya_muhurtha` | `(jd, place)` |  |
| `vivaha_chakra_palan` | `(jd, place)` |  |
| `<lambda>` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1)` |  |
| `<lambda>` | `(jd, place)` |  |
| `yogini_vaasa` | `(jd, place)` |  |


### `jhora.panchanga.vratha` overview
- Handles pradosham, sankranti, amavasya/pournami, ekadashi, srartha, sankatahara, shivarathri, moondraam pirai, festivals, festivals CSV based lookups.
| Function | Signature | Doc |
|---|---|---|
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `chandra_dharshan_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `conjunctions` | `(panchanga_place, panchanga_start_date, panchanga_end_date, minimum_separation_longitude, planets_in_same_house=False)` |  |
| `durgashtami_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `get_festival` | `(tithi=None, nakshatra=None, tamil_month=None, tamil_day=None, vaara=None, adhik_maasa=None)` | TODO: Mahalaya Paksha dates cannot be checked directly. |
| `get_festivals_between_the_dates` | `(start_date: jhora.panchanga.drik.Date, end_date: jhora.panchanga.drik.Date, place: jhora.panchanga.drik.Place, festival_name_contains=None)` |  |
| `get_festivals_of_the_day` | `(jd, place, festival_name_contains=None)` |  |
| `kaalashtami_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `load_festival_data` | `(file_path='D:\\Pyjhora\\PyJHora_broken_backup\\src\\jhora\\data\\hindu_festivals_multilingual_unicode_bom.csv')` |  |
| `mahalaya_paksha_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `moondraam_pirai_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `nakshathra_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None, nakshathra_index_list=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `pradosham_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `sankranti_dates` | `(place, start_date, end_date=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `sathyanarayana_puja_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `search` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None, tithi_index=None, nakshathra_index=None, yoga_index=None, tamil_month_index=None, description='', festival_name_contains=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `special_vratha_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None, vratha_type=None, vratha_index_list=None)` | Find vratha dates between dates |
| `srartha_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date)` |  |
| `tithi_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None, tithi_index_list=None, tag_t='')` | TODO For Amavasya select Date that has amavasya spreads in the afternoon |
| `tithi_pravesha` | `(birth_date: jhora.panchanga.drik.Date = None, birth_time: tuple = None, birth_place: jhora.panchanga.drik.Place = None, year_number=None, plus_or_minus_duration_in_days=30)` | Find tithi pravesha - current date with same tithi and lunar month as birth tithi/lunar_month |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |
| `yoga_dates` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None, yoga_index_list=None, tag_y='')` |  |
| `<lambda>` | `(panchanga_place, panchanga_start_date, panchanga_end_date=None)` |  |

---
## 5. Chart Modules & Strengths

- **Chart modules discovered**: jhora.horoscope.chart, jhora.horoscope.chart.arudhas, jhora.horoscope.chart.ashtakavarga, jhora.horoscope.chart.charts, jhora.horoscope.chart.dosha, jhora.horoscope.chart.house, jhora.horoscope.chart.raja_yoga, jhora.horoscope.chart.sphuta, jhora.horoscope.chart.strength, jhora.horoscope.chart.yoga
### `jhora.horoscope.chart.charts`
- TODO: Custom Divisional Chart with following options:
| Function | Signature | Doc |
|---|---|---|
| `akshavedamsa_chart` | `(planet_positions_in_rasi, chart_method=1)` | Akshavedamsa Chart - D45 Chart |
| `ashtamsa_chart` | `(planet_positions_in_rasi, chart_method=1)` | Ashtamsa Chart - D8 Chart |
| `ashtotharamsa_chart` | `(planet_positions_in_rasi, chart_method=1)` | Ashtotharamsa Chart - D108 Chart |
| `benefics` | `(jd, place, method=2, ayanamsa_mode='LAHIRI', exclude_rahu_ketu=False)` | From BV Raman - Hindu Predictive Astrology - METHOD=1 |
| `benefics_and_malefics` | `(jd, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, method=2, exclude_rahu_ketu=False)` | From BV Raman - Hindu Predictive Astrology - METHOD=1 |
| `bhava_chart` | `(jd, place, ayanamsa_mode='LAHIRI', bhava_madhya_method=1)` | @return: [[house1_rasi,(house1_start,house1_cusp,house1_end),[planets_in_house1]],(...), |
| `bhava_chart_houses` | `(jd_at_dob, place_as_tuple, ayanamsa_mode='LAHIRI', years=1, months=1, sixty_hours=1, calculation_type='drik', bhava_starts_with_ascendant=False)` | Get Bhava chart from Rasi / D1 Chart |
| `bhava_houses` | `(jd, place, ayanamsa_mode='LAHIRI', bhava_starts_with_ascendant=False)` |  |

### `jhora.horoscope.chart.house`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `<lambda>` | `(raasi)` |  |
| `aspected_houses_of_the_planet` | `(house_to_planet_dict, planet, separator='/')` | Uses Graha Drishti |
| `aspected_houses_of_the_raasi` | `(house_to_planet_dict, raasi, separator='/')` | get aspected houses of the given rasi from the chart |
| `aspected_kendras_of_raasi` | `(raasi, reverse_direction=False)` | @param raasi: 0 .. 11 |
| `aspected_planets_of_the_planet` | `(house_to_planet_dict, planet, separator='/')` | Uses Graha Drishti |
| `aspected_planets_of_the_raasi` | `(house_to_planet_dict, raasi, separator='/')` | get planets, from the raasi drishti from the chart, that has drishti on the given raasi |
| `aspected_raasis_of_the_raasi` | `(house_to_planet_dict, raasi, separator='/')` | get aspected raasis of the given rasi from the chart |
| `aspected_rasis_of_the_planet` | `(house_to_planet_dict, planet, separator='/')` | Uses Graha Drishti |

### `jhora.horoscope.chart.ashtakavarga`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `get_ashtaka_varga` | `(house_to_planet_list)` | get binna, samudhaya and prastara varga from the given horoscope chart |
| `<lambda>` | `(planet, planet_positions_in_chart)` |  |
| `sodhaya_pindas` | `(binna_ashtaka_varga, house_to_planet_chart)` | Get sodhaya pindas from binna ashtaka varga |

### `jhora.horoscope.chart.dosha`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `ganda_moola` | `(moon_star)` |  |
| `get_dosha_details` | `(jd_at_dob, place_as_tuple, language='en')` |  |
| `get_dosha_resources` | `(language='en')` | get yoga names from yoga_msgs_<lang>.txt |
| `ghata` | `(planet_positions)` | Mars/Saturn conjunction results in ghata dosha |
| `guru_chandala_dosha` | `(planet_positions)` | returns True/False if guru chandal dosha presents in the chart |
| `kala_sarpa` | `(house_to_planet_list)` | Returns kala Sarpa Dosha True or False  |
| `kalathra` | `(planet_positions, reference_planet='L')` | The placement of malefic planets Mars, Saturn, Sun, Rahu, and Ketu in the  |
| `manglik` | `(planet_positions, manglik_reference_planet='L', include_lagna_house=False, include_2nd_house=True, apply_exceptions=True)` | Sanjay Rath (https://srath.com/jyoti%E1%B9%A3a/amateur/ma%E1%B9%85galika-do%E1%B9%A3a/) |

### `jhora.horoscope.chart.raja_yoga`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `check_other_raja_yoga_1` | `(jd, place, divisional_chart_factor=1)` |  |
| `check_other_raja_yoga_2` | `(jd, place, divisional_chart_factor=1)` |  |
| `check_other_raja_yoga_3` | `(jd, place, divisional_chart_factor=1)` |  |
| `dharma_karmadhipati_raja_yoga` | `(p_to_h, raja_yoga_planet1, raja_yoga_planet2)` | Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords |
| `dharma_karmadhipati_raja_yoga_from_planet_positions` | `(planet_positions, raja_yoga_planet1, raja_yoga_planet2)` | Dharma-Karmadhipati Yoga: This is a special case of the above yoga. If the lords |
| `get_raja_yoga_details` | `(jd, place, divisional_chart_factor=1, language='en')` | Get all the raja yoga information that are present in the requested divisional charts for a given julian day and place |
| `get_raja_yoga_details_for_all_charts` | `(jd, place, language='en', divisional_chart_factor=None)` | Get all the raja yoga information that are present in the divisional charts for a given julian day and place |
| `get_raja_yoga_pairs` | `(house_to_planet_list)` | To get raja yoga planet pairs from house to planet list |

### `jhora.horoscope.chart.sphuta`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `avayogi_sphuta` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, years=1, months=1, sixty_hours=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `avayogi_sphuta_mixed_chart` | `(dob, tob, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `beeja_sphuta` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, years=1, months=1, sixty_hours=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `beeja_sphuta_mixed_chart` | `(dob, tob, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `chatur_sphuta` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, years=1, months=1, sixty_hours=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `chatur_sphuta_mixed_chart` | `(dob, tob, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |
| `deha_sphuta` | `(dob, tob, place, ayanamsa_mode='LAHIRI', divisional_chart_factor=1, chart_method=1, years=1, months=1, sixty_hours=1, base_rasi=None, count_from_end_of_sign=None)` |  |
| `deha_sphuta_mixed_chart` | `(dob, tob, place, varga_factor_1=1, chart_method_1=1, varga_factor_2=1, chart_method_2=1)` |  |

### `jhora.horoscope.chart.arudhas`
- No module docstring captured.
| Function | Signature | Doc |
|---|---|---|
| `bhava_arudhas` | `(chart)` | gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna) |
| `bhava_arudhas_from_planet_positions` | `(planet_positions, arudha_base=0)` | gives Bhava Arudhas for each house from the chart (A1=Arudha Lagna,A2.. A12=Upa Lagna) |
| `chandra_arudhas_from_planet_positions` | `(planet_positions)` |  |
| `graha_arudhas` | `(chart)` | gives Graha Arudhas for each planet from the chart |
| `graha_arudhas_from_planet_positions` | `(planet_positions)` | gives Graha Arudhas for each planet from the planet positions |
| `surya_arudhas_from_planet_positions` | `(planet_positions)` |  |

---
## 6. Strength Calculations (`strength.py`)

- Harsha, Kshetra, Sapthavargaja, Sthana, OjhaYugma, Kendra, Drekkana, Navamsa, Pancha/Dwadasha Vargeeya, Dig, Divaratri, Paksha, Cheshta, Naisargika, Drik, Shad, Bhava balas are available.
| Function | Signature | Doc |
|---|---|---|
| `_cheshta_bala` | `(jd, place)` |  |
| `_dig_bala` | `(jd, place, ayanamsa_mode='LAHIRI')` |  |
| `_divaratri_bala` | `(jd, place)` |  |
| `_drik_bala` | `(jd, place, ayanamsa_mode='LAHIRI')` |  |
| `_kshetra_bala` | `(p_to_h_of_rasi_chart)` |  |
| `_naisargika_bala` | `(jd=None, place=None)` |  |
| `_paksha_bala` | `(jd, place, ayanamsa_mode='LAHIRI')` |  |
| `_sapthavargaja_bala` | `(jd, place)` |  |
| `_sthana_bala` | `(jd, place, ayanamsa_mode='LAHIRI')` |  |
| `bhava_bala` | `(jd, place)` | Computes bhava bala |
| `dwadhasa_vargeeya_bala` | `(jd, place)` | Calculates dwadhasa_vargeeya_bala score of the planets |
| `harsha_bala` | `(dob, tob, place, divisional_factor=1)` | computes the harsha bala score of the planets |
| `pancha_vargeeya_bala` | `(jd, place)` | computes the Pancha Vargeeya bala score of the planets |
| `shad_bala` | `(jd, place, ayanamsa_mode='LAHIRI')` |  |

---
## 7. Yoga Detection

- Yoga definitions loaded via `jhora/lang/yoga_msgs_<lang>.json` and consumed by `get_yoga_details`/`get_yoga_details_for_all_charts`.
| Function | Signature | Doc |
|---|---|---|
| `adhi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `amala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `amsaavatara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `anaphaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `ardha_chandra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `asubha_yoga_from_planet_positions` | `(planet_positions)` |  |
| `bhaarathi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `bhaaskara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `bhadra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `bheri_yoga_from_planet_positions` | `(planet_positions)` |  |
| `brahma_yoga_from_planet_positions` | `(planet_positions)` |  |
| `<lambda>` | `(planet_positions)` |  |
| `chaamara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chaapa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chakra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chandikaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chandra_mangala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chapa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `chatra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `daama_yoga_from_planet_positions` | `(planet_positions)` |  |
| `danda_yoga_from_planet_positions` | `(planet_positions)` |  |
| `devendra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `duradhara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `gadaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `gaja_kesari_yoga_from_planet_positions` | `(planet_positions)` |  |
| `gandharva_yoga_from_planet_positions` | `(planet_positions)` |  |
| `get_yoga_details` | `(jd, place, divisional_chart_factor=1, language='en')` | Get all the yoga information that are present in the requested divisional charts for a given julian day and place |
| `get_yoga_details_for_all_charts` | `(jd, place, language='en', divisional_chart_factor=None)` | Get all the yoga information that are present in the divisional charts for a given julian day and place |
| `get_yoga_resources` | `(language='en')` | get yoga names from yoga_msgs_<lang>.txt |
| `go_yoga_from_planet_positions` | `(planet_positions)` |  |
| `gola_yoga_from_planet_positions` | `(planet_positions)` |  |
| `gouri_yoga_from_planet_positions` | `(planet_positions)` |  |
| `guru_mangala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `hala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `hamsa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `hara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `hari_yoga_from_planet_positions` | `(planet_positions)` |  |
| `harsha_yoga_from_planet_positions` | `(planet_positions)` |  |
| `indra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `jaya_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kaahala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kalaanidhi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kalpadruma_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kamala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kedaara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kemadruma_yoga_from_planet_positions` | `(planet_positions)` |  |
| `khadga_yoga_from_planet_positions` | `(planet_positions)` |  |
| `koorma_yoga_from_planet_positions` | `(planet_positions)` |  |
| `koota_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kulavardhana_yoga_from_planet_positions` | `(planet_positions)` |  |
| `kusuma_yoga_from_planet_positions` | `(planet_positions)` |  |
| `lagnaadhi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `lakshmi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `maalaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `maalavya_yoga_from_planet_positions` | `(planet_positions)` |  |
| `makuta_yoga_from_planet_positions` | `(planet_positions)` |  |
| `matsya_yoga_from_planet_positions` | `(planet_positions)` |  |
| `mridanga_yoga_from_planet_positions` | `(planet_positions)` |  |
| `musala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `nala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `naukaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `nipuna_yoga_from_planet_positions` | `(planet_positions)` |  |
| `paasa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `parvata_yoga_from_planet_positions` | `(planet_positions)` |  |
| `pushkala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `<lambda>` | `(raasi)` |  |
| `rajju_yoga_from_planet_positions` | `(planet_positions)` |  |
| `ravi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `ruchaka_yoga_from_planet_positions` | `(planet_positions)` |  |
| `saarada_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sakata_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sakti_yoga_from_planet_positions` | `(planet_positions)` |  |
| `samudra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sankha_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sara_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sarala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `saraswathi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sarpa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sasa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `siva_yoga_from_planet_positions` | `(planet_positions)` |  |
| `soola_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sreenaatha_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sringaataka_yoga_from_planet_positions` | `(planet_positions)` |  |
| `subha_yoga_from_planet_positions` | `(planet_positions)` |  |
| `sunaphaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `trilochana_yoga_from_planet_positions` | `(planet_positions)` |  |
| `ubhayachara_yoga_from_planet_positions` | `(planet_positions)` | Ubhayachara  Yoga - There is a planet other than Moon in the 2nd and 12th house from Sun. |
| `vaapi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vajra_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vasumati_yoga_from_planet_positions` | `(planet_positions)` |  |
| `veenaa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vesi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vidyut_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vihanga_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vimala_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vishnu_yoga_from_planet_positions` | `(planet_positions)` |  |
| `vosi_yoga_from_planet_positions` | `(planet_positions)` |  |
| `yava_yoga_from_planet_positions` | `(planet_positions)` |  |
| `yoopa_yoga_from_planet_positions` | `(planet_positions)` |  |
| `yuga_yoga_from_planet_positions` | `(planet_positions)` |  |

---
## 8. Dasha Systems

- **Graha dashas**: None discovered.
- **Rasi dashas**: None discovered.
- **Annual/Sudharshana**: None discovered.

---
## 9. Transit, Tajaka & Saham

- Modules: jhora.horoscope.transit, jhora.horoscope.transit.saham, jhora.horoscope.transit.tajaka, jhora.horoscope.transit.tajaka_yoga
- Saham catalog: 36 points (e.g., punya, vidya, yasas, mitra, mahatmaya ...)

### `jhora.horoscope.transit`
- 

### `jhora.horoscope.transit.saham`
- 
| Function | Signature | Doc |
|---|---|---|
| `apamrithyu_saham` | `(planet_positions, night_time_birth=False)` |  |
| `artha_saham` | `(planet_positions, night_time_birth=False)` |  |
| `asha_saham` | `(planet_positions, night_time_birth=False)` |  |
| `bandhana_saham` | `(planet_positions, night_time_birth=False)` |  |
| `bandhu_saham` | `(planet_positions, night_time_birth=False)` |  |
| `bhratri_saham` | `(planet_positions)` |  |

### `jhora.horoscope.transit.tajaka`
- To calculate Tajaka - Annual, monthly, sixty-hour, charts
| Function | Signature | Doc |
|---|---|---|
| `annual_chart` | `(jd_at_dob, place, divisional_chart_factor=1, years=1)` | Also can be called using: |
| `annual_chart_approximate` | `(dob, tob, place, divisional_chart_factor=1, years=1)` | (1) Find the birthday as per western calendar in the required year. |
| `<lambda>` | `(asc_house)` |  |
| `aspects_of_the_planet` | `(house_planet_dict, planet)` | Return benefic, malefic and neutral aspects of the planet |
| `aspects_of_the_raasi` | `(house_planet_dict, raasi)` | Return benefic, malefic and neutral aspected of the rasi |
| `benefic_aspects_of_the_planet` | `(house_planet_dict, planet)` | Benefic Aspects of the planet (weak maleefic aspect) |

### `jhora.horoscope.transit.tajaka_yoga`
- 
| Function | Signature | Doc |
|---|---|---|
| `check_yamaya_yoga` | `(planet, planet1, planet2, planet_positions)` |  |
| `eesarpha_yoga` | `(planet_positions, planet1, planet2)` | @param planet_positions: [ ['L',(7,12,3456)], [0,(4,112,3456)],...]] |
| `get_duhphali_kutta_yoga_planet_pairs` | `(jd, place)` | Get duhphali kutta yoga planet pairs |
| `get_eesarpha_yoga_planet_pairs` | `(planet_positions)` | Get eeasrpha yoga planet pairs |
| `get_gairi_kamboola_yoga_planet_pairs` | `(planet_positions)` | TODO: to be implemented |
| `get_ithasala_yoga_planet_pairs` | `(planet_positions)` | Get ithasala yoga planet pairs |

---
## 10. Match & Prediction

- Match modules: jhora.horoscope.match, jhora.horoscope.match.compatibility
- Prediction modules: jhora.horoscope.prediction, jhora.horoscope.prediction.general, jhora.horoscope.prediction.longevity, jhora.horoscope.prediction.naadi_marriage

### `jhora.horoscope.match`
- 

### `jhora.horoscope.match.compatibility`
- 
| Function | Signature | Doc |
|---|---|---|
| `<lambda>` | `(from_rasi, to_rasi, dir=1, total=12)` |  |
| `<lambda>` | `(from_star, to_star, dir=1, total=27)` |  |
| `update_compatibility_database` | `(method='North')` |  |

### `jhora.horoscope.prediction`
- 

### `jhora.horoscope.prediction.general`
- 
| Function | Signature | Doc |
|---|---|---|
| `get_prediction_details` | `(jd_at_dob, place, language='en')` |  |
| `get_prediction_resources` | `(language='en')` | get resources from prediction_msgs_<lang>.txt |

### `jhora.horoscope.prediction.longevity`
- 
| Function | Signature | Doc |
|---|---|---|
| `life_span_range` | `(jd, place)` | Alpayu = 0; Madhyayu = 1; Poornayu = 2 |

### `jhora.horoscope.prediction.naadi_marriage`
- 

---
## 11. UI Modules (Presentation layer)

- UI widgets aim to display panchanga, chart, calendar, match, vratha, dasha, and transit data.
- `jhora.ui`
- `jhora.ui.chakra`
- `jhora.ui.chart_styles`
- `jhora.ui.conjunction_dialog`
- `jhora.ui.dhasa_bhukthi_options_dialog`
- `jhora.ui.horo_chart`
- `jhora.ui.horo_chart_tabs`
- `jhora.ui.label_grid`
- `jhora.ui.match_ui`
- `jhora.ui.mixed_chart_dialog`
- `jhora.ui.options_dialog`
- `jhora.ui.pancha_pakshi_sastra_widget`
- `jhora.ui.panchangam`
- `jhora.ui.test`
- `jhora.ui.test1`
- `jhora.ui.test2`
- `jhora.ui.vakra_gathi_plot`
- `jhora.ui.varga_chart_dialog`
- `jhora.ui.vedic_calendar`
- `jhora.ui.vedic_clock`
- `jhora.ui.vratha_finder`

---
## 12. Data Files (`jhora/data/`)

- No data files indexed.

---
## 13. Tests as Contract (`jhora/tests/`)

- No tests captured.

---
## 14. Experimental & Unstable Features

| Module | Flags | Notes |
|---|---|---|
| `jhora.const` | experimental | Module describing PyJHora constants |
| `jhora.horoscope.chart.charts` | experimental | TODO: Custom Divisional Chart with following options: |
| `jhora.horoscope.chart.house` | experimental | Marked via keyword scan. |
| `jhora.horoscope.chart.raja_yoga` | experimental | Marked via keyword scan. |
| `jhora.horoscope.chart.strength` | experimental | To Calculate strengths of planets/rasis from chart positions of planets |
| `jhora.horoscope.chart.yoga` | experimental | Marked via keyword scan. |
| `jhora.horoscope.main` | experimental | TODO: Check use of julian_day vs julian_years if used consistently |
| `jhora.horoscope.match.compatibility` | experimental | Marked via keyword scan. |
| `jhora.horoscope.prediction.longevity` | experimental | Marked via keyword scan. |
| `jhora.horoscope.prediction.naadi_marriage` | experimental | Marked via keyword scan. |
| `jhora.horoscope.transit.saham` | experimental | Marked via keyword scan. |
| `jhora.horoscope.transit.tajaka` | experimental | To calculate Tajaka - Annual, monthly, sixty-hour, charts |
| `jhora.horoscope.transit.tajaka_yoga` | experimental | Marked via keyword scan. |
| `jhora.panchanga.drik` | experimental | To calculate panchanga/calendar elements such as tithi, nakshatra, etc. |
| `jhora.panchanga.drik1` | experimental | DO NOT USE THIS YET - EXPERIMENTAL WORK |
| `jhora.panchanga.surya_sidhantha` | experimental | This is an attempt to create horoscope based surya sidhantha meant/true position calculations |
| `jhora.panchanga.vratha` | experimental | Marked via keyword scan. |
| `jhora.tests.pvr_tests` | experimental | Marked via keyword scan. |
| `jhora.tests.test_yogas` | experimental | Marked via keyword scan. |
| `jhora.ui.horo_chart_tabs` | experimental | Marked via keyword scan. |
| `jhora.ui.options_dialog` | experimental | Marked via keyword scan. |
| `jhora.ui.panchangam` | experimental | Marked via keyword scan. |
| `jhora.ui.vedic_calendar` | experimental | Marked via keyword scan. |
| `jhora.ui.vedic_clock` | experimental | Marked via keyword scan. |
| `jhora.utils` | experimental | utils module |
| `jhora.horoscope.dhasa.graha.aayu` | experimental | Computation of pindayu, Nisargayu, Amsayu dasa |
| `jhora.horoscope.dhasa.graha.applicability` | experimental | Marked via keyword scan. |
| `jhora.horoscope.dhasa.graha.ashtottari` | experimental | Calculates Ashtottari (=108) Dasha-bhukthi-antara-sukshma-prana |
| `jhora.horoscope.dhasa.graha.naisargika` | experimental | Marked via keyword scan. |
| `jhora.horoscope.dhasa.graha.tara` | experimental | Tara Dasa - applicable if all the four quadrants are occupied |
| `jhora.horoscope.dhasa.graha.tithi_yogini` | experimental | Tithi Yogini Dasa |
| `jhora.horoscope.dhasa.graha.vimsottari` | experimental | Calculates Vimshottari (=120) Dasha-bhukthi-antara-sukshma-prana |
| `jhora.horoscope.dhasa.graha.yoga_vimsottari` | experimental | Calculates Yoga Vimsottari |
| `jhora.horoscope.dhasa.raasi.chara` | experimental | Marked via keyword scan. |
| `jhora.horoscope.dhasa.raasi.kalachakra` | experimental | Marked via keyword scan. |
| `jhora.horoscope.dhasa.raasi.padhanadhamsa` | experimental | Marked via keyword scan. |
| `jhora.horoscope.dhasa.raasi.sudasa` | experimental | Marked via keyword scan. |

---
## 15. Global Defaults & Configuration

| Key | Value |
|---|---|
| ayanamsa_mode | LAHIRI |
| language | en |
| division_chart_factors | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144] |
| default_bhaava_method | 1 |
| default_house_system | 1 |
| module_failures | {} |
| scan_mode | import-based (import + AST fallback) |

---
## 16. Extractor Design & Safe Entry Points

- No safe entry points captured.

_Document generated: 2025-11-22T17:13:46.880612Z_