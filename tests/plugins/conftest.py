import asyncio
import os
import random
import string
import uuid
from datetime import datetime, timedelta

import pytest
import requests
from jose import jwt
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from virga.plugins.database import make_async_engine
from virga.plugins.noct import NOCT_URL, VALID_DOMAIN
from virga.plugins.noct.handler import _NOCT_JWT_ALGORITHM, _NOCT_JWT_SECRET
from virga.plugins.secure_cookies import write_secure_cookie

user = os.getenv("POSTGRES_USER")
passwd = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
DB_URL = f"postgresql+asyncpg://{user}:{passwd}@{os.getenv('POSTGRES_HOST')}:5432/{db}"
Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = make_async_engine(DB_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.create)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Widget.__table__.drop)


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


@pytest.fixture(scope="session")
def expired_token(mock_user):
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
