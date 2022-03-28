from datetime import datetime, timedelta

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from virga.plugins.noct import User
from virga.plugins.noct.handler import (
    _NOCT_JWT_ALGORITHM,
    _NOCT_JWT_SECRET,
    get_current_user,
)
from virga.plugins.secure_cookies import write_secure_cookie


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


app = FastAPI()
client = TestClient(app)


@app.get("/")
async def get_user(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.name}"}


###
###


def test_get_user_auth(mock_user, mock_tokens):
    auth_token, _, _, _ = mock_tokens
    response = client.get("/", cookies={"auth_token": auth_token})
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello, {mock_user['name']}"}


def test_get_user_expired_token(expired_token):
    response = client.get("/", cookies={"auth_token": expired_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Login is required to access this route"}


def test_get_user_refresh(expired_token, mock_user, mock_tokens):
    _, refresh_token, _, _ = mock_tokens

    # expired token, valid refresh
    response = client.get(
        "/", cookies={"auth_token": expired_token, "refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello, {mock_user['name']}"}
