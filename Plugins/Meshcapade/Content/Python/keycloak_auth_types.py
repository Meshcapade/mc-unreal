from typing import Callable, Literal, Optional, TypedDict

AuthPage = Literal["sign-in", "sign-up"]
AuthCodeCallback = Callable[[Optional[str]], None]
AuthCompletedCallback = Callable[[bool], None]


class Tokens(TypedDict, total=False):
    access_token: str
    expires_in: int
    issued_at: float
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    id_token: str
    session_state: str
    scope: str


class UserInfo(TypedDict, total=False):
    sub: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    picture: str
    email: str
