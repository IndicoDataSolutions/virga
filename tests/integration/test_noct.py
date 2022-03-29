from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from virga.plugins.noct import User
from virga.plugins.noct.handler import get_current_user

app = FastAPI()
client = TestClient(app)


@app.get("/")
async def get_user(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.name}"}


###
###


def test_noauth():
    response = client.get("/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Login is required to access this route"}


def test_valid_auth(mock_user, mock_tokens):
    auth_token, _, _, _ = mock_tokens
    response = client.get("/", cookies={"auth_token": auth_token})
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello, {mock_user['name']}"}


def test_expired_token(expired_token):
    response = client.get("/", cookies={"auth_token": expired_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Login is required to access this route"}


def test_refresh(expired_token, mock_user, mock_tokens):
    _, refresh_token, _, _ = mock_tokens

    # expired token, valid refresh
    response = client.get(
        "/", cookies={"auth_token": expired_token, "refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello, {mock_user['name']}"}
