#!/bin/bash
# Start the interactive dashboard server

echo "=========================================="
echo "🚀 Starting Interactive Dashboard"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")"

# Generate interactive dashboard
echo "Generating interactive dashboard..."
python3 scripts/generate_interactive_dashboard.py

echo ""
echo "Starting server (using Python built-in HTTP server)..."
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:5000"
echo ""

# Start the server in background
python3 dashboard_server_simple.py &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 2

# Try to open browser
echo "Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000 &
elif command -v open &> /dev/null; then
    open http://localhost:5000 &
elif command -v firefox &> /dev/null; then
    firefox http://localhost:5000 &
elif command -v google-chrome &> /dev/null; then
    google-chrome http://localhost:5000 &
else
    echo "Could not auto-open browser. Please manually open:"
    echo "  http://localhost:5000"
fi

echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for the server process
wait $SERVER_PID
