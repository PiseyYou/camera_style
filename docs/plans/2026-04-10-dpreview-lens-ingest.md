# DPReview Lens Ingest Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立一条从 DPReview 抓取镜头索引页与详情页、提取基础规格并保存原始页面与结构化结果的最小可用链路。

**Architecture:** 采用“发现详情页链接 → 获取详情页原始内容 → 解析规格表 → 输出标准化 JSON/CSV”的单向流水线。第一阶段只做 DPReview、只抓基础规格、只覆盖 Canon / Nikon / Sony 三个品牌的小样本，并保留原始 HTML 以便后续重解析。

**Tech Stack:** Python 3、requests/httpx（静态抓取）、Playwright（应对 403 / 动态内容）、pytest、JSON、CSV

---

### Task 1: 固定 DPReview 试点范围与字段字典

**Files:**
- Create: `config/dpreview_pilot.yaml`
- Create: `config/lens_fields.yaml`
- Test: `tests/config/test_dpreview_pilot_config.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
import yaml


def test_dpreview_pilot_config_has_three_brands():
    data = yaml.safe_load(Path("config/dpreview_pilot.yaml").read_text())
    assert data["brands"] == ["Canon", "Nikon", "Sony"]
    assert data["sample_limit_per_brand"] == 20
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/config/test_dpreview_pilot_config.py -v`
Expected: FAIL with `FileNotFoundError` for `config/dpreview_pilot.yaml`

**Step 3: Write minimal implementation**

```yaml
brands:
  - Canon
  - Nikon
  - Sony
sample_limit_per_brand: 20
required_fields:
  - brand
  - model_name
  - mount
  - prime_or_zoom
  - focal_length_min
  - focal_length_max
  - max_aperture_wide
  - max_aperture_tele
  - min_aperture
  - sensor_coverage
  - autofocus
  - image_stabilization
  - min_focus_distance
  - max_magnification
  - filter_thread
  - weight
  - diameter
  - length
  - release_date
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/config/test_dpreview_pilot_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add config/dpreview_pilot.yaml config/lens_fields.yaml tests/config/test_dpreview_pilot_config.py
git commit -m "feat: define dpreview pilot scope and field dictionary"
```

### Task 2: 建立详情页发现器

**Files:**
- Create: `scripts/ingest/dpreview_discovery.py`
- Create: `tests/fixtures/dpreview/index_canon.html`
- Create: `tests/fixtures/dpreview/index_nikon.html`
- Test: `tests/ingest/test_dpreview_discovery.py`

**Step 1: Write the failing test**

```python
from scripts.ingest.dpreview_discovery import extract_lens_links


def test_extract_lens_links_returns_title_brand_url_triplets():
    html = open("tests/fixtures/dpreview/index_canon.html", "r", encoding="utf-8").read()
    rows = extract_lens_links(html, brand="Canon")
    assert rows
    assert set(rows[0].keys()) == {"brand", "title", "url"}
    assert rows[0]["brand"] == "Canon"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_discovery.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing function

**Step 3: Write minimal implementation**

```python
from bs4 import BeautifulSoup


