import base64
import hashlib
import secrets
import socket

from logger.base import Logger


def get_free_port(logger: Logger):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
    except Exception as e:
        logger.warning(f"⚠ Failed to get free port dynamically: {e}")
        return 8000


def generate_pkce():
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    )
    code_challenge_digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = (
        base64.urlsafe_b64encode(code_challenge_digest).rstrip(b"=").decode()
    )
    return code_verifier, code_challenge
