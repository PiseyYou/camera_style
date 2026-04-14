from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.ingest.dpreview_discovery import discover_lenses_for_brand
from scripts.ingest.dpreview_fetch import fetch_url
from scripts.ingest.dpreview_parser import parse_lens_detail

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
    """Extract slug from URL for filename."""
    return url.rstrip("/").split("/")[-1]


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


def _build_summary(rows: list[dict], http_403_count: int = 0) -> dict:
    """Build summary statistics from parsed rows."""
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
        "http_403_count": http_403_count,
        "field_missing_rate": _missing_rate(rows, CORE_FIELDS),
        "manual_review_notes": MANUAL_REVIEW_NOTE,
    }


def run_brand_pilot(brand: str, limit: int = 10) -> dict:
    """
    Run pilot scraping for a specific brand using real network requests.

    Args:
        brand: Brand name (Canon, Nikon, Sony)
        limit: Maximum number of lenses to scrape

    Returns:
        dict with scraping statistics
    """
    print(f"[{brand}] Discovering lens index page...")
    discovered = discover_lenses_for_brand(brand, limit=limit)
    print(f"[{brand}] Found {len(discovered)} lenses")

    parsed_rows = []
    http_403_count = 0

    for idx, item in enumerate(discovered, 1):
        url = item["url"]
        print(f"[{brand}] ({idx}/{len(discovered)}) Fetching {url}...")

        try:
            result = fetch_url(url, mode="browser", delay=3)

            if result["status_code"] == 403:
                http_403_count += 1
                print(f"  ⚠ HTTP 403 - skipping")
                continue

            if result["status_code"] != 200:
                print(f"  ⚠ HTTP {result['status_code']} - skipping")
                continue

            html = result["html"]
            row = parse_lens_detail(html)
            row["source_url"] = url
            row["raw_title"] = item["title"]
            row["fetched_at"] = datetime.now(timezone.utc).isoformat()

            parsed_rows.append(row)
            save_outputs(_slug_from_url(url), html, row)
            print(f"  ✓ Saved: {row.get('model_name', 'Unknown')}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    combined_rows = _merge_rows(_read_summary_csv(), parsed_rows)
    write_summary_csv(combined_rows)
    write_pilot_summary(_build_summary(combined_rows, http_403_count))

    print(f"\n[{brand}] Complete: {len(parsed_rows)}/{len(discovered)} successful")
    return {
        "brand": brand,
        "discovered_count": len(discovered),
        "successful_fetches": len(parsed_rows),
        "http_403_count": http_403_count,
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
