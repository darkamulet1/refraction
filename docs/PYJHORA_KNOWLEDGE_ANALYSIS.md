# 📚 تحلیل جامع PyJHora Knowledge Pack

## حجم اسناد
- **جمع کل**: 21,166 خط
- **فایل‌های JSON**: 14,728 خط (CorePrimitives, API Inventory, Data Map)
- **فایل‌های MD**: 6,430 خط (مستندات)
- **سطح پوشش**: کامل (111 ماژول، 1,163 تابع عمومی، 44 flag تجربی)

---

## 📊 تحلیل کلیدی

### 1. CorePrimitives.json (3,359 خط)
**محتوا**:
- 9 سیاره: SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU
- 12 راشی (burj/sign): ARIES → PISCES
- 27 نکشترا: ASHWINI → REVATI
- 21 سیستم Ayanamsa: LAHIRI (default), KP, RAMAN, etc.
- 17 سیستم خانه: EQUAL, WHOLE_SIGN, PLACIDUS, KP, etc.
- 23 نمودار تقسیمی: D1, D2, D3, ..., D144, D150, D300
- 7 واره: SUNDAY → SATURDAY

**اهمیت**: این **Single Source of Truth** برای تمام IDs، names، و constants است.

**مشکل شناسایی شده**:
```json
"planets": [
    "(12, 1)",    // ❌ چرا tuple به صورت string؟
    "(22, -1)",   // ❌ باید parse شود
    ...
]
```
این باید به format درست تبدیل شود.

---

### 2. PyJHora_API_Inventory.json (9,074 خط)
**محتوا**:
- 111 ماژول Python
- 1,163 تابع عمومی
- توابع کلیدی:
  - `drik.tithi()` - محاسبه تیتی
  - `drik.nakshatra()` - محاسبه نکشترا
  - `drik.yogam()` - محاسبه یوگا
  - `charts.divisional_chart()` - نمودار تقسیمی
  - `vimsottari.vimsottari_dhasa()` - داشا ویمشوتاری
  - `strength.shadbala()` - شدبالا
  - `yoga.hamsa_yoga()` - یوگا هامسا

**اهمیت**: لیست کامل APIهای PyJHora که Refraction Engine باید استفاده کند.

---

### 3. ENGINE_DESIGN_GAPS_REPORT.md (88 خط)
**Gaps شناسایی شده**:

#### Gap #1: Graha Mapping Utilities ✅ حل شد
- **مشکل**: mapping‌های محلی تکراری
- **راه‌حل**: graha.py با type-safe enums

#### Gap #2: Input/Config Ambiguities
- **مشکل**: node_mode/retrograde handling تعریف نشده
- **مشکل**: default ayanamsa/house_system مطابقت ندارند
- **نیاز**: engine_config_spec_v1.yaml

#### Gap #3: Parity Not in CI ✅ حل شد
- **مشکل**: parity tests دستی
- **راه‌حل**: run_parity_suite.sh در CI

#### Gap #4: Core Chart Definition Lacks Detail
- **مشکل**: "core chart" دقیق تعریف نشده
- **نیاز**: مشخص کردن کدام PyJHora APIها core هستند

#### Gap #5: Dashas & Strengths Lack Contracts
- **مشکل**: 46 dasha system ولی spec نداریم
- **نیاز**: dashas_spec_v1.md, strengths_spec_v1.md

#### Gap #6: Test Contracts Lack Mapping
- **مشکل**: PyJHora_Tests_Contract.json به outputs مپ نشده
- **نیاز**: tests_binding_core_chart_v1.yaml

#### Gap #7: Missing Specs
**TODO list**:
- [ ] panchanga_spec_v1.md
- [ ] dashas_spec_v1.md
- [ ] strengths_spec_v1.md
- [ ] special_points_spec_v1.md
- [ ] transits_spec_v1.md
- [ ] yoga_spec_v1.md
- [ ] ui_payload_spec_v1.md

---

### 4. PYJHORA_DATA_STRUCTURES.md (577 خط)
**ساختارهای کلیدی**:

```python
# Date
Date = namedtuple('Date', ['year', 'month', 'day'])

# Place
Place = namedtuple('Place', ['name', 'latitude', 'longitude', 'timezone'])

# Planet Positions
planet_positions = [
    (planet_id, (raasi_index, longitude_in_raasi)),
    ...
]

# House-to-Planet List (12 elements)
house_to_planet_list = ['', '0', '1/2', ...]  # '/' separates multiple planets

# Planet-to-House Dict
planet_to_house_dict = {
    0: 1,    # Sun in house 1
    1: 2,    # Moon in house 2
    ...
}
```

