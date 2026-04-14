"""
Lens comparison tool.
Compare specifications and features of multiple lenses side-by-side.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional

# Ensure we're in the project root
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))


class LensComparator:
    """Compare multiple lenses side-by-side."""

    def __init__(self, data_dir: Path = Path("data/merged")):
        self.data_dir = data_dir
        self.lenses = self.load_all_lenses()

    def load_all_lenses(self) -> Dict[str, dict]:
        """Load all lens data."""
        lenses = {}

        if not self.data_dir.exists():
            return lenses

        for json_file in self.data_dir.glob('*.json'):
            try:
                with json_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    key = f"{data.get('brand')}::{data.get('model_name')}"
                    lenses[key] = data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        return lenses

    def search_lenses(self, query: str) -> List[dict]:
        """Search for lenses by name."""
        query = query.lower()
        results = []

        for key, lens in self.lenses.items():
            model_name = lens.get('model_name', '').lower()
            brand = lens.get('brand', '').lower()

            if query in model_name or query in brand:
                results.append(lens)

        return results

    def compare_lenses(self, lens_keys: List[str]) -> dict:
        """Compare multiple lenses."""
        lenses_to_compare = []

        for key in lens_keys:
            if key in self.lenses:
                lenses_to_compare.append(self.lenses[key])
            else:
                # Try to find by partial match
                results = self.search_lenses(key)
                if results:
                    lenses_to_compare.append(results[0])

        if not lenses_to_compare:
            return {}

        # Build comparison table
        comparison = {
            'lenses': lenses_to_compare,
            'specs': self._build_spec_comparison(lenses_to_compare),
            'scores': self._calculate_scores(lenses_to_compare)
        }

        return comparison

    def _build_spec_comparison(self, lenses: List[dict]) -> dict:
        """Build specification comparison table."""
        specs = {}

        # Define spec categories
        spec_fields = [
            ('brand', 'Brand'),
            ('model_name', 'Model'),
            ('mount', 'Mount'),
            ('prime_or_zoom', 'Type'),
            ('focal_length_min', 'Focal Length Min (mm)'),
            ('focal_length_max', 'Focal Length Max (mm)'),
            ('max_aperture_wide', 'Max Aperture (Wide)'),
            ('max_aperture_tele', 'Max Aperture (Tele)'),
            ('min_aperture', 'Min Aperture'),
            ('weight', 'Weight (g)'),
            ('diameter', 'Diameter (mm)'),
            ('length', 'Length (mm)'),
            ('filter_thread', 'Filter Thread (mm)'),
            ('min_focus_distance', 'Min Focus Distance (m)'),
            ('max_magnification', 'Max Magnification'),
            ('autofocus', 'Autofocus'),
            ('image_stabilization', 'Image Stabilization'),
            ('weather_sealing', 'Weather Sealing'),
            ('current_price', 'Current Price ($)'),
            ('release_date', 'Release Date'),
        ]

        for field, label in spec_fields:
            values = []
            for lens in lenses:
                value = lens.get(field)
                if value is None:
                    values.append('N/A')
                elif isinstance(value, bool):
                    values.append('Yes' if value else 'No')
                elif isinstance(value, float):
                    values.append(f"{value:.2f}")
                else:
                    values.append(str(value))

            specs[label] = values

        return specs

    def _calculate_scores(self, lenses: List[dict]) -> List[dict]:
        """Calculate comparison scores for each lens."""
        scores = []

        for lens in lenses:
            score = {
                'model': lens.get('model_name'),
                'portability': self._calc_portability_score(lens),
                'versatility': self._calc_versatility_score(lens),
                'low_light': self._calc_low_light_score(lens),
                'value': self._calc_value_score(lens),
                'overall': 0
            }

            # Calculate overall score
            score['overall'] = (
                score['portability'] * 0.2 +
                score['versatility'] * 0.3 +
                score['low_light'] * 0.3 +
                score['value'] * 0.2
            )

            scores.append(score)

        return scores

    def _calc_portability_score(self, lens: dict) -> float:
        """Calculate portability score (0-100) based on weight and size."""
        weight = lens.get('weight')
        length = lens.get('length')

        if not weight:
            return 50  # Neutral score if no data

        # Lighter is better (score decreases with weight)
        # 200g = 100, 1000g = 50, 2000g+ = 0
        weight_score = max(0, min(100, 100 - (weight - 200) / 18))

        # Shorter is better
        if length:
            length_score = max(0, min(100, 100 - (length - 50) / 2))
            return (weight_score + length_score) / 2
        else:
            return weight_score

    def _calc_versatility_score(self, lens: dict) -> float:
        """Calculate versatility score based on focal range."""
        focal_min = lens.get('focal_length_min')
        focal_max = lens.get('focal_length_max')

        if not focal_min or not focal_max:
            return 50

        # Prime lenses get lower versatility score
        if focal_min == focal_max:
            return 30

        # Wider range = more versatile
        zoom_range = focal_max / focal_min

        # 1x = 30, 3x = 70, 5x+ = 100
        score = min(100, 30 + (zoom_range - 1) * 17.5)

        return score

    def _calc_low_light_score(self, lens: dict) -> float:
        """Calculate low-light performance score based on aperture."""
        aperture = lens.get('max_aperture_wide')

        if not aperture:
            return 50

        # Wider aperture (lower f-number) = better low light
        # f/1.4 = 100, f/2.8 = 70, f/4 = 50, f/5.6+ = 30
        if aperture <= 1.4:
            score = 100
        elif aperture <= 2.0:
            score = 85
        elif aperture <= 2.8:
            score = 70
        elif aperture <= 4.0:
            score = 50
        else:
            score = max(20, 50 - (aperture - 4) * 10)

        return score

    def _calc_value_score(self, lens: dict) -> float:
        """Calculate value score based on price and features."""
        price = lens.get('current_price')

        if not price:
            return 50

        # Lower price = better value (but consider features)
        # $200 = 100, $1000 = 60, $2000+ = 30
        base_score = max(20, min(100, 100 - (price - 200) / 18))

        # Adjust for features
        feature_bonus = 0

        if lens.get('image_stabilization'):
            feature_bonus += 5

        if lens.get('weather_sealing'):
            feature_bonus += 5

        if lens.get('autofocus'):
            feature_bonus += 5

        return min(100, base_score + feature_bonus)

    def generate_comparison_report(self, lens_keys: List[str], output_path: Path):
        """Generate HTML comparison report."""
        comparison = self.compare_lenses(lens_keys)

        if not comparison:
            print("No lenses found for comparison")
            return

        lenses = comparison['lenses']
        specs = comparison['specs']
        scores = comparison['scores']

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lens Comparison</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .comparison-table {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .spec-label {{
            font-weight: 600;
            color: #666;
        }}
        .score-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .score-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .score-card h3 {{
            margin-top: 0;
            color: #333;
        }}
        .score-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .score-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }}
        .score-value {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <h1>📷 Lens Comparison</h1>

    <div class="score-section">
"""

        # Add score cards
        for score in scores:
            html += f"""
        <div class="score-card">
            <h3>{score['model']}</h3>
            <div>
                <strong>Portability</strong>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score['portability']}%"></div>
                </div>
                <div class="score-value">{score['portability']:.1f}/100</div>
            </div>
            <div>
                <strong>Versatility</strong>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score['versatility']}%"></div>
                </div>
                <div class="score-value">{score['versatility']:.1f}/100</div>
            </div>
            <div>
                <strong>Low Light</strong>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score['low_light']}%"></div>
                </div>
                <div class="score-value">{score['low_light']:.1f}/100</div>
            </div>
            <div>
                <strong>Value</strong>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score['value']}%"></div>
                </div>
                <div class="score-value">{score['value']:.1f}/100</div>
            </div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #667eea;">
                <strong>Overall Score</strong>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score['overall']}%"></div>
                </div>
                <div class="score-value" style="font-size: 1.1em; font-weight: bold;">
                    {score['overall']:.1f}/100
                </div>
            </div>
        </div>
"""

        html += """
    </div>

    <div class="comparison-table">
        <table>
            <thead>
                <tr>
                    <th>Specification</th>
"""

        # Add lens names as column headers
        for lens in lenses:
            html += f"                    <th>{lens.get('model_name', 'Unknown')}</th>\n"

        html += """
                </tr>
            </thead>
            <tbody>
"""

        # Add specification rows
        for spec_label, values in specs.items():
            html += f"                <tr>\n"
            html += f"                    <td class=\"spec-label\">{spec_label}</td>\n"

            for value in values:
                html += f"                    <td>{value}</td>\n"

            html += "                </tr>\n"

        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        # Save HTML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')

        print(f"✓ Comparison report generated: {output_path}")


def main():
    """Run lens comparison."""
    comparator = LensComparator()

    # Example: Compare Canon RF 24-70mm lenses
    print("Comparing lenses...")

    # Search for lenses to compare
    search_terms = ["24-70", "50mm"]

    lens_keys = []
    for term in search_terms:
        results = comparator.search_lenses(term)
        if results:
            key = f"{results[0].get('brand')}::{results[0].get('model_name')}"
            lens_keys.append(key)

    if lens_keys:
        comparator.generate_comparison_report(lens_keys, Path("reports/lens_comparison.html"))
        print(f"\n✓ Compared {len(lens_keys)} lenses")
    else:
        print("No lenses found to compare")


if __name__ == "__main__":
    main()
