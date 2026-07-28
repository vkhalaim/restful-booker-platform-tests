import pytest
import uuid
import random
from datetime import date, timedelta
from api_clients.auth_client import AuthApiClient
from api_clients.booking_client import BookingApiClient

AUTH_BASE_URL = "http://localhost:3004/auth"
BOOKING_BASE_URL = "http://localhost:3000/booking"


def make_booking_payload(**kwargs):
    start_day = random.randint(1, 3650)
    duration = random.randint(1, 14)
    unique_suffix = uuid.uuid4().hex[:6]
    payload = {
        "roomid": random.choice([1, 2, 3]),
        "firstname": "John",
        "lastname": "Smith",
        "depositpaid": True,
        "email": f"john.{unique_suffix}@example.com",
        "phone": "12345678901",
        "bookingdates": {
            "checkin": str(date.today() + timedelta(days=start_day)),
            "checkout": str(date.today() + timedelta(days=start_day + duration)),
        },
    }

    checkin = kwargs.pop("checkin", payload["bookingdates"]["checkin"])
    checkout = kwargs.pop("checkout", payload["bookingdates"]["checkout"])

    payload.update(kwargs)
    payload["bookingdates"] = {"checkin": checkin, "checkout": checkout}

    return payload


@pytest.fixture
def auth_token():
    client = AuthApiClient(AUTH_BASE_URL)
    token = client.login("admin", "password")
    yield token
    client.logout(token)


@pytest.fixture
def created_booking(auth_token):
    booking = BookingApiClient(BOOKING_BASE_URL)
    payload = make_booking_payload()
    response = booking.create_booking(payload)
    yield response, payload
    try:
        booking.delete_booking(response["bookingid"], auth_token)
    except ValueError:
        pass
