#!/usr/bin/env python3
"""
Unified lens analysis pipeline.
Runs all analysis tools in sequence.
"""

import sys
import os
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

# Now import with absolute imports from project root
from scripts.analysis.merge_data import LensMerger
from scripts.analysis.price_tracker import PriceTracker
from scripts.analysis.lens_comparator import LensComparator
from scripts.analysis.lens_recommender import LensRecommender, UserRequirements


def run_full_analysis():
    """Run complete analysis pipeline."""
    print("="*60)
    print("📊 Lens Data Analysis Pipeline")
    print("="*60)
    print()

    # Step 0: Sync data to ensure unified database
    print("[0/5] Synchronizing data sources...")
    from scripts.sync_data import sync_data
    sync_data()
    print()

    # Step 1: Merge data from all sources
    print("[1/5] Merging data from all sources...")

    # Since CSV is the authoritative source, just ensure it's in merged directory
    import shutil
    source_csv = Path("data/parsed/dpreview/summary.csv")
    target_csv = Path("data/merged/merged_summary.csv")

    if source_csv.exists():
        shutil.copy2(source_csv, target_csv)

        # Count lenses
        with source_csv.open('r', encoding='utf-8') as f:
            lens_count = len(f.readlines()) - 1  # Subtract header

        print(f"  Total lenses: {lens_count}")
        print("  ✓ Merged data saved")
    else:
        print("  ⚠️ No source data found")
    print()

    # Step 2: Price tracking analysis
    print("[2/5] Analyzing price trends...")
    tracker = PriceTracker()

    # Price data would come from retailer APIs (not available yet)
    # For now, just generate the report with existing data

    tracker.generate_price_report(Path("reports/price_analysis.md"))
    tracker.export_price_trends_csv(Path("reports/price_trends.csv"))

    deals = tracker.find_best_deals(min_discount_pct=5)
    print(f"  Found {len(deals)} deals")
    print("  ✓ Price analysis complete")
    print()

    # Step 3: Generate lens comparisons
    print("[3/5] Generating lens comparisons...")
    comparator = LensComparator(Path("data/merged"))

    # Find popular focal lengths to compare
    focal_lengths = ["24-70", "50mm", "70-200"]
    for focal_length in focal_lengths:
        results = comparator.search_lenses(focal_length)
        if len(results) >= 2:
            lens_keys = [f"{l.get('brand')}::{l.get('model_name')}" for l in results[:3]]
            output_file = f"reports/comparison_{focal_length.replace('mm', '').replace('-', '_')}.html"
            comparator.generate_comparison_report(lens_keys, Path(output_file))
            print(f"  ✓ Generated comparison for {focal_length}")

    print("  ✓ Comparisons complete")
    print()

    # Step 4: Generate recommendations
    print("[4/5] Generating recommendations...")
    recommender = LensRecommender(Path("data/merged"))

    # Generate recommendations for different use cases
    use_cases = [
        {
            'name': 'Travel Photography',
            'requirements': UserRequirements(
                max_budget=1500,
                max_weight=800,
                portability_priority=0.9,
                versatility_priority=0.8,
                value_priority=0.7
            ),
            'output': 'reports/recommendations_travel.html'
        },
        {
            'name': 'Portrait Photography',
            'requirements': UserRequirements(
                max_budget=2000,
                min_focal_length=50,
                max_focal_length=135,
                max_aperture_requirement=2.8,
                low_light_priority=0.9,
                portability_priority=0.5,
                value_priority=0.6
            ),
            'output': 'reports/recommendations_portrait.html'
        },
        {
            'name': 'Budget Friendly',
            'requirements': UserRequirements(
                max_budget=500,
                value_priority=0.9,
                versatility_priority=0.7,
                portability_priority=0.6
            ),
            'output': 'reports/recommendations_budget.html'
        }
    ]

    for use_case in use_cases:
        recommender.generate_recommendation_report(
            use_case['requirements'],
            Path(use_case['output'])
        )
        print(f"  ✓ Generated recommendations for {use_case['name']}")

    print("  ✓ Recommendations complete")
    print()

    # Step 5: Generate summary dashboard
    print("[5/5] Generating summary dashboard...")
    # Dashboard is already generated as dashboard_enhanced.html
    # No need to regenerate the old dashboard
    print("  ✓ Dashboard complete")
    print()

    # Final summary
    print("="*60)
    print("✓ Analysis Complete!")
    print("="*60)
    print()
    print("Generated reports:")
    print("  📊 data/merged/merged_summary.csv - Merged lens database")
    print("  💰 reports/price_analysis.md - Price trends and deals")
    print("  📈 reports/price_trends.csv - Historical price data")
    print("  🔍 reports/comparison_*.html - Lens comparisons")
    print("  🎯 reports/recommendations_*.html - Personalized recommendations")
    print("  📋 reports/dashboard.html - Summary dashboard")
    print()
    print("Open the dashboard:")
    print("  xdg-open reports/dashboard.html")
    print()


