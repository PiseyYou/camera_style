from pathlib import Path

from scripts.ingest.dpreview_parser import parse_lens_detail


def test_parse_lens_detail_extracts_core_fields():
    html = Path("tests/fixtures/dpreview/detail_sample.html").read_text(encoding="utf-8")
    row = parse_lens_detail(html)
    assert row["brand"] == "Canon"
    assert row["model_name"] == "RF 24-70mm F2.8 L IS USM"
    assert row["mount"] == "Canon RF"
    assert row["focal_length_min"] == 24.0
    assert row["focal_length_max"] == 70.0
    assert row["max_aperture_wide"] == 2.8
    assert row["weight"] == 900.0
