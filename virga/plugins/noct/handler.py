import os
from typing import Dict, Optional, Tuple, Union

import orjson
from fastapi import Cookie, Request, Response, status

from virga.plugins.secure_cookies import read_secure_cookie, write_secure_cookie

from .errors import ExpiredTokenException, LoginRequiredException
from .user import User

try:
    import aiohttp
    from jose import jwt
except ImportError:
    aiohttp = None  # type: ignore
    jwt = None  # type: ignore

_NOCT_SERVICE_LOCATION = os.getenv("NOCT_HOST", "http://noct:5000")
_NOCT_JWT_ALGORITHM = os.getenv("NOCT_TOKEN_ALGORITHM", "HS256")
_NOCT_JWT_SECRET = os.getenv("ATMOSPHERE_TOKEN_SECRET", "atmospheretokensecret")
_NOCT_COOKIE_DOMAIN = os.getenv(
    "ATMOSPHERE_AUTH_COOKIE_DOMAIN", ".indico.domains"
).split(",")[0]
if _NOCT_COOKIE_DOMAIN.startswith("."):
    _NOCT_COOKIE_DOMAIN = _NOCT_COOKIE_DOMAIN[1:]


async def _refresh_token(request: Request, refresh_token: Optional[str]):
    if not refresh_token:
        raise LoginRequiredException()

    refresh_token = read_secure_cookie("refresh_token", refresh_token)

    # if we need to fetch a refresh token, do so with an aiohttp client.
    # since we want to share the client across multiple requests, add it to the
    # application state instead of the route state.
    if not hasattr(request.app.state, "_aiohttpclient"):
        # make a new client, defining our default Host header
        _aiohttpclient = aiohttp.ClientSession(
            headers={"Host": f"virga.{_NOCT_COOKIE_DOMAIN}"},
        )

        # clients require graceful cleanup, so define a shutdown handler
        # to add to our fastapi app that will run before app termination
        async def _close():
            await _aiohttpclient.close()

        # store the async client in the app state, and add the event handler
        request.app.state._aiohttpclient = _aiohttpclient
        request.app.add_event_handler("shutdown", _close)

    # make an async POST request for a new refresh token
    async with request.app.state._aiohttpclient.post(
        f"{_NOCT_SERVICE_LOCATION}/users/refresh_token",
        headers={"Authorization": f"Bearer {refresh_token}"},
    ) as resp:
        if resp.status == status.HTTP_401_UNAUTHORIZED:
            raise LoginRequiredException()

        # decode the payload and return the new token with its domain
        payload = await resp.json(loads=orjson.loads)
        return payload["auth_token"], payload["cookie_domain"]


def _get_token_data(token: Optional[str]):
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
    except jwt.JWTError:
        raise LoginRequiredException()


def _parse_current_user(
    token: Optional[str] = None, cookie: Optional[str] = None
) -> User:
    try:
        token = token or read_secure_cookie("auth_token", str(cookie))
    except Exception:
        raise LoginRequiredException()

    token_data = _get_token_data(token=token)
    user_id = token_data.get("user_id")
    if not user_id:
        raise LoginRequiredException()

    return User(**token_data)


async def read_user(
    request: Request,
    auth_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Tuple[User, str, Optional[Dict[str, Union[str, bool]]]]:
    """
    Handle and process a Noct session JWT stored in an atmosphere secure cookie.
    If the token is expired, the passed refresh token will be used to fetch a new one.
    Returns a User, and if one was regenerated, a new secure token and its cookie. If
    a new token cookie is present, the method caller is responsible for writing it back
    to a Response to ensure the client gets updated.

    If you're using FastAPI with a normal route, it is highly recommended to use the
    `get_current_user` method instead, as is intended to be a FastAPI dependency.
    """
    # complain if the auth extra isn't installed
    assert jwt is not None, "virga[auth] extra must be installed to use the Noct plugin"
    assert (
        aiohttp is not None
    ), "virga[auth] extra must be installed to use the Noct plugin"

    if not auth_token and not refresh_token:
        raise LoginRequiredException()

    try:
        # ensure we have valid credentials
        return _parse_current_user(cookie=auth_token), str(auth_token), None
    except ExpiredTokenException:
        # fetch a new token from Noct
        new_token, domain = await _refresh_token(request, refresh_token)
        user = _parse_current_user(token=new_token)

        # return the user alongside the token and new cookie
        new_token = write_secure_cookie("auth_token", new_token)
        return (
            user,
            new_token,
            {
                "key": "auth_token",
                "value": new_token,
                "domain": domain,
                "httponly": True,
                "secure": True,
            },
        )


async def get_current_user(
    request: Request,
    response: Response,
    auth_token: Optional[str] = Cookie(None),
    refresh_token: Optional[str] = Cookie(None),
) -> User:
    """
    Handle and process a Noct session JWT stored in the current request's cookies.
    Expired tokens are requested for refresh if a refresh token exists. This is a
    FastAPI dependency.
    """
    user, _, cookie = await read_user(
        request, auth_token=auth_token, refresh_token=refresh_token
    )
    if cookie:
        response.set_cookie(**cookie)  # type: ignore

    return user