def generate_dashboard(lenses: list, deals: list):
    """Generate enhanced dashboard HTML with action buttons."""
    # Calculate statistics
    total_lenses = len(lenses)
    brands = set(l.get('brand') for l in lenses if l.get('brand'))
    prime_count = sum(1 for l in lenses if l.get('prime_or_zoom') == 'Prime')
    zoom_count = sum(1 for l in lenses if l.get('prime_or_zoom') == 'Zoom')

    prices = [l.get('current_price') for l in lenses if l.get('current_price')]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lens Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        /* Action Buttons Section */
        .action-buttons {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .action-btn {{
            background: white;
            border: none;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            text-decoration: none;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }}
        .action-btn:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            background: #667eea;
            color: white;
        }}
        .action-btn .icon {{
            font-size: 2.5em;
        }}
        .action-btn .label {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        .action-btn .desc {{
            font-size: 0.85em;
            opacity: 0.8;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #666;
            font-size: 1.1em;
        }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .links-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .link-card {{
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        .link-card:hover {{
            background: #667eea;
            color: white;
            border-color: #667eea;
            transform: translateX(5px);
        }}
        .link-card h3 {{
            margin-bottom: 10px;
        }}
        .link-card p {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .deals-list {{
            list-style: none;
        }}
        .deal-item {{
            background: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }}
        .deal-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .deal-price {{
            color: #667eea;
            font-size: 1.1em;
        }}
        .deal-savings {{
            color: #27ae60;
            font-weight: bold;
        }}

        @media (max-width: 768px) {{
            .action-buttons {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Lens Analysis Dashboard</h1>
            <p class="subtitle">Comprehensive lens data analysis and recommendations</p>
        </header>

        <!-- Action Buttons -->
        <div class="action-buttons">
            <button class="action-btn" onclick="runScraper()">
                <div class="icon">🔄</div>
                <div class="label">Scrape Data</div>
                <div class="desc">Fetch new lens data</div>
            </button>

            <button class="action-btn" onclick="runMerge()">
                <div class="icon">🔗</div>
                <div class="label">Merge Data</div>
                <div class="desc">Combine all sources</div>
            </button>

            <button class="action-btn" onclick="runPriceAnalysis()">
                <div class="icon">💰</div>
                <div class="label">Price Analysis</div>
                <div class="desc">Track price trends</div>
            </button>

            <button class="action-btn" onclick="runComparison()">
                <div class="icon">🔍</div>
                <div class="label">Compare Lenses</div>
                <div class="desc">Side-by-side comparison</div>
            </button>

            <button class="action-btn" onclick="runRecommendations()">
                <div class="icon">🎯</div>
                <div class="label">Get Recommendations</div>
                <div class="desc">Personalized suggestions</div>
            </button>

            <button class="action-btn" onclick="runFullAnalysis()">
                <div class="icon">⚡</div>
                <div class="label">Full Analysis</div>
                <div class="desc">Run everything</div>
            </button>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_lenses}</div>
                <div class="stat-label">Total Lenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(brands)}</div>
                <div class="stat-label">Brands</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{prime_count}</div>
                <div class="stat-label">Prime Lenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{zoom_count}</div>
                <div class="stat-label">Zoom Lenses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${avg_price:.0f}</div>
                <div class="stat-label">Average Price</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(deals)}</div>
                <div class="stat-label">Active Deals</div>
            </div>
        </div>

        <div class="section">
            <h2>🔥 Best Deals</h2>
            <ul class="deals-list">
"""

    for deal in deals[:5]:
        html += f"""
                <li class="deal-item">
                    <div class="deal-title">{deal['brand']} {deal['model_name']}</div>
                    <div class="deal-price">
                        ${deal['current_price']:.2f}
                        <span class="deal-savings">
                            (Save ${deal['savings']:.2f} / {deal['discount_pct']:.1f}% off)
                        </span>
                    </div>
                </li>
"""

    html += """
            </ul>
        </div>

        <div class="section">
            <h2>📈 Analysis Reports</h2>
            <div class="links-grid">
                <a href="price_analysis.md" class="link-card">
                    <h3>💰 Price Analysis</h3>
                    <p>Price trends, statistics, and historical data</p>
                </a>
                <a href="lens_preview.html" class="link-card">
                    <h3>📷 Lens Catalog</h3>
                    <p>Browse all lenses with search and filters</p>
                </a>
                <a href="comparison_24_70.html" class="link-card">
                    <h3>🔍 24-70mm Comparison</h3>
                    <p>Compare popular 24-70mm lenses</p>
                </a>
                <a href="comparison_50.html" class="link-card">
                    <h3>🔍 50mm Comparison</h3>
                    <p>Compare 50mm prime lenses</p>
                </a>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Recommendations</h2>
            <div class="links-grid">
                <a href="recommendations_travel.html" class="link-card">
                    <h3>✈️ Travel Photography</h3>
                    <p>Lightweight, versatile lenses for travel</p>
                </a>
                <a href="recommendations_portrait.html" class="link-card">
                    <h3>👤 Portrait Photography</h3>
                    <p>Best lenses for portrait work</p>
                </a>
                <a href="recommendations_budget.html" class="link-card">
                    <h3>💵 Budget Friendly</h3>
                    <p>Great lenses under $500</p>
                </a>
            </div>
        </div>

        <div class="section">
            <h2>📊 Data Files</h2>
            <div class="links-grid">
                <a href="../data/merged/merged_summary.csv" class="link-card">
                    <h3>📄 Merged Database (CSV)</h3>
                    <p>Complete lens database in CSV format</p>
                </a>
                <a href="price_trends.csv" class="link-card">
                    <h3>📈 Price Trends (CSV)</h3>
                    <p>Historical price data for analysis</p>
                </a>
            </div>
        </div>
    </div>

    <script>
        function showMessage(title, message) {
            alert(title + '\\n\\n' + message);
        }

        function runScraper() {
            showMessage(
                '🔄 Scrape Data',
                'To scrape new data, run in terminal:\\n\\n' +
                'python3 scripts/ingest/dpreview_run.py --brand Canon --limit 10\\n\\n' +
                'Or for B&H Photo:\\n' +
                'python3 scripts/ingest/bhphoto_scraper.py'
            );
        }

        function runMerge() {
            showMessage(
                '🔗 Merge Data',
                'To merge data from all sources, run:\\n\\n' +
                'python3 scripts/analysis/merge_data.py\\n\\n' +
                'This will combine DPReview, B&H Photo, and other sources.'
            );
        }

        function runPriceAnalysis() {
            showMessage(
                '💰 Price Analysis',
                'To analyze price trends, run:\\n\\n' +
                'python3 scripts/analysis/price_tracker.py\\n\\n' +
                'Output: reports/price_analysis.md'
            );
        }

        function runComparison() {
            showMessage(
                '🔍 Compare Lenses',
                'To compare lenses, run:\\n\\n' +
                'python3 scripts/analysis/lens_comparator.py\\n\\n' +
                'Output: reports/lens_comparison.html'
            );
        }

        function runRecommendations() {
            showMessage(
                '🎯 Get Recommendations',
                'To get personalized recommendations, run:\\n\\n' +
                'python3 scripts/analysis/lens_recommender.py\\n\\n' +
                'Output: reports/lens_recommendations.html'
            );
        }

        function runFullAnalysis() {
            showMessage(
                '⚡ Full Analysis',
                'To run complete analysis pipeline, run:\\n\\n' +
                'python3 scripts/run_analysis.py\\n\\n' +
                'This will:\\n' +
                '1. Merge all data\\n' +
                '2. Analyze prices\\n' +
                '3. Generate comparisons\\n' +
                '4. Create recommendations\\n' +
                '5. Update this dashboard'
            );
        }
    </script>
</body>
</html>
"""

    output_path = Path("reports/dashboard.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')


if __name__ == "__main__":
    run_full_analysis()