def extract_lens_links(html: str, brand: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for anchor in soup.select("a"):
        href = anchor.get("href")
        title = anchor.get_text(" ", strip=True)
        if href and title and "/products/lenses/" in href:
            items.append({"brand": brand, "title": title, "url": href})
    return items
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_discovery.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/ingest/dpreview_discovery.py tests/fixtures/dpreview/index_canon.html tests/fixtures/dpreview/index_nikon.html tests/ingest/test_dpreview_discovery.py
git commit -m "feat: add dpreview detail page discovery"
```

### Task 3: 建立详情页获取器并处理 403 回退

**Files:**
- Create: `scripts/ingest/dpreview_fetch.py`
- Create: `tests/ingest/test_dpreview_fetch.py`
- Modify: `config/dpreview_pilot.yaml`

**Step 1: Write the failing test**

```python
from scripts.ingest.dpreview_fetch import choose_fetch_mode


def test_choose_fetch_mode_falls_back_to_browser_after_403():
    assert choose_fetch_mode(status_code=403) == "browser"
    assert choose_fetch_mode(status_code=200) == "http"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_fetch.py -v`
Expected: FAIL with missing module/function

**Step 3: Write minimal implementation**

```python
def choose_fetch_mode(status_code: int) -> str:
    return "browser" if status_code == 403 else "http"
```

并在配置中加入：

```yaml
preferred_fetch_mode: http
fallback_fetch_mode: browser
request_delay_seconds: 3
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_fetch.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/ingest/dpreview_fetch.py tests/ingest/test_dpreview_fetch.py config/dpreview_pilot.yaml
git commit -m "feat: add dpreview fetch mode fallback"
```

### Task 4: 解析 DPReview 详情页基础规格

**Files:**
- Create: `scripts/ingest/dpreview_parser.py`
- Create: `tests/fixtures/dpreview/detail_sample.html`
- Test: `tests/ingest/test_dpreview_parser.py`

**Step 1: Write the failing test**

```python
from scripts.ingest.dpreview_parser import parse_lens_detail


def test_parse_lens_detail_extracts_core_fields():
    html = open("tests/fixtures/dpreview/detail_sample.html", "r", encoding="utf-8").read()
    row = parse_lens_detail(html)
    assert row["brand"]
    assert row["model_name"]
    assert "mount" in row
    assert "focal_length_min" in row
    assert "focal_length_max" in row
    assert "max_aperture_wide" in row
    assert "weight" in row
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_parser.py -v`
Expected: FAIL with missing parser

**Step 3: Write minimal implementation**

```python
def parse_lens_detail(html: str) -> dict:
    return {
        "brand": "Canon",
        "model_name": "placeholder",
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
```

然后逐个把 fixture 中能稳定提取的字段补齐。

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/ingest/dpreview_parser.py tests/fixtures/dpreview/detail_sample.html tests/ingest/test_dpreview_parser.py
git commit -m "feat: parse core fields from dpreview lens pages"
```

### Task 5: 保存原始页面和结构化输出

**Files:**
- Create: `scripts/ingest/dpreview_run.py`
- Create: `data/raw/dpreview/.gitkeep`
- Create: `data/parsed/dpreview/.gitkeep`
- Test: `tests/ingest/test_dpreview_run.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from scripts.ingest.dpreview_run import build_output_paths


def test_build_output_paths_separates_raw_and_parsed_outputs():
    paths = build_output_paths("canon-rf-24-70-f2-8")
    assert str(paths["raw"]).startswith("data/raw/dpreview")
    assert str(paths["parsed"]).startswith("data/parsed/dpreview")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_run.py -v`
Expected: FAIL with missing module/function

**Step 3: Write minimal implementation**

```python
from pathlib import Path


def build_output_paths(slug: str) -> dict:
    return {
        "raw": Path("data/raw/dpreview") / f"{slug}.html",
        "parsed": Path("data/parsed/dpreview") / f"{slug}.json",
    }
```

并让运行脚本输出：
- 原始 HTML
- 解析后的 JSON
- 一个汇总 CSV

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_run.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/ingest/dpreview_run.py data/raw/dpreview/.gitkeep data/parsed/dpreview/.gitkeep tests/ingest/test_dpreview_run.py
git commit -m "feat: save raw and parsed dpreview outputs"
```

### Task 6: 运行 Canon / Nikon / Sony 小样本试点

**Files:**
- Modify: `scripts/ingest/dpreview_run.py`
- Create: `reports/dpreview_pilot_summary.md`
- Test: `tests/ingest/test_dpreview_pilot_summary.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_pilot_summary_exists_after_run():
    assert Path("reports/dpreview_pilot_summary.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_pilot_summary.py -v`
Expected: FAIL because summary file does not exist

**Step 3: Write minimal implementation**

试点运行后生成报告，至少包括：
- 每个品牌发现的详情页数量
- 实际成功抓取数量
- 403 次数
- 字段缺失率
- 人工抽检备注

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_pilot_summary.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/ingest/dpreview_run.py reports/dpreview_pilot_summary.md tests/ingest/test_dpreview_pilot_summary.py
git commit -m "feat: add dpreview pilot summary report"
```

### Task 7: 验证与人工抽检

**Files:**
- Create: `reports/dpreview_manual_review.csv`
- Modify: `reports/dpreview_pilot_summary.md`

**Step 1: Write the failing test**

```python
from pathlib import Path
import csv


def test_manual_review_contains_at_least_ten_rows():
    with Path("reports/dpreview_manual_review.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 10
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_dpreview_manual_review.py -v`
Expected: FAIL because manual review file does not exist

**Step 3: Write minimal implementation**

人工抽检至少 10 条记录，逐项确认：
- 型号名是否准确
- 卡口是否准确
- 焦距与最大光圈是否正确
- 重量与尺寸单位是否统一
- 原始 HTML 与 JSON 是否可回溯

**Step 4: Run test to verify it passes**

Run: `pytest tests/ingest/test_dpreview_manual_review.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add reports/dpreview_manual_review.csv reports/dpreview_pilot_summary.md tests/ingest/test_dpreview_manual_review.py
git commit -m "test: verify dpreview pilot output manually"
```

## DPReview first-batch field set

首批只抓这些字段：

- `brand`
- `model_name`
- `source_url`
- `mount`
- `prime_or_zoom`
- `focal_length_min`
- `focal_length_max`
- `max_aperture_wide`
- `max_aperture_tele`
- `min_aperture`
- `sensor_coverage`
- `autofocus`
- `image_stabilization`
- `min_focus_distance`
- `max_magnification`
- `filter_thread`
- `weight`
- `diameter`
- `length`
- `release_date`
- `fetched_at`
- `raw_title`

以下字段暂缓，不进入首批：

- optical construction
- diaphragm blades
- weather sealing
- msrp
- discontinued date
- review score
- sample images

## Trial scope

- Brands: `Canon`, `Nikon`, `Sony`
- Sample size: 每品牌先抓 `10-20` 支镜头
- Success bar:
  - 详情页发现成功率 > 90%
  - 抓取成功率 > 80%
  - 核心字段（型号 / 卡口 / 焦距 / 最大光圈）缺失率 < 10%
  - 人工抽检 10 条中严重错误不超过 1 条

## Verification commands

- `pytest tests/config/test_dpreview_pilot_config.py -v`
- `pytest tests/ingest/test_dpreview_discovery.py -v`
- `pytest tests/ingest/test_dpreview_fetch.py -v`
- `pytest tests/ingest/test_dpreview_parser.py -v`
- `pytest tests/ingest/test_dpreview_run.py -v`
- `pytest tests/ingest/test_dpreview_pilot_summary.py -v`
- `pytest tests/ingest/test_dpreview_manual_review.py -v`
- `python scripts/ingest/dpreview_run.py --brand Canon --limit 10`
- `python scripts/ingest/dpreview_run.py --brand Nikon --limit 10`
- `python scripts/ingest/dpreview_run.py --brand Sony --limit 10`
