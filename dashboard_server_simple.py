#!/usr/bin/env python3
"""
Simple HTTP server for the lens analysis dashboard.
Uses only Python standard library - no external dependencies.
"""

import http.server
import socketserver
import subprocess
import json
import urllib.parse
from pathlib import Path
import os

PORT = 5000
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard requests."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        print(f"Request: {path}")  # Debug log

        # Serve dashboard
        if path == '/' or path == '/dashboard' or path == '':
            self.serve_file('reports/dashboard_enhanced.html', 'text/html')

        # API: Get stats
        elif path == '/api/stats':
            self.get_stats()

        # API: Get history
        elif path == '/api/history':
            self.get_history()

        # API endpoints
        elif path.startswith('/api/'):
            self.handle_api(path)

        # Serve reports - handle both with and without /reports/ prefix
        elif path.startswith('/reports/'):
            filename = path[9:]  # Remove '/reports/'
            self.serve_file(f'reports/{filename}')

        # Also try without /reports/ prefix for backward compatibility
        elif path.endswith('.html') or path.endswith('.md') or path.endswith('.csv'):
            # Try in reports directory first
            filename = path.lstrip('/')
            if (PROJECT_ROOT / 'reports' / filename).exists():
                self.serve_file(f'reports/{filename}')
            else:
                self.serve_file(filename)

        # Serve data files
        elif path.startswith('/data/'):
            filename = path[6:]  # Remove '/data/'
            self.serve_file(f'data/{filename}')

        else:
            self.send_error(404, f"File not found: {path}")

    def serve_file(self, filepath, content_type=None):
        """Serve a file."""
        try:
            file_path = PROJECT_ROOT / filepath

            if not file_path.exists():
                self.send_error(404, f"File not found: {filepath}")
                return

            # Determine content type
            if content_type is None:
                if filepath.endswith('.html'):
                    content_type = 'text/html'
                elif filepath.endswith('.css'):
                    content_type = 'text/css'
                elif filepath.endswith('.js'):
                    content_type = 'application/javascript'
                elif filepath.endswith('.json'):
                    content_type = 'application/json'
                elif filepath.endswith('.csv'):
                    content_type = 'text/csv'
                elif filepath.endswith('.md'):
                    content_type = 'text/markdown'
                else:
                    content_type = 'text/plain'

            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")

    def get_stats(self):
        """Get current statistics."""
        try:
            import csv

            # Try to load merged data first
            csv_path = PROJECT_ROOT / 'data/merged/merged_summary.csv'
            if not csv_path.exists():
                csv_path = PROJECT_ROOT / 'data/parsed/dpreview/summary.csv'

            if not csv_path.exists():
                self.send_json_response({
                    'success': True,
                    'stats': {
                        'total': 0,
                        'brands': 0,
                        'prime': 0,
                        'zoom': 0,
                        'avg_price': 0
                    }
                })
                return

            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                lenses = list(reader)

            brands = set(l.get('brand') for l in lenses if l.get('brand'))
            prime_count = sum(1 for l in lenses if l.get('prime_or_zoom') == 'Prime')
            zoom_count = sum(1 for l in lenses if l.get('prime_or_zoom') == 'Zoom')

            prices = [float(l.get('current_price', 0)) for l in lenses if l.get('current_price')]
            avg_price = sum(prices) / len(prices) if prices else 0

            self.send_json_response({
                'success': True,
                'stats': {
                    'total': len(lenses),
                    'brands': len(brands),
                    'prime': prime_count,
                    'zoom': zoom_count,
                    'avg_price': round(avg_price, 2)
                }
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def get_history(self):
        """Get analysis history."""
        try:
            history_file = PROJECT_ROOT / 'data/analysis_history.json'

            if not history_file.exists():
                self.send_json_response({
                    'success': True,
                    'history': []
                })
                return

            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            self.send_json_response({
                'success': True,
                'history': history
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, 500)

    def handle_api(self, path):
        """Handle API requests."""
        try:
            result = None

            if path.startswith('/api/scrape/'):
                # Extract brand and limit from path
                parts = path.split('/')
                if len(parts) >= 5:
                    brand = parts[3]
                    limit = parts[4]
                    result = self.run_command([
                        'python3', 'scripts/ingest/dpreview_run.py',
                        '--brand', brand, '--limit', limit
                    ])

            elif path == '/api/merge':
                result = self.run_command(['python3', 'scripts/analysis/merge_data.py'])

            elif path == '/api/price-analysis':
                result = self.run_command(['python3', 'scripts/analysis/price_tracker.py'])

            elif path == '/api/comparison':
                result = self.run_command(['python3', 'scripts/analysis/lens_comparator.py'])

            elif path == '/api/recommendations':
                result = self.run_command(['python3', 'scripts/analysis/lens_recommender.py'])

            elif path == '/api/full-analysis':
                result = self.run_command(['python3', 'scripts/run_analysis.py'])

            else:
                self.send_json_response({'success': False, 'error': 'Unknown API endpoint'}, 404)
                return

            if result:
                self.send_json_response(result)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': f'API error: {str(e)}'
            }, 500)

    def run_command(self, cmd):
        """Run a command and return the result."""
        try:
            # Add better error handling
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=PROJECT_ROOT,
                env={**os.environ, 'PYTHONPATH': str(PROJECT_ROOT)}
            )

            success = result.returncode == 0

            # Save to history
            if success:
                self.save_to_history(cmd, result.stdout)

            return {
                'success': success,
                'output': result.stdout if success else f"Command failed:\n{result.stderr}",
                'error': result.stderr if not success else None
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out (10 minutes)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error running command: {str(e)}'
            }

    def save_to_history(self, cmd, output):
        """Save command execution to history."""
        try:
            from datetime import datetime

            history_file = PROJECT_ROOT / 'data/analysis_history.json'
            history_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing history
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []

            # Add new entry
            history.append({
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(cmd),
                'output': output[:500]  # First 500 chars
            })

            # Keep only last 50 entries
            history = history[-50:]

            # Save
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving history: {e}")

    def send_json_response(self, data, status=200):
        """Send JSON response."""
        json_data = json.dumps(data).encode('utf-8')

        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(json_data))
        self.end_headers()
        self.wfile.write(json_data)

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the server."""
    print("=" * 60)
    print("📊 Lens Analysis Dashboard Server")
    print("=" * 60)
    print()
    print(f"Server starting at: http://localhost:{PORT}")
    print()
    print("Available endpoints:")
    print("  GET  /                          - Dashboard")
    print("  GET  /api/scrape/<brand>/<limit> - Scrape data")
    print("  GET  /api/merge                 - Merge data")
    print("  GET  /api/price-analysis        - Price analysis")
    print("  GET  /api/comparison            - Lens comparison")
    print("  GET  /api/recommendations       - Recommendations")
    print("  GET  /api/full-analysis         - Full analysis")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()


if __name__ == '__main__':
    main()
