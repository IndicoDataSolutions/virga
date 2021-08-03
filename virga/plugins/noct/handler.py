import os
from typing import Optional, Tuple

import requests
from fastapi import Cookie, Response
from jose import JWTError, jwt
from virga.plugins.secure_cookies import read_secure_cookie, write_secure_cookie

from .errors import ExpiredTokenException, LoginRequiredException
from .user import User

_NOCT_SERVICE_LOCATION = os.getenv("NOCT_HOST", "http://noct:5000")
_NOCT_JWT_ALGORITHM = os.getenv("NOCT_TOKEN_ALGORITHM", "HS256")
_NOCT_JWT_SECRET = os.getenv("ATMOSPHERE_TOKEN_SECRET", "atmospheretokensecret")
_NOCT_COOKIE_DOMAIN = os.getenv(
    "ATMOSPHERE_AUTH_COOKIE_DOMAIN", ".indico.domains"
).split(",")[0]
if _NOCT_COOKIE_DOMAIN.startswith("."):
    _NOCT_COOKIE_DOMAIN = _NOCT_COOKIE_DOMAIN[1:]


def _refresh_token(refresh_token):
    refresh_token = read_secure_cookie("refresh_token", refresh_token)

    req = requests.post(
        f"{_NOCT_SERVICE_LOCATION}/users/refresh_token",
        headers={
            "Authorization": f"Bearer {refresh_token}",
            "Host": f"virga.{_NOCT_COOKIE_DOMAIN}",
        },
    )

    if req.status_code == 401:
        raise LoginRequiredException()

    return req.json()["auth_token"], req.json()["cookie_domain"]


def _get_token_data(token):
    scopes = set([f"indico:{s}" for s in (["base", "app_access"])])
    try:
        payload = jwt.decode(
            token,
            _NOCT_JWT_SECRET,
            algorithms=[_NOCT_JWT_ALGORITHM],
            audience=next(iter(scopes)),
        )

        if not scopes.issubset(set(payload["aud"])):
            raise LoginRequiredException()

        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException()
    except JWTError:
        raise LoginRequiredException()


def _parse_current_user(token=None, cookie=None):
    token = token or read_secure_cookie("auth_token", cookie)

    if not token:
        raise LoginRequiredException()

    token_data = _get_token_data(token=token)
    user_id = token_data.get("user_id")

    if user_id:
        return User(**token_data)


def read_user(
    auth_token: Optional[str] = None, refresh_token: Optional[str] = None
) -> Tuple[User, str]:
    """
    Handle and process a Noct session JWT stored in an atmosphere secure cookie.
    If the token is expired, the passed refresh token will be used to fetch a new one.
    Returns a User, and if one was regenerated, a new secure token cookie with
    attributes. If a new token cookie is present, the method caller is responsible for
    writing it back to a Response to ensure the client gets updated.

    If you're using FastAPI with a normal route, it is highly recommended to use the
    `get_current_user` method instead, as is intended to be a FastAPI dependency.
    """
    if not auth_token and not refresh_token:
        raise LoginRequiredException()

    try:
        # ensure we have valid credentials
        return _parse_current_user(cookie=auth_token), None
    except ExpiredTokenException:
        # fetch a new tocken from Noct
        new_token, domain = _refresh_token(refresh_token)
        user = _parse_current_user(token=new_token)

        # return the user alonside the new cookie
        return user, {
            "key": "auth_token",
            "value": write_secure_cookie("auth_token", new_token),
            "domain": domain,
            "httponly": True,
            "secure": True,
        }


def get_current_user(
    response: Response,
    auth_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
) -> User:
    """
    Handle and process a Noct session JWT stored in the current request's cookies.
    Expired tokens are requested for refresh if a refresh token exists. This is a
    FastAPI dependency.
    """
    user, cookie = read_user(auth_token=auth_token, refresh_token=refresh_token)
    if cookie:
        response.set_cookie(**cookie)

    return user
