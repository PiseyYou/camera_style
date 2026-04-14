"""
Lens recommendation system.
Recommends lenses based on user requirements and preferences.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Ensure we're in the project root
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))


@dataclass
class UserRequirements:
    """User requirements for lens recommendation."""
    # Budget
    max_budget: Optional[float] = None
    min_budget: Optional[float] = None

    # Brand preference
    preferred_brands: Optional[List[str]] = None
    excluded_brands: Optional[List[str]] = None

    # Mount type
    mount: Optional[str] = None

    # Lens type
    lens_type: Optional[str] = None  # "prime", "zoom", or None for both

    # Focal length
    min_focal_length: Optional[float] = None
    max_focal_length: Optional[float] = None

    # Aperture
    max_aperture_requirement: Optional[float] = None  # e.g., 2.8 or wider

    # Weight
    max_weight: Optional[float] = None  # in grams

    # Features
    require_autofocus: bool = False
    require_image_stabilization: bool = False
    require_weather_sealing: bool = False

    # Use case priorities (0-1 scale)
    portability_priority: float = 0.5
    low_light_priority: float = 0.5
    versatility_priority: float = 0.5
    value_priority: float = 0.5


class LensRecommender:
    """Recommend lenses based on user requirements."""

    def __init__(self, data_dir: Path = Path("data/merged")):
        self.data_dir = data_dir
        self.lenses = self.load_all_lenses()

    def load_all_lenses(self) -> List[dict]:
        """Load all lens data."""
        lenses = []

        if not self.data_dir.exists():
            return lenses

        for json_file in self.data_dir.glob('*.json'):
            try:
                with json_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    lenses.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        return lenses

    def filter_lenses(self, requirements: UserRequirements) -> List[dict]:
        """Filter lenses based on hard requirements."""
        filtered = []

        for lens in self.lenses:
            # Check budget
            price = lens.get('current_price')
            if price:
                if requirements.max_budget and price > requirements.max_budget:
                    continue
                if requirements.min_budget and price < requirements.min_budget:
                    continue

            # Check brand
            brand = lens.get('brand')
            if requirements.preferred_brands and brand not in requirements.preferred_brands:
                continue
            if requirements.excluded_brands and brand in requirements.excluded_brands:
                continue

            # Check mount
            if requirements.mount:
                lens_mount = lens.get('mount', '')
                if requirements.mount.lower() not in lens_mount.lower():
                    continue

            # Check lens type
            if requirements.lens_type:
                lens_type = lens.get('prime_or_zoom', '').lower()
                if requirements.lens_type.lower() not in lens_type.lower():
                    continue

            # Check focal length
            focal_min = lens.get('focal_length_min')
            focal_max = lens.get('focal_length_max')

            if requirements.min_focal_length and focal_max:
                if focal_max < requirements.min_focal_length:
                    continue

            if requirements.max_focal_length and focal_min:
                if focal_min > requirements.max_focal_length:
                    continue

            # Check aperture
            if requirements.max_aperture_requirement:
                aperture = lens.get('max_aperture_wide')
                if not aperture or aperture > requirements.max_aperture_requirement:
                    continue

            # Check weight
            if requirements.max_weight:
                weight = lens.get('weight')
                if weight and weight > requirements.max_weight:
                    continue

            # Check features
            if requirements.require_autofocus:
                if not lens.get('autofocus'):
                    continue

            if requirements.require_image_stabilization:
                if not lens.get('image_stabilization'):
                    continue

            if requirements.require_weather_sealing:
                if not lens.get('weather_sealing'):
                    continue

            filtered.append(lens)

        return filtered

    def score_lens(self, lens: dict, requirements: UserRequirements) -> float:
        """Calculate recommendation score for a lens."""
        score = 0.0

        # Portability score
        weight = lens.get('weight')
        if weight:
            # Lighter is better
            portability_score = max(0, min(100, 100 - (weight - 200) / 18))
            score += portability_score * requirements.portability_priority

        # Low light score
        aperture = lens.get('max_aperture_wide')
        if aperture:
            if aperture <= 1.4:
                low_light_score = 100
            elif aperture <= 2.0:
                low_light_score = 85
            elif aperture <= 2.8:
                low_light_score = 70
            elif aperture <= 4.0:
                low_light_score = 50
            else:
                low_light_score = max(20, 50 - (aperture - 4) * 10)

            score += low_light_score * requirements.low_light_priority

        # Versatility score
        focal_min = lens.get('focal_length_min')
        focal_max = lens.get('focal_length_max')

        if focal_min and focal_max:
            if focal_min == focal_max:
                versatility_score = 30  # Prime lens
            else:
                zoom_range = focal_max / focal_min
                versatility_score = min(100, 30 + (zoom_range - 1) * 17.5)

            score += versatility_score * requirements.versatility_priority

        # Value score
        price = lens.get('current_price')
        if price:
            base_score = max(20, min(100, 100 - (price - 200) / 18))

            # Feature bonuses
            if lens.get('image_stabilization'):
                base_score += 5
            if lens.get('weather_sealing'):
                base_score += 5
            if lens.get('autofocus'):
                base_score += 5

            value_score = min(100, base_score)
            score += value_score * requirements.value_priority

        # Normalize score
        total_priority = (
            requirements.portability_priority +
            requirements.low_light_priority +
            requirements.versatility_priority +
            requirements.value_priority
        )

        if total_priority > 0:
            score = score / total_priority

        return score

    def recommend(self, requirements: UserRequirements, top_n: int = 10) -> List[dict]:
        """Recommend lenses based on requirements."""
        # Filter lenses
        filtered = self.filter_lenses(requirements)

        if not filtered:
            return []

        # Score each lens
        scored_lenses = []
        for lens in filtered:
            score = self.score_lens(lens, requirements)
            scored_lenses.append({
                'lens': lens,
                'score': score
            })

        # Sort by score
        scored_lenses.sort(key=lambda x: x['score'], reverse=True)

        # Return top N
        return scored_lenses[:top_n]

    def generate_recommendation_report(self, requirements: UserRequirements, output_path: Path):
        """Generate HTML recommendation report."""
        recommendations = self.recommend(requirements, top_n=10)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lens Recommendations</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .requirements {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .requirements h2 {{
            margin-top: 0;
            color: #667eea;
        }}
        .requirements ul {{
            list-style: none;
            padding: 0;
        }}
        .requirements li {{
            padding: 5px 0;
            color: #666;
        }}
        .recommendation {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 20px;
        }}
        .rank {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            min-width: 50px;
        }}
        .lens-info {{
            flex: 1;
        }}
        .lens-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .lens-specs {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .spec {{
            color: #666;
        }}
        .spec strong {{
            color: #333;
        }}
        .score {{
            text-align: right;
            min-width: 100px;
        }}
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .score-label {{
            color: #999;
            font-size: 0.9em;
        }}
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 10px;
            color: #999;
        }}
    </style>
</head>
<body>
    <h1>🎯 Lens Recommendations</h1>

    <div class="requirements">
        <h2>Your Requirements</h2>
        <ul>
"""

        # Add requirements
        if requirements.max_budget:
            html += f"            <li>💰 Budget: Up to ${requirements.max_budget:.0f}</li>\n"

        if requirements.mount:
            html += f"            <li>🔧 Mount: {requirements.mount}</li>\n"

        if requirements.lens_type:
            html += f"            <li>📷 Type: {requirements.lens_type.capitalize()}</li>\n"

        if requirements.max_aperture_requirement:
            html += f"            <li>🌙 Max Aperture: f/{requirements.max_aperture_requirement} or wider</li>\n"

        if requirements.max_weight:
            html += f"            <li>⚖️ Max Weight: {requirements.max_weight}g</li>\n"

        # Add priorities
        priorities = []
        if requirements.portability_priority > 0.7:
            priorities.append("Portability")
        if requirements.low_light_priority > 0.7:
            priorities.append("Low Light")
        if requirements.versatility_priority > 0.7:
            priorities.append("Versatility")
        if requirements.value_priority > 0.7:
            priorities.append("Value")

        if priorities:
            html += f"            <li>⭐ Priorities: {', '.join(priorities)}</li>\n"

        html += """
        </ul>
    </div>
"""

        if not recommendations:
            html += """
    <div class="no-results">
        <h2>No lenses found matching your requirements</h2>
        <p>Try adjusting your filters or budget</p>
    </div>
"""
        else:
            for idx, rec in enumerate(recommendations, 1):
                lens = rec['lens']
                score = rec['score']

                html += f"""
    <div class="recommendation">
        <div class="rank">#{idx}</div>
        <div class="lens-info">
            <div class="lens-title">{lens.get('brand')} {lens.get('model_name')}</div>
            <div class="lens-specs">
                <div class="spec"><strong>Mount:</strong> {lens.get('mount', 'N/A')}</div>
                <div class="spec"><strong>Type:</strong> {lens.get('prime_or_zoom', 'N/A')}</div>
                <div class="spec"><strong>Focal Length:</strong> {lens.get('focal_length_min', 'N/A')}-{lens.get('focal_length_max', 'N/A')}mm</div>
                <div class="spec"><strong>Max Aperture:</strong> f/{lens.get('max_aperture_wide', 'N/A')}</div>
                <div class="spec"><strong>Weight:</strong> {lens.get('weight', 'N/A')}g</div>
                <div class="spec"><strong>Price:</strong> ${lens.get('current_price', 'N/A')}</div>
            </div>
        </div>
        <div class="score">
            <div class="score-value">{score:.0f}</div>
            <div class="score-label">Match Score</div>
        </div>
    </div>
"""

        html += """
</body>
</html>
"""

        # Save HTML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')

        print(f"✓ Recommendation report generated: {output_path}")


def main():
    """Run lens recommendation."""
    recommender = LensRecommender()

    # Example: Recommend lenses for travel photography
    requirements = UserRequirements(
        max_budget=1500,
        mount="Canon RF",
        max_weight=800,
        portability_priority=0.8,
        versatility_priority=0.9,
        low_light_priority=0.6,
        value_priority=0.7
    )

    print("Generating recommendations...")
    recommender.generate_recommendation_report(requirements, Path("reports/lens_recommendations.html"))

    # Show top 5
    recommendations = recommender.recommend(requirements, top_n=5)

    if recommendations:
        print("\n🎯 Top 5 Recommendations:")
        for idx, rec in enumerate(recommendations, 1):
            lens = rec['lens']
            print(f"  {idx}. {lens.get('brand')} {lens.get('model_name')} "
                  f"(Score: {rec['score']:.0f})")
    else:
        print("\nNo lenses found matching requirements")


if __name__ == "__main__":
    main()