**اهمیت**: این structureها باید در graha.py و extractors استفاده شوند.

---

### 5. PYJHORA_INTEGRATION_PATTERNS.md (453 خط)
**الگوهای کلیدی**:

#### Pattern 1: Horoscope Class (High-level)
```python
from jhora.horoscope.main import Horoscope

h = Horoscope(
    place_with_country_code='Chennai,IN',
    date_in=drik.Date(1985, 6, 9),
    birth_time='10:30:00',
    ayanamsa_mode='LAHIRI'
)

calendar = h.get_calendar_information()
d1_chart = h.get_horoscope_information_for_chart(chart_index=0)
```

#### Pattern 2: Direct drik Usage (Low-level)
```python
from jhora.panchanga import drik

place = drik.Place('Chennai', 13.0827, 80.2707, +5.5)
jd = utils.julian_day_number((1985, 6, 9), (10, 30, 0))

tithi_no, tithi_name, t_start, t_end = drik.tithi(jd, place)
nak_no, nak_name, pada, n_start, n_end = drik.nakshatra(jd, place)
```

**توصیه**: Refraction Engine باید Pattern 2 (direct drik) را استفاده کند چون:
- کنترل بیشتر
- performance بهتر
- dependency کمتر

---

### 6. PYJHORA_CONFIGURATION_OPTIONS.md (464 خط)
**گزینه‌های کلیدی**:

#### Ayanamsa (21 options)
- **LAHIRI** (default in India)
- **RAMAN**
- **KP** (Krishnamurti)
- **TRUE_CITRA**
- **SURYASIDDHANTA**

#### House Systems (17 options)
- **EQUAL** (default)
- **WHOLE_SIGN**
- **PLACIDUS**
- **KP**
- **SRIPATHI**

#### Division Charts (D1-D300)
- Standard: D1, D2, D3, D9, D12, D16, D20, D24, D30, D60
- Extended: D81, D108, D144, D150, D300

#### Languages (6)
- en, ta, te, hi, ka, ml

---

## 🎯 نتیجه‌گیری

### قوت‌ها:
1. ✅ Knowledge pack بسیار جامع (21K+ lines)
2. ✅ CorePrimitives.json به عنوان single source
3. ✅ API Inventory کامل (1,163 functions)
4. ✅ Data structures به خوبی document شده
5. ✅ Integration patterns واضح

### ضعف‌ها:
1. ❌ CorePrimitives.json format مشکل دارد (strings به جای dicts)
2. ❌ 7 spec missing (panchanga, dashas, strengths, etc.)
3. ❌ Input validation spec نداریم
4. ❌ Test binding به outputs مپ نشده

### اولویت‌های Implementation:
**Phase 0** (این هفته):
1. ✅ Gap #1: graha.py - DONE
2. ✅ Gap #3: Parity in CI - DONE
3. 🔄 Fix CorePrimitives.json format
4. 🔄 Create engine_config_spec_v1.yaml

**Phase 1** (هفته بعد):
1. پیاده‌سازی panchanga_spec_v1
2. پیاده‌سازی dashas_vimshottari_spec_v1
3. پیاده‌سازی strengths_spec_v1
4. Validation layer

**Phase 2** (دو هفته بعد):
1. Special points (Bhava lagna, Sahams)
2. Yogas (Pancha Mahapurusha, Raja)
3. Transits
4. UI payload specs

---

## 📝 توصیه‌های معماری

### 1. CorePrimitives Parser
باید یک parser برای CorePrimitives.json بسازیم که:
- Strings را به proper types تبدیل کند
- Validation اضافه کند
- به graha.py sync شود

### 2. Config System
باید یک config system مرکزی داشته باشیم:
```python
from refraction_engine.config import EngineConfig

config = EngineConfig(
    ayanamsa_mode="LAHIRI",
    house_system="EQUAL",
    node_mode="TRUE",
    include_bodies=["SUN", "MOON", ...]
)
```

### 3. Extractor Factory
```python
from refraction_engine.factory import ExtractorFactory

factory = ExtractorFactory(config)
core_chart = factory.create_extractor("core_chart")
panchanga = factory.create_extractor("panchanga")
```

### 4. Validation Layer
```python
from refraction_engine.validation import validate_input

errors = validate_input(payload, "core_input_spec_v1")
if errors:
    raise ValidationError(errors)
```

---

**آماده برای طراحی کامل! 🚀**
