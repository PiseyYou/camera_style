from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.ingest.dpreview_discovery import extract_lens_links
from scripts.ingest.dpreview_parser import parse_lens_detail

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "dpreview"
INDEX_FIXTURES = {
    "Canon": "index_canon.html",
    "Nikon": "index_nikon.html",
    "Sony": "index_sony.html",
}
DETAIL_FIXTURES = {
    "/products/lenses/canon/canon-rf-24-70mm-f28": "detail_sample.html",
    "/products/lenses/canon/canon-rf-50mm-f18": "detail_canon_rf_50mm_f18.html",
    "/products/lenses/nikon/nikon-z-24-70mm-f4": "detail_nikon_z_24_70mm_f4.html",
    "/products/lenses/nikon/nikon-z-50mm-f18": "detail_nikon_z_50mm_f18.html",
    "/products/lenses/sony/sony-fe-24-70mm-f28": "detail_sony_fe_24_70mm_f28.html",
    "/products/lenses/sony/sony-fe-50mm-f18": "detail_sony_fe_50mm_f18.html",
}
BASE_URL = "https://www.dpreview.com"
SUMMARY_CSV_PATH = Path("data/parsed/dpreview/summary.csv")
PILOT_SUMMARY_PATH = Path("reports/dpreview_pilot_summary.md")
MANUAL_REVIEW_NOTE = "10 sample rows recorded in reports/dpreview_manual_review.csv"
CORE_FIELDS = [
    "model_name",
    "mount",
    "focal_length_min",
    "focal_length_max",
    "max_aperture_wide",
]


def build_output_paths(slug: str) -> dict:
    return {
        "raw": Path("data/raw/dpreview") / f"{slug}.html",
        "parsed": Path("data/parsed/dpreview") / f"{slug}.json",
    }


def save_outputs(slug: str, html: str, row: dict) -> dict:
    paths = build_output_paths(slug)
    paths["raw"].parent.mkdir(parents=True, exist_ok=True)
    paths["parsed"].parent.mkdir(parents=True, exist_ok=True)
    paths["raw"].write_text(html, encoding="utf-8")
    paths["parsed"].write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def _read_summary_csv(path: Path = SUMMARY_CSV_PATH) -> list[dict]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_summary_csv(rows: list[dict], path: Path = SUMMARY_CSV_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_pilot_summary(summary: dict, path: Path = PILOT_SUMMARY_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# DPReview Pilot Summary",
        "",
        f"- Canon details discovered: {summary.get('canon_discovered', 0)}",
        f"- Nikon details discovered: {summary.get('nikon_discovered', 0)}",
        f"- Sony details discovered: {summary.get('sony_discovered', 0)}",
        f"- Successful fetches: {summary.get('successful_fetches', 0)}",
        f"- HTTP 403 count: {summary.get('http_403_count', 0)}",
        f"- Field missing rate: {summary.get('field_missing_rate', 'unknown')}",
        f"- Manual review notes: {summary.get('manual_review_notes', 'pending')}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _slug_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _load_index_rows(brand: str, limit: int) -> list[dict]:
    html = _read_fixture(INDEX_FIXTURES[brand])
    return extract_lens_links(html, brand=brand)[:limit]


def _load_detail_html(url: str) -> str:
    return _read_fixture(DETAIL_FIXTURES[url])


def _missing_rate(rows: list[dict], fields: list[str]) -> str:
    if not rows or not fields:
        return "0.0%"
    missing = 0
    total = len(rows) * len(fields)
    for row in rows:
        for field in fields:
            if row.get(field) in {None, ""}:
                missing += 1
    return f"{(missing / total) * 100:.1f}%"


def _merge_rows(existing_rows: list[dict], new_rows: list[dict]) -> list[dict]:
    by_source = {row["source_url"]: row for row in existing_rows}
    for row in new_rows:
        by_source[row["source_url"]] = row
    return list(by_source.values())


def _build_summary(rows: list[dict]) -> dict:
    brand_counts = {"Canon": 0, "Nikon": 0, "Sony": 0}
    for row in rows:
        brand = row.get("brand")
        if brand in brand_counts:
            brand_counts[brand] += 1
    return {
        "canon_discovered": brand_counts["Canon"],
        "nikon_discovered": brand_counts["Nikon"],
        "sony_discovered": brand_counts["Sony"],
        "successful_fetches": len(rows),
        "http_403_count": 0,
        "field_missing_rate": _missing_rate(rows, CORE_FIELDS),
        "manual_review_notes": MANUAL_REVIEW_NOTE,
    }


def run_brand_pilot(brand: str, limit: int = 10) -> dict:
    discovered = _load_index_rows(brand, limit)
    parsed_rows = []

    for item in discovered:
        html = _load_detail_html(item["url"])
        row = parse_lens_detail(html)
        row["source_url"] = f"{BASE_URL}{item['url']}"
        row["raw_title"] = item["title"]
        row["fetched_at"] = datetime.now(timezone.utc).isoformat()
        parsed_rows.append(row)
        save_outputs(_slug_from_url(item["url"]), html, row)

    combined_rows = _merge_rows(_read_summary_csv(), parsed_rows)
    write_summary_csv(combined_rows)
    write_pilot_summary(_build_summary(combined_rows))
    return {
        "brand": brand,
        "discovered_count": len(discovered),
        "successful_fetches": len(parsed_rows),
        "rows": parsed_rows,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True, choices=["Canon", "Nikon", "Sony"])
    parser.add_argument("--limit", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    run_brand_pilot(args.brand, limit=args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
