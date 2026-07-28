from playwright.sync_api import Page, expect
from api_clients.booking_client import BookingApiClient
from pages.admin_login_page import AdminLoginPage
from pages.room_details_page import RoomDetailsPage
from conftest import make_booking_payload, BOOKING_BASE_URL, LOGIN_BASE_URL


def test_created_booking_is_visible_in_admin_ui(auth_token, page: Page):
    booking = BookingApiClient(BOOKING_BASE_URL)
    payload = make_booking_payload(roomid=1, firstname="Jake", lastname="Doe")
    created = booking.create_booking(payload)

    try:
        page.goto(LOGIN_BASE_URL)
        AdminLoginPage(page).login("admin", "password")

        expect(page.get_by_role("link", name="Rooms")).to_be_visible()

        room_page = RoomDetailsPage(page)
        room_page.goto(payload["roomid"])
        row = room_page.get_booking_row(payload["firstname"], payload["lastname"])

        expect(row).to_contain_text(payload["firstname"])
        expect(row).to_contain_text(payload["lastname"])
        expect(row).to_contain_text(payload["bookingdates"]["checkin"])
        expect(row).to_contain_text(payload["bookingdates"]["checkout"])
    finally:
        booking.delete_booking(created["bookingid"], auth_token)
