import hmac
import uuid

import pytest

from virga.plugins.secure_cookies import read_secure_cookie, write_secure_cookie


@pytest.mark.integration
def test_tornado_tokens(mock_tokens):
    (auth_e, refresh_e, auth, refresh) = mock_tokens
    decoded = read_secure_cookie("auth_token", auth_e)
    assert decoded == auth

    decoded = read_secure_cookie("refresh_token", refresh_e)
    assert decoded == refresh


def test_coding_identity():
    rng = str(uuid.uuid4())
    encoded = write_secure_cookie("random-test-cookie", rng)
    decoded = read_secure_cookie("random-test-cookie", encoded)
    assert isinstance(encoded, str)
    assert isinstance(decoded, str)
    assert rng == decoded


def test_decoding_invalid():
    decoded = read_secure_cookie("random-test-cookie", str(uuid.uuid4()))
    assert decoded is None


def test_decoding_wrongname():
    encoded = write_secure_cookie("random-test-cookie", str(uuid.uuid4()))
    decoded = read_secure_cookie("wrong-cookie-name", encoded)
    assert decoded is None


def test_decoding_tampered(monkeypatch):
    def comp_digest(sig1, sig2):
        if not hmac.compare_digest(sig1, sig2):
            raise Exception("MOCK")

    monkeypatch.setattr(
        "virga.plugins.secure_cookies.secure_cookies.hmac.compare_digest", comp_digest
    )
    encoded = write_secure_cookie("random-test-cookie", str(uuid.uuid4()))

    with pytest.raises(Exception):
        read_secure_cookie("random-test-cookie", encoded[:-1])


def test_decoding_expired():
    encoded = write_secure_cookie("random-test-cookie", str(uuid.uuid4()))
    decoded = read_secure_cookie("random-test-cookie", encoded)
    assert decoded

    decoded = read_secure_cookie("random-test-cookie", encoded, max_age_days=0)
    assert decoded is None


def test_decoding_invalid_b64value():
    encoded = write_secure_cookie("random-test-cookie", str(uuid.uuid4()))
    decoded = read_secure_cookie("random-test-cookie", encoded)
    assert decoded

    decoded = read_secure_cookie(
        "random-test-cookie", encoded[:47] + "===" + encoded[47:]
    )
    assert decoded is None
