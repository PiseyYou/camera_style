from pathlib import Path

import yaml


def test_dpreview_pilot_config_has_three_brands():
    data = yaml.safe_load(Path("config/dpreview_pilot.yaml").read_text())
    assert data["brands"] == ["Canon", "Nikon", "Sony"]
    assert data["sample_limit_per_brand"] == 20
