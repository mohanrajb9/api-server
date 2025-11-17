"""
Start the HTTP server on port 8080 and handle requests
"""

import socketserver
from gists_controller import GistController


def main():
    """Start the HTTP server"""
    PORT = 8080
    with socketserver.TCPServer(("", PORT), GistController) as httpd:
        try:
            print(f"Serving at port {PORT}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server.")
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    main()
