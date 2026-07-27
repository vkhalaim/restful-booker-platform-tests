import pytest
import uuid
import random
from datetime import date, timedelta
from api_clients.booking_client import BookingApiClient
from conftest import BOOKING_BASE_URL


def make_booking_payload(**kwargs):
    start_day = random.randint(1, 3650)
    duration = random.randint(1, 14)
    unique_suffix = uuid.uuid4().hex[:6]
    payload = {
        "roomid": 1,
        "firstname": "John",
        "lastname": "Smith",
        "depositpaid": True,
        "email": f"john.{unique_suffix}@example.com",
        "phone": "12345678901",
        "bookingdates": {
            "checkin": str(date.today() + timedelta(days=start_day)),
            "checkout": str(date.today() + timedelta(days=start_day+duration)),
        },
    }

    checkin = kwargs.pop("checkin", payload["bookingdates"]["checkin"])
    checkout = kwargs.pop("checkout", payload["bookingdates"]["checkout"])

    payload.update(kwargs)
    payload["bookingdates"] = {"checkin": checkin, "checkout": checkout}

    return payload


def test_create_and_get_booking(auth_token):
    booking = BookingApiClient(BOOKING_BASE_URL)
    booking_payload = make_booking_payload()

    response = booking.create_booking(booking_payload)
    booked_room = booking.get_booking(response["bookingid"], auth_token)

    assert isinstance(booked_room, dict)
    assert booked_room["roomid"] == 1
    assert booked_room["firstname"] == booking_payload["firstname"]
    assert booked_room["lastname"] == booking_payload["lastname"]
    assert booked_room["bookingdates"] == booking_payload["bookingdates"]


def test_deleted_booking_is_not_retrievable(auth_token):
    booking = BookingApiClient(BOOKING_BASE_URL)
    booking_payload = make_booking_payload()

    response = booking.create_booking(booking_payload)

    booking.delete_booking(response["bookingid"], auth_token)

    with pytest.raises(ValueError):
        booking.get_booking(response["bookingid"], auth_token)


def test_delete_without_token_fails():
    booking = BookingApiClient(BOOKING_BASE_URL)
    booking_payload = make_booking_payload()
    created = booking.create_booking(booking_payload)

    with pytest.raises(ValueError):
        booking.delete_booking(created["bookingid"], "wrong_token")


def test_deleting_already_deleted_booking_fails(auth_token):
    booking = BookingApiClient(BOOKING_BASE_URL)
    booking_payload = make_booking_payload()

    response = booking.create_booking(booking_payload)    
    booking.delete_booking(response["bookingid"], auth_token)

    with pytest.raises(ValueError):
        booking.delete_booking(response["bookingid"], auth_token)
