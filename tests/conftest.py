import pytest
import requests
import random, string
import uuid

from virga.requests.noct import _NOCT_SERVICE_LOCATION, _NOCT_COOKIE_DOMAIN


def _rng_password():
    uppercase = random.choices(string.ascii_uppercase, k=4)
    lowercase = random.choices(string.ascii_lowercase, k=4)
    digit = random.choices(string.digits, k=4)
    punc = random.choices(string.punctuation, k=4)

    x = "".join([*uppercase, *lowercase, *digit, *punc])
    return "".join(random.sample(x, len(x)))


@pytest.fixture(scope="session")
def mock_user():
    id = str(uuid.uuid4()).replace("-", "")
    password = _rng_password()
    req = requests.post(
        f"{_NOCT_SERVICE_LOCATION}/users/register",
        data={
            "name": "Mock User",
            "email": f"mockuser{id}@indico.io",
            "password": password,
            "accept_terms": "y",
        },
        headers={"Host": f"virga.{_NOCT_COOKIE_DOMAIN}"},
    )

    return {"password": password, **req.json()["user"]}


@pytest.fixture(scope="session")
def mock_tokens(mock_user):
    req = requests.post(
        f"{_NOCT_SERVICE_LOCATION}/users/authenticate",
        data={"email": mock_user["email"], "password": mock_user["password"]},
        headers={"Host": f"virga.{_NOCT_COOKIE_DOMAIN}"},
    )

    return (
        req.cookies["auth_token"],
        req.cookies["refresh_token"],
        req.json()["auth_token"],
        req.json()["refresh_token"],
    )
