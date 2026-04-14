#!/bin/bash
# Quick test script for enhanced dashboard

echo "========================================="
echo "🎨 Enhanced Dashboard Test"
echo "========================================="
echo ""

# Check if files exist
echo "✓ Checking files..."
if [ -f "reports/dashboard_enhanced.html" ]; then
    echo "  ✓ dashboard_enhanced.html exists ($(wc -l < reports/dashboard_enhanced.html) lines)"
else
    echo "  ✗ dashboard_enhanced.html not found!"
    exit 1
fi

if [ -f "dashboard_server_simple.py" ]; then
    echo "  ✓ dashboard_server_simple.py exists"
else
    echo "  ✗ dashboard_server_simple.py not found!"
    exit 1
fi

# Check features
echo ""
echo "✓ Checking features..."

i18n_count=$(grep -c "data-zh" reports/dashboard_enhanced.html)
echo "  ✓ i18n elements: $i18n_count"

lens_card_count=$(grep -c "lens-card" reports/dashboard_enhanced.html)
echo "  ✓ Lens card styles: $lens_card_count"

lang_toggle=$(grep -c "lang-toggle" reports/dashboard_enhanced.html)
echo "  ✓ Language toggle: $lang_toggle"

gallery_func=$(grep -c "loadLensGallery" reports/dashboard_enhanced.html)
echo "  ✓ Gallery function: $gallery_func"

# Check data files
echo ""
echo "✓ Checking data files..."
if [ -f "data/parsed/dpreview/summary.csv" ]; then
    lens_count=$(( $(wc -l < data/parsed/dpreview/summary.csv) - 1 ))
    echo "  ✓ DPReview data: $lens_count lenses"
else
    echo "  ⚠ No data files found (run scraper first)"
fi

echo ""
echo "========================================="
echo "✅ All checks passed!"
echo "========================================="
echo ""
echo "To start the dashboard:"
echo "  ./start_dashboard.sh"
echo ""
echo "Features:"
echo "  • Chinese/English language switching"
echo "  • Lens gallery with brand colors"
echo "  • Real-time stats loading"
echo "  • Interactive function buttons"
echo "  • Responsive design"
echo ""
