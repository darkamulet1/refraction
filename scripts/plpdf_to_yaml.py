# scripts/plpdf_to_yaml.py
# -*- coding: utf-8 -*-
"""Extract Parashara Light PDF tables into YAML/JSON parity fixtures."""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from typing import Dict

from pdfminer.high_level import extract_text
import yaml

HAS_OCR = False
try:
    import pypdfium2 as pdfium
    import pytesseract
    from PIL import Image

    HAS_OCR = True
    tess_cmd = os.environ.get("TESSERACT_CMD")
    if tess_cmd:
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
except Exception:
    HAS_OCR = False

SIGNS = {
    "Ari": 0,
    "Tau": 30,
    "Gem": 60,
    "Can": 90,
    "Leo": 120,
    "Vir": 150,
    "Lib": 180,
    "Sco": 210,
    "Sag": 240,
    "Cap": 270,
    "Aqu": 300,
    "Pis": 330,
    "Aries": 0,
    "Taurus": 30,
    "Gemini": 60,
    "Cancer": 90,
    "Virgo": 150,
    "Libra": 180,
    "Scorpio": 210,
    "Sagittarius": 240,
    "Capricorn": 270,
    "Aquarius": 300,
    "Pisces": 330,
}
PLANETS = [
    "Lagna",
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]
DMS = re.compile(r"(?P<d>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})")
ROW = re.compile(
    r"^(?P<pl>Lagna|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\s+"
    r"(?:(?:R|Rx)\s+)?"
    r"(?P<sign>Ari|Tau|Gem|Can|Leo|Vir|Lib|Sco|Sag|Cap|Aqu|Pis|Aries|Taurus|Gemini|"
    r"Cancer|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)\s+"
    r"(?P<dms>\d{1,2}:\d{2}:\d{2})"
)


def dms_to_deg(text: str) -> float:
    match = DMS.match(text)
    if not match:
        raise ValueError(f"Unparseable DMS value: {text}")
    deg = int(match["d"])
    minutes = int(match["m"])
    seconds = int(match["s"])
    return deg + minutes / 60 + seconds / 3600


def parse_row_table(raw_text: str) -> Dict[str, Dict[str, object]]:
    data: Dict[str, Dict[str, object]] = {}
    for ln in (re.sub(r"\s+", " ", chunk).strip() for chunk in raw_text.splitlines()):
        match = ROW.match(ln)
        if not match:
            continue
        planet = match["pl"].lower()
        sign_token = match["sign"]
        sign_key = sign_token[:3]
        base = SIGNS.get(sign_token, SIGNS.get(sign_key))
        if base is None:
            continue
        dms = match["dms"]
        deg = round((base + dms_to_deg(dms)) % 360, 6)
        data[planet] = {"sign": sign_key, "dms": dms, "deg_0_360": deg}
    return data


def parse_vertical_table(raw_text: str) -> Dict[str, Dict[str, object]] | None:
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    targets = [p.lower() for p in PLANETS]
    for idx in range(len(lines)):
        window = [ln.lower() for ln in lines[idx : idx + len(targets)]]
        if window != targets:
            continue
        cursor = idx + len(targets)
        signs: list[str] = []
        while cursor < len(lines) and len(signs) < len(targets):
            token = lines[cursor].split()[0]
            token3 = token[:3]
            if token in SIGNS or token3 in SIGNS:
                signs.append(token3 if token3 in SIGNS else token[:3])
            cursor += 1
        degrees: list[str] = []
        while cursor < len(lines) and len(degrees) < len(targets):
            match = DMS.match(lines[cursor])
            if match:
                degrees.append(match.group())
            cursor += 1
        if len(signs) == len(targets) and len(degrees) == len(targets):
            result: Dict[str, Dict[str, object]] = {}
            for planet, sign, dms in zip(PLANETS, signs, degrees):
                base = SIGNS.get(sign, SIGNS.get(sign[:3]))
                if base is None:
                    continue
                deg = round((base + dms_to_deg(dms)) % 360, 6)
                result[planet.lower()] = {"sign": sign[:3], "dms": dms, "deg_0_360": deg}
            if len(result) == len(targets):
                return result
    return None


def parse_table(raw_text: str) -> Dict[str, Dict[str, object]]:
    data = parse_row_table(raw_text)
    if len(data) >= len(PLANETS):
        return data
    vertical = parse_vertical_table(raw_text)
    if vertical:
        return vertical
    raise RuntimeError(f"Too few rows parsed: {len(data)}")


def extract_text_pdfminer(pdf_path: pathlib.Path) -> str:
    try:
        return extract_text(str(pdf_path)) or ""
    except Exception:
        return ""


def extract_text_ocr(pdf_path: pathlib.Path) -> str:
    if not HAS_OCR:
        raise RuntimeError("OCR backend unavailable (install pypdfium2 / pytesseract / Pillow).")
    document = pdfium.PdfDocument(str(pdf_path))
    pages: list[str] = []
    for index in range(len(document)):
        pil_image = document[index].render(scale=2.0).to_pil().convert("L")
        pages.append(pytesseract.image_to_string(pil_image, lang="eng"))
    return "\n".join(pages)


def run_one(pdf_path: pathlib.Path, out_dir: pathlib.Path) -> None:
    text = extract_text_pdfminer(pdf_path)
    data = None
    if text and any(token in text for token in PLANETS):
        try:
            data = parse_table(text)
        except Exception:
            data = None
    if data is None:
        text = extract_text_ocr(pdf_path)
        data = parse_table(text)

    subject = pdf_path.stem.replace("_pl", "")
    payload = {
        "subject": subject,
        "source": f"PL-PDF:{pdf_path.name}",
        "ayanamsa": {"name": "Lahiri", "node_mode": "mean"},
        "planets_d1": data,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{subject}.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    (out_dir / f"{subject}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    pdf_dir = root / "references" / "pl_pdfs"
    out_dir = root / "references" / "out"
    log_path = root / "references" / "checks" / "parse_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in {pdf_dir}")
        sys.exit(2)

    ok: list[str] = []
    bad: list[tuple[str, str]] = []
    for pdf in pdfs:
        try:
            run_one(pdf, out_dir)
            ok.append(pdf.name)
            print("OK:", pdf.name)
        except Exception as exc:
            bad.append((pdf.name, str(exc)))
            print("FAIL:", pdf.name, "->", exc)

    with log_path.open("w", encoding="utf-8") as handle:
        handle.write("OK:\n")
        for name in ok:
            handle.write(f"  {name}\n")
        handle.write("\nFailed:\n")
        for name, reason in bad:
            handle.write(f"  {name} -> {reason}\n")

    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
