from pathlib import Path
import csv


def test_manual_review_contains_at_least_ten_rows():
    with Path("reports/dpreview_manual_review.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 10
