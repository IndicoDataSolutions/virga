import random
import string
import uuid

import pytest
import requests
from virga.plugins.noct import NOCT_URL, VALID_DOMAIN


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
    name = "Mock User"
    email = f"mockuser{id}@indicodata.ai"

    requests.post(
        f"{NOCT_URL}/users/register",
        data={"name": name, "email": email, "password": password, "accept_terms": "y"},
        headers={"Host": f"virga.{VALID_DOMAIN}"},
        allow_redirects=True,
    )

    return {"password": password, "name": name, "email": email, "id": 1}


@pytest.fixture(scope="session")
def mock_tokens(mock_user):
    req = requests.post(
        f"{NOCT_URL}/users/authenticate",
        data={"email": mock_user["email"], "password": mock_user["password"]},
        headers={"Host": f"virga.{VALID_DOMAIN}"},
    )

    return (
        req.cookies["auth_token"],
        req.cookies["refresh_token"],
        req.json()["auth_token"],
        req.json()["refresh_token"],
    )
