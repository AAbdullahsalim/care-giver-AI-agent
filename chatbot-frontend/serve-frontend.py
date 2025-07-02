#!/usr/bin/env python3
"""
Simple web server to serve the frontend files
This avoids CORS issues when connecting to the backend
"""
import http.server
import socketserver
import os
import webbrowser
from threading import Timer

PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

def open_browser():
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    print(f"🌐 Starting frontend server on http://localhost:{PORT}")
    print("📁 Serving files from current directory")
    print("🔗 Frontend will connect to backend at http://localhost:8000")
    print("🚀 Opening browser in 2 seconds...")
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Frontend server stopped")
            httpd.shutdown() 