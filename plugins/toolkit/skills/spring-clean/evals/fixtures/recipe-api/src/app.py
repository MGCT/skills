"""recipe-api entry point. Sets up routes and starts the server."""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from handlers import handle_list, handle_get, handle_create
from db import init_db


class Router(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/recipes":
            handle_list(self)
        else:
            handle_get(self)

    def do_POST(self):
        handle_create(self)


def main():
    init_db()
    port = int(os.environ.get("PORT", "5000"))
    server = HTTPServer(("", port), Router)
    print(f"recipe-api listening on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
