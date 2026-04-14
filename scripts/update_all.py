#!/usr/bin/env python3
"""
Complete data update pipeline.
Synchronizes data and regenerates all HTML pages.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def main():
    """Run complete update pipeline."""
    print("\n" + "="*60)
    print("🔄 Complete Data Update Pipeline")
    print("="*60)

    steps = [
        ("python3 scripts/sync_data.py", "Step 1: Synchronize data sources"),
        ("python3 scripts/generate_dynamic_catalog.py", "Step 2: Generate dynamic catalog"),
        ("python3 scripts/run_analysis.py", "Step 3: Run full analysis"),
    ]

    success_count = 0
    for cmd, description in steps:
        if run_command(cmd, description):
            success_count += 1
        else:
            print(f"\n⚠️ Step failed: {description}")

    print("\n" + "="*60)
    if success_count == len(steps):
        print("✅ All updates completed successfully!")
    else:
        print(f"⚠️ Completed {success_count}/{len(steps)} steps")
    print("="*60)

    print("\n📊 Updated files:")
    print("  • data/merged/merged_summary.csv - Unified data source (31 lenses)")
    print("  • reports/dashboard_enhanced.html - Main dashboard")
    print("  • reports/lens_catalog.html - Dynamic catalog")
    print("  • reports/lens_data_table.html - Data table")
    print("  • reports/comparison_*.html - Lens comparisons")
    print("  • reports/recommendations_*.html - Recommendations")
    print("\n🌐 Open dashboard:")
    print("  xdg-open reports/dashboard_enhanced.html")
    print()

if __name__ == '__main__':
    main()
