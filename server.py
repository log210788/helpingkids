import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ResilientHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # If it is save_annotations or any API endpoint, respond gracefully
            if '/api/save_annotations' in self.path or 'annotations' in self.path:
                try:
                    data = json.loads(body.decode('utf-8'))
                    with open(os.path.join(DIRECTORY, 'annotations.json'), 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

            response = json.dumps({"status": "ok", "path": self.path}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status": "recovered"}')
            except Exception:
                pass

    def log_message(self, format, *args):
        # Clean logging
        print(f"[{self.log_date_time_string()}] {format % args}", flush=True)

if __name__ == '__main__':
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, ResilientHandler)
    print(f"Server actively serving {DIRECTORY} on http://127.0.0.1:{PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...", flush=True)
        httpd.server_close()
