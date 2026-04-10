from scripts.ingest.dpreview_run import build_output_paths


def test_build_output_paths_separates_raw_and_parsed_outputs():
    paths = build_output_paths("canon-rf-24-70-f2-8")
    assert str(paths["raw"]).startswith("data/raw/dpreview")
    assert str(paths["parsed"]).startswith("data/parsed/dpreview")
