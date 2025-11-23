# Experimental & Hidden Capabilities

## Experimental markers found in code
- `src\jhora\panchanga\drik1.py`
  - 23:    DO NOT USE THIS YET - EXPERIMENTAL WORK
D:\Pyjhora\PyJHora_broken_backup\src\jhora\panchanga\drik.py: 2392:        !!!!!! EXPERIMENTAL WORK - RESULTS MAY NOT BE ACCURATE !!!!
- `src\jhora\panchanga\surya_sidhantha.py`
  - 108:    """ TODO NOT WORKING STILL UNDER TESTING """
D:\Pyjhora\PyJHora_broken_backup\src\jhora\panchanga\surya_sidhantha.py: 144:    """ TODO NOT WORKING STILL UNDER TESTING """

## Hidden capabilities referenced in README/PyPI docs
- `src/v0min/varshaphal_extract.py` - Annual Varshaphal/Tajaka engine with optional maasa/60-hour charts.
- `src/v0min/prasna_extract.py` - Prasna & KP-Adhipathi engine for KP-249/Prasna-108/Naadi-1800 numbers.
- `src/v0min/chakra_extract.py` - Multi-layer chakra dashboards (Sarvatobadra, Kaala, Kota, Shoola, Tripataki, etc.).
- `src/v0min/muhurta_extract.py` - Muhurta optimizer that scores windows around activities such as CLASS_START, TRAVEL, and PROJECT_LAUNCH.
- `src/v0min/panchanga_extras_extract.py` - Pancha Pakshi + Vratha/festival snapshot generator.
- `src/v0min/event_scan_extract.py` - Timeline scanner for sign entries, retrogrades, Sankranti, eclipses, and event filtering.

## NEWLY DISCOVERED CAPABILITIES
- `src/v0min/varshaphal_extract.py` - exposes the annual Varshaphal, monthly Maasa Pravesh, and 60-hour Tajaka charts per the README notes and CLI references.
- `src/v0min/prasna_extract.py` - generates KP/Prasna/Naadi charts plus KP Adhipathi chains described under the "Prasna / KP-Adhipathi Engine" section of README.
- `src/v0min/chakra_extract.py` - compiles chakras (Sarvatobadra, Kaala, Kota, Shoola, Tripataki, Surya/Chandra Kalanala, Saptha/Pancha Shalaka) into `chakra.v1` payloads.
- `src/v0min/muhurta_extract.py` - scores windows by weights (RahuKalam, Benefic Lagna, etc.) for activities such as `CLASS_START`, matching the README sample.
- `src/v0min/panchanga_extras_extract.py` - exports Pancha Pakshi, day schedule, and vratha/festival lists referenced in README under "Panchanga Extras".
- `src/v0min/event_scan_extract.py` - timelines of sign entries, retrogrades, Sankranti/eclipses, and interpolated events directly mentioned in README.