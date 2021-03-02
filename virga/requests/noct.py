import os
import secrets
import requests
from jose import JWTError, jwt
from typing import Optional
from fastapi import Response, Cookie, Header

from virga.errors import LoginRequiredException, ExpiredTokenException
from .secure_cookies import read_secure_cookie, write_secure_cookie
from virga.types import User


_NOCT_SERVICE_LOCATION = os.getenv("NOCT_HOST", "http://noct:5000")
_NOCT_JWT_ALGORITHM = os.getenv("NOCT_TOKEN_ALGORITHM", "HS256")
_NOCT_JWT_SECRET = os.getenv("ATMOSPHERE_TOKEN_SECRET", "atmospheretokensecret")
_NOCT_COOKIE_DOMAIN = os.getenv("ATMOSPHERE_AUTH_COOKIE_DOMAIN", ".indico.domains")


def _refresh_token(refresh_token):
    refresh_token = read_secure_cookie("refresh_token", refresh_token)

    req = requests.post(
        f"{_NOCT_SERVICE_LOCATION}/users/refresh_token",
        headers={
            "Authorization": f"Bearer {refresh_token}",
            "Host": f"virga{_NOCT_COOKIE_DOMAIN}",
        },
    )

    if req.status_code == 401:
        raise LoginRequiredException()

    return req.json()["auth_token"], req.json()["cookie_domain"]


def _get_token_data(token):
    scopes = set([f"indico:{s}" for s in (["base"])])
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


def _get_current_user(token=None, cookie=None):
    token = token or read_secure_cookie("auth_token", cookie)

    if not token:
        raise LoginRequiredException()

    token_data = _get_token_data(token=token)
    user_id = token_data.get("user_id")

    if user_id:
        return User.parse_obj(token_data)


def get_current_user(
    response: Response,
    auth_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
) -> User:
    """
    Handle and process a Noct session JWT stored in an atmosphere secure cookie.
    Expired tokens are requested for refresh
    """
    if not auth_token and not refresh_token:
        raise LoginRequiredException()

    try:
        # ensure we have valid credentials
        return _get_current_user(cookie=auth_token)
    except ExpiredTokenException:
        # fetch a new tocken from Noct
        new_token, domain = _refresh_token(refresh_token)

        response.set_cookie(
            "auth_token",
            write_secure_cookie("auth_token", new_token),
            domain=domain,
            httponly=True,
            secure=True,
        )

        return _get_current_user(token=new_token)
