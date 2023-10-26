try:
    import pytest
    import requests
except ImportError:
    raise AssertionError(
        "virga[testing] extra must be installed to use the pytest plugin"
    )

try:
    from jose import jwt
except ImportError:
    jwt = None  # type: ignore

from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from typing import Dict, Tuple, Union

from virga.plugins.noct import NOCT_URL, VALID_DOMAIN
from virga.plugins.noct.handler import _NOCT_JWT_ALGORITHM, _NOCT_JWT_SECRET
from virga.plugins.secure_cookies import write_secure_cookie


@pytest.fixture(scope="session")
def mock_user() -> Dict[str, Union[str, int]]:
    """Returns a the credentials and unique id of a registered Noct user."""
    password = "P@ssw0rd!"
    name = "Mock User"
    email = "mockuser@indicodata.ai"

    requests.post(
        f"{NOCT_URL}/users/register",
        data={"name": name, "email": email, "password": password, "accept_terms": "y"},
        headers={"Host": f"virga.{VALID_DOMAIN}"},
        allow_redirects=True,
    )

    return {"password": password, "name": name, "email": email, "id": 1}


@pytest.fixture(scope="session")
def mock_tokens(mock_user: Dict[str, Union[str, int]]) -> Tuple[str, str, str, str]:
    """
    Returns the valid authentication and refresh tokens for a Mock User. The first two
    tokens are encrypted and can be used for making authenticated calls, while the
    latter are equivalent decrypted versions.
    """
    res = requests.post(
        f"{NOCT_URL}/users/authenticate",
        data={"email": mock_user["email"], "password": mock_user["password"]},
        headers={"Host": f"virga.{VALID_DOMAIN}"},
    )

    try:
        from_cookie = (res.cookies["auth_token"], res.cookies["refresh_token"])
    except KeyError:
        # for some reason requests sometimes fails to populate the cookie jar. it looks
        # like it has to do with if either the domain is missing or known to be local
        # https://github.com/psf/requests/issues/6344
        # if the above failed, its likely to do this, but we can pull the cookie
        # out of the header instead
        jar: SimpleCookie[str] = SimpleCookie(res.headers["Set-Cookie"])
        from_cookie = (jar["auth_token"].value, jar["refresh_token"].value)

    # the first two are the encrypted versions returned by Noct
    # the latter are the decrypted versions of the same tokens
    return (
        *from_cookie,
        res.json()["auth_token"],
        res.json()["refresh_token"],
    )


@pytest.fixture(scope="session")
def expired_token(mock_user: Dict[str, Union[str, int]]) -> str:
    """
    Returns an encrypted but expired (by 1 minute) authentication token for a Mock User.
    """
    assert jwt is not None, "virga[auth] extra must be installed to use this mock"

    expired_token = write_secure_cookie(
        "auth_token",
        jwt.encode(
            {
                "rt_id": 0,
                "user_id": mock_user["id"],
                "user_name": mock_user["name"],
                "user_email": mock_user["email"],
                "aud": ["indico:base", "indico:app_access"],
                "exp": datetime.utcnow() - timedelta(minutes=1),
            },
            _NOCT_JWT_SECRET,
            algorithm=_NOCT_JWT_ALGORITHM,
        ),
    )

    return expired_token
