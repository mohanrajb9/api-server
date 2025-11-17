"""
It uses the web_api_helper module to retrieve gists and
formats it to json response.
"""

from http.server import BaseHTTPRequestHandler
import json
from web_api_helper import GetPublicGistsService


class GistController(BaseHTTPRequestHandler):
    """
    Controller to handle HTTP requests for gists
    """
    def do_GET(self):
        """Handle GET requests"""
        gist_obj = GetPublicGistsService(self.path)
        status_code, response = gist_obj.handle_request()
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if response:
            self.wfile.write(json.dumps(response).encode())
