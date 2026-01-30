from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import os

PORT = 9000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web_models')

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

def run(server_class=HTTPServer, handler_class=CORSRequestHandler):
    os.chdir(WEB_DIR)
    with server_class(('', PORT), handler_class) as httpd:
        print(f"Serving models from {WEB_DIR} at http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down server')

if __name__ == '__main__':
    if not os.path.isdir(WEB_DIR):
        os.makedirs(WEB_DIR, exist_ok=True)
    run()
