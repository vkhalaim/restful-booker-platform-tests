import pytest
from api_clients.booking_client import BookingApiClient
from conftest import BOOKING_BASE_URL, make_booking_payload
from datetime import date, timedelta


def test_create_and_get_booking(created_booking, auth_token):
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)
    booked_room = booking.get_booking(response["bookingid"], auth_token)

    assert isinstance(booked_room, dict)
    assert booked_room["roomid"] == payload["roomid"]
    assert booked_room["firstname"] == payload["firstname"]
    assert booked_room["lastname"] == payload["lastname"]
    assert booked_room["bookingdates"] == payload["bookingdates"]


def test_deleted_booking_is_not_retrievable(created_booking, auth_token):
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)

    booking.delete_booking(response["bookingid"], auth_token)

    with pytest.raises(ValueError):
        booking.get_booking(response["bookingid"], auth_token)


def test_delete_without_token_fails(created_booking):
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)

    with pytest.raises(ValueError):
        booking.delete_booking(response["bookingid"], "wrong_token")


def test_deleting_already_deleted_booking_fails(created_booking, auth_token):
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)

    booking.delete_booking(response["bookingid"], auth_token)

    with pytest.raises(ValueError):
        booking.delete_booking(response["bookingid"], auth_token)


def test_update_booking_changes_data(created_booking, auth_token):
    """Update with a non-overlapping date range should succeed and persist changes."""
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)

    original_checkin = date.fromisoformat(payload["bookingdates"]["checkin"])
    original_checkout = date.fromisoformat(payload["bookingdates"]["checkout"])

    # Shift far enough to guarantee no overlap with the original range
    new_checkin = original_checkin + timedelta(days=100)
    new_checkout = original_checkout + timedelta(days=100)

    updated_payload = {
        **payload,
        "firstname": "Jake",
        "lastname": "Doe",
        "bookingdates": {"checkin": str(new_checkin), "checkout": str(new_checkout)},
    }
    updated_response = booking.update_booking(
        response["bookingid"], updated_payload, auth_token
    )

    updated_booking = updated_response["booking"]
    assert updated_booking["firstname"] == updated_payload["firstname"]
    assert updated_booking["lastname"] == updated_payload["lastname"]
    assert updated_booking["bookingdates"] == updated_payload["bookingdates"]


def test_update_booking_conflicts_with_own_partial_date_overlap(created_booking, auth_token):
    """
    Known platform bug: PUT /booking/{id} treats a partially overlapping
    new date range as a conflict with an EXISTING booking, without excluding
    the booking being updated itself from that check. Confirmed via a
    dedicated diagnostic script on 2026-07-27 — a full non-overlapping
    shift succeeds, while a 1-day partial shift fails with 409.
    """
    response, payload = created_booking

    booking = BookingApiClient(BOOKING_BASE_URL)

    original_checkin = date.fromisoformat(payload["bookingdates"]["checkin"])
    original_checkout = date.fromisoformat(payload["bookingdates"]["checkout"])

    partially_overlapping_payload = {
        **payload,
        "bookingdates": {
            "checkin": str(original_checkin + timedelta(days=1)),
            "checkout": str(original_checkout + timedelta(days=1)),
        },
    }

    with pytest.raises(ValueError):
        booking.update_booking(
            response["bookingid"], partially_overlapping_payload, auth_token
        )
