from playwright.sync_api import Page


class RoomDetailsPage:
    def __init__(self, page: Page, base_url: str = "http://localhost:3003"):
        self.page = page
        self.base_url = base_url

    def goto(self, room_id: int):
        self.page.goto(f"{self.base_url}/admin/room/{room_id}")

    def get_booking_row(self, firstname: str, lastname: str):
        return self.page.locator(".detail").filter(has_text=firstname).filter(has_text=lastname)
