import csv
import json
from pathlib import Path

from scripts.ingest.dpreview_run import main, run_brand_pilot


def test_run_brand_pilot_writes_raw_parsed_and_summary_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_brand_pilot("Canon", limit=1)

    raw_path = Path("data/raw/dpreview/canon-rf-24-70mm-f28.html")
    parsed_path = Path("data/parsed/dpreview/canon-rf-24-70mm-f28.json")
    summary_csv = Path("data/parsed/dpreview/summary.csv")
    summary_md = Path("reports/dpreview_pilot_summary.md")

    parsed = json.loads(parsed_path.read_text(encoding="utf-8"))

    assert result["discovered_count"] == 1
    assert result["successful_fetches"] == 1
    assert raw_path.exists()
    assert parsed_path.exists()
    assert summary_csv.exists()
    assert summary_md.exists()
    assert parsed["source_url"].endswith("/products/lenses/canon/canon-rf-24-70mm-f28")
    assert parsed["raw_title"] == "Canon RF 24-70mm F2.8"
    assert parsed["fetched_at"]


def test_main_runs_requested_brand(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    exit_code = main(["--brand", "Nikon", "--limit", "1"])

    assert exit_code == 0
    assert Path("data/raw/dpreview/nikon-z-24-70mm-f4.html").exists()
    assert Path("data/parsed/dpreview/nikon-z-24-70mm-f4.json").exists()


def test_running_multiple_brands_accumulates_summary_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    main(["--brand", "Canon", "--limit", "1"])
    main(["--brand", "Sony", "--limit", "1"])

    with Path("data/parsed/dpreview/summary.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    summary_text = Path("reports/dpreview_pilot_summary.md").read_text(encoding="utf-8")

    assert len(rows) == 2
    assert {row["brand"] for row in rows} == {"Canon", "Sony"}
    assert "- Canon details discovered: 1" in summary_text
    assert "- Sony details discovered: 1" in summary_text
    assert "- Successful fetches: 2" in summary_text
