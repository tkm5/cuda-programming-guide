"""Simple HTTP server to receive transcript data from browser."""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'transcripts')
os.makedirs(SAVE_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        saved = 0
        for lecture_id, text in data.items():
            filepath = os.path.join(SAVE_DIR, f'{lecture_id}.txt')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            saved += 1
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'saved': saved})
        self.wfile.write(response.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 18765), Handler)
    print(f'Server listening on http://127.0.0.1:18765')
    print(f'Saving to: {SAVE_DIR}')
    server.serve_forever()
