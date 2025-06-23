import http.server
import socketserver
import urllib.parse
from pathlib import Path

from logger.base import Logger
from keycloak_auth_types import AuthCodeCallback


class AuthTCPServer(socketserver.TCPServer):
    def __init__(self, port, on_auth_code_received, logger):
        request_handler = make_o_auth_handler(
            logger=logger, on_auth_code_received=on_auth_code_received
        )
        super().__init__(("", port), request_handler)


def make_o_auth_handler(on_auth_code_received, logger: Logger):
    def handler(*args, **kwargs):
        return OAuthHandler(
            *args, logger=logger, on_auth_code_received=on_auth_code_received, **kwargs
        )

    return handler


class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, on_auth_code_received, logger, **kwargs):
        self.logger: Logger = logger
        self.on_auth_code_received: AuthCodeCallback = on_auth_code_received
        super().__init__(*args, **kwargs)

    def do_GET(self):
        query_params = self._parse_query_params()
        session_state = query_params.get("session_state", [None])[0]

        if session_state is None:
            self.send_response(400)
            return

        code = query_params.get("code", [None])[0]
        if code:
            self.on_auth_code_received(code)
            self.respond(
                "auth_success.html",
                "Authentication successful. You can close this window.",
            )
        else:
            self.on_auth_code_received(None)
            self.respond(
                "auth_failure.html",
                "Error: Authorization code not found. Please try again.",
                status=400,
            )

    def _parse_query_params(self):
        query = urllib.parse.urlparse(self.path).query
        return urllib.parse.parse_qs(query)

    def respond(self, filename, fallback_message, status=200):
        self.send_response(status)
        try:
            file_path = (
                Path(__file__).resolve().parent.parent.parent / "static" / filename
            )
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self._send_headers("text/html")
            self.wfile.write(content.encode("utf-8"))
        except Exception as e:
            self.logger.error(f"❌ Failed to serve {filename}: {e}")
            self._send_headers("text/plain")
            self.wfile.write(fallback_message.encode("utf-8"))

    def _send_headers(self, content_type):
        self.send_header("Content-type", content_type)
        self.end_headers()
