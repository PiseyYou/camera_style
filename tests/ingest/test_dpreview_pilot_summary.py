from pathlib import Path


def test_pilot_summary_exists_after_run():
    assert Path("reports/dpreview_pilot_summary.md").exists()
