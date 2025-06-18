import time
import urllib.parse
from urllib3.util.retry import Retry
import threading
import webbrowser
import requests
from requests.adapters import HTTPAdapter

from typing import Optional
from logger.base import Logger
from o_auth import AuthTCPServer
from utils import get_free_port, generate_pkce
from keycloak_auth_types import AuthPage, AuthCompletedCallback, Tokens, UserInfo

SESSION_RETRIES = 3
SESSION_BACKOFF_FACTOR = 0.3
SESSION_STATUS_FORCELIST = (500, 502, 503, 504)
SESSION_RETRY_METHODS = [
    "HEAD",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]


class AuthenticationCancelledError(Exception):
    pass


class AuthManager:
    def __init__(
        self,
        keycloak_domain,
        realm,
        client_id,
        logger,
        auth_redirect_port=None,
        check_token_interval=10,
        refresh_margin_in_seconds=60,
    ):
        self.keycloak_domain = keycloak_domain
        self.realm = realm
        self.client_id = client_id

        self.auth_redirect_port = auth_redirect_port or get_free_port(logger)
        self.redirect_uri = f"http://localhost:{self.auth_redirect_port}"
        self.base_auth_url = f"{keycloak_domain}/realms/{realm}/protocol/openid-connect"
        self.token_url = f"{self.base_auth_url}/token"

        self.tokens: Optional[Tokens] = None
        self.user_info: Optional[UserInfo] = None
        self.code_verifier = None
        self.code_challenge = None
        self.auth_url = None
        self.refresh_margin = refresh_margin_in_seconds
        self.check_interval = check_token_interval

        self.auth_server: Optional[AuthTCPServer] = None
        self.auth_server_thread: Optional[threading.Thread] = None
        self.auth_succeded = None

        self._stop_event = threading.Event()
        self._refresh_token_thread = self._get_refresh_token_thread()

        self.logger: Logger = logger
        self.session = self._create_session_with_retries()

    def _create_session_with_retries(
        self,
        total_retries=SESSION_RETRIES,
        backoff_factor=SESSION_BACKOFF_FACTOR,
        status_forcelist=SESSION_STATUS_FORCELIST,
        retry_methods=SESSION_RETRY_METHODS,
    ):
        session = requests.Session()
        retries = Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=retry_methods,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_refresh_token_thread(self):
        return threading.Thread(target=self._auto_refresh, daemon=True)

    def start_automatic_refresh(self):
        if not self._refresh_token_thread.is_alive():
            self._stop_event.clear()
            self._refresh_token_thread = self._get_refresh_token_thread()
            self._refresh_token_thread.start()
            self.logger.info("Automatic token refresh thread started")

    def stop_automatic_refresh(self):
        self._stop_event.set()

    def is_token_valid(self):
        return (
            bool(self.tokens)
            and time.time() < self.tokens["issued_at"] + self.tokens["expires_in"]
        )

    def is_logged_in(self):
        try:
            user_info = self.get_user_info()
            return bool(self.user_info)
        except:
            return False

    def get_access_token(self):
        return self.tokens.get("access_token") if self.tokens else None

    def get_refresh_token(self):
        return self.tokens.get("refresh_token") if self.tokens else None

    def get_user_email(self):
        user_info = self.user_info or self.get_user_info()
        return user_info.get("email") if user_info else None

    def get_authentication_url(self):
        return self.auth_url

    def authenticate(self, page: AuthPage = "sign-in"):
        try:
            auth_url = self.auth_url or self._generate_auth_url(page)
            self._run_local_auth_server()
            self._open_auth_web_page(auth_url)
            is_success = self._wait_for_auth_end()
            self._shutdown_authentication_server()

            if is_success is False:
                raise Exception("Authentication not successfull. Try again.")

            return auth_url
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            raise

    def _wait_for_auth_end(self, timeout=120):
        start = time.time()
        while self.auth_succeded is None:
            if time.time() - start > timeout:
                self.logger.error("❌ Timed out waiting for tokens.")
                raise TimeoutError("Timed out waiting for auth code.")
            time.sleep(1)
        if self.auth_succeded:
            self.logger.info("✅ Tokens saved successfully")
            return True
        else:
            self.logger.error("❌ Authentication failed: failed to get the code")
            return False

    def authenticate_async(
        self,
        page: AuthPage = "sign-in",
        on_complete: Optional[AuthCompletedCallback] = None,
    ):
        auth_url = self._generate_auth_url(page)

        def worker():
            success = False
            try:
                self.authenticate(page)
                success = True
            except AuthenticationCancelledError:
                self.logger.info("❌ Authentication cancelled.")
            except TimeoutError:
                self.logger.info("❌ Authentication timed out.")
            except Exception as e:
                self.logger.error(f"❌ Auth thread error: {e}")
            if on_complete:
                on_complete(success)

        threading.Thread(target=worker, daemon=True).start()
        return auth_url

    def sign_in_directly(self, username: str, password: str):
        token_url = (
            f"{self.keycloak_domain}/realms/{self.realm}/protocol/openid-connect/token"
        )
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "username": username,
            "password": password,
        }
        response = self.session.post(token_url, data=data)
        response.raise_for_status()
        self._map_tokens(response.json())

    def sign_in(self):
        self.authenticate("sign-in")

    def sign_in_async(self, on_complete: Optional[AuthCompletedCallback] = None):
        return self.authenticate_async("sign-in", on_complete)

    def sign_up(self):
        self.authenticate("sign-up")

    def sign_up_async(self, on_complete: Optional[AuthCompletedCallback] = None):
        return self.authenticate_async("sign-up", on_complete)

    def sign_out(self):
        if not self.tokens:
            self.logger.info("🔓 No session to sign out from.")
            return

        logout_url = f"{self.base_auth_url}/logout"
        data = {
            "client_id": self.client_id,
            "refresh_token": self.tokens.get("refresh_token"),
        }

        try:
            response = self.session.post(
                logout_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )

            if response.ok:
                self.logger.info("🔒 Signed out successfully.")
            else:
                self.logger.warning(
                    f"⚠ Sign-out failed: {response.status_code} {response.text}"
                )
        except Exception as e:
            self.logger.error(f"❌ Exception during sign-out: {e}")
        finally:
            self.stop_automatic_refresh()
            self._shutdown_authentication_server()
            self._clean_up_authentication_state()

    def cancel_authentication(self):
        self.logger.info("🚫 Authentication flow cancelled.")
        self._shutdown_authentication_server()
        self._clean_up_authentication_state()

    def _clean_up_authentication_state(self):
        self.tokens = None
        self.user_info = None
        self.code_verifier = None
        self.code_challenge = None
        self.auth_url = None
        self.auth_server = None
        self.auth_server_thread = None
        self.auth_succeded = None

    def get_user_info(self) -> UserInfo:
        if not self.is_token_valid():
            raise RuntimeError(
                "🔒 Cannot fetch user info: not authenticated or token expired."
            )

        userinfo_url = f"{self.base_auth_url}/userinfo"

        try:
            response = self.authorized_request("GET", userinfo_url)
            response.raise_for_status()
            self.user_info = response.json()
            self.logger.debug(self.user_info)
            return self.user_info
        except requests.RequestException as e:
            self.logger.debug(f"❌ Failed to get user info: {e}")
            raise

    def _run_local_auth_server(self):
        try:
            self.auth_server = AuthTCPServer(
                port=self.auth_redirect_port,
                on_auth_code_received=self.on_auth_code_received,
                logger=self.logger,
            )
            self.auth_server_thread = threading.Thread(
                target=self.auth_server.serve_forever, daemon=True
            )
            self.logger.info(
                f"Listening on http://localhost:{self.auth_redirect_port} for the authentication redirect..."
            )
            self.auth_server_thread.start()
        except Exception as e:
            self.logger.error(f"❌ Failed running local auth server: {e}")
            self.cancel_authentication()
            raise

    def on_auth_code_received(self, auth_code):
        try:
            if auth_code is None:
                self.auth_succeded = False
            else:
                self._exchange_code_for_token(auth_code)
                self.auth_succeded = True
        except Exception as e:
            self.logger.error(f"❌ Failed to excenge auth code: {e}")
            self.auth_succeded = False

    def _shutdown_authentication_server(self):
        if self.auth_server:
            self.auth_server.shutdown()
            self.auth_server.server_close()
        if self.auth_server_thread and self.auth_server_thread.is_alive():
            self.auth_server_thread.join(timeout=2)

    def _generate_auth_url(self, page: AuthPage = "sign-in"):
        self.code_verifier, self.code_challenge = generate_pkce()
        url_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid",
            "redirect_uri": self.redirect_uri,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
        action = "registrations" if page == "sign-up" else "auth"
        base_url = self.base_auth_url.rstrip("/")
        self.auth_url = f"{base_url}/{action}?{urllib.parse.urlencode(url_params)}"

        return self.auth_url

    def _open_auth_web_page(self, auth_url):
        try:
            webbrowser.open(auth_url)
            self.logger.info(f"🌍 Authentication URL opened in browser: {auth_url}")
        except Exception as e:
            self.logger.error(f"❌ Failed to open browser: {e}")
            raise

    def _exchange_code_for_token(self, auth_code):
        try:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
                "code_verifier": self.code_verifier,
            }
            response = self.session.post(self.token_url, data=data)
            response.raise_for_status()
            self._map_tokens(response.json())
        except Exception as e:
            self.logger.error(f"❌ Token exchange failed: {e}")
            raise

    def _refresh_tokens(self):
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.get_refresh_token(),
        }
        response = self.session.post(self.token_url, data=data)
        response.raise_for_status()
        self._map_tokens(response.json())

    def _map_tokens(self, tokens):
        tokens["issued_at"] = time.time()
        self.tokens = tokens

    def _auto_refresh(self):
        while not self._stop_event.is_set():
            if not self.tokens:
                time.sleep(2)
                continue

            now = time.time()
            expiry = (
                self.tokens["issued_at"]
                + self.tokens["expires_in"]
                - self.refresh_margin
            )

            if now >= expiry:
                try:
                    self._refresh_tokens()
                    self.logger.info("🔁 Tokens refreshed successfully.")
                except Exception as e:
                    self.logger.error(
                        f"❌ Auto-refresh failed, please sign-in again: {e}"
                    )
                    self.sign_out()

            time.sleep(self.check_interval)

    def authorized_request(self, method, url, retry_when_invalid=True, **kwargs):
        token = self.get_access_token()
        if not token:
            raise Exception("Missing access token")

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        response = self.session.request(method, url, headers=headers, **kwargs)

        # If token is invalid or expired, try refreshing once and retry the request
        if response.status_code == 401 and retry_when_invalid:
            self.logger.warning("⚠ Token expired or invalid, retrying once.")
            try:
                self._refresh_tokens()
                self.logger.debug("🔁 Tokens refreshed successfully.")
                return self.authorized_request(
                    method, url, retry_when_invalid=False, **kwargs
                )
            except Exception as e:
                self.logger.error(
                    f"❌ Auto-refresh additional fallback failed too, please sign-in again: {e}"
                )
                self.sign_out()

        return response
