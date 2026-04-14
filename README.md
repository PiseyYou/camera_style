# Camera Style - Lens Data Analysis System

A comprehensive lens data collection and analysis platform that scrapes specifications from multiple sources, tracks prices, compares lenses, and provides intelligent recommendations.

## ✨ Features

### Data Collection
- **Real Web Scraping**: Uses Playwright to bypass 403 restrictions
- **Multiple Data Sources**: DPReview, B&H Photo, and more
- **Multi-Brand Support**: Canon, Nikon, Sony, Fujifilm, Panasonic, Olympus
- **Comprehensive Specs**: Focal length, aperture, weight, dimensions, mount type, prices, and more

### Data Analysis
- **Smart Data Merging**: Automatically deduplicate and merge data from multiple sources
- **Price Tracking**: Historical price analysis and trend detection
- **Lens Comparison**: Side-by-side comparison with performance scoring
- **Recommendation Engine**: Personalized lens recommendations based on your needs
- **Interactive Dashboards**: Beautiful HTML reports and visualizations

## Quick Start

### Option 1: Quick Demo (Recommended for First Time)

```bash
# Automatically scrape sample data and open preview
./demo_preview.sh
```

### Option 2: Full Setup

```bash
# 1. Install dependencies
./setup.sh

# 2. Test the scraper
python3 test_real_scraper.py

# 3. Scrape data
python3 scripts/ingest/dpreview_run.py --brand Canon --limit 10

# 4. Run complete analysis
python3 scripts/run_analysis.py

# 5. Open dashboard
xdg-open reports/dashboard.html
```

## 📊 Analysis Tools

### 1. Complete Analysis Pipeline

Run all analysis tools at once:

```bash
python3 scripts/run_analysis.py
```

This will:
- ✅ Merge data from all sources
- ✅ Analyze price trends and find deals
- ✅ Generate lens comparisons
- ✅ Create personalized recommendations
- ✅ Build interactive dashboard

**Output**: `reports/dashboard.html` - Your one-stop analysis hub

### 2. Individual Analysis Tools

#### Data Merging & Deduplication

```bash
python3 scripts/analysis/merge_data.py
```

- Combines data from DPReview, B&H Photo, etc.
- Intelligent fuzzy matching to detect duplicates
- Resolves conflicts using source priority
- **Output**: `data/merged/merged_summary.csv`

#### Price Tracking & Trend Analysis

```bash
python3 scripts/analysis/price_tracker.py
```

- Tracks historical prices
- Detects trends (increasing/decreasing/stable)
- Finds best deals (discounts > 5%)
- Calculates price volatility
- **Output**: `reports/price_analysis.md`, `reports/price_trends.csv`

#### Lens Comparison

```bash
python3 scripts/analysis/lens_comparator.py
```

- Side-by-side specification comparison
- Performance scoring:
  - 🎒 Portability (weight, size)
  - 🔄 Versatility (zoom range)
  - 🌙 Low Light (aperture)
  - 💰 Value (price vs features)
- **Output**: `reports/lens_comparison.html`

#### Recommendation Engine

```bash
python3 scripts/analysis/lens_recommender.py
```

- Personalized recommendations based on:
  - Budget constraints
  - Brand preferences
  - Mount type
  - Focal length needs
  - Feature requirements
- Pre-built profiles:
  - ✈️ Travel Photography
  - 👤 Portrait Photography
  - 💵 Budget Friendly
- **Output**: `reports/lens_recommendations.html`

### 3. Web Preview Interface

Browse all lenses with search and filters:

```bash
python3 scripts/generate_preview.py
xdg-open reports/lens_preview.html
```

**Features:**
- 📊 Statistics dashboard
- 🔍 Real-time search
- 🏷️ Filter by brand/type
- 📱 Responsive design
- 🏷️ Category tabs (by brand, type)
- 📱 Responsive design
- 🎨 Beautiful card layout

See [PREVIEW_GUIDE.md](PREVIEW_GUIDE.md) for detailed usage.

### Example Output

JSON format (`data/parsed/dpreview/canon-rf-24-70mm-f28.json`):

