#!/usr/bin/env python3
"""
Plex Info Web Server
Minimal HTTP server using only Python standard library
"""

import http.server
import socketserver
import json
import subprocess
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PORT = 9924


class PlexInfoHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for Plex Info web interface"""

    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            # Serve the index.html file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            # Read and serve index.html
            index_path = Path(__file__).parent / 'index.html'
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            else:
                error_msg = '<h1>Error: index.html not found</h1><p>Make sure index.html is in the same directory as server.py</p>'
                self.wfile.write(error_msg.encode())

        elif self.path == '/api/libraries':
            # Get list of available libraries
            try:
                result = subprocess.run(
                    ['python', 'plex_info.py'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Parse library names from output
                libraries = []
                lines = result.stdout.split('\n')
                capture = False

                for line in lines:
                    if 'AVAILABLE PLEX LIBRARIES' in line:
                        capture = True
                        continue
                    if capture:
                        if line.startswith('='):
                            continue
                        if 'To analyze' in line or 'Examples:' in line:
                            break
                        if line.strip() and 'Type:' in line:
                            # Extract library name (line before "Type:")
                            continue
                        if line.strip() and not line.startswith(' '):
                            libraries.append(line.strip())

                response = {
                    'success': True,
                    'libraries': libraries
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        """Handle POST requests for running plex_info commands"""
        if self.path == '/api/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))

                # Build command
                cmd = ['python', 'plex_info.py']

                # Add library if specified
                if data.get('library'):
                    cmd.extend(['--library', data['library']])

                # Add flags
                if data.get('list_missing'):
                    cmd.append('--list-missing')
                if data.get('quality'):
                    cmd.append('--quality')
                if data.get('stats'):
                    cmd.append('--stats')
                if data.get('health'):
                    cmd.append('--health')
                if data.get('system'):
                    cmd.append('--system')
                if data.get('verbose'):
                    cmd.append('--verbose')
                if data.get('type'):
                    cmd.extend(['--type', data['type']])

                print(f"Running command: {' '.join(cmd)}")

                # Run command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                # Send response
                response = {
                    'success': result.returncode == 0,
                    'output': result.stdout if result.returncode == 0 else result.stderr,
                    'command': ' '.join(cmd)
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())

            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': 'Invalid JSON'}
                self.wfile.write(json.dumps(response).encode())

            except subprocess.TimeoutExpired:
                self.send_response(408)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': 'Command timeout (5 minutes)'}
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, 'Not Found')


def main():
    """Start the web server"""
    handler = PlexInfoHandler

    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print("=" * 60)
            print("Plex Info Web App")
            print("=" * 60)
            print(f"\nWeb app running at: http://localhost:{PORT}")
            print(f"\nOpen your browser and navigate to:")
            print(f"  http://localhost:{PORT}")
            print(f"\nPress Ctrl+C to stop the server")
            print("=" * 60)

            # Start server (no auto-open browser)
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\nShutting down web app...")
        print("Goodbye!")
    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Address already in use
            print(f"\nError: Port {PORT} is already in use.")
            print("Either close the other application or change PORT in server.py")
        else:
            print(f"\nError: {e}")


if __name__ == '__main__':
    main()