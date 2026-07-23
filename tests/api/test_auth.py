import pytest
from api_clients.auth_client import AuthApiClient

BASE_URL = "http://localhost:3004/auth"


def test_login_returns_valid_token():
    client = AuthApiClient(BASE_URL)
    token = client.login("admin", "password")

    assert isinstance(token, str)
    assert len(token) > 0


def test_login_with_invalid_credentials_raises():
    client = AuthApiClient(BASE_URL)
    with pytest.raises(ValueError):
        client.login("admin", "wrong_password")


def test_logout_invalidates_token():
    client = AuthApiClient(BASE_URL)
    token = client.login("admin", "password")

    assert client.validate(token) is True

    client.logout(token)

    assert client.validate(token) is False
