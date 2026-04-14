"""
Data merging and deduplication system.
Combines data from multiple sources and resolves conflicts.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
import difflib

# Ensure we're in the project root
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))


class LensMerger:
    """Merge lens data from multiple sources."""

    def __init__(self):
        self.similarity_threshold = 0.85  # For fuzzy matching

    def normalize_model_name(self, name: str) -> str:
        """Normalize model name for comparison."""
        if not name:
            return ""

        # Convert to lowercase
        name = name.lower()

        # Remove common prefixes
        for prefix in ['canon', 'nikon', 'sony', 'fujifilm', 'panasonic', 'olympus']:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()

        # Normalize spacing
        name = ' '.join(name.split())

        # Remove special characters but keep numbers and letters
        import re
        name = re.sub(r'[^\w\s\-\.]', '', name)

        return name

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two model names."""
        norm1 = self.normalize_model_name(name1)
        norm2 = self.normalize_model_name(name2)

        return difflib.SequenceMatcher(None, norm1, norm2).ratio()

    def are_same_lens(self, lens1: dict, lens2: dict) -> bool:
        """Determine if two lens records refer to the same lens."""
        # Check brand first
        if lens1.get('brand') != lens2.get('brand'):
            return False

        # Check model name similarity
        similarity = self.calculate_similarity(
            lens1.get('model_name', ''),
            lens2.get('model_name', '')
        )

        if similarity >= self.similarity_threshold:
            return True

        # Check focal length and aperture as additional confirmation
        if (lens1.get('focal_length_min') == lens2.get('focal_length_min') and
            lens1.get('focal_length_max') == lens2.get('focal_length_max') and
            lens1.get('max_aperture_wide') == lens2.get('max_aperture_wide')):
            return True

        return False

    def merge_lens_data(self, lenses: List[dict]) -> dict:
        """
        Merge multiple records of the same lens from different sources.
        Priority: manufacturer > bhphoto > dpreview
        """
        if not lenses:
            return {}

        if len(lenses) == 1:
            return lenses[0]

        # Sort by source priority
        source_priority = {'manufacturer': 0, 'bhphoto': 1, 'dpreview': 2, 'adorama': 3}
        lenses = sorted(lenses, key=lambda x: source_priority.get(x.get('source', 'unknown'), 99))

        # Start with the highest priority source
        merged = lenses[0].copy()
        merged['sources'] = [lenses[0].get('source')]
        merged['source_urls'] = {lenses[0].get('source'): lenses[0].get('source_url')}

        # Merge data from other sources
        for lens in lenses[1:]:
            source = lens.get('source')
            merged['sources'].append(source)
            merged['source_urls'][source] = lens.get('source_url')

            # Fill in missing fields
            for key, value in lens.items():
                if key in ['source', 'source_url', 'fetched_at', 'raw_title']:
                    continue

                # If current value is None or empty, use the new value
                if merged.get(key) in [None, '', []]:
                    merged[key] = value

                # For prices, keep track of all sources
                elif key == 'current_price' and value:
                    if 'prices' not in merged:
                        merged['prices'] = {}
                    merged['prices'][source] = value

        # Calculate average price if multiple sources
        if 'prices' in merged and len(merged['prices']) > 1:
            prices = [p for p in merged['prices'].values() if p]
            if prices:
                merged['avg_price'] = sum(prices) / len(prices)
                merged['min_price'] = min(prices)
                merged['max_price'] = max(prices)

        return merged

    def deduplicate_lenses(self, lenses: List[dict]) -> List[dict]:
        """Remove duplicate lenses and merge their data."""
        if not lenses:
            return []

        # Group lenses by brand first for efficiency
        by_brand = defaultdict(list)
        for lens in lenses:
            brand = lens.get('brand', 'Unknown')
            by_brand[brand].append(lens)

        # Find duplicates within each brand
        merged_lenses = []

        for brand, brand_lenses in by_brand.items():
            processed = set()

            for i, lens1 in enumerate(brand_lenses):
                if i in processed:
                    continue

                # Find all duplicates of this lens
                duplicates = [lens1]

                for j, lens2 in enumerate(brand_lenses[i+1:], start=i+1):
                    if j in processed:
                        continue

                    if self.are_same_lens(lens1, lens2):
                        duplicates.append(lens2)
                        processed.add(j)

                # Merge all duplicates
                merged = self.merge_lens_data(duplicates)
                merged_lenses.append(merged)
                processed.add(i)

        return merged_lenses

    def load_from_csv(self, csv_path: Path) -> List[dict]:
        """Load lens data from CSV file."""
        if not csv_path.exists():
            return []

        with csv_path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def load_from_json_dir(self, json_dir: Path) -> List[dict]:
        """Load all JSON files from a directory."""
        if not json_dir.exists():
            return []

        lenses = []
        for json_file in json_dir.glob('*.json'):
            if json_file.name == 'summary.json':
                continue

            try:
                with json_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    lenses.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        return lenses

    def save_merged_data(self, lenses: List[dict], output_dir: Path):
        """Save merged data to JSON and CSV."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save individual JSON files
        for lens in lenses:
            model_slug = self.normalize_model_name(lens.get('model_name', 'unknown'))
            model_slug = model_slug.replace(' ', '-')[:50]
            brand_slug = lens.get('brand', 'unknown').lower()
            filename = f"{brand_slug}-{model_slug}.json"

            json_path = output_dir / filename
            with json_path.open('w', encoding='utf-8') as f:
                json.dump(lens, f, ensure_ascii=False, indent=2)

        # Save summary CSV
        if lenses:
            csv_path = output_dir / 'merged_summary.csv'
            fieldnames = list(lenses[0].keys())

            # Remove complex fields from CSV
            fieldnames = [f for f in fieldnames if f not in ['sources', 'source_urls', 'prices']]

            with csv_path.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(lenses)

        print(f"✓ Saved {len(lenses)} merged lenses to {output_dir}")


def main():
    """Merge data from all sources."""
    merger = LensMerger()

    print("Loading data from all sources...")

    # Load from DPReview
    dpreview_lenses = merger.load_from_json_dir(Path("data/parsed/dpreview"))
    print(f"  DPReview: {len(dpreview_lenses)} lenses")

    # Load from B&H Photo
    bhphoto_lenses = merger.load_from_json_dir(Path("data/parsed/bhphoto"))
    print(f"  B&H Photo: {len(bhphoto_lenses)} lenses")

    # Load from Adorama
    adorama_lenses = merger.load_from_json_dir(Path("data/parsed/adorama"))
    print(f"  Adorama: {len(adorama_lenses)} lenses")

    # Combine all
    all_lenses = dpreview_lenses + bhphoto_lenses + adorama_lenses
    print(f"\nTotal before deduplication: {len(all_lenses)}")

    # Deduplicate and merge
    print("Deduplicating and merging...")
    merged_lenses = merger.deduplicate_lenses(all_lenses)
    print(f"Total after deduplication: {len(merged_lenses)}")

    # Save merged data
    print("\nSaving merged data...")
    merger.save_merged_data(merged_lenses, Path("data/merged"))

    print("\n✓ Merge complete!")
    print(f"  Output: data/merged/merged_summary.csv")


if __name__ == "__main__":
    main()
