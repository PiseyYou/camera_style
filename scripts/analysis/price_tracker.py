"""
Price tracking and trend analysis system.
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import statistics

# Ensure we're in the project root
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))


class PriceTracker:
    """Track lens prices over time and analyze trends."""

    def __init__(self, history_file: Path = Path("data/price_history.json")):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> dict:
        """Load price history from file."""
        if not self.history_file.exists():
            return {}

        try:
            with self.history_file.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading price history: {e}")
            return {}

    def save_history(self):
        """Save price history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        with self.history_file.open('w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_lens_key(self, lens: dict) -> str:
        """Generate unique key for a lens."""
        brand = lens.get('brand', 'unknown')
        model = lens.get('model_name', 'unknown')
        return f"{brand}::{model}"

    def record_price(self, lens: dict, source: str, price: float, currency: str = "USD"):
        """Record a price observation."""
        lens_key = self.get_lens_key(lens)

        if lens_key not in self.history:
            self.history[lens_key] = {
                'brand': lens.get('brand'),
                'model_name': lens.get('model_name'),
                'prices': []
            }

        # Add price record
        self.history[lens_key]['prices'].append({
            'date': datetime.utcnow().isoformat(),
            'source': source,
            'price': price,
            'currency': currency
        })

        self.save_history()

    def get_price_history(self, lens_key: str) -> List[dict]:
        """Get price history for a lens."""
        if lens_key not in self.history:
            return []

        return self.history[lens_key]['prices']

    def calculate_price_stats(self, lens_key: str, days: int = 30) -> Optional[dict]:
        """Calculate price statistics for a lens."""
        prices = self.get_price_history(lens_key)

        if not prices:
            return None

        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_prices = [
            p for p in prices
            if datetime.fromisoformat(p['date'].replace('Z', '+00:00')) >= cutoff_date
        ]

        if not recent_prices:
            recent_prices = prices[-10:]  # Use last 10 if no recent data

        price_values = [p['price'] for p in recent_prices]

        if not price_values:
            return None

        stats = {
            'current_price': price_values[-1],
            'min_price': min(price_values),
            'max_price': max(price_values),
            'avg_price': statistics.mean(price_values),
            'median_price': statistics.median(price_values),
            'price_range': max(price_values) - min(price_values),
            'num_observations': len(price_values),
            'first_seen': recent_prices[0]['date'],
            'last_seen': recent_prices[-1]['date'],
        }

        # Calculate trend
        if len(price_values) >= 2:
            first_price = price_values[0]
            last_price = price_values[-1]
            price_change = last_price - first_price
            price_change_pct = (price_change / first_price) * 100

            stats['price_change'] = price_change
            stats['price_change_pct'] = price_change_pct

            if price_change_pct > 5:
                stats['trend'] = 'increasing'
            elif price_change_pct < -5:
                stats['trend'] = 'decreasing'
            else:
                stats['trend'] = 'stable'
        else:
            stats['trend'] = 'unknown'

        # Calculate volatility (standard deviation)
        if len(price_values) >= 3:
            stats['volatility'] = statistics.stdev(price_values)
        else:
            stats['volatility'] = 0

        return stats

    def find_best_deals(self, min_discount_pct: float = 10) -> List[dict]:
        """Find lenses with significant price drops."""
        deals = []

        for lens_key, data in self.history.items():
            stats = self.calculate_price_stats(lens_key, days=90)

            if not stats:
                continue

            # Check if current price is significantly below average
            discount_pct = ((stats['avg_price'] - stats['current_price']) / stats['avg_price']) * 100

            if discount_pct >= min_discount_pct:
                deals.append({
                    'brand': data['brand'],
                    'model_name': data['model_name'],
                    'current_price': stats['current_price'],
                    'avg_price': stats['avg_price'],
                    'discount_pct': discount_pct,
                    'savings': stats['avg_price'] - stats['current_price']
                })

        # Sort by discount percentage
        deals.sort(key=lambda x: x['discount_pct'], reverse=True)

        return deals

    def generate_price_report(self, output_path: Path):
        """Generate comprehensive price analysis report."""
        report_lines = [
            "# Lens Price Analysis Report",
            f"\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        ]

        if len(self.history) == 0:
            report_lines.extend([
                "\n## ⚠️ No Price Data Available",
                "\nCurrently, no price information is available in the dataset.",
                "\n### Why?",
                "- DPReview does not provide current pricing information",
                "- Price data needs to be collected from retailers like B&H Photo, Adorama, etc.",
                "\n### Next Steps",
                "To enable price tracking:",
                "1. Integrate with retailer APIs (B&H Photo, Adorama, Amazon)",
                "2. Add web scraping for current prices",
                "3. Set up automated price monitoring",
                "\n### Available Data",
                "The current dataset includes:",
                "- Lens specifications (focal length, aperture, weight, etc.)",
                "- Release dates",
                "- Technical details",
                "\nFor now, you can:",
                "- Browse the lens catalog",
                "- Compare lens specifications",
                "- Get recommendations based on features",
            ])
        else:
            report_lines.append(f"\nTotal lenses with price data: {len(self.history)}")
            report_lines.append("\n## Price Statistics by Lens\n")

            # Analyze each lens
            for lens_key, data in sorted(self.history.items()):
                stats = self.calculate_price_stats(lens_key, days=30)

                if not stats:
                    continue

                report_lines.append(f"\n### {data['brand']} {data['model_name']}\n")
                report_lines.append(f"- **Current Price**: ${stats['current_price']:.2f}")
                report_lines.append(f"- **Average Price (30d)**: ${stats['avg_price']:.2f}")
                report_lines.append(f"- **Price Range**: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
                report_lines.append(f"- **Trend**: {stats['trend'].capitalize()}")

                if 'price_change_pct' in stats:
                    change_symbol = "📈" if stats['price_change_pct'] > 0 else "📉"
                    report_lines.append(f"- **30-Day Change**: {change_symbol} {stats['price_change_pct']:.1f}%")

                report_lines.append(f"- **Observations**: {stats['num_observations']}")

            # Find best deals
            deals = self.find_best_deals(min_discount_pct=5)

            if deals:
                report_lines.append("\n## 🔥 Best Deals (Current Price Below Average)\n")

                for deal in deals[:10]:
                    report_lines.append(
                        f"- **{deal['brand']} {deal['model_name']}**: "
                        f"${deal['current_price']:.2f} "
                        f"(was ${deal['avg_price']:.2f}, "
                        f"save ${deal['savings']:.2f} / {deal['discount_pct']:.1f}%)"
                    )

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('\n'.join(report_lines), encoding='utf-8')

        print(f"✓ Price report generated: {output_path}")

    def export_price_trends_csv(self, output_path: Path):
        """Export price trends to CSV for visualization."""
        rows = []

        for lens_key, data in self.history.items():
            for price_record in data['prices']:
                rows.append({
                    'brand': data['brand'],
                    'model_name': data['model_name'],
                    'date': price_record['date'],
                    'source': price_record['source'],
                    'price': price_record['price'],
                    'currency': price_record['currency']
                })

        if rows:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            print(f"✓ Price trends exported: {output_path}")


def main():
    """Run price tracking analysis."""
    tracker = PriceTracker()

    print("Analyzing price data...")

    # Load existing lens data and record prices
    from pathlib import Path
    import csv

    # Try to load from merged data first
    csv_path = Path("data/merged/merged_summary.csv")
    if not csv_path.exists():
        csv_path = Path("data/parsed/dpreview/summary.csv")

    if csv_path.exists():
        print(f"Loading data from {csv_path}...")
        with csv_path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            lenses = list(reader)

        print(f"Found {len(lenses)} lenses")

        # Record prices for lenses that have price data
        for lens in lenses:
            price = lens.get('current_price')
            if price and price != 'N/A':
                try:
                    price_float = float(price)
                    if price_float > 0:
                        tracker.record_price(
                            lens,
                            lens.get('source', 'dpreview'),
                            price_float,
                            lens.get('currency', 'USD')
                        )
                except (ValueError, TypeError):
                    continue

        print(f"Recorded prices for {len(tracker.history)} lenses")

    # Generate reports
    tracker.generate_price_report(Path("reports/price_analysis.md"))
    tracker.export_price_trends_csv(Path("reports/price_trends.csv"))

    # Show best deals
    deals = tracker.find_best_deals(min_discount_pct=5)

    if deals:
        print("\n🔥 Best Deals Found:")
        for deal in deals[:5]:
            print(f"  {deal['brand']} {deal['model_name']}: "
                  f"${deal['current_price']:.2f} "
                  f"(save ${deal['savings']:.2f} / {deal['discount_pct']:.1f}%)")
    else:
        print("\nNo significant deals found.")

    print("\n✓ Price analysis complete!")


if __name__ == "__main__":
    main()
