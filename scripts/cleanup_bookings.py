import requests

AUTH_BASE_URL = "http://localhost:3004/auth"
BOOKING_BASE_URL = "http://localhost:3000/booking"


def get_token():
    response = requests.post(
        f"{AUTH_BASE_URL}/login",
        json={"username": "admin", "password": "password"},
    )
    return response.cookies.get("token")


def cleanup_all_bookings():
    token = get_token()
    response = requests.get(
        f"{BOOKING_BASE_URL}/",
        cookies={"token": token},
    )
    booking_ids = [b["bookingid"] for b in response.json()["bookings"]]

    print(f"Found {len(booking_ids)} bookings, deleting...")

    for booking_id in booking_ids:
        delete_response = requests.delete(
            f"{BOOKING_BASE_URL}/{booking_id}",
            cookies={"token": token},
        )
        status = (
            "OK"
            if delete_response.status_code == 202
            else f"FAILED ({delete_response.status_code})"
        )
        print(f"  {booking_id}: {status}")

    print("Done.")


if __name__ == "__main__":
    cleanup_all_bookings()
