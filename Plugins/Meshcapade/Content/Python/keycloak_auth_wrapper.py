from authentication import AuthManager
from keycloak_auth_types import AuthPage
from logger.mcme_logger import logger as mcme_logger

from typing import Optional
import unreal

# Auth config
from mc_plugin_config import KEYCLOAK_DOMAIN, REALM, CLIENT_ID


@unreal.uclass()
class AuthBridge(unreal.BlueprintFunctionLibrary):
    auth_manager = None

    _auth_done = False
    _auth_success = False

    @unreal.ufunction(static=True, ret=bool)
    def is_auth_done() -> bool:
        return AuthBridge._auth_done

    @unreal.ufunction(static=True, ret=bool)
    def was_auth_successful() -> bool:
        return AuthBridge._auth_success

    @unreal.ufunction(static=True, ret=str, params=[str])
    def authenticate(page: AuthPage = "sign-in") -> str:
        try:
            if AuthBridge.auth_manager is not None:
                AuthBridge.destroy_auth_manager()

            AuthBridge.auth_manager = AuthManager(
                keycloak_domain=KEYCLOAK_DOMAIN,
                realm=REALM,
                client_id=CLIENT_ID,
                logger=mcme_logger,
            )

            auth_url = AuthBridge.auth_manager.authenticate_async(
                page, on_complete=AuthBridge._on_auth_complete
            )
            return auth_url or ""
        except Exception as e:
            unreal.log_error(f"❌ Error in authenticate: {e}")
            AuthBridge.auth_manager.cancel_authentication()
            return ""

    @staticmethod
    def _on_auth_complete(success: bool) -> None:
        if success:
            unreal.log("✅ Authentication successful")
        else:
            unreal.log("✅ Authentication failed")
            AuthBridge._auth_done = True
            return

        try:
            AuthBridge.auth_manager.start_automatic_refresh()
            AuthBridge._auth_success = True
        except Exception as e:
            unreal.log_error(f"❌ Error in _on_auth_complete: {e}")
            AuthBridge.auth_manager.cancel_authentication()
        finally:
            AuthBridge._auth_done = True

    @staticmethod
    def _clean_up() -> None:
        AuthBridge._auth_done = False
        AuthBridge._auth_success = False

    @unreal.ufunction(static=True)
    def destroy_auth_manager() -> None:
        if AuthBridge.auth_manager is not None:
            AuthBridge.cancel_authentication()
            AuthBridge.auth_manager = None

    @staticmethod
    def authorized_request(**kwargs):
        if AuthBridge.auth_manager:
            response = AuthBridge.auth_manager.authorized_request(**kwargs)

            if response.status_code == 401:
                AuthBridge._clean_up()

            return response

        unreal.log_warning("AuthManager not initialized yet.")
        return None

    @unreal.ufunction(static=True, ret=str)
    def sign_in() -> str:
        return AuthBridge.authenticate("sign-in")

    @unreal.ufunction(static=True, ret=str)
    def sign_up() -> str:
        return AuthBridge.authenticate("sign-up")

    @unreal.ufunction(static=True)
    def sign_out() -> None:
        if AuthBridge.auth_manager:
            AuthBridge.auth_manager.sign_out()
            AuthBridge._clean_up()
        else:
            unreal.log_warning("AuthManager not initialized yet.")

    @unreal.ufunction(static=True, ret=bool)
    def is_logged_in() -> bool:
        if AuthBridge.auth_manager:
            return AuthBridge.auth_manager.is_logged_in()
        else:
            return False

    @unreal.ufunction(static=True, ret=str)
    def get_token() -> str:
        if AuthBridge.auth_manager:
            return AuthBridge.auth_manager.get_access_token()
        unreal.log_warning("AuthManager not initialized yet.")
        return ""

    @unreal.ufunction(static=True)
    def stop_automatic_token_refresh() -> None:
        if AuthBridge.auth_manager:
            AuthBridge.auth_manager.stop_automatic_refresh()
            unreal.log("Automatic token refresh stopped.")
        else:
            unreal.log_warning("AuthManager not initialized yet.")

    @unreal.ufunction(static=True)
    def cancel_authentication() -> None:
        if AuthBridge.auth_manager:
            AuthBridge.auth_manager.cancel_authentication()
            AuthBridge._clean_up()
        else:
            unreal.log_warning("AuthManager not initialized yet.")

    @unreal.ufunction(static=True, ret=str)
    def get_user_email() -> str:
        if AuthBridge.auth_manager:
            email = AuthBridge.auth_manager.get_user_email()
            return email or ""
        unreal.log_warning("AuthManager not initialized yet.")
        return ""

    @unreal.ufunction(static=True, ret=str)
    def get_authentication_url() -> Optional[str]:
        if AuthBridge.auth_manager:
            auth_url = AuthBridge.auth_manager.get_authentication_url()
            return auth_url or ""
        unreal.log_warning("AuthManager not initialized yet.")
        return ""
