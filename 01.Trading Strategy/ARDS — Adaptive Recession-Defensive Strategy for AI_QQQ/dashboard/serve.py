# -*- coding: utf-8 -*-
"""
ARDS-X 대시보드용 초경량 정적 서버.
    python3 serve.py [port]      (기본 3142)
자기 자신이 있는 폴더를 루트로 서빙하므로 실행 위치와 무관하다.
"""
import http.server
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3142
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"ARDS-X dashboard → http://localhost:{PORT}  (root: {ROOT})")
    httpd.serve_forever()
