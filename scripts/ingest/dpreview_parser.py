from __future__ import annotations

import re
from bs4 import BeautifulSoup


FIELD_MAP = {
    "brand": "brand",
    "model name": "model_name",
    "mount": "mount",
    "lens type": "prime_or_zoom",
    "sensor coverage": "sensor_coverage",
    "autofocus": "autofocus",
    "image stabilization": "image_stabilization",
    "release date": "release_date",
}


def _to_float(value: str) -> float | None:
    match = re.search(r"\d+(?:\.\d+)?", value)
    return float(match.group()) if match else None


def _to_bool(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered in {"yes", "true"}:
        return True
    if lowered in {"no", "false"}:
        return False
    return None


def _parse_focal_length(value: str) -> tuple[float | None, float | None]:
    numbers = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", value)]
    if not numbers:
        return None, None
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return numbers[0], numbers[1]


def _parse_aperture(value: str) -> tuple[float | None, float | None]:
    numbers = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", value)]
    if not numbers:
        return None, None
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return numbers[0], numbers[1]


def parse_lens_detail(html: str) -> dict:
    row = {
        "brand": None,
        "model_name": None,
        "mount": None,
        "prime_or_zoom": None,
        "focal_length_min": None,
        "focal_length_max": None,
        "max_aperture_wide": None,
        "max_aperture_tele": None,
        "min_aperture": None,
        "sensor_coverage": None,
        "autofocus": None,
        "image_stabilization": None,
        "min_focus_distance": None,
        "max_magnification": None,
        "filter_thread": None,
        "weight": None,
        "diameter": None,
        "length": None,
        "release_date": None,
    }

    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one("h1")
    if heading and not row["model_name"]:
        title = heading.get_text(" ", strip=True)
        row["model_name"] = re.sub(r"^(Canon|Nikon|Sony)\s+", "", title)
        if title.startswith("Canon "):
            row["brand"] = "Canon"
        elif title.startswith("Nikon "):
            row["brand"] = "Nikon"
        elif title.startswith("Sony "):
            row["brand"] = "Sony"

    for tr in soup.select("tr"):
        header = tr.select_one("th")
        value = tr.select_one("td")
        if not header or not value:
            continue
        key = header.get_text(" ", strip=True).lower()
        text = value.get_text(" ", strip=True)

        if key in FIELD_MAP:
            mapped = FIELD_MAP[key]
            if mapped in {"autofocus", "image_stabilization"}:
                row[mapped] = _to_bool(text)
            else:
                row[mapped] = text
            continue

        if key == "focal length":
            row["focal_length_min"], row["focal_length_max"] = _parse_focal_length(text)
        elif key == "max aperture":
            row["max_aperture_wide"], row["max_aperture_tele"] = _parse_aperture(text)
        elif key == "min aperture":
            row["min_aperture"] = _to_float(text)
        elif key == "min focus distance":
            row["min_focus_distance"] = _to_float(text)
        elif key == "max magnification":
            row["max_magnification"] = _to_float(text)
        elif key == "filter thread":
            row["filter_thread"] = _to_float(text)
        elif key == "weight":
            row["weight"] = _to_float(text)
        elif key == "diameter":
            row["diameter"] = _to_float(text)
        elif key == "length":
            row["length"] = _to_float(text)

    return row