```json
{
  "brand": "Canon",
  "model_name": "RF 24-70mm F2.8 L IS USM",
  "mount": "Canon RF",
  "prime_or_zoom": "Zoom",
  "focal_length_min": 24.0,
  "focal_length_max": 70.0,
  "max_aperture_wide": 2.8,
  "max_aperture_tele": 2.8,
  "weight": 900.0,
  "diameter": 88.5,
  "length": 125.7,
  "release_date": "2019-08-28",
  "source_url": "https://www.dpreview.com/products/lenses/canon/canon-rf-24-70mm-f28",
  "fetched_at": "2026-04-14T02:30:00.000000+00:00"
}
```

## 📁 Project Structure

```
camera_style/
├── scripts/
│   ├── ingest/                    # Data collection
│   │   ├── base_scraper.py        # Base scraper framework
│   │   ├── dpreview_*.py          # DPReview scraper
│   │   └── bhphoto_scraper.py     # B&H Photo scraper
│   ├── analysis/                  # Data analysis
│   │   ├── merge_data.py          # Data merging & deduplication
│   │   ├── price_tracker.py       # Price tracking & trends
│   │   ├── lens_comparator.py     # Lens comparison tool
│   │   └── lens_recommender.py    # Recommendation engine
│   ├── generate_preview.py        # Web preview generator
│   └── run_analysis.py            # Complete analysis pipeline
├── data/
│   ├── raw/                       # Raw HTML pages
│   ├── parsed/                    # Parsed JSON data
│   └── merged/                    # Merged & deduplicated data
├── reports/                       # Generated reports
│   ├── dashboard.html             # Main dashboard
│   ├── lens_preview.html          # Lens catalog
│   ├── price_analysis.md          # Price analysis
│   ├── lens_comparison.html       # Comparison reports
│   └── lens_recommendations.html  # Recommendation reports
├── tests/                         # Test files
├── docs/                          # Documentation
├── setup.sh                       # Setup script
├── quickstart.sh                  # Quick start script
├── demo_preview.sh                # Demo script
└── requirements.txt               # Python dependencies
```

## Troubleshooting

### 403 Forbidden Errors

The scraper uses Playwright with a real browser to bypass 403 restrictions. If you still get 403 errors:

1. Increase the delay: Edit `dpreview_fetch.py` and increase `wait_seconds`
2. Check if DPReview has updated their anti-bot measures
3. Try using a different user agent

### Missing Data

If parsed data is incomplete:

1. Check the raw HTML file in `data/raw/dpreview/`
2. DPReview may have changed their HTML structure
3. Update the CSS selectors in `dpreview_parser.py`

### Playwright Installation Issues

```bash
# Reinstall Playwright browsers
python3 -m playwright install --force chromium

# Check Playwright installation
python3 -m playwright --version
```

## 🎯 Use Cases

### For Photographers

- **Research**: Compare specifications across multiple lenses
- **Shopping**: Track prices and find the best deals
- **Decision Making**: Get personalized recommendations based on your needs
- **Budget Planning**: Analyze price trends to time your purchase

### For Developers

- **Data Source**: Clean, structured lens data in JSON/CSV format
- **API Integration**: Build applications using the scraped data
- **Machine Learning**: Train models on lens specifications and prices
- **Market Analysis**: Analyze photography equipment market trends

### For Researchers

- **Market Research**: Study pricing patterns and trends
- **Product Analysis**: Compare technical specifications across brands
- **Consumer Behavior**: Analyze lens popularity and preferences
- **Data Visualization**: Create charts and graphs from the data

## 📚 Documentation

- **[README.md](README.md)** - This file (project overview)
- **[USAGE_CN.md](USAGE_CN.md)** - 中文使用指南 (Chinese usage guide)
- **[CHANGES.md](CHANGES.md)** - Mock vs Real comparison (详细对比)
- **[SUMMARY.md](SUMMARY.md)** - Complete project summary (项目总结)
- **[PREVIEW_GUIDE.md](PREVIEW_GUIDE.md)** - Web preview interface guide (预览界面指南)

