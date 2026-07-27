import pytest
from api_clients.auth_client import AuthApiClient

AUTH_BASE_URL = "http://localhost:3004/auth"
BOOKING_BASE_URL = "http://localhost:3000/booking"


@pytest.fixture
def auth_token():
    client = AuthApiClient(AUTH_BASE_URL)
    token = client.login("admin", "password")
    yield token
    client.logout(token)
