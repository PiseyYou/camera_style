#!/usr/bin/env python3
"""
Synchronize data across all sources to ensure unified database.
"""

import shutil
from pathlib import Path

def sync_data():
    """Sync parsed data to merged directory."""

    source = Path('data/parsed/dpreview/summary.csv')
    target = Path('data/merged/merged_summary.csv')

    if not source.exists():
        print(f"❌ Source file not found: {source}")
        return False

    # Ensure target directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Copy file
    shutil.copy2(source, target)

    # Count lines
    with source.open('r', encoding='utf-8') as f:
        source_lines = len(f.readlines())

    with target.open('r', encoding='utf-8') as f:
        target_lines = len(f.readlines())

    print(f"✓ Data synchronized:")
    print(f"  Source: {source} ({source_lines} lines)")
    print(f"  Target: {target} ({target_lines} lines)")
    print(f"  Lenses: {source_lines - 1}")

    return True

if __name__ == '__main__':
    sync_data()