## 🔧 Advanced Usage

### Custom Scraping

```python
from scripts.ingest.bhphoto_scraper import BHPhotoScraper

scraper = BHPhotoScraper()
lenses = scraper.scrape_brand("Canon", limit=20)

for lens in lenses:
    print(f"{lens.model_name}: ${lens.current_price}")
```

### Custom Recommendations

```python
from scripts.analysis.lens_recommender import LensRecommender, UserRequirements

recommender = LensRecommender()

requirements = UserRequirements(
    max_budget=1000,
    mount="Canon RF",
    max_weight=600,
    portability_priority=0.9,
    low_light_priority=0.7
)

recommendations = recommender.recommend(requirements, top_n=5)
```

### Price Alerts

```python
from scripts.analysis.price_tracker import PriceTracker

tracker = PriceTracker()
deals = tracker.find_best_deals(min_discount_pct=10)

for deal in deals:
    print(f"🔥 {deal['model_name']}: Save ${deal['savings']:.2f}!")
```

## Data Quality

### Current Status

- ✓ Real network scraping (not mock data)
- ✓ Playwright bypasses 403 restrictions
- ✓ Saves raw HTML for re-parsing
- ✓ Structured JSON output
- ⚠ Limited to DPReview data availability
- ⚠ Requires manual verification of accuracy

### Verification

Always verify scraped data against manufacturer specifications:

1. Check `reports/dpreview_manual_review.csv`
2. Compare against official spec sheets
3. Cross-reference with multiple sources

## License

This tool is for educational and research purposes. Respect DPReview's terms of service and robots.txt. Do not overload their servers with excessive requests.

## Contributing

Contributions welcome! Please:

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Verify data accuracy

## 🆕 Advanced Features

### Data Source Expansion

The system now supports multiple data sources:

- **DPReview**: Technical specifications and reviews
- **B&H Photo**: Current prices and availability
- **Adorama**: Alternative pricing (coming soon)
- **Manufacturer Sites**: Official specifications (coming soon)

### Data Analysis Tools

#### 1. Data Merging & Deduplication

Automatically merge data from multiple sources and remove duplicates:

```bash
python3 scripts/analysis/merge_data.py
```

Output: `data/merged/merged_summary.csv`

#### 2. Price Tracking & Trend Analysis

Track price changes over time and find the best deals:

```bash
python3 scripts/analysis/price_tracker.py
```

Features:
- Historical price tracking
- Price trend analysis
- Best deals finder
- Price volatility metrics

Output: `reports/price_analysis.md`, `reports/price_trends.csv`

#### 3. Lens Comparison Tool

Compare multiple lenses side-by-side:

```bash
python3 scripts/analysis/lens_comparator.py
```

Features:
- Specification comparison
- Performance scores (portability, versatility, low-light, value)
- Interactive HTML reports

Output: `reports/lens_comparison.html`

#### 4. Recommendation System

Get personalized lens recommendations based on your needs:

```bash
python3 scripts/analysis/lens_recommender.py
```

Features:
- Budget-based filtering
- Use-case specific recommendations
- Scoring algorithm
- Multiple recommendation profiles

Output: `reports/lens_recommendations.html`

### 🚀 Run Complete Analysis Pipeline

Run all analysis tools in one command:

```bash
python3 scripts/run_analysis.py
```

This will:
1. Merge data from all sources
2. Analyze price trends
3. Generate lens comparisons
4. Create recommendations for different use cases
5. Build a comprehensive dashboard

Output: `reports/dashboard.html` (open this to see everything)

## Changelog

### 2026-04-14 - Real Scraper Implementation

- ✓ Replaced mock fixtures with real Playwright scraper
- ✓ Added 403 bypass functionality
- ✓ Implemented real network requests
- ✓ Added comprehensive error handling
- ✓ Created setup and test scripts

### 2026-04-14 - Advanced Features

- ✓ Added B&H Photo scraper
- ✓ Implemented data merging and deduplication
- ✓ Created price tracking system
- ✓ Built lens comparison tool
- ✓ Developed recommendation engine
- ✓ Generated interactive dashboards
